from app.models.script import Story, StoryCharacter
from app.models.user import User
from app.models.virtual_ip import VirtualIP
from app.services.story.story_novel_export_payload import build_story_novel_payload


def test_story_novel_payload_includes_virtual_ip_biography(db_session):
 user = User(
 username="payload_admin",
 email="payload_admin@example.com",
 hashed_password="not-used",
 full_name="Payload Admin",
 is_active=True,
 is_approved=True,
 email_verified=True,
 is_admin=True,
 is_superuser=True,
)
 db_session.add(user)
 db_session.commit()
 db_session.refresh(user)

 vip = VirtualIP(
 user_id=user.id,
 name="Test VIP",
 biography="Ren Wu Xiao Zhuan content",
 background_story="Bei Jing story content",
 description="Jue Se Miao Shu",
 tags=["tag1"],
)
 story = Story(title="Test Story", genre="Romance", user_id=user.id)
 db_session.add_all([vip, story])
 db_session.commit()
 db_session.refresh(vip)
 db_session.refresh(story)

 story_character = StoryCharacter(
 story_id=story.id,
 virtual_ip_id=vip.id,
 virtual_ip_business_id=vip.business_id,
 character_name="Protagonist",
 role_type="protagonist",
)
 db_session.add(story_character)
 db_session.commit()

 payload = build_story_novel_payload(db_session, story=story)
 characters = payload.get("characters")
 assert isinstance(characters, list)
 assert any(
 (item.get("virtual_ip") or {}).get("biography") == "Ren Wu Xiao Zhuan content"
 for item in characters
)
