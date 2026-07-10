"""
work migration test
"""

import os
import tempfile

import pytest
from sqlalchemy import create_engine, inspect, text


@pytest.mark.integration
def test_database_creation_with_sqlalchemy():
    """test useSQLAlchemyZhi Jie create database"""
    # create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    try:
        db_url = f"sqlite:///{db_path}"

        # create Yin Qing
        engine = create_engine(db_url)

        # import model and create Biao
        from app.core.database import Base

        # create Suo You Biao
        Base.metadata.create_all(engine)

        # Jian Cha Biao Shi Fou exists
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        # validate key Biao exists
        expected_tables = ["users", "virtual_ips", "stories", "episodes", "scripts"]
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in {tables}"

        engine.dispose()

    finally:
        # clean up Lin Shi Wen Jian
        if os.path.exists(db_path):
            try:
                os.unlink(db_path)
            except PermissionError:
                pass


@pytest.mark.integration
def test_sqlite_crud_operations():
    """testSQLite CRUDoperation"""
    # create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    try:
        db_url = f"sqlite:///{db_path}"

        # create Yin Qing
        engine = create_engine(db_url)

        # import model and create Biao
        from app.core.database import Base

        # create Suo You Biao
        Base.metadata.create_all(engine)

        # test Ji BenSQLoperation
        with engine.connect() as conn:
            # test Cha Ru user
            conn.execute(
                text(
                    """
                INSERT INTO users (business_id, is_deleted, username, email, hashed_password, full_name, is_active, is_superuser)
                VALUES ('useruseruseruseruseruseruseruser', 0, 'testuser', 'test@example.com', 'hashed_password', 'Test User', 1, 0)
            """
                )
            )
            conn.commit()

            # test Cha Xun user
            result = conn.execute(
                text("SELECT username FROM users WHERE username = 'testuser'")
            )
            user = result.fetchone()
            assert user is not None
            assert user[0] == "testuser"

            # test Cha Ru virtualIP
            conn.execute(
                text(
                    """
                INSERT INTO virtual_ips (business_id, is_deleted, name, description, tags, is_active, is_public)
                VALUES ('vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv', 0, 'Test IP', 'Test description', '["tag1", "tag2"]', 1, 0)
            """
                )
            )
            conn.commit()

            # test Cha Xun virtualIP
            result = conn.execute(
                text("SELECT name, tags FROM virtual_ips WHERE name = 'Test IP'")
            )
            vip = result.fetchone()
            assert vip is not None
            assert vip[0] == "Test IP"

            # test Cha Ru story
            conn.execute(
                text(
                    """
                INSERT INTO stories (business_id, is_deleted, title, story_format, default_aspect_ratio, genre, premise, synopsis, main_characters, character_relationships, generation_params)
                VALUES ('storystorystorystorystorystory12', 0, 'Test Story', 'short_drama', '9:16', 'Romance', 'Test premise', 'Test synopsis', '[]', '{}', '{}')
            """
                )
            )
            conn.commit()

            # test Cha Xun story
            result = conn.execute(
                text("SELECT title FROM stories WHERE title = 'Test Story'")
            )
            story = result.fetchone()
            assert story is not None
            assert story[0] == "Test Story"

        engine.dispose()

    finally:
        # clean up Lin Shi Wen Jian
        if os.path.exists(db_path):
            try:
                os.unlink(db_path)
            except PermissionError:
                pass


