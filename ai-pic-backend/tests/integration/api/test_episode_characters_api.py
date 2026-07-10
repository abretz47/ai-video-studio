"""Integration tests for Episode Character Management API.

Tests complete workflows including:
- CRUD operations
- Voice binding integration
- Script generation with auto-creation
- Resource resolution
- Error handling
"""

import pytest
from app.models.episode_character import EpisodeCharacter
from app.models.script import Episode, Story
from app.models.user import User
from app.models.virtual_ip import VirtualIP
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def test_user(db: Session):
 """Create test user."""
 user = User(
 username="test_user_episode_chars",
 email="test_episode_chars@example.com",
 hashed_password="test_hash",
 is_active=True,
 is_approved=True,
 email_verified=True,
)
 db.add(user)
 db.commit()
 db.refresh(user)
 return user


@pytest.fixture
def test_story(db: Session, test_user: User):
 """Create test story."""
 story = Story(
 user_id=test_user.id,
 title="Test Story for Episode Characters",
 genre="drama",
 story_format="short_video",
)
 db.add(story)
 db.commit()
 db.refresh(story)
 return story


@pytest.fixture
def test_episode(db: Session, test_story: Story):
 """Create test episode."""
 episode = Episode(
 story_id=test_story.id,
 episode_number=1,
 title="Test Episode",
 summary="Test episode for character integration",
 duration_minutes=5,
)
 db.add(episode)
 db.commit()
 db.refresh(episode)
 return episode


@pytest.fixture
def test_virtual_ip(db: Session, test_user: User):
 """Create test VirtualIP."""
 vip = VirtualIP(
 user_id=test_user.id,
 name="Test VirtualIP",
 description="Test virtual IP for episode characters",
 biography="Ce Shi Xing Ge",
 background_story="Ce Shi Bei Jing",
 style_prompt="Ce Shi Wai Guan",
 voice_config={
 "provider": "minimax",
 "voice_id": "male-qn-jingying",
 },
)
 db.add(vip)
 db.commit()
 db.refresh(vip)
 return vip


