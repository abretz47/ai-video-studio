"""
model Dan Yuan Ce Shi
"""

import pytest
from app.models.script import Episode, Script, Story, StoryCharacter
from app.models.virtual_ip import VirtualIP, VirtualIPImage
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from tests.factories import (
 EpisodeFactory,
 ScriptFactory,
 ScriptTemplateFactory,
 StoryCharacterFactory,
 StoryFactory,
 UserFactory,
 VirtualIPFactory,
 VirtualIPImageFactory,
 setup_factories,
)


@pytest.mark.unit
class TestUserModel:
 """user model test"""

 def test_create_user(self, db_session: Session):
 """test create user"""
 setup_factories(db_session)

 user = UserFactory()

 assert user.id is not None
 assert user.username is not None
 assert user.email is not None
 assert user.is_active is True
 assert user.created_at is not None

 def test_user_unique_username(self, db_session: Session):
 """test Yong Hu Ming Wei Yi Xing"""
 setup_factories(db_session)

 UserFactory(username="testuser")

 with pytest.raises(IntegrityError):
 UserFactory(username="testuser")

 def test_user_unique_email(self, db_session: Session):
 """test You Xiang Wei Yi Xing"""
 setup_factories(db_session)

 UserFactory(email="test@example.com")

 with pytest.raises(IntegrityError):
 UserFactory(email="test@example.com")

 def test_user_string_representation(self, db_session: Session):
 """test user Zi Fu Chuan Biao Shi"""
 setup_factories(db_session)

 user = UserFactory(username="testuser")
 assert str(user) == "testuser"


@pytest.mark.unit
class TestVirtualIPModel:
 """virtualIPMo Xing Ce Shi"""

 def test_create_virtual_ip(self, db_session: Session):
 """test create virtualIP"""
 setup_factories(db_session)

 vip = VirtualIPFactory()

 assert vip.id is not None
 assert vip.name is not None
 assert vip.is_active is True
 assert vip.created_at is not None

 def test_virtual_ip_unique_name(self, db_session: Session):
 """Ce Shi Xu NiIPname Wei Yi Xing"""
 setup_factories(db_session)

 owner = UserFactory()
 VirtualIPFactory(name="TestIP", owner=owner)

 with pytest.raises(IntegrityError):
 VirtualIPFactory(name="TestIP", owner=owner)

 def test_virtual_ip_images_relationship(self, db_session: Session):
 """Ce Shi Xu NiIPTu Xiang Guan Xi"""
 setup_factories(db_session)

 vip = VirtualIPFactory()
 image1 = VirtualIPImageFactory(virtual_ip=vip)
 image2 = VirtualIPImageFactory(virtual_ip=vip)

 assert len(vip.images) == 2
 assert image1 in vip.images
 assert image2 in vip.images
 assert image1.virtual_ip == vip
 assert image2.virtual_ip == vip

 def test_virtual_ip_json_fields(self, db_session: Session):
 """Ce Shi Xu NiIP JSONZi Duan"""
 setup_factories(db_session)

 tags = ["tag1", "tag2", "tag3"]
 reference_images = [
 "http://example.com/image1.jpg",
 "http://example.com/image2.jpg",
 ]

 vip = VirtualIPFactory(tags=tags, style_reference_images=reference_images)

 assert vip.tags == tags
 assert vip.style_reference_images == reference_images

 def test_virtual_ip_cascade_delete(self, db_session: Session):
 """Ce Shi Xu NiIPJi Lian Shan Chu"""
 setup_factories(db_session)

 vip = VirtualIPFactory()
 image = VirtualIPImageFactory(virtual_ip=vip)

 vip_id = vip.id
 image_id = image.id

 # Shan Chu Xu NiIP
 db_session.delete(vip)
 db_session.commit()

 # check image Ye Bei delete
 assert (
 db_session.query(VirtualIP).filter(VirtualIP.id == vip_id).first() is None
)
 assert (
 db_session.query(VirtualIPImage)
.filter(VirtualIPImage.id == image_id)
.first()
 is None
)


@pytest.mark.unit
class TestVirtualIPImageModel:
 """virtualIPimage model test"""

 def test_create_virtual_ip_image(self, db_session: Session):
 """test create virtualIPimage"""
 setup_factories(db_session)

 image = VirtualIPImageFactory()

 assert image.id is not None
 assert image.filename is not None
 assert image.virtual_ip_id is not None
 assert image.created_at is not None

 def test_virtual_ip_image_categories(self, db_session: Session):
 """Ce Shi Xu NiIPTu Xiang Fen Lei"""
 setup_factories(db_session)

 categories = ["avatar", "expression", "costume", "scene", "prop"]

 for category in categories:
 image = VirtualIPImageFactory(category=category)
 assert image.category == category

 def test_virtual_ip_image_json_tags(self, db_session: Session):
 """Ce Shi Xu NiIPimageJSONBiao Qian"""
 setup_factories(db_session)

 tags = ["happy", "portrait", "high-quality"]
 image = VirtualIPImageFactory(tags=tags)

 assert image.tags == tags


