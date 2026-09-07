from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    """FastAPI dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

def _migrate_sqlite_schema(sync_conn):
    """Safely apply schema migrations for existing SQLite tables."""
    for table_name in ["sessions", "journal_entries", "mood_logs"]:
        res = sync_conn.execute(text(f"PRAGMA table_info({table_name});")).fetchall()
        column_names = [row[1] for row in res]
        if column_names and "user_id" not in column_names:
            sync_conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN user_id VARCHAR(36) REFERENCES users(id);"))

async def init_db():
    """Initialize database tables and run lightweight migrations."""
    # Ensure all models are imported so Base.metadata contains them
    import app.models  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_migrate_sqlite_schema)
