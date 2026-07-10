"""
database migration test
"""

import pytest

# NOTE: This suite uses an in-process SQLite database. The project's Alembic
# migration chain targets MySQL in production and contains MySQL-only DDL (e.g.
# type/constraint alterations) that SQLite cannot execute end-to-end to head.
# We keep lightweight SQLite-focused migration coverage in
# `tests/test_migration_simple.py` instead.
pytest.skip(
 "Alembic head migrations are MySQL-targeted; skip SQLite-only migration suite.",
 allow_module_level=True,
)

import tempfile
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from app.models.script import Episode, Story
from app.models.user import User
from app.models.virtual_ip import VirtualIP, VirtualIPImage
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker


class TestMigrations:
 """migration test Lei"""

 def setup_method(self):
 """Mei Ge Ce Shi Fang Fa Qian De set"""
 # create temporary database
 self.db_file = tempfile.NamedTemporaryFile(delete=False)
 self.db_url = f"sqlite:///{self.db_file.name}"

 # Chuang Jian Yin Qing
 self.engine = create_engine(self.db_url, echo=False)

 # Chuang Jian Hui Hua
 self.SessionLocal = sessionmaker(bind=self.engine)

 # configurationAlembic
 self.alembic_cfg = Config("alembic.ini")
 self.alembic_cfg.set_main_option("sqlalchemy.url", self.db_url)

 def teardown_method(self):
 """Mei Ge Ce Shi Fang Fa Hou De clean up"""
 self.engine.dispose()
 Path(self.db_file.name).unlink(missing_ok=True)

 def test_migration_creates_all_tables(self):
 """test migration create Suo You table"""
 # Yun Xing Qian Yi
 command.upgrade(self.alembic_cfg, "head")

 # Jian Cha Biao Shi Fou exists
 inspector = inspect(self.engine)
 tables = inspector.get_table_names()

 expected_tables = [
 "users",
 "virtual_ips",
 "virtual_ip_images",
 "stories",
 "episodes",
 "scripts",
 "story_characters",
 "script_templates",
 "alembic_version",
 ]

 for table in expected_tables:
 assert table in tables, f"Table {table} not found"

 def test_migration_creates_correct_columns(self):
 """test migration create correct De Lie"""
 # Yun Xing Qian Yi
 command.upgrade(self.alembic_cfg, "head")

 inspector = inspect(self.engine)

 # Jian Cha Yong Hu Biao Lie
 user_columns = [col["name"] for col in inspector.get_columns("users")]
 expected_user_columns = [
 "id",
 "username",
 "email",
 "hashed_password",
 "full_name",
 "is_active",
 "is_superuser",
 "created_at",
 "updated_at",
 ]
 for col in expected_user_columns:
 assert col in user_columns, f"Column {col} not found in users table"

 # Jian Cha Xu NiIPBiao Lie
 vip_columns = [col["name"] for col in inspector.get_columns("virtual_ips")]
 expected_vip_columns = [
 "id",
 "name",
 "description",
 "tags",
 "background_story",
 "style_prompt",
 "style_reference_images",
 "default_avatar_url",
 "is_active",
 "is_public",
 "created_at",
 "updated_at",
 ]
 for col in expected_vip_columns:
 assert col in vip_columns, f"Column {col} not found in virtual_ips table"

 # check story Biao Lie
 story_columns = [col["name"] for col in inspector.get_columns("stories")]
 expected_story_columns = [
 "id",
 "title",
 "genre",
 "theme",
 "target_audience",
 "duration_minutes",
 "premise",
 "synopsis",
 "main_conflict",
 "resolution",
 "main_characters",
 "character_relationships",
 "setting_time",
 "setting_location",
 "world_building",
 "generation_prompt",
 "ai_model",
 "generation_params",
 "status",
 "is_public",
 "tags",
 "extra_metadata",
 "created_at",
 "updated_at",
 ]
 for col in expected_story_columns:
 assert col in story_columns, f"Column {col} not found in stories table"

 def test_migration_creates_indexes(self):
 """test migration create Suo Yin"""
 # Yun Xing Qian Yi
 command.upgrade(self.alembic_cfg, "head")

 inspector = inspect(self.engine)

 # Jian Cha Yong Hu table Suo Yin
 user_indexes = inspector.get_indexes("users")
 index_names = [idx["name"] for idx in user_indexes]

 expected_indexes = ["ix_users_id", "ix_users_username", "ix_users_email"]
 for idx in expected_indexes:
 assert idx in index_names, f"Index {idx} not found in users table"

 def test_migration_creates_foreign_keys(self):
 """test migration create Wai Jian"""
 # Yun Xing Qian Yi
 command.upgrade(self.alembic_cfg, "head")

 inspector = inspect(self.engine)

 # Jian Cha Xu NiIPimage Biao Wai Jian
 vip_image_fks = inspector.get_foreign_keys("virtual_ip_images")
 assert (
 len(vip_image_fks) > 0
), "No foreign keys found in virtual_ip_images table"

 # check episode Biao Wai Jian
 episode_fks = inspector.get_foreign_keys("episodes")
 assert len(episode_fks) > 0, "No foreign keys found in episodes table"

 # check script Biao Wai Jian
 script_fks = inspector.get_foreign_keys("scripts")
 assert len(script_fks) > 0, "No foreign keys found in scripts table"

 def test_migration_sqlite_compatibility(self):
 """test migration YuSQLiteJian Rong Xing"""
 # Yun Xing Qian Yi
 command.upgrade(self.alembic_cfg, "head")

 # test Ji Ben DeCRUDoperation
 session = self.SessionLocal()

 try:
 # Chuang Jian Yong Hu
 user = User(
 username="testuser",
 email="test@example.com",
 hashed_password="hashed_password",
 full_name="Test User",
)
 session.add(user)
 session.commit()

 # Cha Xun Yong Hu
 queried_user = (
 session.query(User).filter(User.username == "testuser").first()
)
 assert queried_user is not None
 assert queried_user.email == "test@example.com"

 # Chuang Jian Xu NiIP
 virtual_ip = VirtualIP(
 name="Test IP",
 description="Test description",
 tags=["test", "ip"],
 is_active=True,
)
 session.add(virtual_ip)
 session.commit()

 # Chuang Jian Xu NiIPimage
 vip_image = VirtualIPImage(
 virtual_ip_id=virtual_ip.id,
 filename="test.jpg",
 original_filename="test.jpg",
 file_path="/uploads/test.jpg",
 file_size=1024,
 mime_type="image/jpeg",
 category="avatar",
)
 session.add(vip_image)
 session.commit()

 # Ce Shi Guan Xi
 assert virtual_ip.images[0] == vip_image
 assert vip_image.virtual_ip == virtual_ip

 finally:
 session.close()

 def test_migration_downgrade(self):
 """test migration Hui Tui"""
 # Yun Xing Qian Yi
 command.upgrade(self.alembic_cfg, "head")

 # Jian Cha Biao exists
 inspector = inspect(self.engine)
 tables_before = inspector.get_table_names()
 assert "users" in tables_before

 # Hui Tui Qian Yi
 command.downgrade(self.alembic_cfg, "base")

 # Jian Cha Biao Bei delete
 inspector = inspect(self.engine)
 tables_after = inspector.get_table_names()

 # only Ying Gai Sheng Xiaalembic_versiontable
 assert "users" not in tables_after
 assert "virtual_ips" not in tables_after
 assert "stories" not in tables_after

 def test_migration_idempotent(self):
 """test migration Mi etc. Xing"""
 # run migration Liang Ci
 command.upgrade(self.alembic_cfg, "head")
 command.upgrade(self.alembic_cfg, "head")

 # Jian Cha Biao Reng Ran exists Qie structure correct
 inspector = inspect(self.engine)
 tables = inspector.get_table_names()

 expected_tables = [
 "users",
 "virtual_ips",
 "virtual_ip_images",
 "stories",
 "episodes",
 "scripts",
 "story_characters",
 "script_templates",
 "alembic_version",
 ]

 for table in expected_tables:
 assert table in tables, f"Table {table} not found after second migration"

 def test_migration_version_tracking(self):
 """test migration Ban Ben Zhui Zong"""
 # Yun Xing Qian Yi
 command.upgrade(self.alembic_cfg, "head")

 # check Ban Ben table
 session = self.SessionLocal()
 try:
 result = session.execute(text("SELECT version_num FROM alembic_version"))
 version = result.scalar()
 assert version is not None, "No version found in alembic_version table"

 # check Ban Ben format
 assert len(version) == 12, f"Invalid version format: {version}"

 finally:
 session.close()

 def test_migration_script_syntax(self):
 """test migration Jiao Ben Yu Fa"""
 # check migration Jiao Ben Mu Lu
 script_dir = ScriptDirectory.from_config(self.alembic_cfg)

 # get Suo You migration Jiao Ben
 revisions = script_dir.get_revisions("head", "base")

 assert len(revisions) > 0, "No migration scripts found"

 # check Mei Ge Jiao Ben De Yu Fa
 for revision in revisions:
 assert (
 revision.revision is not None
), f"Revision {revision} has no revision ID"
 assert revision.doc is not None, f"Revision {revision} has no description"

 def test_migration_json_columns(self):
 """testJSONLie DeSQLiteJian Rong Xing"""
 # Yun Xing Qian Yi
 command.upgrade(self.alembic_cfg, "head")

 session = self.SessionLocal()
 try:
 # testJSONLie
 virtual_ip = VirtualIP(
 name="Test IP",
 description="Test description",
 tags=["tag1", "tag2"],
 style_reference_images=["http://example.com/image1.jpg"],
 is_active=True,
)
 session.add(virtual_ip)
 session.commit()

 # Cha Xun Bing validateJSONdata
 queried_ip = (
 session.query(VirtualIP).filter(VirtualIP.name == "Test IP").first()
)
 assert queried_ip.tags == ["tag1", "tag2"]
 assert queried_ip.style_reference_images == [
 "http://example.com/image1.jpg"
 ]

 finally:
 session.close()


