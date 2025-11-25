from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from core.settings import settings

engine = create_async_engine(
    settings.PG_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

LocalSession = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)