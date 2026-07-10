"""
Initial data seed
Created at: 2024-12-12 12:00:00

This seed creates the system's base data, including:
1. Sample virtual IPs
2. Base configuration data
3. System administrator users (if needed)
"""

import logging

from app.core.database import SessionLocal
from app.models.script import Story
from app.models.virtual_ip import VirtualIP
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def get_or_create(db: Session, model, defaults=None, **kwargs):
    """Get or create an object."""
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.items())
        params.update(defaults or {})
        instance = model(**params)
        db.add(instance)
        return instance, True


def seed_data():
    """Execute the data seed."""
    db = SessionLocal()
    try:
        logger.info("Starting initial data seed execution")

        # Create sample virtual IPs
        virtual_ips_data = [
            {
                "name": "Maya",
                "description": "A lively and adorable young woman full of curiosity and a spirit of adventure",
                "tags": ["young", "lively", "female", "modern"],
                "background_story": "Maya is a 22-year-old university student majoring in art and design. She has an outgoing personality, loves exploring new things, and often shares her daily life and creations on social media. She dreams of becoming a well-known graphic designer.",
                "style_prompt": "Young Asian woman, 22 years old, long black hair, big eyes, sweet smile, modern fashionable clothing, full of energy",
                "is_active": True,
                "is_public": True,
            },
            {
                "name": "Professor Lee",
                "description": "A knowledgeable middle-aged professor who is gentle and wise",
                "tags": ["middle-aged", "professor", "male", "intellectual"],
                "background_story": "Professor Lee is a 45-year-old university professor specializing in artificial intelligence and machine learning. He is gentle, beloved by his students, and often speaks at academic conferences. He has a happy family and enjoys reading and gardening in his free time.",
                "style_prompt": "Middle-aged Asian man, 45 years old, wearing glasses, gentle expression, scholarly demeanor, formal or casual attire",
                "is_active": True,
                "is_public": True,
            },
            {
                "name": "Grandma Chen",
                "description": "A kind elderly grandmother full of life wisdom",
                "tags": ["elderly", "grandmother", "female", "kind"],
                "background_story": "Grandma Chen is 70 years old and a retired elementary school teacher. She has three grandchildren and loves them deeply. She enjoys cooking and knitting sweaters, and often tells stories to the neighborhood children. Her rich life experience allows her to always offer good advice to young people.",
                "style_prompt": "Elderly Asian woman, 70 years old, silver-white hair, kind smile, traditional or comfortable clothing, warm presence",
                "is_active": True,
                "is_public": True,
            },
        ]

        created_count = 0
        for vip_data in virtual_ips_data:
            virtual_ip, created = get_or_create(
                db, VirtualIP, name=vip_data["name"], defaults=vip_data
            )

            if created:
                created_count += 1
                logger.info(f"Created virtual IP: {virtual_ip.name}")

        logger.info(f"Successfully created {created_count} virtual IPs")

        # Create sample stories
        stories_data = [
            {
                "title": "Campus Youth Story",
                "genre": "Youth",
                "theme": "Growth and friendship",
                "target_audience": "Young people",
                "duration_minutes": 15,
                "premise": "Tells a youthful story set in university life",
                "synopsis": "Maya encounters all kinds of interesting people and events at university, grows under the guidance of Professor Lee, and also learns life wisdom from Grandma Chen.",
                "main_conflict": "The conflict between academic pressure and personal dreams",
                "resolution": "Through hard work and help from those around her, she finds a balance",
                "setting_time": "Modern day",
                "setting_location": "University campus",
                "world_building": "A campus environment in a realist style",
                "status": "draft",
                "is_public": True,
                "tags": ["campus", "youth", "growth"],
            }
        ]

        story_created_count = 0
        for story_data in stories_data:
            story, created = get_or_create(
                db, Story, title=story_data["title"], defaults=story_data
            )

            if created:
                story_created_count += 1
                logger.info(f"Created story: {story.title}")

        logger.info(f"Successfully created {story_created_count} stories")

        db.commit()
        logger.info("Initial data seed executed successfully")

    except Exception as e:
        logger.error(f"Seed data execution failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def rollback_data():
    """Roll back seed data."""
    db = SessionLocal()
    try:
        logger.info("Starting initial data seed rollback")

        # Delete the created data
        story_count = db.query(Story).filter(Story.title.in_(["Campus Youth Story"])).count()
        db.query(Story).filter(Story.title.in_(["Campus Youth Story"])).delete(
            synchronize_session=False
        )

        vip_count = (
            db.query(VirtualIP)
            .filter(VirtualIP.name.in_(["Maya", "Professor Lee", "Grandma Chen"]))
            .count()
        )
        db.query(VirtualIP).filter(
            VirtualIP.name.in_(["Maya", "Professor Lee", "Grandma Chen"])
        ).delete(synchronize_session=False)

        db.commit()
        logger.info(f"Rollback successful: deleted {vip_count} virtual IPs and {story_count} stories")

    except Exception as e:
        logger.error(f"Seed data rollback failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def check_prerequisites():
    """Check prerequisites."""
    db = SessionLocal()
    try:
        # Check whether the required tables exist
        tables_to_check = ["virtual_ips", "stories"]

        for table_name in tables_to_check:
            try:
                result = db.execute(text(f"SELECT 1 FROM {table_name} LIMIT 1"))
                result.fetchone()
            except Exception:
                logger.error(f"Table {table_name} does not exist or cannot be accessed")
                return False

        logger.info("Prerequisite check passed")
        return True

    except Exception as e:
        logger.error(f"Prerequisite check failed: {e}")
        return False
    finally:
        db.close()


def get_seed_info():
    """Get seed information."""
    return {
        "name": "initial_data",
        "description": "Create initial system data, including sample virtual IPs and stories",
        "version": "1.0.0",
        "dependencies": [],
        "create_time": "2024-12-12 12:00:00",
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_data()
    else:
        if check_prerequisites():
            seed_data()
        else:
            logger.error("Prerequisite check failed, seed execution aborted")
