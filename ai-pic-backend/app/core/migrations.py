"""
database migration core module

Ti Gong andFastAPIJia Gou Yi Zhi database migration Ji Zhi, Kuo ZhanAlembicfeature
"""

import importlib.util
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from app.core.config import settings
from app.core.database import Base
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


class MigrationError(Exception):
    """migration exception"""

    pass


class MigrationManager:
    """database migration manager"""

    def __init__(self, engine: Engine = None):
        self.engine = engine or create_engine(settings.DATABASE_URL)
        self.config = self._get_alembic_config()
        self.script_dir = ScriptDirectory.from_config(self.config)

    def _get_alembic_config(self) -> Config:
        """getAlembicconfiguration"""
        # get Xiang Mu Gen Mu Lu
        project_root = Path(__file__).parent.parent.parent
        alembic_ini_path = project_root / "alembic.ini"

        if not alembic_ini_path.exists():
            raise MigrationError(f"找不到alembic.ini文件: {alembic_ini_path}")

        config = Config(str(alembic_ini_path))
        config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

        return config

    def get_current_revision(self) -> Optional[str]:
        """get current database version"""
        try:
            with self.engine.connect() as conn:
                context = MigrationContext.configure(conn)
                return context.get_current_revision()
        except Exception as e:
            logger.error(f"获取当前版本失败: {e}")
            return None

    def get_head_revision(self) -> Optional[str]:
        """get Zui Xin version"""
        try:
            return self.script_dir.get_current_head()
        except Exception as e:
            logger.error(f"获取最新版本失败: {e}")
            return None

    def get_migration_history(self) -> List[Dict[str, Any]]:
        """get migration Li Shi"""
        history = []
        try:
            for revision in self.script_dir.walk_revisions():
                history.append(
                    {
                        "revision": revision.revision,
                        "down_revision": revision.down_revision,
                        "message": revision.doc,
                        "branch_labels": revision.branch_labels,
                        "depends_on": revision.depends_on,
                        "create_date": getattr(revision.module, "create_date", None),
                    }
                )
        except Exception as e:
            logger.error(f"获取迁移历史失败: {e}")

        return history

    def check_migration_status(self) -> Dict[str, Any]:
        """Check migration status"""
        current = self.get_current_revision()
        head = self.get_head_revision()

        status = {
            "current_revision": current,
            "head_revision": head,
            "is_up_to_date": current == head,
            "needs_upgrade": current != head,
            "database_exists": self._check_database_exists(),
        }

        if current and head:
            # check Shi Fou has not Ying Yong migration
            pending_migrations = self._get_pending_migrations(current, head)
            status["pending_migrations"] = pending_migrations
            status["pending_count"] = len(pending_migrations)

        return status

    def _check_database_exists(self) -> bool:
        """check database Shi Fou Cun Zai"""
        try:
            with self.engine.connect() as conn:
                # Chang Shi execute Jian Dan Cha Xun
                conn.execute(text("SELECT 1"))
                return True
        except Exception:
            return False

    def _get_pending_migrations(self, current: str, head: str) -> List[str]:
        """get pending Ying Yong migration"""
        pending = []
        try:
            for revision in self.script_dir.walk_revisions(head, current):
                if revision.revision != current:
                    pending.append(revision.revision)
        except Exception as e:
            logger.error(f"获取待应用迁移失败: {e}")

        return pending

    def create_migration(self, message: str, autogenerate: bool = True) -> str:
        """create Xin migration file"""
        try:
            # Sheng Cheng time Chuo Zuo Weirevision idYi Bu Fen
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            command.revision(
                self.config,
                message=f"{timestamp}_{message}",
                autogenerate=autogenerate,
            )

            logger.info(f"迁移文件创建成功: {message}")
            return self.get_head_revision()

        except Exception as e:
            logger.error(f"创建迁移失败: {e}")
            raise MigrationError(f"创建迁移失败: {e}")

    def upgrade(self, revision: str = "head") -> bool:
        """escalate database"""
        try:
            logger.info(f"开始升级数据库到版本: {revision}")
            command.upgrade(self.config, revision)
            logger.info("database escalate successful")
            return True
        except Exception as e:
            logger.error(f"数据库升级失败: {e}")
            raise MigrationError(f"数据库升级失败: {e}")

    def downgrade(self, revision: str) -> bool:
        """Jiang Ji database"""
        try:
            logger.info(f"开始降级数据库到版本: {revision}")
            command.downgrade(self.config, revision)
            logger.info("database Jiang Ji successful")
            return True
        except Exception as e:
            logger.error(f"数据库降级失败: {e}")
            raise MigrationError(f"数据库降级失败: {e}")

    def stamp(self, revision: str) -> bool:
        """Biao Ji database version(not run migration)"""
        try:
            logger.info(f"标记数据库版本: {revision}")
            command.stamp(self.config, revision)
            logger.info("version Biao Ji successful")
            return True
        except Exception as e:
            logger.error(f"版本标记失败: {e}")
            raise MigrationError(f"版本标记失败: {e}")

    def validate_migrations(self) -> Dict[str, Any]:
        """validation migration file Wan Zheng Xing"""
        validation_result = {"valid": True, "errors": [], "warnings": []}

        try:
            # check migration file Yu Fa
            for revision in self.script_dir.walk_revisions():
                try:
                    # Chang Shi Dao Ru migration module
                    spec = importlib.util.spec_from_file_location(
                        f"migration_{revision.revision}", revision.path
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        # check Bi Xu function
                        if not hasattr(module, "upgrade"):
                            validation_result["errors"].append(
                                f"迁移 {revision.revision} 缺少 upgrade 函数"
                            )
                            validation_result["valid"] = False

                        if not hasattr(module, "downgrade"):
                            validation_result["warnings"].append(
                                f"迁移 {revision.revision} 缺少 downgrade 函数"
                            )

                except Exception as e:
                    validation_result["errors"].append(
                        f"迁移 {revision.revision} 语法错误: {e}"
                    )
                    validation_result["valid"] = False

        except Exception as e:
            validation_result["errors"].append(f"验证过程失败: {e}")
            validation_result["valid"] = False

        return validation_result

    def backup_before_migration(self) -> Optional[str]:
        """migration before backup database(MySQL)"""
        if "mysql" not in settings.DATABASE_URL:
            logger.warning("current database Bu ShiMySQL, Tiao Guo backup")
            return None

        try:
            import subprocess
            from urllib.parse import urlparse

            # Parse database URL
            parsed = urlparse(
                settings.DATABASE_URL.replace("mysql+pymysql://", "mysql://")
            )

            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"backup_{timestamp}.sql"
            backup_path = Path(__file__).parent.parent.parent / "backups" / backup_file
            backup_path.parent.mkdir(exist_ok=True)

            # Build mysqldump command
            cmd = [
                "mysqldump",
                f"--host={parsed.hostname}",
                f"--port={parsed.port}",
                f"--user={parsed.username}",
                f"--password={parsed.password}",
                "--single-transaction",
                "--routines",
                "--triggers",
                parsed.path.lstrip("/"),
            ]

            # Execute backup
            with open(backup_path, "w") as f:
                result = subprocess.run(
                    cmd, stdout=f, stderr=subprocess.PIPE, text=True
                )

            if result.returncode == 0:
                logger.info(f"数据库备份成功: {backup_path}")
                return str(backup_path)
            else:
                logger.error(f"数据库备份失败: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"备份过程失败: {e}")
            return None

    def get_schema_diff(self) -> Dict[str, Any]:
        """get current database and model Cha Yi"""
        try:
            from alembic.autogenerate import compare_metadata

            with self.engine.connect() as conn:
                context = MigrationContext.configure(conn)
                diff = compare_metadata(context, Base.metadata)

                return {
                    "has_changes": len(diff) > 0,
                    "changes": [str(change) for change in diff],
                    "change_count": len(diff),
                }

        except Exception as e:
            logger.error(f"获取模式差异失败: {e}")
            return {"has_changes": False, "error": str(e)}


class DataSeeder:
    """data seed manager"""

    def __init__(self, engine: Engine = None):
        self.engine = engine or create_engine(settings.DATABASE_URL)
        self.seeds_dir = Path(__file__).parent.parent.parent / "seeds"
        self.seeds_dir.mkdir(exist_ok=True)

    def create_seed_file(self, name: str) -> Path:
        """create seed file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.py"
        seed_file = self.seeds_dir / filename

        template = '''"""
data seed file: {name}
create time: {create_time}
"""

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import *

def seed_data():
 """execute data seed"""
    db = SessionLocal()
    try:
 # TODO: in here Tian Jia seed data

 # Shi Li:
        # user = User(username="admin", email="admin@example.com")
        # db.add(user)
        # db.commit()

 print(f"seed data {name} execute successful")

    except Exception as e:
 print(f"seed data execute failed: {__PH_0__}")
        db.rollback()
        raise
    finally:
        db.close()

def rollback_data():
 """Hui Gun seed data"""
    db = SessionLocal()
    try:
 # TODO: in here Tian Jia Hui Gun Luo Ji

 print(f"seed data {name} Hui Gun successful")

    except Exception as e:
 print(f"seed data Hui Gun failed: {__PH_0__}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
'''.format(
            name=name, create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        seed_file.write_text(template, encoding="utf-8")
        logger.info(f"种子文件创建成功: {seed_file}")
        return seed_file

    def run_seed(self, seed_name: str) -> bool:
        """run Zhi Ding seed"""
        try:
            seed_files = list(self.seeds_dir.glob(f"*{seed_name}.py"))
            if not seed_files:
                raise ValueError(f"找不到种子文件: {seed_name}")

            seed_file = seed_files[0]

            # Dong Tai Dao Ru and execute seed
            spec = importlib.util.spec_from_file_location("seed_module", seed_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, "seed_data"):
                    module.seed_data()
                    logger.info(f"种子 {seed_name} 执行成功")
                    return True
                else:
                    raise ValueError(f"种子文件 {seed_file} 缺少 seed_data 函数")
            else:
                raise ValueError(f"无法加载种子文件: {seed_file}")

        except Exception as e:
            logger.error(f"种子执行失败: {e}")
            raise

    def run_all_seeds(self) -> int:
        """run all seed"""
        seed_files = sorted(self.seeds_dir.glob("*.py"))
        success_count = 0

        for seed_file in seed_files:
            try:
                seed_name = seed_file.stem.split("_", 2)[-1]  # extract seed name
                self.run_seed(seed_name)
                success_count += 1
            except Exception as e:
                logger.error(f"种子 {seed_file.name} 执行失败: {e}")
                continue

        logger.info(f"成功执行 {success_count}/{len(seed_files)} 个种子")
        return success_count


# Quan Ju instance
migration_manager = MigrationManager()
data_seeder = DataSeeder()
