"""
migration An Quan Ji Zhi

Ti Gong database migration An Quan Jian Cha, Hui Gun Bao Hu and Shu Ju Wan Zheng Xing validation
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import settings
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


class MigrationSafetyError(Exception):
    """migration An Quan exception"""

    pass


class DataIntegrityChecker:
    """Shu Ju Wan Zheng Xing check Qi"""

    def __init__(self, engine: Engine = None):
        self.engine = engine or create_engine(settings.DATABASE_URL)

    def check_referential_integrity(self) -> Dict[str, Any]:
        """check Wai Jian Yin Yong Wan Zheng Xing"""
        result = {"valid": True, "violations": [], "warnings": []}

        try:
            inspector = inspect(self.engine)

            with self.engine.connect() as conn:
                for table_name in inspector.get_table_names():
                    foreign_keys = inspector.get_foreign_keys(table_name)

                    for fk in foreign_keys:
                        # check Wai Jian Yue Shu
                        local_cols = ", ".join(fk["constrained_columns"])
                        ref_table = fk["referred_table"]
                        ref_cols = ", ".join(fk["referred_columns"])

                        query = f"""
                        SELECT COUNT(*) as violation_count
                        FROM {table_name} t1
                        LEFT JOIN {ref_table} t2 ON t1.{local_cols} = t2.{ref_cols}
                        WHERE t1.{local_cols} IS NOT NULL AND t2.{ref_cols} IS NULL
                        """

                        try:
                            violation_result = conn.execute(text(query))
                            count = violation_result.fetchone()[0]

                            if count > 0:
                                violation = {
                                    "table": table_name,
                                    "foreign_key": fk["name"],
                                    "violation_count": count,
                                    "description": f"Biao {table_name} You {count} Xing Wei Fan Wai Jian Yue Shu {fk['name']}",
                                }
                                result["violations"].append(violation)
                                result["valid"] = False

                        except Exception as e:
                            logger.warning(
                                f"Jian Cha Wai Jian Yue Shu failed {table_name}.{fk['name']}: {e}"
                            )

        except Exception as e:
            result["valid"] = False
            result["error"] = str(e)
            logger.error(f"Yin Yong Wan Zheng Xing Jian Cha failed: {e}")

        return result

    def check_data_consistency(self) -> Dict[str, Any]:
        """Check data consistency"""
        result = {"valid": True, "inconsistencies": [], "statistics": {}}

        try:
            with self.engine.connect() as conn:
                # check Ji Ben data Tong Ji
                inspector = inspect(self.engine)

                for table_name in inspector.get_table_names():
                    try:
                        # get Xing Shu
                        count_result = conn.execute(
                            text(f"SELECT COUNT(*) FROM {table_name}")
                        )
                        row_count = count_result.fetchone()[0]

                        result["statistics"][table_name] = {"row_count": row_count}

                        # checkNULLZhi ratio
                        columns = inspector.get_columns(table_name)
                        for column in columns:
                            if not column.get("nullable", True):  # Fei Kong Lie
                                null_check = conn.execute(
                                    text(
                                        f"SELECT COUNT(*) FROM {table_name} WHERE {column['name']} IS NULL"
                                    )
                                )
                                null_count = null_check.fetchone()[0]

                                if null_count > 0:
                                    inconsistency = {
                                        "table": table_name,
                                        "column": column["name"],
                                        "type": "null_in_not_null_column",
                                        "count": null_count,
                                        "description": f"Fei Kong Lie {table_name}.{column['name']} Bao Han {null_count} GeNULLZhi",
                                    }
                                    result["inconsistencies"].append(inconsistency)
                                    result["valid"] = False

                    except Exception as e:
                        logger.warning(f"Jian Cha Biao {table_name} Yi Zhi Xing failed: {e}")

        except Exception as e:
            result["valid"] = False
            result["error"] = str(e)
            logger.error(f"Shu Ju Yi Zhi Xing Jian Cha failed: {e}")

        return result

    def generate_data_fingerprint(self) -> str:
        """Sheng Cheng data Zhi Wen Yong Yu Bian Geng Jian Ce"""
        try:
            fingerprint_data = {}
            is_mysql = self.engine.dialect.name == "mysql"

            with self.engine.connect() as conn:
                inspector = inspect(self.engine)

                for table_name in inspector.get_table_names():
                    try:
                        # get Biao Xing Shu He Jiao Yan and
                        count_result = conn.execute(
                            text(f"SELECT COUNT(*) FROM {table_name}")
                        )
                        row_count = count_result.fetchone()[0]

                        # Dui YuMySQL, CanShi YongCHECKSUM TABLE
                        if is_mysql:
                            checksum_result = conn.execute(
                                text(f"CHECKSUM TABLE {table_name}")
                            )
                            checksum = checksum_result.fetchone()[1]
                        else:
                            # Dui Yu Qi Ta database, Shi Yong Xing Shu Zuo Wei Jian Dan Jiao Yan
                            checksum = row_count

                        fingerprint_data[table_name] = {
                            "row_count": row_count,
                            "checksum": checksum,
                        }

                    except Exception as e:
                        logger.warning(f"generate Biao {table_name} Zhi Wen failed: {e}")
                        fingerprint_data[table_name] = {"error": str(e)}

            # Sheng ChengMD5Ha Xi
            fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
            return hashlib.md5(fingerprint_str.encode()).hexdigest()

        except Exception as e:
            logger.error(f"generate Shu Ju Zhi Wen failed: {e}")
            return f"error_{datetime.now().timestamp()}"


class MigrationRollbackManager:
    """migration Hui Gun manager"""

    def __init__(self, engine: Engine = None):
        self.engine = engine or create_engine(settings.DATABASE_URL)
        self.rollback_dir = Path(__file__).parent.parent.parent / "rollbacks"
        self.rollback_dir.mkdir(exist_ok=True)

    def create_rollback_point(self, migration_id: str, description: str = "") -> str:
        """create Hui Gun Dian"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rollback_id = f"{timestamp}_{migration_id}"

            rollback_info = {
                "rollback_id": rollback_id,
                "migration_id": migration_id,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "database_url": (
                    settings.DATABASE_URL.split("@")[-1]
                    if "@" in settings.DATABASE_URL
                    else "local"
                ),
                "schema_snapshot": self._capture_schema_snapshot(),
                "data_fingerprint": DataIntegrityChecker(
                    self.engine
                ).generate_data_fingerprint(),
            }

            # save Hui Gun Xin Xi
            rollback_file = self.rollback_dir / f"{rollback_id}.json"
            with open(rollback_file, "w", encoding="utf-8") as f:
                json.dump(rollback_info, f, indent=2, ensure_ascii=False)

            # create Shu Ju Bei Fen(Ru Guo ShiMySQL)
            if "mysql" in settings.DATABASE_URL:
                backup_file = self._create_data_backup(rollback_id)
                rollback_info["backup_file"] = backup_file

                # update Hui Gun Xin Xi file
                with open(rollback_file, "w", encoding="utf-8") as f:
                    json.dump(rollback_info, f, indent=2, ensure_ascii=False)

            logger.info(f"Hui Gun Dian Chuang Jian Cheng Gong: {rollback_id}")
            return rollback_id

        except Exception as e:
            logger.error(f"Chuang Jian Hui Gun Dian failed: {e}")
            raise MigrationSafetyError(f"Chuang Jian Hui Gun Dian failed: {e}")

    def _capture_schema_snapshot(self) -> Dict[str, Any]:
        """Bu Huo database Jia Gou Kuai Zhao"""
        try:
            inspector = inspect(self.engine)
            schema_snapshot = {"tables": {}, "indexes": {}, "foreign_keys": {}}

            for table_name in inspector.get_table_names():
                # Biao structure
                columns = inspector.get_columns(table_name)
                schema_snapshot["tables"][table_name] = {
                    "columns": [
                        {
                            "name": col["name"],
                            "type": str(col["type"]),
                            "nullable": col.get("nullable", True),
                            "default": (
                                str(col.get("default")) if col.get("default") else None
                            ),
                        }
                        for col in columns
                    ]
                }

                # index
                indexes = inspector.get_indexes(table_name)
                schema_snapshot["indexes"][table_name] = [
                    {
                        "name": idx["name"],
                        "columns": idx["column_names"],
                        "unique": idx.get("unique", False),
                    }
                    for idx in indexes
                ]

                # Wai Jian
                foreign_keys = inspector.get_foreign_keys(table_name)
                schema_snapshot["foreign_keys"][table_name] = [
                    {
                        "name": fk["name"],
                        "constrained_columns": fk["constrained_columns"],
                        "referred_table": fk["referred_table"],
                        "referred_columns": fk["referred_columns"],
                    }
                    for fk in foreign_keys
                ]

            return schema_snapshot

        except Exception as e:
            logger.error(f"Bu Huo Jia Gou Kuai Zhao failed: {e}")
            return {"error": str(e)}

    def _create_data_backup(self, rollback_id: str) -> Optional[str]:
        """create Shu Ju Bei Fen"""
        try:
            import subprocess
            from urllib.parse import urlparse

            # Parse database URL
            parsed = urlparse(
                settings.DATABASE_URL.replace("mysql+pymysql://", "mysql://")
            )

            # Generate backup filename
            backup_file = f"rollback_{rollback_id}.sql"
            backup_path = self.rollback_dir / backup_file

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
                "--add-drop-table",
                parsed.path.lstrip("/"),
            ]

            # Execute backup
            with open(backup_path, "w") as f:
                result = subprocess.run(
                    cmd, stdout=f, stderr=subprocess.PIPE, text=True
                )

            if result.returncode == 0:
                logger.info(f"Shu Ju Bei Fen Cheng Gong: {backup_path}")
                return str(backup_file)
            else:
                logger.error(f"Shu Ju Bei Fen failed: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"Chuang Jian Shu Ju Bei Fen failed: {e}")
            return None

    def list_rollback_points(self) -> List[Dict[str, Any]]:
        """Lie Chu all Hui Gun Dian"""
        rollback_points = []

        try:
            for rollback_file in self.rollback_dir.glob("*.json"):
                try:
                    with open(rollback_file, "r", encoding="utf-8") as f:
                        rollback_info = json.load(f)

                    # Tian Jia file Xin Xi
                    rollback_info["file_path"] = str(rollback_file)
                    rollback_info["file_size"] = rollback_file.stat().st_size

                    rollback_points.append(rollback_info)

                except Exception as e:
                    logger.warning(f"Du Qu Hui Gun Dian file failed {rollback_file}: {e}")

            # An create time Pai Xu
            rollback_points.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        except Exception as e:
            logger.error(f"Lie Chu Hui Gun Dian failed: {e}")

        return rollback_points

    def cleanup_old_rollbacks(self, keep_days: int = 30):
        """Qing Li Guo Qi Hui Gun Dian"""
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            cleaned_count = 0

            for rollback_file in self.rollback_dir.glob("*.json"):
                try:
                    with open(rollback_file, "r", encoding="utf-8") as f:
                        rollback_info = json.load(f)

                    created_at = datetime.fromisoformat(rollback_info["created_at"])

                    if created_at < cutoff_date:
                        # delete Hui Gun file
                        rollback_file.unlink()

                        # delete related Bei Fen Wen Jian
                        backup_file = rollback_info.get("backup_file")
                        if backup_file:
                            backup_path = self.rollback_dir / backup_file
                            if backup_path.exists():
                                backup_path.unlink()

                        cleaned_count += 1
                        logger.info(f"Shan Chu Guo Qi Hui Gun Dian: {rollback_info['rollback_id']}")

                except Exception as e:
                    logger.warning(f"Qing Li Hui Gun Dian failed {rollback_file}: {e}")

            logger.info(f"Qing Li Wan Cheng，Shan Chu Le {cleaned_count} Ge Guo Qi Hui Gun Dian")
            return cleaned_count

        except Exception as e:
            logger.error(f"Qing Li Hui Gun Dian failed: {e}")
            return 0


class MigrationValidator:
    """migration validation Qi"""

    def __init__(self, engine: Engine = None):
        self.engine = engine or create_engine(settings.DATABASE_URL)
        self.integrity_checker = DataIntegrityChecker(self.engine)

    def pre_migration_check(self) -> Dict[str, Any]:
        """migration before check"""
        result = {"safe_to_migrate": True, "warnings": [], "errors": [], "checks": {}}

        try:
            # check database connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            result["checks"]["database_connection"] = True

            # check Shu Ju Wan Zheng Xing
            integrity_result = self.integrity_checker.check_referential_integrity()
            result["checks"]["referential_integrity"] = integrity_result["valid"]

            if not integrity_result["valid"]:
                result["safe_to_migrate"] = False
                for violation in integrity_result["violations"]:
                    result["errors"].append(f"Wai Jian Yue Shu Wei Fan: {violation['description']}")

            # Check data consistency
            consistency_result = self.integrity_checker.check_data_consistency()
            result["checks"]["data_consistency"] = consistency_result["valid"]

            if not consistency_result["valid"]:
                result["safe_to_migrate"] = False
                for inconsistency in consistency_result["inconsistencies"]:
                    result["errors"].append(
                        f"Shu Ju Bu Yi Zhi: {inconsistency['description']}"
                    )

            # check Ci Pan Kong Jian(Ru Guo Ke Neng)
            try:
                import shutil

                total, used, free = shutil.disk_usage(Path(__file__).parent)
                free_gb = free // (1024**3)

                if free_gb < 1:  # Shao Yu1GB
                    result["warnings"].append(f"Ci Pan Kong Jian Bu Zu: Jin Sheng {free_gb}GB")

                result["checks"]["disk_space"] = free_gb

            except Exception:
                result["warnings"].append("unable to check Ci Pan Kong Jian")

            # Jian Cha Biao lock status
            if "mysql" in settings.DATABASE_URL:
                try:
                    with self.engine.connect() as conn:
                        lock_result = conn.execute(
                            text("SHOW OPEN TABLES WHERE In_use > 0")
                        )
                        locked_tables = lock_result.fetchall()

                        if locked_tables:
                            result["warnings"].append(
                                f"Fa Xian {len(locked_tables)} Ge Suo Ding De Biao"
                            )

                        result["checks"]["table_locks"] = len(locked_tables) == 0

                except Exception as e:
                    result["warnings"].append(f"Wu Fa Jian Cha Biao Suo Ding status: {e}")

        except Exception as e:
            result["safe_to_migrate"] = False
            result["errors"].append(f"Qian Yi Qian Jian Cha failed: {e}")
            logger.error(f"Qian Yi Qian Jian Cha failed: {e}")

        return result

    def post_migration_check(self, pre_migration_fingerprint: str) -> Dict[str, Any]:
        """migration after check"""
        result = {
            "migration_successful": True,
            "warnings": [],
            "errors": [],
            "checks": {},
        }

        try:
            # retry check Shu Ju Wan Zheng Xing
            integrity_result = self.integrity_checker.check_referential_integrity()
            result["checks"]["referential_integrity"] = integrity_result["valid"]

            if not integrity_result["valid"]:
                result["migration_successful"] = False
                for violation in integrity_result["violations"]:
                    result["errors"].append(
                        f"Qian Yi Hou Wai Jian Yue Shu Wei Fan: {violation['description']}"
                    )

            # Check data consistency
            consistency_result = self.integrity_checker.check_data_consistency()
            result["checks"]["data_consistency"] = consistency_result["valid"]

            if not consistency_result["valid"]:
                for inconsistency in consistency_result["inconsistencies"]:
                    result["warnings"].append(
                        f"Qian Yi Hou Shu Ju Bu Yi Zhi: {inconsistency['description']}"
                    )

            # Bi Jiao data Zhi Wen
            post_migration_fingerprint = (
                self.integrity_checker.generate_data_fingerprint()
            )
            result["checks"]["data_fingerprint_changed"] = (
                pre_migration_fingerprint != post_migration_fingerprint
            )

            if pre_migration_fingerprint == post_migration_fingerprint:
                result["warnings"].append("data Zhi Wen not change, migration Ke Neng not Sheng Xiao")

            result["pre_migration_fingerprint"] = pre_migration_fingerprint
            result["post_migration_fingerprint"] = post_migration_fingerprint

        except Exception as e:
            result["migration_successful"] = False
            result["errors"].append(f"Qian Yi Hou Jian Cha failed: {e}")
            logger.error(f"Qian Yi Hou Jian Cha failed: {e}")

        return result


# Quan Ju instance
migration_validator = MigrationValidator()
rollback_manager = MigrationRollbackManager()
integrity_checker = DataIntegrityChecker()
