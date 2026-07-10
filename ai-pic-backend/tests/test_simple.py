"""
Jian Hua Ce Shi - validate Ji Ben Gong Neng
"""

import os
import sys

import pytest

# Tian Jia project Gen Mu Lu to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.mark.unit
def test_basic_functionality():
 """test Ji Ben Gong Neng"""
 assert 1 + 1 == 2
 assert "hello" == "hello"
 assert True is True


@pytest.mark.unit
def test_sqlite_memory_database():
 """testSQLiteNei Cun database"""
 import sqlite3

 # create Nei Cun database
 conn = sqlite3.connect(":memory:")
 cursor = conn.cursor()

 # create test table
 cursor.execute(
 """
 CREATE TABLE test_table (
 id INTEGER PRIMARY KEY,
 name TEXT NOT NULL
)
 """
)

 # Cha Ru Ce Shi Shu Ju
 cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test",))
 conn.commit()

 # Cha Xun Shu Ju
 cursor.execute("SELECT name FROM test_table WHERE id = 1")
 result = cursor.fetchone()

 assert result is not None
 assert result[0] == "test"

 conn.close()


@pytest.mark.unit
def test_json_serialization():
 """testJSONXu Lie Hua"""
 import json

 test_data = {
 "name": "Test IP",
 "tags": ["tag1", "tag2"],
 "metadata": {"key": "value"},
 }

 # Xu Lie Hua
 json_str = json.dumps(test_data)

 # Fan Xu Lie Hua
 parsed_data = json.loads(json_str)

 assert parsed_data["name"] == "Test IP"
 assert parsed_data["tags"] == ["tag1", "tag2"]
 assert parsed_data["metadata"]["key"] == "value"


@pytest.mark.unit
def test_alembic_import():
 """testAlembicimport"""
 try:
 from alembic import command
 from alembic.config import Config

 assert command is not None
 assert Config is not None
 except ImportError:
 pytest.fail("Alembic not properly installed")


@pytest.mark.unit
def test_sqlalchemy_import():
 """testSQLAlchemyimport"""
 try:
 from sqlalchemy import Column, create_engine
 from sqlalchemy.ext.declarative import declarative_base
 from sqlalchemy.orm import sessionmaker

 assert create_engine is not None
 assert Column is not None
 assert declarative_base is not None
 assert sessionmaker is not None
 except ImportError:
 pytest.fail("SQLAlchemy not properly installed")


@pytest.mark.unit
def test_factory_boy_import():
 """testFactory Boyimport"""
 try:
 import factory

 assert factory is not None
 except ImportError:
 pytest.fail("Factory Boy not properly installed")


@pytest.mark.unit
def test_pytest_import():
 """testpytestimport"""
 try:
 import pytest

 assert pytest is not None
 except ImportError:
 pytest.fail("pytest not properly installed")