class TestEpisodeCharacterCRUD:
 """Test CRUD operations for Episode characters."""

 def test_create_episode_character(
 self,
 client: TestClient,
 db: Session,
 test_episode: Episode,
 test_virtual_ip: VirtualIP,
 auth_headers: dict,
):
 """Test creating an Episode character."""
 response = client.post(
 f"/api/v1/episodes/{test_episode.id}/characters",
 headers=auth_headers,
 json={
 "virtual_ip_id": test_virtual_ip.id,
 "character_name": "Kuai Di Yuan",
 "role_type": "temporary",
 "importance": 2,
 "personality": "Re Qing, Fu Ze",
 "background": "courier Gong Si Yuan Gong",
 "appearance_override": "wearing courier Zhi Fu",
 },
)

 assert response.status_code == 200
 data = response.json()
 assert data["character_name"] == "Kuai Di Yuan"
 assert data["importance"] == 2
 assert data["role_type"] == "temporary"
 assert "business_id" in data
 assert "id" in data

 def test_list_episode_characters(
 self,
 client: TestClient,
 db: Session,
 test_episode: Episode,
 test_virtual_ip: VirtualIP,
 auth_headers: dict,
):
 """Test listing Episode characters with pagination."""
 # Create test characters
 for i in range(3):
 char = EpisodeCharacter(
 episode_id=test_episode.id,
 virtual_ip_id=test_virtual_ip.id,
 character_name=f"character{i}",
 importance=i + 1,
)
 db.add(char)
 db.commit()

 response = client.get(
 f"/api/v1/episodes/{test_episode.id}/characters?page=1&page_size=10",
 headers=auth_headers,
)

 assert response.status_code == 200
 data = response.json()
 assert data["total"] == 3
 assert len(data["items"]) == 3
 assert data["has_more"] is False

 # Verify sorted by importance descending
 importances = [item["importance"] for item in data["items"]]
 assert importances == [3, 2, 1]

 def test_get_episode_character(
 self,
 client: TestClient,
 db: Session,
 test_episode: Episode,
 test_virtual_ip: VirtualIP,
 auth_headers: dict,
):
 """Test getting Episode character details."""
 char = EpisodeCharacter(
 episode_id=test_episode.id,
 virtual_ip_id=test_virtual_ip.id,
 character_name="doctor",
 importance=3,
)
 db.add(char)
 db.commit()
 db.refresh(char)

 response = client.get(
 f"/api/v1/episodes/{test_episode.id}/characters/{char.id}",
 headers=auth_headers,
)

 assert response.status_code == 200
 data = response.json()
 assert data["character_name"] == "doctor"
 assert data["importance"] == 3

 def test_get_character_resources(
 self,
 client: TestClient,
 db: Session,
 test_episode: Episode,
 test_virtual_ip: VirtualIP,
 auth_headers: dict,
):
 """Test getting resolved character resources."""
 char = EpisodeCharacter(
 episode_id=test_episode.id,
 virtual_ip_id=test_virtual_ip.id,
 character_name="Hu Shi",
 appearance_override="wearing Hu Shi Fu",
 voice_config_override={
 "provider": "minimax",
 "voice_id": "female-qn-qingse",
 },
)
 db.add(char)
 db.commit()
 db.refresh(char)

 response = client.get(
 f"/api/v1/episodes/{test_episode.id}/characters/{char.id}/resources",
 headers=auth_headers,
)

 assert response.status_code == 200
 data = response.json()
 assert data["display_name"] == "Hu Shi"
 assert data["resolved_voice_config"]["voice_id"] == "female-qn-qingse"
 assert "wearing Hu Shi Fu" in data["resolved_appearance_prompt"]

 def test_update_episode_character(
 self,
 client: TestClient,
 db: Session,
 test_episode: Episode,
 test_virtual_ip: VirtualIP,
 auth_headers: dict,
):
 """Test updating Episode character."""
 char = EpisodeCharacter(
 episode_id=test_episode.id,
 virtual_ip_id=test_virtual_ip.id,
 character_name="Jing Cha",
 importance=1,
)
 db.add(char)
 db.commit()
 db.refresh(char)

 response = client.put(
 f"/api/v1/episodes/{test_episode.id}/characters/{char.id}",
 headers=auth_headers,
 json={
 "importance": 3,
 "personality": "Yan Su, Zheng Yi",
 },
)

 assert response.status_code == 200
 data = response.json()
 assert data["importance"] == 3
 assert data["personality"] == "Yan Su, Zheng Yi"

 def test_delete_episode_character(
 self,
 client: TestClient,
 db: Session,
 test_episode: Episode,
 test_virtual_ip: VirtualIP,
 auth_headers: dict,
):
 """Test soft deleting Episode character."""
 char = EpisodeCharacter(
 episode_id=test_episode.id,
 virtual_ip_id=test_virtual_ip.id,
 character_name="Fu Wu Yuan",
)
 db.add(char)
 db.commit()
 db.refresh(char)

 response = client.delete(
 f"/api/v1/episodes/{test_episode.id}/characters/{char.id}?reason=Test+deletion",
 headers=auth_headers,
)

 assert response.status_code == 200
 assert "deleted successfully" in response.json()["message"]

 # Verify soft delete in database
 db.refresh(char)
 assert char.is_deleted is True
 assert char.deleted_reason == "Test deletion"


class TestCharacterExtraction:
 """Test character extraction from script content."""

 def test_extract_from_dialogues(self):
 """Test extracting characters from dialogues."""
 from app.services.script.temporary_character_extractor import (
 extract_temporary_characters,
)

 script_content = {
 "dialogues": [
 {"character": "Kuai Di Yuan", "content": "Nin De courier to Le", "scene_number": 3},
 {"character": "Kuai Di Yuan", "content": "Qing Qian Shou", "scene_number": 3},
 {"character": "doctor", "content": "Bing Ren Qing Kuang Ru He?", "scene_number": 5},
 ],
 "stage_directions": [
 {"content": "courier Yuan wearing courier Zhi Fu Zou Jin Lai", "scene_number": 3},
 ],
 }

 results = extract_temporary_characters(
 script_content=script_content,
 unknown_names=["Kuai Di Yuan", "doctor"],
)

 assert len(results) == 2
 assert results[0].character_name == "Kuai Di Yuan"
 assert results[0].dialogue_count == 2
 assert results[0].first_appearance_scene == 3
 assert len(results[0].appearance_hints) > 0

 def test_extract_appearance_hints(self):
 """Test extracting appearance hints from stage directions."""
 from app.services.script.temporary_character_extractor import (
 _extract_appearance_hints,
)

 stage_direction = "wearing courier Zhi Fu, Dai Zhe Kou Zhao, Bei Zhe courier Bao De young adults"
 hints = _extract_appearance_hints(stage_direction, "Kuai Di Yuan")

 assert "Kuai Di Zhi Fu" in hints
 assert "Kou Zhao" in hints
 assert any("Kuai Di Bao" in hint for hint in hints)


