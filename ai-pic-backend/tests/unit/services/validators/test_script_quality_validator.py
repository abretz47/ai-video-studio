"""Unit tests for ScriptQualityValidator."""

from __future__ import annotations

import pytest

from app.services.validators.script_quality_validator import (
    SceneEmotionalArc,
    ScriptQualityIssue,
    ScriptQualityIssueType,
    ScriptQualityResult,
    ScriptQualitySeverity,
    ScriptQualityValidator,
)


@pytest.fixture
def validator() -> ScriptQualityValidator:
    """Create a validator instance."""
    return ScriptQualityValidator()


class TestScriptQualityIssue:
    """Tests for ScriptQualityIssue dataclass."""

    def test_to_dict(self) -> None:
        """Test serialization."""
        issue = ScriptQualityIssue(
            issue_type=ScriptQualityIssueType.UNNATURAL_DIALOGUE,
            severity=ScriptQualitySeverity.WARNING,
            message="Test message",
            scene_number=1,
            dialogue_index=5,
            details={"key": "value"},
            suggestions=["Fix it"],
        )
        result = issue.to_dict()
        assert result["issue_type"] == "unnatural_dialogue"
        assert result["severity"] == "warning"
        assert result["message"] == "Test message"
        assert result["scene_number"] == 1
        assert result["dialogue_index"] == 5


class TestSceneEmotionalArc:
    """Tests for SceneEmotionalArc dataclass."""

    def test_to_dict_with_progression(self) -> None:
        """Test serialization with emotion progression."""
        arc = SceneEmotionalArc(
            scene_number=1,
            entry_emotion="calm",
            exit_emotion="angry",
            emotion_sequence=["calm", "Yi Huo", "angry"],
            has_progression=True,
        )
        d = arc.to_dict()
        assert d["scene_number"] == 1
        assert d["entry_emotion"] == "calm"
        assert d["exit_emotion"] == "angry"
        assert d["has_progression"] is True

    def test_to_dict_flat(self) -> None:
        """Test serialization with flat emotion."""
        arc = SceneEmotionalArc(
            scene_number=2,
            entry_emotion="happy",
            exit_emotion="happy",
            emotion_sequence=["happy", "happy", "happy"],
            has_progression=False,
        )
        d = arc.to_dict()
        assert d["has_progression"] is False


class TestScriptQualityResult:
    """Tests for ScriptQualityResult dataclass."""

    def test_to_dict_minimal(self) -> None:
        """Test serialization with minimal data."""
        result = ScriptQualityResult(passed=True)
        d = result.to_dict()
        assert d["passed"] is True
        assert d["issues"] == []
        assert d["dialogue_authenticity_score"] == 0.0

    def test_to_dict_full(self) -> None:
        """Test serialization with full data."""
        result = ScriptQualityResult(
            passed=True,
            dialogue_authenticity_score=0.75,
            exposition_ratio=0.15,
            dialogue_action_ratio=2.5,
        )
        d = result.to_dict()
        assert d["dialogue_authenticity_score"] == 0.75
        assert d["exposition_ratio"] == 0.15
        assert d["dialogue_action_ratio"] == 2.5


