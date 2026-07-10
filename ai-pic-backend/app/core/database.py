import logging
from contextlib import contextmanager

from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


# Gen Ju database type She Zhi connection parameters
def get_engine_config():
    """Gen Ju databaseURLtype get Xiang Ying Yin Qing configuration"""
    if "sqlite" in settings.DATABASE_URL:
        return {"connect_args": {"check_same_thread": False}}
    elif "mysql" in settings.DATABASE_URL:
        return {
            "pool_size": 20,
            "max_overflow": 0,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
            "connect_args": {"charset": "utf8mb4", "autocommit": False},
        }
    else:
        return {}


# create database Yin Qing
engine_config = get_engine_config()
engine = create_engine(settings.DATABASE_URL, **engine_config)

# create Hui Hua Gong Chang
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create basic model Lei
Base = declarative_base()


# Yi Lai Zhu Ru function
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_task_db():
    """Context manager for DB sessions in Celery task processors.

    Usage::

        with get_task_db() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
