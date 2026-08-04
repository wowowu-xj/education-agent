# -*- coding: utf-8 -*-
"""认证中间件的流式响应测试。

JWTAuthMiddleware 写成纯 ASGI 而不是 ``BaseHTTPMiddleware``，唯一原因就是
后者会把响应体经 anyio memory stream 转发。Phase 3 的
``/api/agent/chat/stream`` 依赖 SSE 逐块下发，所以这个性质必须有测试守住。

**这里踩过一个坑，记录下来免得重犯**：最初的测试断言的是「第二块必须在
第一块送达之后才产出」。这个断言对 ``BaseHTTPMiddleware`` **同样成立**
（实测 starlette 0.36.3），所以它根本抓不到回退，属于假的防护。

两种实现真正的差异是**背压**。实测数据（下游收到第一块后停 150ms）：

===================== ==================== ====================
实现                   收到第 1 块时已产出   停 150ms 后已产出
===================== ==================== ====================
纯 ASGI                1                    1
``BaseHTTPMiddleware`` 1                    2
===================== ==================== ====================

纯 ASGI 下生成器直接 await 下游的 ``send``，下游不消费、上游就不产出；
``BaseHTTPMiddleware`` 的内部 stream 有缓冲位，生产者会跑到消费者前面一块。
所以 :func:`test_streaming_response_is_backpressured` 才是真正的防回退测试。
"""
from __future__ import annotations

import asyncio

import pytest
from fastapi import FastAPI
from starlette.responses import StreamingResponse
from starlette.types import Message, Scope

from app.core.jwt import create_access_token
from app.middleware.auth import JWTAuthMiddleware

STREAM_PATH = "/api/agent/chat/stream"

# 下游拿到第一块后故意停顿的时长。实测 150ms 足以让 BaseHTTPMiddleware
# 的生产者跑到前面一块；留到 250ms 是给慢机器的余量。
BACKPRESSURE_WINDOW = 0.25


def _http_scope(path: str, *, token: str | None) -> Scope:
    """手工构造一个 GET 请求 scope。

    不用 TestClient / httpx 是因为它们的传输层自身可能缓冲响应体，
    那样就分辨不出缓冲发生在中间件还是测试客户端。直连 ASGI 接口最干净。
    """
    headers: list[tuple[bytes, bytes]] = [(b"host", b"testserver")]
    if token is not None:
        headers.append((b"authorization", f"Bearer {token}".encode()))
    return {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": headers,
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }


def _make_receive() -> "callable":
    """构造一个行为像真实客户端的 receive。

    第一次调用返回请求体，之后**挂起**（模拟"客户端始终不断开"）。

    必须挂起，不能直接 return：Starlette 的 ``StreamingResponse`` 会起一个
    ``while True: await receive()`` 的断连监听协程，如果 receive 里没有任何
    挂起点，这个循环就成了纯 CPU 忙等，连 ``asyncio.wait_for`` 的定时器都
    拿不到调度机会——测试会挂死而不是超时失败。
    """
    never_disconnect = asyncio.Event()
    state = {"first": True}

    async def receive() -> Message:
        if state["first"]:
            state["first"] = False
            return {"type": "http.request", "body": b"", "more_body": False}
        await never_disconnect.wait()
        return {"type": "http.disconnect"}  # pragma: no cover - 永不到达

    return receive


@pytest.mark.asyncio
async def test_streaming_response_is_backpressured() -> None:
    """下游不消费时，上游生成器不得继续产出。

    这是防止有人把 JWTAuthMiddleware 改回 ``BaseHTTPMiddleware`` 的关键测试：
    换回去之后生产者会跑到消费者前面，``produced_while_held`` 变成 2，断言失败。
    """
    produced: list[int] = []
    delivered: list[bytes] = []
    produced_while_held: list[int] = []

    app = FastAPI()
    app.add_middleware(JWTAuthMiddleware)

    async def chunks():
        for i in range(1, 4):
            produced.append(i)
            yield f"chunk-{i}".encode()

    @app.get(STREAM_PATH)
    async def stream() -> StreamingResponse:
        return StreamingResponse(chunks(), media_type="text/event-stream")

    async def send(message: Message) -> None:
        if message["type"] != "http.response.body":
            return
        body = message.get("body") or b""
        if not body:
            return
        delivered.append(body)
        if len(delivered) == 1:
            # 抓住第一块不放，给生成器充足的机会跑到前面去
            await asyncio.sleep(BACKPRESSURE_WINDOW)
            produced_while_held.append(len(produced))

    token = create_access_token(user_id=1, role="teacher", school_id=1)
    await asyncio.wait_for(
        app(_http_scope(STREAM_PATH, token=token), _make_receive(), send),
        timeout=10.0,
    )

    assert produced_while_held == [1], (
        f"下游持有第一块期间生成器已产出 {produced_while_held} 块，说明响应体被缓冲了。"
        "JWTAuthMiddleware 必须是纯 ASGI 中间件，不能用 BaseHTTPMiddleware。"
    )
    assert delivered == [b"chunk-1", b"chunk-2", b"chunk-3"]


@pytest.mark.asyncio
async def test_streaming_chunks_are_delivered_separately() -> None:
    """响应体分多条 ``http.response.body`` 消息下发，而不是攒成一条。

    注意：这条断言对 ``BaseHTTPMiddleware`` 也成立，因此它**不能**替代
    上面的背压测试，只是保证流式链路整体是通的。
    """
    delivered: list[bytes] = []

    app = FastAPI()
    app.add_middleware(JWTAuthMiddleware)

    @app.get(STREAM_PATH)
    async def stream() -> StreamingResponse:
        async def chunks():
            yield b"a"
            yield b"b"

        return StreamingResponse(chunks(), media_type="text/event-stream")

    async def send(message: Message) -> None:
        if message["type"] == "http.response.body" and message.get("body"):
            delivered.append(message["body"])

    token = create_access_token(user_id=1, role="teacher", school_id=1)
    await asyncio.wait_for(
        app(_http_scope(STREAM_PATH, token=token), _make_receive(), send),
        timeout=10.0,
    )

    assert delivered == [b"a", b"b"]


@pytest.mark.asyncio
async def test_streaming_path_still_requires_token() -> None:
    """流式接口同样受认证保护，不能因为改写中间件实现而漏掉。"""
    statuses: list[int] = []
    body_chunks: list[bytes] = []

    app = FastAPI()
    app.add_middleware(JWTAuthMiddleware)

    @app.get(STREAM_PATH)
    async def stream() -> StreamingResponse:  # pragma: no cover - 不应被调用
        return StreamingResponse(iter([b"data"]), media_type="text/event-stream")

    async def send(message: Message) -> None:
        if message["type"] == "http.response.start":
            statuses.append(message["status"])
        elif message["type"] == "http.response.body" and message.get("body"):
            body_chunks.append(message["body"])

    await asyncio.wait_for(
        app(_http_scope(STREAM_PATH, token=None), _make_receive(), send),
        timeout=10.0,
    )

    assert statuses == [401]
    assert b"missing_token" in b"".join(body_chunks)
