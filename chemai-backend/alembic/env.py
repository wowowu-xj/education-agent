"""Alembic 迁移环境配置

配置 target_metadata 指向 app.models 的 Base，让 autogenerate 能识别所有模型。
"""

from logging.config import fileConfig
from pathlib import Path
import os
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

# 将项目根目录加入 sys.path，让 alembic 能 import app.models
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from app.models import Base  # noqa: E402  必须在 sys.path 修改后导入
from app.models import (  # noqa: E402,F401  导入所有模型让 metadata 感知
    account,
    teacher,
    student,
    parent,
    school,
    grade,
    class_,
    teacher_class_subject,
    student_parent_binding,
)
from app.models.base import UTCDateTime  # noqa: E402  render_item 钩子需要

# Alembic 配置对象
config = context.config

# 从环境变量覆盖数据库 URL（生产环境用）
_db_url = os.getenv("DATABASE_URL")
if _db_url:
    config.set_main_option("sqlalchemy.url", _db_url)

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# autogenerate 的元数据来源
target_metadata = Base.metadata


def render_item(type_: str, obj: object, autogen_context: object) -> str | bool:
    """控制 autogenerate 如何把类型渲染成迁移脚本里的代码。

    默认行为会把自定义 ``TypeDecorator`` 渲染成完整点号路径
    （``app.models.base.UTCDateTime(timezone=True)``），但不会自动加上
    对应的 import，迁移一跑就 ``NameError: name 'app' is not defined``。

    :class:`~app.models.base.UTCDateTime` 只是一层 Python 侧的时区强制转换
    （写入转 UTC、读出补 tzinfo），它的 ``impl`` 就是 ``DateTime(timezone=True)``，
    在数据库里生成的 DDL 与原生 DateTime 完全相同。所以迁移脚本渲染成
    ``sa.DateTime(timezone=True)`` 既正确又不引入对 app 包的依赖——
    迁移不应该 import 业务代码，否则模型重构会让历史迁移失效。

    返回 ``False`` 表示交回默认渲染逻辑。
    """
    if type_ == "type" and isinstance(obj, UTCDateTime):
        return "sa.DateTime(timezone=True)"
    return False


def run_migrations_offline() -> None:
    """离线模式：不连数据库，直接生成 SQL 脚本"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # 检测字段类型变化
        render_as_batch=True,  # SQLite 兼容：ALTER TABLE 用 batch 模式
        render_item=render_item,  # UTCDateTime → sa.DateTime(timezone=True)
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式：连数据库执行迁移"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True,  # SQLite 兼容
            render_item=render_item,  # UTCDateTime → sa.DateTime(timezone=True)
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