@pytest.mark.integration
class TestMigrationIntegration:
 """migration integration test"""

 def test_full_migration_workflow(self):
 """test complete De migration work Liu"""
 # create temporary database
 with tempfile.NamedTemporaryFile(delete=False) as db_file:
 db_url = f"sqlite:///{db_file.name}"

 # configurationAlembic
 alembic_cfg = Config("alembic.ini")
 alembic_cfg.set_main_option("sqlalchemy.url", db_url)

 try:
 # 1. Yun Xing Qian Yi
 command.upgrade(alembic_cfg, "head")

 # 2. create Yin Qing He Hui Hua
 engine = create_engine(db_url, echo=False)
 SessionLocal = sessionmaker(bind=engine)
 session = SessionLocal()

 # 3. create Ce Shi Shu Ju
 user = User(
 username="testuser",
 email="test@example.com",
 hashed_password="hashed_password",
 full_name="Test User",
)
 session.add(user)

 virtual_ip = VirtualIP(
 name="Test IP",
 description="Test description",
 tags=["test"],
 is_active=True,
)
 session.add(virtual_ip)

 story = Story(
 title="Test Story",
 genre="Romance",
 premise="A test story",
 synopsis="Test synopsis",
 main_characters=[{"name": "Character1"}],
 character_relationships={},
 generation_params={"temperature": 0.7},
)
 session.add(story)

 session.commit()

 # 4. Yan Zheng Shu Ju
 assert session.query(User).count() == 1
 assert session.query(VirtualIP).count() == 1
 assert session.query(Story).count() == 1

 # 5. Ce Shi Guan Xi
 story_with_episodes = Story(
 title="Story with Episodes",
 genre="Action",
 premise="Test premise",
 synopsis="Test synopsis",
 main_characters=[],
 character_relationships={},
 generation_params={},
)
 session.add(story_with_episodes)
 session.commit()

 episode = Episode(
 story_id=story_with_episodes.id,
 episode_number=1,
 title="Episode 1",
 summary="Test episode",
 duration_minutes=10,
 scene_descriptions=[],
 character_arcs={},
 key_events=[],
 emotional_beats=[],
 generation_params={},
)
 session.add(episode)
 session.commit()

 # Yan Zheng Guan Xi
 assert len(story_with_episodes.episodes) == 1
 assert episode.story == story_with_episodes

 session.close()
 engine.dispose()

 finally:
 Path(db_file.name).unlink(missing_ok=True)