class TestBackgroundGeneration:
 """Test AI background generation."""

 @pytest.mark.asyncio
 async def test_generate_with_heuristics(self):
 """Test background generation with heuristics."""
 from app.services.script.character_background_generator import (
 generate_character_background,
)
 from app.services.script.temporary_character_extractor import (
 TemporaryCharacterInfo,
)

 char_info = TemporaryCharacterInfo(
 character_name="Kuai Di Yuan",
 dialogues=["Nin De courier to Le", "Qing Qian Shou"],
 stage_directions=[],
 scene_appearances=[3],
 first_appearance_scene=3,
 last_appearance_scene=3,
 dialogue_count=2,
 appearance_hints=["Kuai Di Zhi Fu"],
)

 scene_context = {
 "setting_location": "city Zhu Zhai Xiao Qu",
 "setting_time": "modern",
 }

 result = await generate_character_background(
 character_info=char_info,
 scene_context=scene_context,
 ai_service=None, # Use heuristics
)

 assert "personality" in result
 assert "background" in result
 assert "appearance_override" in result
 assert len(result["personality"]) > 0

 def test_heuristic_templates(self):
 """Test pre-defined heuristic templates."""
 from app.services.script.character_background_generator import (
 _generate_with_heuristics,
)
 from app.services.script.temporary_character_extractor import (
 TemporaryCharacterInfo,
)

 # Test known character types
 known_types = ["Kuai Di Yuan", "doctor", "Hu Shi", "Jing Cha", "Fu Wu Yuan", "Si Ji"]

 for char_name in known_types:
 char_info = TemporaryCharacterInfo(
 character_name=char_name,
 dialogues=[],
 stage_directions=[],
 scene_appearances=[1],
 first_appearance_scene=1,
 last_appearance_scene=1,
 dialogue_count=0,
 appearance_hints=[],
)

 result = _generate_with_heuristics(char_info)

 assert (
 result["personality"]!= "general, You Hao, Li Mao"
) # Should use specific template
 assert char_name in result["background"] or "work" in result["background"]


class TestAutoCreation:
 """Test auto-creation workflow."""

 @pytest.mark.asyncio
 async def test_auto_create_workflow(
 self,
 db: Session,
 test_episode: Episode,
 test_user: User,
):
 """Test complete auto-creation workflow."""
 from app.services.script.auto_character_creator import (
 auto_create_episode_characters,
)

 script_content = {
 "dialogues": [
 {"character": "Kuai Di Yuan", "content": "Nin De courier to Le", "scene_number": 3},
 {"character": "Kuai Di Yuan", "content": "Qing Qian Shou", "scene_number": 3},
 ],
 "stage_directions": [
 {"content": "wearing courier Zhi Fu De young adults Zou Jin Lai", "scene_number": 3},
 ],
 "metadata": {
 "setting_location": "city Zhu Zhai Xiao Qu",
 "setting_time": "modern",
 },
 }

 results = await auto_create_episode_characters(
 db=db,
 episode_id=test_episode.id,
 script_content=script_content,
 unknown_names=["Kuai Di Yuan"],
 user_id=test_user.id,
 ai_service=None, # Use heuristics
)

 assert len(results) == 1
 assert results[0]["character_name"] == "Kuai Di Yuan"
 assert results[0]["needs_customization"] is True
 assert "episode_character_id" in results[0]

 # Verify in database
 char = (
 db.query(EpisodeCharacter)
.filter(EpisodeCharacter.id == results[0]["episode_character_id"])
.first()
)
 assert char is not None
 assert char.character_name == "Kuai Di Yuan"

 @pytest.mark.asyncio
 async def test_auto_create_with_default_virtualip(
 self,
 db: Session,
 test_episode: Episode,
 test_user: User,
):
 """Test auto-creation creates default VirtualIP if needed."""
 from app.services.script.auto_character_creator import (
 auto_create_episode_characters,
)

 # Ensure no default VirtualIP exists
 existing_default = (
 db.query(VirtualIP)
.filter(
 VirtualIP.user_id == test_user.id,
 VirtualIP.name == "temporary character Mo Ren Xing Xiang",
)
.first()
)
 if existing_default:
 db.delete(existing_default)
 db.commit()

 script_content = {
 "dialogues": [
 {"character": "passerby", "content": "Ni Hao", "scene_number": 1},
 ],
 "stage_directions": [],
 "metadata": {},
 }

 results = await auto_create_episode_characters(
 db=db,
 episode_id=test_episode.id,
 script_content=script_content,
 unknown_names=["passerby"],
 user_id=test_user.id,
 ai_service=None,
)

 assert len(results) == 1

 # Verify default VirtualIP was created
 default_vip = (
 db.query(VirtualIP)
.filter(
 VirtualIP.user_id == test_user.id,
 VirtualIP.name == "temporary character Mo Ren Xing Xiang",
)
.first()
)
 assert default_vip is not None
 assert default_vip.voice_config["provider"] == "minimax"

 def test_importance_inference(self):
 """Test importance inference from dialogue count."""
 from app.services.script.auto_character_creator import _infer_importance

 assert _infer_importance(15) == 3 # >= 10
 assert _infer_importance(7) == 2 # >= 5
 assert _infer_importance(2) == 1 # < 5


