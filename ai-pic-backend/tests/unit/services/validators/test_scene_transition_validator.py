"""Unit tests for SceneTransitionValidator."""

from __future__ import annotations

import pytest

from app.services.validators.scene_transition_validator import (
    SceneInfo,
    SceneTransitionValidator,
    TransitionIssue,
    TransitionIssueType,
    TransitionSeverity,
)


class TestTransitionIssue:
    """Tests for TransitionIssue dataclass."""

    def test_to_dict_basic(self) -> None:
        """Test basic serialization."""
        issue = TransitionIssue(
            issue_type=TransitionIssueType.TIME_DISCONTINUITY,
            severity=TransitionSeverity.WARNING,
            message="Time jump detected",
            from_scene=1,
            to_scene=2,
        )
        result = issue.to_dict()
        assert result["issue_type"] == "time_discontinuity"
        assert result["severity"] == "warning"
        assert result["message"] == "Time jump detected"
        assert result["from_scene"] == 1
        assert result["to_scene"] == 2

    def test_to_dict_full(self) -> None:
        """Test full serialization with all fields."""
        issue = TransitionIssue(
            issue_type=TransitionIssueType.GEOGRAPHIC_IMPOSSIBILITY,
            severity=TransitionSeverity.ERROR,
            message="Impossible travel",
            from_scene=3,
            to_scene=4,
            from_location="Bei Jing Shi",
            to_location="Shang Hai Shi",
            affected_characters=["John Doe"],
            fix_suggestion="Tian Jia Lv Tu scene",
        )
        result = issue.to_dict()
        assert result["from_location"] == "Bei Jing Shi"
        assert result["to_location"] == "Shang Hai Shi"
        assert result["affected_characters"] == ["John Doe"]
        assert result["fix_suggestion"] == "Tian Jia Lv Tu scene"


