import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'app', '.env')

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path)
    DATABASE_URL = (
        f"postgresql+asyncpg://{os.getenv('POSTGRESQL_ADDON_USER')}:"
        f"{os.getenv('POSTGRESQL_ADDON_PASSWORD')}@"
        f"{os.getenv('POSTGRESQL_ADDON_HOST')}:"
        f"{os.getenv('POSTGRESQL_ADDON_PORT')}/"
        f"{os.getenv('POSTGRESQL_ADDON_DB')}"
    )

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session():
    async with async_session() as session:
        yield session