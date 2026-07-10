"""
test database configuration He Gong Ju
"""

from importlib import import_module
from typing import AsyncGenerator, Generator

from alembic import command
from alembic.config import Config
from app.core.database import Base
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from tests.unit.test_config import test_settings


class TestDatabase:
 """test database Guan Li Qi"""

 def __init__(self, use_memory: bool = True):
 self.use_memory = use_memory
 self.database_url = (
 test_settings.MEMORY_DATABASE_URL
 if use_memory
 else test_settings.TEST_DATABASE_URL
)

 # Chuang Jian Yin Qing
 self.engine = create_engine(
 self.database_url,
 connect_args=(
 {"check_same_thread": False, "isolation_level": "DEFERRED"}
 if "sqlite" in self.database_url
 else {}
),
 poolclass=StaticPool if use_memory else None,
 echo=False, # She Zhi WeiTrueKe Yi Kan DaoSQLYu Ju
)

 # Que Bao Suo You model Bei Jia Zai Yi Zhu Ce to Base.metadata
 import_module("app.models")

 # create Hui Hua Gong Chang
 self.SessionLocal = sessionmaker(
 autocommit=False, autoflush=False, bind=self.engine
)

 # Qi Yong Wai Jian Yue Shu(SQLite)
 if "sqlite" in self.database_url:

 @event.listens_for(self.engine, "connect")
 def set_sqlite_pragma(dbapi_connection, connection_record):
 cursor = dbapi_connection.cursor()
 cursor.execute("PRAGMA foreign_keys=ON")
 cursor.close()

 def create_tables(self):
 """create Suo You table"""
 Base.metadata.create_all(bind=self.engine)

 def drop_tables(self):
 """delete Suo You table"""
 Base.metadata.drop_all(bind=self.engine)

 def get_session(self) -> Generator[Session, None, None]:
 """get database Hui Hua"""
 session = self.SessionLocal()
 try:
 yield session
 finally:
 session.close()

 def run_migrations(self):
 """Yun Xing Qian Yi"""
 alembic_cfg = Config("alembic.ini")
 alembic_cfg.set_main_option("sqlalchemy.url", self.database_url)

 # Yun Xing Qian Yi
 command.upgrade(alembic_cfg, "head")

 def reset_database(self):
 """Zhong Zhi database"""
 self.drop_tables()
 self.create_tables()


# Quan Ju test database Shi Li
test_db = TestDatabase(use_memory=True)


def get_test_db() -> Generator[Session, None, None]:
 """get test database Hui Hua De Yi Lai Zhu Ru Han Shu"""
 yield from test_db.get_session()


def setup_test_database():
 """set test database"""
 test_db.create_tables()


def teardown_test_database():
 """clean up test database"""
 test_db.drop_tables()


def reset_test_database():
 """Zhong Zhi test database"""
 test_db.reset_database()


# Yi Bu database Zhi Chi(Ru Guo Xu Yao)
class AsyncTestDatabase:
 """Yi Bu test database Guan Li Qi"""

 def __init__(self, use_memory: bool = True):
 self.use_memory = use_memory
 self.database_url = (
 test_settings.MEMORY_DATABASE_URL
 if use_memory
 else test_settings.TEST_DATABASE_URL
)

 # Zhuan Huan Wei Yi BuURL
 if self.database_url.startswith("sqlite:///"):
 self.async_database_url = self.database_url.replace(
 "sqlite:///", "sqlite+aiosqlite:///"
)
 else:
 self.async_database_url = self.database_url

 # create Yi Bu Yin Qing
 self.async_engine = create_async_engine(
 self.async_database_url,
 echo=False,
 poolclass=StaticPool if use_memory else None,
)

 # create Yi Bu Hui Hua Gong Chang
 self.AsyncSessionLocal = sessionmaker(
 self.async_engine, class_=AsyncSession, expire_on_commit=False
)

 async def create_tables(self):
 """create Suo You table"""
 async with self.async_engine.begin() as conn:
 await conn.run_sync(Base.metadata.create_all)

 async def drop_tables(self):
 """delete Suo You table"""
 async with self.async_engine.begin() as conn:
 await conn.run_sync(Base.metadata.drop_all)

 async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
 """get Yi Bu database Hui Hua"""
 async with self.AsyncSessionLocal() as session:
 yield session

 async def reset_database(self):
 """Zhong Zhi database"""
 await self.drop_tables()
 await self.create_tables()


# Quan Ju Yi Bu test database Shi Li
async_test_db = AsyncTestDatabase(use_memory=True)
