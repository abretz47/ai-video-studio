"""
Seed data file: admin_user
Created at: 2025-08-14 00:48:59
"""

from app.core.database import SessionLocal
from app.models import *


def seed_data():
    """Execute the data seed."""
    db = SessionLocal()
    try:
        from app.core.security import get_password_hash

        # Check whether the admin user already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("Admin user already exists, skipping creation")
            return

        # Create the default admin user
        hashed_password = get_password_hash("Ai7dio")
        admin_user = User(
            username="admin",
            email="admin@ai-video-studio.com",
            hashed_password=hashed_password,
            full_name="System Administrator",
            is_active=True,
            is_superuser=True,
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("✅ Default admin user created successfully")
        print("   Username: admin")
        print("   Password: Ai7dio")
        print("   Email: admin@ai-video-studio.com")

    except Exception as e:
        print(f"Seed data execution failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def rollback_data():
    """Roll back seed data."""
    db = SessionLocal()
    try:
        # Delete the admin user
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            db.delete(admin_user)
            db.commit()
            print("✅ Admin user deleted")
        else:
            print("Admin user does not exist")

        print("Seed data admin_user rolled back successfully")

    except Exception as e:
        print(f"Seed data rollback failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
