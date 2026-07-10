#!/usr/bin/env python3
"""
MySQLconnection test Jiao Ben

testMySQLdatabase connection He Ji Ben Cao Zuo
"""

import sys
from pathlib import Path

# Tian Jia project Gen Mu Lu toPythonpath
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_mysql_connection():
 """testMySQLconnection"""
 print("=" * 60)
 print("MySQLLian Jie Ce Shi")
 print("=" * 60)

 try:
 # testPyMySQLZhi Jie Lian Jie
 print("1. testPyMySQLZhi Jie Lian Jie...")
 import pymysql

 connection = pymysql.connect(
 host="127.0.0.1",
 port=13306,
 user="root",
 password="Pa88word",
 database="ai_video_studio",
 charset="utf8mb4",
)

 with connection.cursor() as cursor:
 cursor.execute("SELECT VERSION()")
 version = cursor.fetchone()[0]
 print(f" ✅ MySQLBan Ben: {version}")

 cursor.execute("SELECT DATABASE()")
 database = cursor.fetchone()[0]
 print(f" ✅ Dang Qian database: {database}")

 cursor.execute("SHOW TABLES")
 tables = cursor.fetchall()
 print(f" ✅ Biao Shu Liang: {len(tables)}")
 if tables:
 print(f" Biao Lie Biao: {[table[0] for table in tables]}")

 connection.close()
 print(" ✅ PyMySQLconnection test success")

 except Exception as e:
 print(f" ❌ PyMySQLLian Jie Shi Bai: {str(e)}")
 return False

 try:
 # testSQLAlchemyconnection
 print("\n2. testSQLAlchemyconnection...")
 from app.core.database import engine
 from sqlalchemy import text

 with engine.connect() as conn:
 result = conn.execute(text("SELECT VERSION()"))
 version = result.fetchone()[0]
 print(f" ✅ SQLAlchemyLian Jie Cheng Gong, MySQLBan Ben: {version}")

 result = conn.execute(text("SELECT DATABASE()"))
 database = result.fetchone()[0]
 print(f" ✅ Dang Qian database: {database}")

 except Exception as e:
 print(f" ❌ SQLAlchemyLian Jie Shi Bai: {str(e)}")
 return False

 try:
 # test configuration Jia Zai
 print("\n3. test configuration Jia Zai...")
 from app.core.config import settings

 print(f" ✅ databaseURL: {settings.DATABASE_URL}")
 print(f" ✅ Xiang Mu Ming Cheng: {settings.PROJECT_NAME}")

 except Exception as e:
 print(f" ❌ configuration Jia Zai failed: {str(e)}")
 return False

 print("\n" + "=" * 60)
 print("✅ Suo You connection Ce Shi Tong Guo!")
 print("=" * 60)
 return True


def test_database_operations():
 """test database Ji Ben Cao Zuo"""
 print("\n" + "=" * 60)
 print("database operation test")
 print("=" * 60)

 try:
 from app.core.database import engine
 from sqlalchemy import text

 with engine.connect() as conn:
 # create test table
 print("1. create test table...")
 conn.execute(
 text(
 """
 CREATE TABLE IF NOT EXISTS test_table (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(100) NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
 """
)
)
 conn.commit()
 print(" ✅ test table create success")

 # Cha Ru Ce Shi Shu Ju
 print("\n2. Cha Ru Ce Shi Shu Ju...")
 conn.execute(
 text(
 """
 INSERT INTO test_table (name) VALUES ('Ce Shi Shu Ju')
 """
)
)
 conn.commit()
 print(" ✅ Ce Shi Shu Ju Cha Ru success")

 # Cha Xun Ce Shi Shu Ju
 print("\n3. Cha Xun Ce Shi Shu Ju...")
 result = conn.execute(text("SELECT * FROM test_table"))
 rows = result.fetchall()
 print(f" ✅ Cha Xun Dao {len(rows)} Tiao Ji Lu")
 for row in rows:
 print(f" ID: {row[0]}, Name: {row[1]}, Created: {row[2]}")

 # clean up test table
 print("\n4. clean up test table...")
 conn.execute(text("DROP TABLE IF EXISTS test_table"))
 conn.commit()
 print(" ✅ test table clean up success")

 print("\n" + "=" * 60)
 print("✅ database operation Ce Shi Tong Guo!")
 print("=" * 60)
 return True

 except Exception as e:
 print(f" ❌ database operation test failed: {str(e)}")
 return False


if __name__ == "__main__":
 success = test_mysql_connection()
 if success:
 test_database_operations()
 else:
 sys.exit(1)
