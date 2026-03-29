import os
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"

engine = create_async_engine(DATABASE_URL, echo= False)

AsyncSessionLocal = async_sessionmaker(
    bind= engine,
    class_= AsyncSession,
    expire_on_commit= False
)

@asynccontextmanager
async def get_db_session():
    session = AsyncSessionLocal()

    try:
        yield session
        await session.commit()

    except Exception as error:
        await session.rollback()
        # TODO Tratar o erro

    finally:
        await session.close()


class Base(DeclarativeBase):
    pass