class TestVoiceBinding:
 """Test voice binding integration with Episode characters."""

 def test_get_episode_character_map(
 self,
 db: Session,
 test_episode: Episode,
 test_virtual_ip: VirtualIP,
):
 """Test getting Episode character voice mapping."""
 from app.services.voice_binding_service import get_episode_character_map

 # Create Episode character with voice override
 char = EpisodeCharacter(
 episode_id=test_episode.id,
 virtual_ip_id=test_virtual_ip.id,
 character_name="Bo Yin Yuan",
 voice_config_override={
 "provider": "minimax",
 "voice_id": "female-qn-qingse",
 },
)
 db.add(char)
 db.commit()

 char_map = get_episode_character_map(db, test_episode.id)

 # Normalized name should be in map
 assert "Bo Yin Yuan" in char_map or any("Bo Yin Yuan" in key for key in char_map.keys())

 def test_get_combined_character_map(
 self,
 db: Session,
 test_story: Story,
 test_episode: Episode,
 test_virtual_ip: VirtualIP,
):
 """Test combined Story + Episode character mapping."""
 from app.services.voice_binding_service import get_combined_character_map

 # Create Episode character
 char = EpisodeCharacter(
 episode_id=test_episode.id,
 virtual_ip_id=test_virtual_ip.id,
 character_name="Lin Shi Jue Se",
)
 db.add(char)
 db.commit()

 combined_map = get_combined_character_map(db, test_story.id, test_episode.id)

 assert isinstance(combined_map, dict)
 # Should include Episode characters


class TestErrorHandling:
 """Test error handling scenarios."""

 @pytest.mark.asyncio
 async def test_auto_create_with_empty_unknown_names(
 self,
 db: Session,
 test_episode: Episode,
 test_user: User,
):
 """Test auto-creation with empty unknown_names."""
 from app.services.script.auto_character_creator import (
 auto_create_episode_characters,
)

 results = await auto_create_episode_characters(
 db=db,
 episode_id=test_episode.id,
 script_content={},
 unknown_names=[],
 user_id=test_user.id,
)

 assert results == []

 @pytest.mark.asyncio
 async def test_auto_create_with_invalid_script(
 self,
 db: Session,
 test_episode: Episode,
 test_user: User,
):
 """Test auto-creation with invalid script content."""
 from app.services.script.auto_character_creator import (
 auto_create_episode_characters,
)

 results = await auto_create_episode_characters(
 db=db,
 episode_id=test_episode.id,
 script_content=None, # Invalid
 unknown_names=["Ce Shi Jue Se"],
 user_id=test_user.id,
)

 # Should handle gracefully and return empty
 assert results == []

 def test_character_not_found(
 self,
 client: TestClient,
 test_episode: Episode,
 auth_headers: dict,
):
 """Test getting non-existent character."""
 response = client.get(
 f"/api/v1/episodes/{test_episode.id}/characters/99999",
 headers=auth_headers,
)

 assert response.status_code == 404
