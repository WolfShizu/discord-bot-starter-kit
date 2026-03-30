import os
import importlib
import pkgutil
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

def load_models():
    """Importa todos os módulos na pasta models"""
    models_path = os.path.join(os.path.dirname(__file__), "models")
    package_prefix = "app.services.database.base.models"

    for _, module_name, is_package in pkgutil.iter_modules([models_path]):
        if is_package:
            module_path = f"{package_prefix}.{module_name}"
            try:
                _ = importlib.import_module(module_path)
            except Exception as error:
                # TODO Tratar o erro
                pass

async def setup_database():
    load_models()

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

class Base(DeclarativeBase):
    pass