class TestSceneTransitionValidator:
    """Tests for SceneTransitionValidator."""

    @pytest.fixture
    def validator(self) -> SceneTransitionValidator:
        """Create a validator instance."""
        return SceneTransitionValidator()

    def test_normalize_time_morning(self, validator: SceneTransitionValidator) -> None:
        """Test time normalization for morning."""
        assert validator._normalize_time("morning") == "morning"
        assert validator._normalize_time("morning") == "morning"
        assert validator._normalize_time("Shang Wu") == "morning"

    def test_normalize_time_night(self, validator: SceneTransitionValidator) -> None:
        """Test time normalization for night."""
        assert validator._normalize_time("night") == "night"
        assert validator._normalize_time("Ye Wan") == "night"
        assert validator._normalize_time("Shen Ye") == "night"

    def test_normalize_time_unknown(self, validator: SceneTransitionValidator) -> None:
        """Test time normalization for unknown time."""
        assert validator._normalize_time("random") is None
        assert validator._normalize_time(None) is None

    def test_extract_city_chinese(self, validator: SceneTransitionValidator) -> None:
        """Test city extraction from Chinese location."""
        assert validator._extract_city("Bei Jing Shi Chao Yang Qu") == "Bei Jing"
        assert validator._extract_city("Shang Hai Shi Pu Dong Xin Qu") == "Shang Hai"
        assert validator._extract_city("Guang Zhou Tian He Qu") == "Guang Zhou"

    def test_extract_city_unknown(self, validator: SceneTransitionValidator) -> None:
        """Test city extraction for unknown location."""
        assert validator._extract_city("Mou Ge Xiao Zhen") is None
        assert validator._extract_city(None) is None

    def test_check_time_transition_valid(self, validator: SceneTransitionValidator) -> None:
        """Test valid time transitions."""
        from_scene = SceneInfo(scene_number=1, time_of_day="morning")
        to_scene = SceneInfo(scene_number=2, time_of_day="Zhong Wu")
        issue = validator._check_time_transition(from_scene, to_scene)
        assert issue is None

    def test_check_time_transition_invalid(self, validator: SceneTransitionValidator) -> None:
        """Test invalid time transition (afternoon to morning)."""
        from_scene = SceneInfo(scene_number=1, time_of_day="afternoon")
        to_scene = SceneInfo(scene_number=2, time_of_day="morning")
        issue = validator._check_time_transition(from_scene, to_scene)
        assert issue is not None
        assert issue.issue_type == TransitionIssueType.TIME_DISCONTINUITY
        assert issue.severity == TransitionSeverity.WARNING

    def test_check_time_transition_night_to_dawn_valid(
        self, validator: SceneTransitionValidator
    ) -> None:
        """Test valid night to dawn transition."""
        from_scene = SceneInfo(scene_number=1, time_of_day="Ye Wan")
        to_scene = SceneInfo(scene_number=2, time_of_day="Li Ming")
        issue = validator._check_time_transition(from_scene, to_scene)
        assert issue is None

    def test_check_geographic_transition_same_city(
        self, validator: SceneTransitionValidator
    ) -> None:
        """Test transition within same city."""
        from_scene = SceneInfo(scene_number=1, location="Bei Jing Shi Chao Yang Qu")
        to_scene = SceneInfo(scene_number=2, location="Bei Jing Shi Hai Dian Qu")
        issue = validator._check_geographic_transition(from_scene, to_scene)
        assert issue is None

    def test_check_geographic_transition_different_city_error(
        self, validator: SceneTransitionValidator
    ) -> None:
        """Test transition between different cities with same time (impossible)."""
        from_scene = SceneInfo(
            scene_number=1, location="Bei Jing Shi Chao Yang Qu", time_of_day="morning"
        )
        to_scene = SceneInfo(
            scene_number=2, location="Shang Hai Shi Pu Dong", time_of_day="morning"
        )
        issue = validator._check_geographic_transition(from_scene, to_scene)
        assert issue is not None
        assert issue.issue_type == TransitionIssueType.GEOGRAPHIC_IMPOSSIBILITY
        assert issue.severity == TransitionSeverity.ERROR

    def test_check_geographic_transition_different_city_warning(
        self, validator: SceneTransitionValidator
    ) -> None:
        """Test transition between different cities with different time (warning)."""
        from_scene = SceneInfo(
            scene_number=1, location="Bei Jing Shi Chao Yang Qu", time_of_day="morning"
        )
        to_scene = SceneInfo(
            scene_number=2, location="Shang Hai Shi Pu Dong", time_of_day="Bang Wan"
        )
        issue = validator._check_geographic_transition(from_scene, to_scene)
        # With enough time difference, it should be OK (5 hours Beijing to Shanghai)
        assert issue is None

    def test_detect_character_state_injured(
        self, validator: SceneTransitionValidator
    ) -> None:
        """Test detection of injured state."""
        assert validator._detect_character_state("John Doe Shou Shang Dao Di") == "injured"
        assert validator._detect_character_state("He was injured badly") == "injured"

    def test_detect_character_state_unconscious(
        self, validator: SceneTransitionValidator
    ) -> None:
        """Test detection of unconscious state."""
        assert validator._detect_character_state("Jane Roe Hun Mi Bu Xing") == "unconscious"
        assert validator._detect_character_state("She passed out") == "unconscious"

    def test_detect_character_state_none(
        self, validator: SceneTransitionValidator
    ) -> None:
        """Test no state detected."""
        assert validator._detect_character_state("John Doe Zou Jin Fang Jian") is None

    def test_extract_scene_info(self, validator: SceneTransitionValidator) -> None:
        """Test scene info extraction."""
        scene = {
            "scene_number": 1,
            "location": "Bei Jing Shi Chao Yang Qu Ka Fei Guan",
            "time_of_day": "afternoon",
            "dialogues": [
                {"character": "John Doe", "content": "Ni Hao"},
                {"character": "Jane Roe", "content": "Ni Hao"},
            ],
            "stage_directions": [
                {"content": "John Doe Shou Shang after Man Man Zuo Xia"},
            ],
        }
        info = validator.extract_scene_info(scene)
        assert info.scene_number == 1
        assert info.city == "Bei Jing"
        assert info.time_of_day == "afternoon"
        assert "John Doe" in info.characters_present
        assert "Jane Roe" in info.characters_present
        assert info.character_states.get("John Doe") == "injured"

    def test_validate_transitions_no_issues(
        self, validator: SceneTransitionValidator
    ) -> None:
        """Test validation with no issues."""
        scenes = [
            {
                "scene_number": 1,
                "location": "Bei Jing Shi Chao Yang Qu",
                "time_of_day": "morning",
            },
            {
                "scene_number": 2,
                "location": "Bei Jing Shi Hai Dian Qu",
                "time_of_day": "Zhong Wu",
            },
        ]
        issues = validator.validate_transitions(scenes)
        assert len(issues) == 0

    def test_validate_transitions_time_issue(
        self, validator: SceneTransitionValidator
    ) -> None:
        """Test validation detecting time discontinuity."""
        scenes = [
            {
                "scene_number": 1,
                "location": "office",
                "time_of_day": "Bang Wan",
            },
            {
                "scene_number": 2,
                "location": "office",
                "time_of_day": "morning",
            },
        ]
        issues = validator.validate_transitions(scenes)
        assert len(issues) > 0
        assert any(i.issue_type == TransitionIssueType.TIME_DISCONTINUITY for i in issues)

    def test_validate_transitions_geographic_issue(
        self, validator: SceneTransitionValidator
    ) -> None:
        """Test validation detecting geographic impossibility."""
        scenes = [
            {
                "scene_number": 1,
                "location": "Bei Jing Shi Zhong Xin",
                "time_of_day": "afternoon",
            },
            {
                "scene_number": 2,
                "location": "Shang Hai Shi Zhong Xin",
                "time_of_day": "afternoon",
            },
        ]
        issues = validator.validate_transitions(scenes)
        assert len(issues) > 0
        assert any(
            i.issue_type == TransitionIssueType.GEOGRAPHIC_IMPOSSIBILITY for i in issues
        )

    def test_validate_transitions_single_scene(
        self, validator: SceneTransitionValidator
    ) -> None:
        """Test validation with single scene (no transitions)."""
        scenes = [{"scene_number": 1, "location": "office"}]
        issues = validator.validate_transitions(scenes)
        assert len(issues) == 0

    def test_generate_fix_suggestions(
        self, validator: SceneTransitionValidator
    ) -> None:
        """Test fix suggestion generation."""
        issues = [
            TransitionIssue(
                issue_type=TransitionIssueType.GEOGRAPHIC_IMPOSSIBILITY,
                severity=TransitionSeverity.ERROR,
                message="Di Li not Ke Neng",
                from_scene=1,
                to_scene=2,
            ),
            TransitionIssue(
                issue_type=TransitionIssueType.TIME_DISCONTINUITY,
                severity=TransitionSeverity.WARNING,
                message="time Tiao Yue",
                from_scene=2,
                to_scene=3,
            ),
        ]
        suggestions = validator.generate_fix_suggestions(issues)
        assert len(suggestions) == 2
        assert "suggested_actions" in suggestions[0]
        assert len(suggestions[0]["suggested_actions"]) > 0


class TestSceneInfo:
    """Tests for SceneInfo dataclass."""

    def test_default_values(self) -> None:
        """Test default values."""
        info = SceneInfo(scene_number=1)
        assert info.scene_number == 1
        assert info.location is None
        assert info.city is None
        assert info.time_of_day is None
        assert info.characters_present == []
        assert info.character_states == {}

    def test_with_values(self) -> None:
        """Test with populated values."""
        info = SceneInfo(
            scene_number=3,
            location="Shang Hai Shi",
            city="Shang Hai",
            time_of_day="Ye Wan",
            characters_present=["John Doe", "Jane Roe"],
            character_states={"John Doe": "injured"},
        )
        assert info.scene_number == 3
        assert info.city == "Shang Hai"
        assert "John Doe" in info.characters_present
        assert info.character_states["John Doe"] == "injured"
