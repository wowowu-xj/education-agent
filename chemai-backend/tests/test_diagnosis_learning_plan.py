# -*- coding: utf-8 -*-
"""学习计划生成 + 缓存测试（L1）。

覆盖 task 8.1：障碍类型中文映射、24h 缓存命中不重复调用 LLM、
缓存过期 / 主动失效后刷新。
"""
from __future__ import annotations

from app.core.enums import BarrierType
from chem_skills.chemistry_diagnosis.engine.learning_plan import (
    PLAN_CACHE_TTL,
    LearningPlanGenerator,
    build_plan_messages,
)


class FakeLLM:
    """记录调用次数与 messages 的假 LLM。"""

    def __init__(self, result: dict | None = None) -> None:
        self._result = result or {"title": "计划", "goal": "补强", "items": ["任务一"], "duration_days": 7}
        self.calls = 0
        self.messages: list[list[dict[str, str]]] = []

    def chat(self, messages: list[dict[str, str]]) -> dict:
        self.calls += 1
        self.messages.append(messages)
        return self._result


class TestBuildPlanMessages:
    def test_barrier_chinese_mapping(self) -> None:
        messages = build_plan_messages(
            student_name="小明",
            barrier_types=[BarrierType.CONCEPT],
            weak_knowledge_points=["化学平衡"],
        )
        user = messages[1]["content"]
        assert "小明" in user
        assert "概念理解型-基础概念和原理掌握不扎实" in user
        assert "化学平衡" in user

    def test_multiple_barriers_and_empty_kp(self) -> None:
        messages = build_plan_messages(
            student_name="小明",
            barrier_types=[BarrierType.CONCEPT, BarrierType.READING],
            weak_knowledge_points=[],
        )
        user = messages[1]["content"]
        assert "概念理解型" in user
        assert "审题障碍型" in user
        assert "暂无" in user  # 无知识点时占位

    def test_empty_barriers(self) -> None:
        messages = build_plan_messages(
            student_name="小明", barrier_types=[], weak_knowledge_points=[]
        )
        assert "暂无明确障碍" in messages[1]["content"]

    def test_student_name_delimited_and_prompt_safety_note(self) -> None:
        messages = build_plan_messages(
            student_name="小明", barrier_types=[], weak_knowledge_points=[]
        )
        # 姓名用 <<<>>> 定界包裹（code-review F1）
        assert "学生姓名：<<<小明>>>" in messages[1]["content"]
        # 系统提示词声明输入为数据、忽略指令
        assert "忽略" in messages[0]["content"] and "指令" in messages[0]["content"]


class TestCache:
    def test_cache_hit_no_second_llm_call(self) -> None:
        fake = FakeLLM()
        gen = LearningPlanGenerator(fake)
        kwargs = dict(
            student_id=1,
            student_name="小明",
            barrier_types=[BarrierType.CONCEPT],
            weak_knowledge_points=["化学平衡"],
        )
        first = gen.generate(**kwargs)
        second = gen.generate(**kwargs)
        assert fake.calls == 1
        assert first == second

    def test_different_student_separate_cache(self) -> None:
        fake = FakeLLM()
        gen = LearningPlanGenerator(fake)
        base = dict(
            student_name="小明",
            barrier_types=[BarrierType.CONCEPT],
            weak_knowledge_points=["化学平衡"],
        )
        gen.generate(student_id=1, **base)
        gen.generate(student_id=2, **base)
        assert fake.calls == 2

    def test_cache_expiry_refreshes(self) -> None:
        fake = FakeLLM()
        now = [1000.0]

        def clock() -> float:
            return now[0]

        gen = LearningPlanGenerator(fake, clock=clock)
        base = dict(
            student_id=1,
            student_name="小明",
            barrier_types=[BarrierType.CONCEPT],
            weak_knowledge_points=["化学平衡"],
        )
        gen.generate(**base)
        # 推进时钟越过 TTL
        now[0] += PLAN_CACHE_TTL + 1
        gen.generate(**base)
        assert fake.calls == 2

    def test_invalidate_refreshes(self) -> None:
        fake = FakeLLM()
        gen = LearningPlanGenerator(fake)
        base = dict(
            student_id=1,
            student_name="小明",
            barrier_types=[BarrierType.CONCEPT],
            weak_knowledge_points=["化学平衡"],
        )
        gen.generate(**base)
        gen.invalidate(1)
        gen.generate(**base)
        assert fake.calls == 2

    def test_peek_does_not_generate(self) -> None:
        fake = FakeLLM()
        gen = LearningPlanGenerator(fake)
        assert gen.peek(1) is None
        assert fake.calls == 0
