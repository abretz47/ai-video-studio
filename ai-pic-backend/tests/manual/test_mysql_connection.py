#!/usr/bin/env python3
"""
MySQLconnection test Jiao Ben

testMySQLdatabase connection and Ji Ben Cao Zuo
"""

import sys
from pathlib import Path

# Tian Jia project Gen Mu Lu toPythonpath
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_mysql_connection():
    """testMySQLconnection"""
    print("=" * 60)
    print("MySQLconnection test")
    print("=" * 60)

    try:
        # testPyMySQLZhi Jie connection
        print("1. testPyMySQLZhi Jie connection...")
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
            print(f"   ✅ MySQLBan Ben: {version}")

            cursor.execute("SELECT DATABASE()")
            database = cursor.fetchone()[0]
            print(f"   ✅ Dang Qian database: {database}")

            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"   ✅ Biao count: {len(tables)}")
            if tables:
                print(f"   Biao list: {[table[0] for table in tables]}")

        connection.close()
        print("   ✅ PyMySQLconnection test Cheng Gong")

    except Exception as e:
        print(f"   ❌ PyMySQLconnection failed: {str(e)}")
        return False

    try:
        # testSQLAlchemyconnection
        print("\n2. testSQLAlchemyconnection...")
        from app.core.database import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            print(f"   ✅ SQLAlchemyconnection Cheng Gong，MySQLBan Ben: {version}")

            result = conn.execute(text("SELECT DATABASE()"))
            database = result.fetchone()[0]
            print(f"   ✅ Dang Qian database: {database}")

    except Exception as e:
        print(f"   ❌ SQLAlchemyconnection failed: {str(e)}")
        return False

    try:
        # test configuration Jia Zai
        print("\n3. test configuration Jia Zai...")
        from app.core.config import settings

        print(f"   ✅ databaseURL: {settings.DATABASE_URL}")
        print(f"   ✅ Xiang Mu Ming Cheng: {settings.PROJECT_NAME}")

    except Exception as e:
        print(f"   ❌ configuration Jia Zai failed: {str(e)}")
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
            # create test Biao
            print("1. create test Biao...")
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
            print("   ✅ test Biao create Cheng Gong")

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
            print("   ✅ Ce Shi Shu Ju Cha Ru Cheng Gong")

            # Cha Xun Ce Shi Shu Ju
            print("\n3. Cha Xun Ce Shi Shu Ju...")
            result = conn.execute(text("SELECT * FROM test_table"))
            rows = result.fetchall()
            print(f"   ✅ Cha Xun to {len(rows)} Tiao record")
            for row in rows:
                print(f"      ID: {row[0]}, Name: {row[1]}, Created: {row[2]}")

            # clean up test Biao
            print("\n4. clean up test Biao...")
            conn.execute(text("DROP TABLE IF EXISTS test_table"))
            conn.commit()
            print("   ✅ test Biao clean up Cheng Gong")

        print("\n" + "=" * 60)
        print("✅ database operation Ce Shi Tong Guo!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"   ❌ database operation test failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_mysql_connection()
    if success:
        test_database_operations()
    else:
        sys.exit(1)
