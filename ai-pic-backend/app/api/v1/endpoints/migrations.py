"""
Database migration API endpoints

Provides API access to migration status and management operations
"""

from typing import Any, Dict, List

from app.core.config import settings
from app.core.migrations import MigrationError, data_seeder, migration_manager
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()


# Response models
class MigrationStatusResponse(BaseModel):
    """Migration status response"""

    current_revision: str | None
    head_revision: str | None
    is_up_to_date: bool
    needs_upgrade: bool
    database_exists: bool
    pending_migrations: List[str] | None = None
    pending_count: int | None = None


class MigrationHistoryItem(BaseModel):
    """Migration history item"""

    revision: str
    down_revision: str | None
    message: str | None
    branch_labels: str | None
    depends_on: str | None
    create_date: str | None


class ValidationResult(BaseModel):
    """Validation result"""

    valid: bool
    errors: List[str]
    warnings: List[str]


class SchemaDiff(BaseModel):
    """Schema diff"""

    has_changes: bool
    changes: List[str]
    change_count: int
    error: str | None = None


class OperationResult(BaseModel):
    """Operation result"""

    success: bool
    message: str
    details: Dict[str, Any] | None = None


# Dependency functions
def check_admin_permission():
    """Check administrator privileges (example; should be implemented according to the authentication system)"""
    # TODO: Implement actual permission checks
    # In production, this should verify whether the user has database management privileges
    pass


@router.get("/status", response_model=MigrationStatusResponse)
async def get_migration_status():
    """Get database migration status"""
    try:
        status = migration_manager.check_migration_status()
        return MigrationStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get migration status: {str(e)}")


@router.get("/history", response_model=List[MigrationHistoryItem])
async def get_migration_history():
    """Get migration history"""
    try:
        history = migration_manager.get_migration_history()
        return [MigrationHistoryItem(**item) for item in history]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get migration history: {str(e)}")


@router.get("/validate", response_model=ValidationResult)
async def validate_migrations():
    """Validate migration file integrity"""
    try:
        validation = migration_manager.validate_migrations()
        return ValidationResult(**validation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration validation failed: {str(e)}")


@router.get("/schema-diff", response_model=SchemaDiff)
async def get_schema_diff():
    """Get the diff between the current database and the models"""
    try:
        diff = migration_manager.get_schema_diff()
        return SchemaDiff(**diff)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schema diff: {str(e)}")


@router.post("/upgrade", response_model=OperationResult)
async def upgrade_database(
    background_tasks: BackgroundTasks,
    revision: str = "head",
    backup: bool = True,
    _: None = Depends(check_admin_permission),
):
    """Upgrade database (background task)"""
    try:
        # Check current status
        status = migration_manager.check_migration_status()

        if not status["needs_upgrade"] and revision == "head":
            return OperationResult(
                success=True, message="Database is already at the latest version", details=status
            )

        # Validate migration files
        validation = migration_manager.validate_migrations()
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Migration file validation failed: {'; '.join(validation['errors'])}",
            )

        # Perform upgrade in the background
        def perform_upgrade():
            try:
                if backup and "mysql" in settings.DATABASE_URL:
                    migration_manager.backup_before_migration()

                migration_manager.upgrade(revision)
            except Exception as e:
                # Errors can be logged or notifications sent here
                print(f"Background upgrade failed: {e}")

        background_tasks.add_task(perform_upgrade)

        return OperationResult(
            success=True,
            message=f"Database upgrade task started, target revision: {revision}",
            details={
                "current_revision": status["current_revision"],
                "target_revision": revision,
            },
        )

    except MigrationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database upgrade failed: {str(e)}")


@router.post("/create-migration", response_model=OperationResult)
async def create_migration(
    message: str, autogenerate: bool = True, _: None = Depends(check_admin_permission)
):
    """Create a new migration file"""
    try:
        if not message.strip():
            raise HTTPException(status_code=400, detail="Migration description cannot be empty")

        revision = migration_manager.create_migration(message, autogenerate)

        # Get schema diff information
        diff = migration_manager.get_schema_diff() if autogenerate else None

        return OperationResult(
            success=True,
            message=f"Migration created successfully: {message}",
            details={
                "revision": revision,
                "message": message,
                "autogenerate": autogenerate,
                "schema_diff": diff,
            },
        )

    except MigrationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create migration: {str(e)}")


@router.post("/stamp", response_model=OperationResult)
async def stamp_revision(revision: str, _: None = Depends(check_admin_permission)):
    """Stamp database version"""
    try:
        migration_manager.stamp(revision)

        return OperationResult(
            success=True,
            message=f"Version stamped successfully: {revision}",
            details={"revision": revision},
        )

    except MigrationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Version stamp failed: {str(e)}")


# Health check endpoint
@router.get("/health")
async def migration_health_check():
    """Migration system health check"""
    try:
        status = migration_manager.check_migration_status()
        validation = migration_manager.validate_migrations()

        health_status = {
            "database_connected": status["database_exists"],
            "migrations_valid": validation["valid"],
            "up_to_date": status["is_up_to_date"],
            "system_healthy": (
                status["database_exists"]
                and validation["valid"]
                and status["is_up_to_date"]
            ),
        }

        return {
            "status": "healthy" if health_status["system_healthy"] else "degraded",
            "checks": health_status,
            "timestamp": status.get("timestamp", "unknown"),
        }

    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "timestamp": "unknown"}


# Development-only endpoints (should be disabled in production)
@router.post("/reset-database", response_model=OperationResult)
async def reset_database(
    confirm: bool = False, _: None = Depends(check_admin_permission)
):
    """Reset database (dangerous operation, development only)"""
    if settings.PROJECT_NAME != "AI Image Generation API" or not confirm:
        raise HTTPException(status_code=403, detail="This operation is only available in development and requires confirmation")

    try:
        # Back up first
        backup_file = migration_manager.backup_before_migration()

        # Downgrade to base
        migration_manager.downgrade("base")

        # Upgrade again
        migration_manager.upgrade("head")

        return OperationResult(
            success=True,
            message="Database reset successfully",
            details={
                "backup_file": backup_file,
                "new_status": migration_manager.check_migration_status(),
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database reset failed: {str(e)}")


# Data seed endpoints
@router.post("/seeds/run", response_model=OperationResult)
async def run_seed(
    seed_name: str | None = None,
    run_all: bool = False,
    _: None = Depends(check_admin_permission),
):
    """Run data seeds"""
    try:
        if run_all:
            count = data_seeder.run_all_seeds()
            return OperationResult(
                success=True,
                message=f"Successfully ran {count} seeds",
                details={"seeds_count": count},
            )
        elif seed_name:
            data_seeder.run_seed(seed_name)
            return OperationResult(
                success=True,
                message=f"Seed ran successfully: {seed_name}",
                details={"seed_name": seed_name},
            )
        else:
            raise HTTPException(
                status_code=400, detail="Specify a seed name or set run_all=true"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run seeds: {str(e)}")


@router.get("/info")
async def get_migration_info():
    """Get migration system information"""
    return {
        "database_url": (
            settings.DATABASE_URL.split("@")[-1]
            if "@" in settings.DATABASE_URL
            else "hidden"
        ),
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "migration_system": "Custom FastAPI Migration System",
        "alembic_integration": True,
        "features": [
            "Auto-migration generation",
            "Data seeding",
            "Schema validation",
            "Backup integration",
            "API management",
            "CLI tools",
        ],
    }
