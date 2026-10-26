from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import select, text

from app.db.models import Base, RAGRecord
from tests.test_accounts import login


def test_migration_matches_models_and_preserves_records(client):
    login(client)
    database = client.app.state.db
    with database.engine.connect() as connection:
        assert connection.scalar(text("select version_num from alembic_version")) == "0001"
        assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
        assert connection.scalar(text("PRAGMA foreign_keys")) == 1
    with database.sessions.begin() as session:
        session.add(RAGRecord(id="interrupted", user_id=1, question="待处理", status="processing"))
    database.migrate()
    database.recover_interrupted()
    with database.sessions() as session:
        assert session.scalar(select(RAGRecord)).status == "interrupted"
