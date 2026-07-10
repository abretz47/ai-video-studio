"""Unit tests for CinematicRulesValidator."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.services.storyboard.pipeline.pipeline_state import (
 PipelineState,
 ValidationSeverity,
)
from app.services.storyboard.validators.cinematic_rules_validator import (
 CinematicRulesValidator,
)


@pytest.fixture
def validator() -> CinematicRulesValidator:
 """Create a validator instance."""
 return CinematicRulesValidator()


@pytest.fixture
def mock_context() -> MagicMock:
 """Create a mock pipeline context."""
 return MagicMock()


@pytest.fixture
def mock_state() -> PipelineState:
 """Create a mock pipeline state with minimal required fields."""
 return PipelineState(script_id=1, episode_id=1, frames=[])


class TestCinematicRulesValidator:
 """Tests for CinematicRulesValidator."""

 def test_validator_name(self, validator: CinematicRulesValidator) -> None:
 """Test validator name property."""
 assert validator.name == "cinematic_rules_validator"

 def test_validator_description(self, validator: CinematicRulesValidator) -> None:
 """Test validator description property."""
 assert "180-degree" in validator.description

 def test_validate_empty_frames(
 self,
 validator: CinematicRulesValidator,
 mock_state: PipelineState,
 mock_context: MagicMock,
) -> None:
 """Test validation with no frames."""
 results = validator.validate(mock_state, mock_context)
 assert len(results) == 1
 assert results[0].severity == ValidationSeverity.WARNING
 assert "No frames" in results[0].message

 def test_classify_shot_type_close_up(
 self, validator: CinematicRulesValidator
) -> None:
 """Test shot type classification for close-up."""
 frame = {"description": "John Doe close shot camera, Biao Qing Jin Zhang"}
 assert validator._classify_shot_type(frame) == "close_up"

 def test_classify_shot_type_extreme_close_up(
 self, validator: CinematicRulesValidator
) -> None:
 """Test shot type classification for extreme close-up."""
 frame = {"description": "John Doe Da Te Xie, Yan Shen Te Xie"}
 assert validator._classify_shot_type(frame) == "extreme_close_up"

 def test_classify_shot_type_wide(
 self, validator: CinematicRulesValidator
) -> None:
 """Test shot type classification for wide shot."""
 frame = {"description": "Quan Jing camera Zhan Shi Zheng Ge office"}
 assert validator._classify_shot_type(frame) == "wide"

 def test_classify_shot_type_medium(
 self, validator: CinematicRulesValidator
) -> None:
 """Test shot type classification for medium shot."""
 frame = {"description": "medium shot, Liang Ren Mian Dui Mian Jiao Tan"}
 assert validator._classify_shot_type(frame) == "medium"

 def test_classify_shot_type_from_field(
 self, validator: CinematicRulesValidator
) -> None:
 """Test shot type classification from explicit field."""
 frame = {"shot_type": "close-up", "description": "Ren Yi Miao Shu"}
 assert validator._classify_shot_type(frame) == "close_up"

 def test_classify_shot_type_unknown(
 self, validator: CinematicRulesValidator
) -> None:
 """Test shot type classification with no indicators."""
 frame = {"description": "Liang Ren Zai Fang Jian Li"}
 assert validator._classify_shot_type(frame) is None

 def test_detect_lighting_day(
 self, validator: CinematicRulesValidator
) -> None:
 """Test lighting detection for day."""
 frame = {"description": "Bai Tian, Yang Guang Tou Guo Chuang Hu Zhao Jin Lai"}
 assert validator._detect_lighting(frame) == "day"

 def test_detect_lighting_night(
 self, validator: CinematicRulesValidator
) -> None:
 """Test lighting detection for night."""
 frame = {"description": "Ye Wan, Yue Guang Sa Zai Di Mian"}
 assert validator._detect_lighting(frame) == "night"

 def test_detect_lighting_from_field(
 self, validator: CinematicRulesValidator
) -> None:
 """Test lighting detection from explicit field."""
 frame = {"time_of_day": "morning", "description": "Ren Yi Miao Shu"}
 assert validator._detect_lighting(frame) == "day"

 def test_detect_lighting_unknown(
 self, validator: CinematicRulesValidator
) -> None:
 """Test lighting detection with no indicators."""
 frame = {"description": "Liang Ren Jiao Tan"}
 assert validator._detect_lighting(frame) is None

 def test_is_position_flip_left_to_right(
 self, validator: CinematicRulesValidator
) -> None:
 """Test position flip detection left to right."""
 assert validator._is_position_flip("left", "right") is True

 def test_is_position_flip_same_side(
 self, validator: CinematicRulesValidator
) -> None:
 """Test position flip detection same side."""
 assert validator._is_position_flip("left", "left") is False
 assert validator._is_position_flip("left", "over_shoulder_left") is False

 def test_is_position_flip_center(
 self, validator: CinematicRulesValidator
) -> None:
 """Test position flip with center position."""
 assert validator._is_position_flip("center", "left") is False
 assert validator._is_position_flip("center", "right") is False

 def test_check_shot_variety_good(
 self,
 validator: CinematicRulesValidator,
 mock_state: PipelineState,
 mock_context: MagicMock,
) -> None:
 """Test shot variety check with good variety."""
 mock_state.frames = [
 {"scene_number": 1, "description": "Quan Jing Jian Li scene"},
 {"scene_number": 1, "description": "medium shot Liang Ren Jiao Tan"},
 {"scene_number": 1, "description": "close-up John Doe Biao Qing"},
 {"scene_number": 1, "description": "medium shot Fan Da Jane Roe"},
 {"scene_number": 1, "description": "Quan Jing Jie Shu scene"},
 ]
 results = validator.validate(mock_state, mock_context)
 # Should have no shot variety warnings
 variety_warnings = [
 r for r in results
 if "Jing Bie Que Fa Bian Hua" in r.message
 ]
 assert len(variety_warnings) == 0

 def test_check_shot_variety_poor(
 self,
 validator: CinematicRulesValidator,
 mock_state: PipelineState,
 mock_context: MagicMock,
) -> None:
 """Test shot variety check with poor variety (all close-ups)."""
 mock_state.frames = [
 {"scene_number": 1, "description": "Te Xie Zhang San"},
 {"scene_number": 1, "description": "Te Xie Li Si"},
 {"scene_number": 1, "description": "close-up John Doe Fan Ying"},
 {"scene_number": 1, "description": "close-up Jane Roe Hui Ying"},
 {"scene_number": 1, "description": "Te Xie Wo Shou"},
 ]
 results = validator.validate(mock_state, mock_context)
 # Should have shot variety warning
 variety_warnings = [
 r for r in results
 if "Jing Bie Que Fa Bian Hua" in r.message
 ]
 assert len(variety_warnings) > 0
 assert variety_warnings[0].severity == ValidationSeverity.WARNING

 def test_check_lighting_continuity_good(
 self,
 validator: CinematicRulesValidator,
 mock_state: PipelineState,
 mock_context: MagicMock,
) -> None:
 """Test lighting continuity with consistent lighting."""
 mock_state.frames = [
 {"scene_number": 1, "description": "Bai Tian, Yang Guang Ming Mei"},
 {"scene_number": 1, "description": "Bai Tian, Shi Nei Guang Xian Chong Zu"},
 {"scene_number": 1, "description": "Bai Tian, Chuang Wai Ke Jian Lan Tian"},
 ]
 results = validator.validate(mock_state, mock_context)
 # Should have no lighting errors
 lighting_errors = [
 r for r in results
 if "Guang Xian Tu Bian" in r.message and r.severity == ValidationSeverity.ERROR
 ]
 assert len(lighting_errors) == 0

 def test_check_lighting_continuity_bad(
 self,
 validator: CinematicRulesValidator,
 mock_state: PipelineState,
 mock_context: MagicMock,
) -> None:
 """Test lighting continuity with sudden day/night change."""
 mock_state.frames = [
 {"scene_number": 1, "description": "Bai Tian, Yang Guang Ming Mei"},
 {"scene_number": 1, "description": "Ye Wan, Yue Guang Sa Luo"},
 ]
 results = validator.validate(mock_state, mock_context)
 # Should have lighting error
 lighting_errors = [
 r for r in results
 if "Guang Xian Tu Bian" in r.message
 ]
 assert len(lighting_errors) > 0
 assert lighting_errors[0].severity == ValidationSeverity.ERROR

 def test_check_shot_rhythm_good(
 self,
 validator: CinematicRulesValidator,
 mock_state: PipelineState,
 mock_context: MagicMock,
) -> None:
 """Test shot rhythm with good variety."""
 mock_state.frames = [
 {"scene_number": 1, "description": "Te Xie Zhang San"},
 {"scene_number": 1, "description": "Zhong Jing Liang Ren"},
 {"scene_number": 1, "description": "Te Xie Li Si"},
 ]
 results = validator.validate(mock_state, mock_context)
 # Should have no rhythm warnings
 rhythm_warnings = [
 r for r in results
 if "Tiao Qie" in r.message
 ]
 assert len(rhythm_warnings) == 0

 def test_check_shot_rhythm_bad(
 self,
 validator: CinematicRulesValidator,
 mock_state: PipelineState,
 mock_context: MagicMock,
) -> None:
 """Test shot rhythm with consecutive same shots."""
 mock_state.frames = [
 {"scene_number": 1, "description": "Te Xie Zhang San"},
 {"scene_number": 1, "description": "Te Xie Li Si"},
 {"scene_number": 1, "description": "Te Xie Zhang San"},
 {"scene_number": 1, "description": "Te Xie Li Si"},
 {"scene_number": 1, "description": "Te Xie Wo Shou"},
 ]
 results = validator.validate(mock_state, mock_context)
 # Should have rhythm warning
 rhythm_warnings = [
 r for r in results
 if "Tiao Qie" in r.message or "Lian Xu" in r.message
 ]
 assert len(rhythm_warnings) > 0

 def test_group_frames_by_scene(
 self, validator: CinematicRulesValidator
) -> None:
 """Test frame grouping by scene number."""
 frames = [
 {"scene_number": 1, "description": "Scene 1 frame 1"},
 {"scene_number": 1, "description": "Scene 1 frame 2"},
 {"scene_number": 2, "description": "Scene 2 frame 1"},
 {"scene_number": 2, "description": "Scene 2 frame 2"},
 {"scene_number": 2, "description": "Scene 2 frame 3"},
 ]
 scenes = validator._group_frames_by_scene(frames)
 assert len(scenes) == 2
 assert len(scenes[1]) == 2
 assert len(scenes[2]) == 3

 def test_can_auto_fix(self, validator: CinematicRulesValidator) -> None:
 """Test that validator cannot auto-fix."""
 assert validator.can_auto_fix() is False

 def test_validate_multiple_scenes(
 self,
 validator: CinematicRulesValidator,
 mock_state: PipelineState,
 mock_context: MagicMock,
) -> None:
 """Test validation across multiple scenes."""
 mock_state.frames = [
 # Scene 1 - good
 {"scene_number": 1, "description": "Bai Tian, Quan Jing"},
 {"scene_number": 1, "description": "Bai Tian, medium shot"},
 {"scene_number": 1, "description": "Bai Tian, close-up"},
 # Scene 2 - lighting issue
 {"scene_number": 2, "description": "Bai Tian, Hu Wai"},
 {"scene_number": 2, "description": "Ye Wan, Yue Guang"},
 ]
 results = validator.validate(mock_state, mock_context)
 # Should have lighting error for scene 2
 scene2_errors = [
 r for r in results
 if r.details.get("scene_number") == 2 and "Guang Xian" in r.message
 ]
 assert len(scene2_errors) > 0

 def test_validate_success_result(
 self,
 validator: CinematicRulesValidator,
 mock_state: PipelineState,
 mock_context: MagicMock,
) -> None:
 """Test that success result is added when all checks pass."""
 mock_state.frames = [
 {"scene_number": 1, "description": "Bai Tian, Quan Jing Zhan Shi scene"},
 {"scene_number": 1, "description": "Bai Tian, medium shot Liang Ren Jiao Tan"},
 ]
 results = validator.validate(mock_state, mock_context)
 success_results = [r for r in results if r.passed and "successfully" in r.message]
 assert len(success_results) >= 1