@pytest.mark.unit
class TestStoryModel:
 """story model test"""

 def test_create_story(self, db_session: Session):
 """test create story"""
 setup_factories(db_session)

 story = StoryFactory()

 assert story.id is not None
 assert story.title is not None
 assert story.genre is not None
 assert story.created_at is not None

 def test_story_json_fields(self, db_session: Session):
 """Ce Shi Gu ShiJSONZi Duan"""
 setup_factories(db_session)

 main_characters = [
 {"name": "Character1", "role": "protagonist"},
 {"name": "Character2", "role": "antagonist"},
 ]
 character_relationships = {"Character1": {"Character2": "enemy"}}
 generation_params = {"temperature": 0.7}

 story = StoryFactory(
 main_characters=main_characters,
 character_relationships=character_relationships,
 generation_params=generation_params,
)

 assert story.main_characters == main_characters
 assert story.character_relationships == character_relationships
 assert story.generation_params == generation_params

 def test_story_episodes_relationship(self, db_session: Session):
 """test story episode relationship"""
 setup_factories(db_session)

 story = StoryFactory()
 episode1 = EpisodeFactory(story=story)
 episode2 = EpisodeFactory(story=story)

 assert len(story.episodes) == 2
 assert episode1 in story.episodes
 assert episode2 in story.episodes
 assert episode1.story == story
 assert episode2.story == story

 def test_story_characters_relationship(self, db_session: Session):
 """test story character relationship"""
 setup_factories(db_session)

 story = StoryFactory()
 character1 = StoryCharacterFactory(story=story)
 character2 = StoryCharacterFactory(story=story)

 assert len(story.story_characters) == 2
 assert character1 in story.story_characters
 assert character2 in story.story_characters


@pytest.mark.unit
class TestEpisodeModel:
 """episode model test"""

 def test_create_episode(self, db_session: Session):
 """test create episode"""
 setup_factories(db_session)

 episode = EpisodeFactory()

 assert episode.id is not None
 assert episode.title is not None
 assert episode.story_id is not None
 assert episode.episode_number is not None
 assert episode.created_at is not None

 def test_episode_json_fields(self, db_session: Session):
 """Ce Shi Ju JiJSONZi Duan"""
 setup_factories(db_session)

 plot_points = [
 {"order": 1, "description": "Opening scene"},
 {"order": 2, "description": "Conflict scene"},
 ]
 character_arcs = {
 "Character1": "Character growth arc",
 "Character2": "Redemption arc",
 }
 conflicts = [
 {"type": "internal", "description": "Doubt"},
 {"type": "external", "description": "Rival shows up"},
 ]

 episode = EpisodeFactory(
 plot_points=plot_points,
 character_arcs=character_arcs,
 conflicts=conflicts,
)

 assert episode.plot_points == plot_points
 assert episode.character_arcs == character_arcs
 assert episode.conflicts == conflicts

 def test_episode_scripts_relationship(self, db_session: Session):
 """test episode script relationship"""
 setup_factories(db_session)

 episode = EpisodeFactory()
 script1 = ScriptFactory(episode=episode)
 script2 = ScriptFactory(episode=episode)

 assert len(episode.scripts) == 2
 assert script1 in episode.scripts
 assert script2 in episode.scripts
 assert script1.episode == episode
 assert script2.episode == episode


@pytest.mark.unit
class TestScriptModel:
 """script model test"""

 def test_create_script(self, db_session: Session):
 """test create script"""
 setup_factories(db_session)

 script = ScriptFactory()

 assert script.id is not None
 assert script.title is not None
 assert script.episode_id is not None
 assert script.content is not None
 assert script.created_at is not None

 def test_script_json_fields(self, db_session: Session):
 """Ce Shi Ju BenJSONZi Duan"""
 setup_factories(db_session)

 scenes = [
 {"scene_number": 1, "slug_line": "INT. ROOM - DAY", "summary": "Opening"},
 {
 "scene_number": 2,
 "slug_line": "EXT. STREET - NIGHT",
 "summary": "Conflict",
 },
 ]
 dialogues = [
 {"scene_number": 1, "character": "Character1", "content": "Hello!"},
 {"scene_number": 2, "character": "Character2", "content": "Stop!"},
 ]
 stage_directions = [
 {"scene_number": 1, "direction": "Camera pans across the room."},
 {"scene_number": 2, "direction": "Cut to close-up."},
 ]
 generation_params = {"temperature": 0.8}

 script = ScriptFactory(
 scenes=scenes,
 dialogues=dialogues,
 stage_directions=stage_directions,
 generation_params=generation_params,
)

 assert script.scenes == scenes
 assert script.dialogues == dialogues
 assert script.stage_directions == stage_directions
 assert script.generation_params == generation_params

 def test_script_counts(self, db_session: Session):
 """test script Ji Shu Zi Duan"""
 setup_factories(db_session)

 script = ScriptFactory(word_count=1500, character_count=7500)

 assert script.word_count == 1500
 assert script.character_count == 7500


