"""
pytest Pei Zhi Wen Jian

Ji Zhong Zhu Ce fixtures Cha Jian, Bing Bao Liu Jiu test Yin Yong De Jian Rong Han Shu.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Generator

# Tian Jia project Gen Mu Lu to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.unit.test_database import get_test_db as unit_get_test_db

pytest_plugins = [
 "tests.fixtures.asyncio_loop",
 "tests.fixtures.db",
 "tests.fixtures.client",
 "tests.fixtures.mock_ai_service",
 "tests.fixtures.selenium_driver",
 "tests.fixtures.markers",
]


def get_test_db() -> Generator:
 """Jian Rong Jiu test import path, Fu Yong Dan Yuan Ce Shi database Hui Hua Sheng Cheng Qi."""
 yield from unit_get_test_db()


def override_get_db() -> Generator:
 """Yong Yu FastAPI Yi Lai Fu Gai De database Hui Hua Sheng Cheng Qi."""
 yield from get_test_db()
