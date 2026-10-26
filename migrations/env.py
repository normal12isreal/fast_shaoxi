"""连接由应用或 scripts/migrate.py 提供，不在迁移文件保存路径和凭据。"""

from alembic import context

from app.db.models import Base

context.configure(connection=context.config.attributes["connection"], target_metadata=Base.metadata)
with context.begin_transaction():
    context.run_migrations()
