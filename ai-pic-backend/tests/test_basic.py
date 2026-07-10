"""
Ji Chu Ce Shi - validate test Kuang Jia Shi Fou normal work
"""

import pytest
from sqlalchemy import text
from tests.unit.test_database import reset_test_database, test_db


@pytest.mark.unit
def test_basic_functionality():
 """test Ji Ben Gong Neng"""
 assert 1 + 1 == 2
 assert "hello" == "hello"
 assert True is True


@pytest.mark.unit
def test_database_connection():
 """test database connection"""
 # Zhong Zhi test database
 reset_test_database()

 # Huo Qu Hui Hua
 session = next(test_db.get_session())

 try:
 # Zhi Xing Jian Dan Cha Xun
 result = session.execute(text("SELECT 1 as test_value"))
 value = result.scalar()
 assert value == 1

 finally:
 session.close()


@pytest.mark.unit
def test_imports():
 """test Zhong Yao Mo Kuai import"""
 from app.core.config import settings
 from app.models.user import User
 from app.models.virtual_ip import VirtualIP

 # Ji Ben Duan Yan
 assert User is not None
 assert VirtualIP is not None
 assert settings is not None