class TestScriptQualityValidator:
    """Tests for ScriptQualityValidator."""

    def test_validate_empty_content(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test validation with empty content."""
        result = validator.validate({"dialogues": []})
        assert result.passed is True
        assert len(result.issues) == 0

    def test_score_dialogue_authenticity_natural(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test authenticity scoring with natural dialogue."""
        dialogues = [
            {"content": "N...Ni Shuo Dui Ba？Wo Ye not Que Ding Ne。"},
            {"content": "Zhen De Ma？Tai Hao Le！"},
            {"content": "A，Na Zen Me Ban Ne？"},
        ]
        score = validator._score_dialogue_authenticity(dialogues)
        assert score > 0.5  # Natural dialogue should score above average

    def test_score_dialogue_authenticity_unnatural(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test authenticity scoring with expository dialogue."""
        dialogues = [
            {"content": "Zheng Ru Ni Suo Zhi，Wo Men Ren Wu is Fei Chang Zhong Yao，Yin Wei it relationship to Zheng Ge Ji Hua Cheng Bai。"},
            {"content": "Rang Wo Jie Shi Yi Xia，Shi Qing is Zhe Yang，in Hen Jiu Yi Qian Fa Sheng Yi Jian Shi Qing。"},
        ]
        score = validator._score_dialogue_authenticity(dialogues)
        assert score < 0.6  # Expository dialogue should score lower

    def test_score_single_dialogue_with_questions(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test single dialogue scoring with questions."""
        natural = "Ni Zen Me Kan？Tong Yi Ma？"
        expository = "Zheng Ru Ni Suo Zhi，Shi Shi Shang，Jian Dan Lai Shuo Jiu Shi Zhe Yang。"

        natural_score = validator._score_single_dialogue(natural)
        exp_score = validator._score_single_dialogue(expository)

        assert natural_score > exp_score

    def test_calculate_exposition_ratio(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test exposition ratio calculation."""
        dialogues = [
            {"content": "Rang Wo Jie Shi Yi Xia，Shi Qing is Zhe Yang。"},  # Expository
            {"content": "Ni Hao A！"},  # Natural
            {"content": "Zheng Ru Ni Suo Zhi，Wo Lai Gao Su Ni reason。"},  # Expository
            {"content": "N，Hao。"},  # Natural
        ]
        ratio = validator._calculate_exposition_ratio(dialogues)
        assert ratio == 0.5  # 2 out of 4 are expository

    def test_is_expository_true(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test expository detection with expository content."""
        content = "Zheng Ru Ni Suo Zhi，Rang Wo Jie Shi Yi Xia Zhe Jian Shi Qing。"
        assert validator._is_expository(content) is True

    def test_is_expository_false(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test expository detection with natural content."""
        content = "Ni Zen Me？Fa Sheng Shen Me Shi？"
        assert validator._is_expository(content) is False

    def test_check_exposition_excessive(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test excessive exposition detection."""
        dialogues = [
            {"scene_number": 1, "content": "Zheng Ru Ni Suo Zhi，Wo Lai Gao Su Ni。"},
            {"scene_number": 1, "content": "Rang Wo Jie Shi Yi Xia Shi Qing is Zhe Yang。"},
            {"scene_number": 1, "content": "Shi Shi Shang Jian Dan Lai Shuo Jiu Shi Zhe Yang。"},
            {"scene_number": 1, "content": "Ni Ke Neng not Zhi Dao，Qi Shi Yuan Lai is Zhe Yang。"},
        ]
        issues = validator._check_exposition(dialogues)
        assert len(issues) > 0
        assert issues[0].issue_type == ScriptQualityIssueType.EXCESSIVE_EXPOSITION

    def test_calculate_dialogue_action_ratio(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test dialogue-action ratio calculation."""
        dialogues = [{"content": "a"}, {"content": "b"}, {"content": "c"}]
        stage_directions = [{"content": "x"}]

        ratio = validator._calculate_dialogue_action_ratio(dialogues, stage_directions)
        assert ratio == 3.0

    def test_check_dialogue_action_ratio_imbalanced(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test dialogue-action ratio with imbalance."""
        # Too many dialogues
        issues = validator._check_dialogue_action_ratio(10.0, [])
        assert len(issues) > 0
        assert issues[0].issue_type == ScriptQualityIssueType.TALKING_HEADS

    def test_check_dialogue_action_ratio_balanced(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test dialogue-action ratio with balanced content."""
        issues = validator._check_dialogue_action_ratio(2.0, [])
        assert len(issues) == 0

    def test_analyze_emotional_arcs(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test emotional arc analysis."""
        scenes = [{"scene_number": 1}, {"scene_number": 2}]
        dialogues = [
            {"scene_number": 1, "content": "a", "emotion": "calm"},
            {"scene_number": 1, "content": "b", "emotion": "Yi Huo"},
            {"scene_number": 1, "content": "c", "emotion": "angry"},
            {"scene_number": 2, "content": "d", "emotion": "happy"},
            {"scene_number": 2, "content": "e", "emotion": "happy"},
        ]

        arcs = validator._analyze_emotional_arcs(scenes, dialogues)

        assert len(arcs) == 2
        assert arcs[0].has_progression is True  # Scene 1 has progression
        assert arcs[1].has_progression is False  # Scene 2 is flat

    def test_check_emotional_arcs_flat(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test emotional arc check with flat emotion."""
        arcs = [
            SceneEmotionalArc(
                scene_number=1,
                entry_emotion="happy",
                exit_emotion="happy",
                emotion_sequence=["happy", "happy", "happy"],
                has_progression=False,
            )
        ]
        issues = validator._check_emotional_arcs(arcs)
        assert len(issues) > 0
        assert issues[0].issue_type == ScriptQualityIssueType.EMOTIONAL_ARC_FLAT

    def test_check_emotional_arcs_jump(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test emotional arc check with unreasonable jump."""
        arcs = [
            SceneEmotionalArc(
                scene_number=1,
                entry_emotion="happy",
                exit_emotion="Zhen Jing angry",
                emotion_sequence=["happy", "Zhen Jing angry"],
                has_progression=True,
            )
        ]
        issues = validator._check_emotional_arcs(arcs)
        jump_issues = [
            i for i in issues
            if i.issue_type == ScriptQualityIssueType.EMOTIONAL_ARC_JUMP
        ]
        assert len(jump_issues) > 0

    def test_categorize_emotion(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test emotion categorization."""
        assert validator._categorize_emotion("happy") == "positive"
        assert validator._categorize_emotion("angry") == "intense"
        assert validator._categorize_emotion("calm") == "neutral"
        assert validator._categorize_emotion("Bei Shang") == "negative"
        assert validator._categorize_emotion("Wei Zhi") == "neutral"

    def test_check_subtext_missing(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test subtext check with missing subtext."""
        # Create 15 direct dialogues with no subtext
        dialogues = [
            {"content": f"Zhi Jie Biao Da {i}。"} for i in range(15)
        ]
        issues = validator._check_subtext(dialogues)
        subtext_issues = [
            i for i in issues
            if i.issue_type == ScriptQualityIssueType.MISSING_SUBTEXT
        ]
        assert len(subtext_issues) > 0

    def test_check_subtext_present(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test subtext check with subtext present."""
        dialogues = [
            {"content": "Mei Shi，Hen Hao。Dan Shi..."},  # Has subtext
            {"content": "Ting Hao，Bu Guo Wo Hai Shi Dan Xin。"},  # Has subtext
            {"content": "Mei Guan Xi，Ran Er Xin Li Hen Tong。"},  # Has subtext
        ]
        issues = validator._check_subtext(dialogues)
        # Should not report missing subtext
        subtext_issues = [
            i for i in issues
            if i.issue_type == ScriptQualityIssueType.MISSING_SUBTEXT
        ]
        assert len(subtext_issues) == 0

    def test_check_repetitive_dialogue(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test repetitive dialogue detection."""
        dialogues = [
            {"content": "Ni Hao A，Jin Tian Tian Qi Zhen Hao"},
            {"content": "Ni Hao A，Jin Tian Tian Qi Zhen Hao"},
            {"content": "Ni Hao A，Jin Tian Tian Qi Zhen Hao"},
            {"content": "Bu Tong content"},
        ]
        issues = validator._check_repetitive_dialogue(dialogues)
        assert len(issues) > 0
        assert issues[0].issue_type == ScriptQualityIssueType.REPETITIVE_DIALOGUE

    def test_validate_full_script_good(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test full validation with good script."""
        content = {
            "scenes": [{"scene_number": 1}],
            "dialogues": [
                {"scene_number": 1, "content": "N...Ni Zen Me Kan？", "emotion": "curious"},
                {"scene_number": 1, "content": "Wo Jue De...Bu Tai Dui Jin！", "emotion": "Yi Huo"},
                {"scene_number": 1, "content": "Tian A！Yuan Lai is Zhe Yang？", "emotion": "Zhen Jing"},
            ],
            "stage_directions": [
                {"scene_number": 1, "content": "characterAZhou Mei"},
                {"scene_number": 1, "content": "characterBZhan Qi Shen"},
            ],
        }

        result = validator.validate(content)

        assert result.passed is True
        assert result.dialogue_authenticity_score > 0.4
        assert result.dialogue_action_ratio > 0

    def test_validate_full_script_with_issues(
        self, validator: ScriptQualityValidator
    ) -> None:
        """Test full validation with problematic script."""
        content = {
            "scenes": [{"scene_number": 1}],
            "dialogues": [
                {"scene_number": 1, "content": "Zheng Ru Ni Suo Zhi，Rang Wo Jie Shi Yi Xia Shi Qing is Zhe Yang。", "emotion": "calm"},
                {"scene_number": 1, "content": "Shi Shi Shang Jian Dan Lai Shuo，Wo Lai Gao Su Ni reason。", "emotion": "calm"},
                {"scene_number": 1, "content": "Ni Ke Neng not Zhi Dao，Qi Shi Yuan Lai is Zhe Yang。", "emotion": "calm"},
            ],
            "stage_directions": [],
        }

        result = validator.validate(content)

        # Should have issues for:
        # - Excessive exposition
        # - Talking heads (no stage directions)
        # - Flat emotional arc
        assert len(result.issues) > 0
        assert result.dialogue_authenticity_score < 0.6