@pytest.mark.integration
def test_foreign_key_relationships():
    """test Wai Jian relationship"""
    # create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    try:
        db_url = f"sqlite:///{db_path}"

        # create Yin Qing
        engine = create_engine(db_url)

        # import model and create Biao
        from app.core.database import Base

        # create Suo You Biao
        Base.metadata.create_all(engine)

        # test Wai Jian relationship
        with engine.connect() as conn:
            # Cha Ru virtualIP
            conn.execute(
                text(
                    """
                INSERT INTO virtual_ips (business_id, is_deleted, name, description, is_active, is_public)
                VALUES ('vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv', 0, 'Test IP', 'Test description', 1, 0)
            """
                )
            )
            conn.commit()

            # get virtualIP ID
            result = conn.execute(
                text("SELECT id FROM virtual_ips WHERE name = 'Test IP'")
            )
            vip_id = result.scalar()
            assert vip_id is not None

            # Cha Ru virtualIPimage
            conn.execute(
                text(
                    """
                INSERT INTO virtual_ip_images (business_id, is_deleted, virtual_ip_id, filename, original_filename, file_path, file_size, mime_type, category)
                VALUES ('iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii', 0, :vip_id, 'test.jpg', 'test.jpg', '/uploads/test.jpg', 1024, 'image/jpeg', 'avatar')
            """
                ),
                {"vip_id": vip_id},
            )
            conn.commit()

            # test relationship Cha Xun
            result = conn.execute(
                text(
                    """
                SELECT vi.name, vii.filename
                FROM virtual_ips vi
                JOIN virtual_ip_images vii ON vi.id = vii.virtual_ip_id
                WHERE vi.name = 'Test IP'
            """
                )
            )
            relation = result.fetchone()
            assert relation is not None
            assert relation[0] == "Test IP"
            assert relation[1] == "test.jpg"

        engine.dispose()

    finally:
        # clean up Lin Shi Wen Jian
        if os.path.exists(db_path):
            try:
                os.unlink(db_path)
            except PermissionError:
                pass


@pytest.mark.integration
def test_json_columns():
    """testJSONLieSQLiteJian Rong Xing"""
    # create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    try:
        db_url = f"sqlite:///{db_path}"

        # create Yin Qing
        engine = create_engine(db_url)

        # import model and create Biao
        from app.core.database import Base

        # create Suo You Biao
        Base.metadata.create_all(engine)

        # testJSONLie
        with engine.connect() as conn:
            # test virtualIP JSONBiao Qian
            conn.execute(
                text(
                    """
                INSERT INTO virtual_ips (business_id, is_deleted, name, description, tags, style_reference_images, is_active, is_public)
                VALUES ('vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv', 0, 'Test IP', 'Test description', '["tag1", "tag2", "tag3"]', '["http://example.com/image.jpg"]', 1, 0)
            """
                )
            )
            conn.commit()

            # Cha XunJSONdata
            result = conn.execute(
                text(
                    "SELECT tags, style_reference_images FROM virtual_ips WHERE name = 'Test IP'"
                )
            )
            data = result.fetchone()
            assert data is not None
            assert data[0] == '["tag1", "tag2", "tag3"]'
            assert data[1] == '["http://example.com/image.jpg"]'

            # test storyJSONZi Duan
            conn.execute(
                text(
                    """
                INSERT INTO stories (business_id, is_deleted, title, story_format, default_aspect_ratio, genre, premise, synopsis, main_characters, character_relationships, generation_params)
                VALUES ('storystorystorystorystorystory12', 0, 'Test Story', 'short_drama', '9:16', 'Romance', 'Test premise', 'Test synopsis',
                        '[{"name": "Character1", "role": "protagonist"}]',
                        '{"Character1": {"Character2": "friend"}}',
                        '{"temperature": 0.7}')
            """
                )
            )
            conn.commit()

            # Cha Xun storyJSONdata
            result = conn.execute(
                text(
                    "SELECT main_characters, character_relationships, generation_params FROM stories WHERE title = 'Test Story'"
                )
            )
            story_data = result.fetchone()
            assert story_data is not None
            assert '"name": "Character1"' in story_data[0]
            assert '"Character2": "friend"' in story_data[1]
            assert '"temperature": 0.7' in story_data[2]

        engine.dispose()

    finally:
        # clean up Lin Shi Wen Jian
        if os.path.exists(db_path):
            try:
                os.unlink(db_path)
            except PermissionError:
                pass
