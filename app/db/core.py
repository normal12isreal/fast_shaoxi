"""应用启动时迁移 SQLite；每次数据库操作用短会话，不跨模型等待。"""

import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, update
from sqlalchemy.orm import sessionmaker

from app.db.models import Message, RAGRecord
from app.services.knowledge import PROJECT_ROOT


class Database:
    def __init__(self):
        path = Path(os.environ.get("HANDBOOK_DATABASE_PATH", PROJECT_ROOT / "data/site.sqlite3"))
        path = path.resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(
            "sqlite:///" + path.as_posix(),
            connect_args={"check_same_thread": False, "timeout": 5},
        )

        @event.listens_for(self.engine, "connect")
        def sqlite_settings(connection, _):
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

        self.sessions = sessionmaker(self.engine, expire_on_commit=False)

    def migrate(self) -> None:
        config = Config()
        config.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))
        with self.engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")

    def recover_interrupted(self) -> None:
        # 单进程启动时，上一次进程未完成的调用不会自动重新执行。
        with self.sessions.begin() as session:
            session.execute(
                update(RAGRecord)
                .where(RAGRecord.status == "processing")
                .values(status="interrupted", error="服务重启，调用未完成。")
            )
            session.execute(
                update(Message)
                .where(Message.status == "pending")
                .values(status="failed", error="服务重启，调用未完成。")
            )

    def close(self) -> None:
        self.engine.dispose()