@pytest.mark.unit
class TestStoryCharacterModel:
 """story character model test"""

 def test_create_story_character(self, db_session: Session):
 """test create story character"""
 setup_factories(db_session)

 character = StoryCharacterFactory()

 assert character.id is not None
 assert character.story_id is not None
 assert character.virtual_ip_id is not None
 assert character.character_name is not None
 assert character.created_at is not None

 def test_story_character_json_fields(self, db_session: Session):
 """test story characterJSONZi Duan"""
 setup_factories(db_session)

 relationships = {"Character2": "friend", "Character3": "rival"}

 character = StoryCharacterFactory(relationships=relationships)

 assert character.relationships == relationships

 def test_story_character_relationships(self, db_session: Session):
 """test story character relationship"""
 setup_factories(db_session)

 story = StoryFactory()
 virtual_ip = VirtualIPFactory()
 character = StoryCharacterFactory(story=story, virtual_ip=virtual_ip)

 assert character.story == story
 assert character.virtual_ip == virtual_ip
 assert character in story.story_characters


@pytest.mark.unit
class TestScriptTemplateModel:
 """script template model test"""

 def test_create_script_template(self, db_session: Session):
 """test create script template"""
 setup_factories(db_session)

 template = ScriptTemplateFactory()

 assert template.id is not None
 assert template.name is not None
 assert template.created_at is not None

 def test_script_template_json_fields(self, db_session: Session):
 """test script templateJSONZi Duan"""
 setup_factories(db_session)

 structure = {"acts": 3, "scenes_per_act": 3, "total_scenes": 9}
 variables = {
 "character_name": "string",
 "location": "string",
 "time_period": "string",
 }

 template = ScriptTemplateFactory(structure=structure, variables=variables)

 assert template.structure == structure
 assert template.variables == variables

 def test_script_template_usage_count(self, db_session: Session):
 """test script template use Ji Shu"""
 setup_factories(db_session)

 template = ScriptTemplateFactory(usage_count=0)

 assert template.usage_count == 0

 # mock use template
 template.usage_count += 1
 db_session.commit()

 assert template.usage_count == 1


@pytest.mark.unit
class TestModelRelationships:
 """model relationship test"""

 def test_complete_story_workflow(self, db_session: Session):
 """test complete De story work Liu"""
 setup_factories(db_session)

 # Chuang Jian Xu NiIP
 virtual_ip = VirtualIPFactory()

 # Chuang Jian Gu Shi
 story = StoryFactory()

 # create story character
 character = StoryCharacterFactory(story=story, virtual_ip=virtual_ip)

 # Chuang Jian Ju Ji
 episode = EpisodeFactory(story=story)

 # Chuang Jian Ju Ben
 script = ScriptFactory(episode=episode)

 # validate Suo You relationship
 assert character.story == story
 assert character.virtual_ip == virtual_ip
 assert episode.story == story
 assert script.episode == episode
 assert script.episode.story == story

 # validate Fan Xiang relationship
 assert character in story.story_characters
 assert episode in story.episodes
 assert script in episode.scripts

 def test_cascade_delete_story(self, db_session: Session):
 """test story Ji Lian delete"""
 setup_factories(db_session)

 story = StoryFactory()
 character = StoryCharacterFactory(story=story)
 episode = EpisodeFactory(story=story)
 script = ScriptFactory(episode=episode)

 story_id = story.id
 character_id = character.id
 episode_id = episode.id
 script_id = script.id

 # Shan Chu Gu Shi
 db_session.delete(story)
 db_session.commit()

 # check Ji Lian delete
 assert db_session.query(Story).filter(Story.id == story_id).first() is None
 assert (
 db_session.query(StoryCharacter)
.filter(StoryCharacter.id == character_id)
.first()
 is None
)
 assert (
 db_session.query(Episode).filter(Episode.id == episode_id).first() is None
)
 assert db_session.query(Script).filter(Script.id == script_id).first() is None

 def test_virtual_ip_multiple_stories(self, db_session: Session):
 """Ce Shi Xu NiIPZai Duo Ge story Zhong De use"""
 setup_factories(db_session)

 virtual_ip = VirtualIPFactory()
 story1 = StoryFactory()
 story2 = StoryFactory()

 character1 = StoryCharacterFactory(story=story1, virtual_ip=virtual_ip)
 character2 = StoryCharacterFactory(story=story2, virtual_ip=virtual_ip)

 # Yan Zheng Xu NiIPKe Yi Zai Duo Ge story Zhong use
 assert character1.virtual_ip == virtual_ip
 assert character2.virtual_ip == virtual_ip
 assert character1.story!= character2.story
