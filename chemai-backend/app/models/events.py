# -*- coding: utf-8 -*-
"""ORM 事件监听器。

这里集中放置所有 SQLAlchemy session/mapper 事件，在 ``app/models/__init__``
import 本模块时自动注册——不需要在业务代码里主动调用什么初始化函数。

**Teacher.role → Account.role 同步**
--------------------------------------
决策 #12：Account.role 冗余缓存角色，目的是让登录时无需 JOIN Teacher 表。
冗余字段有一个不变量：凡是 teacher_id 指向同一个 Teacher 的 Account，
其 role 值必须与 Teacher.role 一致。

如果这个不变量不被强制执行，后果是：
- 管理员在后台把 张三 从 teacher 提升为 academic_admin
- 张三已经登录，JWT 里的 role 还是 teacher，直到下次重新登录才改变——
  这本来是正常的 JWT 有效期行为
- 但现在 **下一次登录也拿不到新 role**：登录时从 Account.role 读缓存，
  而缓存没有被同步，所以 张三 的 JWT 永远是 teacher 角色

修复：在 before_flush 里检测 Teacher.role 变更，立刻把对应 Account.role
改到同一 session，让它们参与同一个事务提交。

实现细节见 :func:`_sync_teacher_role_to_account`。
"""
from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models.teacher import Teacher


def _sync_teacher_role_to_account(
    session: Session, flush_context: object, instances: object
) -> None:
    """在 flush 前把 Teacher.role 变更同步到 Account.role。

    遍历 ``session.dirty`` 里的 Teacher 对象；凡是 role 属性有实质变化的，
    把它绑定的 Account（如果存在）也改成相同的值。

    修改是对 ORM 对象直接赋值，不走 bulk UPDATE，好处是：
    1. 参与同一个 flush 周期，保证原子性。
    2. 不需要处理 ``synchronize_session``——直接改的就是 session 里的对象。
    3. 如果 Account 已在 session 中被其他代码修改过（attribute history），
       这里的赋值会追加到那份变更上，而不是覆盖掉。

    注意：`account` 是懒加载关系。在 `before_flush` 里做懒加载有触发递归
    flush 的风险；用 `no_autoflush` 上下文保护。
    """
    for obj in session.dirty:
        if not isinstance(obj, Teacher):
            continue
        # 检查 role 属性是否真的变了（added vs deleted history）
        from sqlalchemy.orm import attributes

        attr_history = attributes.get_history(obj, "role")
        if not attr_history.added:
            # role 没有变（新值 == 旧值，或属性根本未被赋值）
            # 注意：不能用 attr_history.deleted，因为 commit() 之后属性变成
            # expired 状态，直接赋新值时 SQLAlchemy 不会加载旧值，
            # deleted=[] 而 added=[new_value]——用 added 才能正确检测到变更。
            continue

        new_role_value = obj.role.value if hasattr(obj.role, "value") else str(obj.role)

        with session.no_autoflush:
            if obj.account is not None:
                obj.account.role = new_role_value


def register_events() -> None:
    """注册所有 session 事件监听器。在 models/__init__ 里调用一次。"""
    event.listen(Session, "before_flush", _sync_teacher_role_to_account)
