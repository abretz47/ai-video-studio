"""Unit tests for EpisodeQualityValidator."""

from __future__ import annotations

import pytest

from app.services.validators.episode_quality_validator import (
    CharacterArc,
    EpisodeQualityIssue,
    EpisodeQualityIssueType,
    EpisodeQualityResult,
    EpisodeQualitySeverity,
    EpisodeQualityValidator,
    ForeshadowingItem,
)


@pytest.fixture
def validator() -> EpisodeQualityValidator:
    """Create a validator instance."""
    return EpisodeQualityValidator()


class TestEpisodeQualityIssue:
    """Tests for EpisodeQualityIssue dataclass."""

    def test_to_dict(self) -> None:
        """Test serialization."""
        issue = EpisodeQualityIssue(
            issue_type=EpisodeQualityIssueType.CHARACTER_ARC_STAGNANT,
            severity=EpisodeQualitySeverity.WARNING,
            message="Test message",
            episode_number=1,
            character_name="Alice",
            details={"key": "value"},
            suggestions=["Fix it"],
        )
        result = issue.to_dict()
        assert result["issue_type"] == "character_arc_stagnant"
        assert result["severity"] == "warning"
        assert result["message"] == "Test message"
        assert result["episode_number"] == 1
        assert result["character_name"] == "Alice"


class TestCharacterArc:
    """Tests for CharacterArc dataclass."""

    def test_has_progression_with_changes(self) -> None:
        """Test progression detection with changes."""
        arc = CharacterArc(
            character_name="Alice",
            episode_goals={1: "Zhao Dao truth", 2: "Tao Li Wei Xian", 3: "Zhan Sheng Di Ren"},
            episode_states={1: "Mi Mang", 2: "Jue Xing", 3: "Cheng Shu"},
        )
        assert arc.has_progression() is True

    def test_has_progression_stagnant(self) -> None:
        """Test progression detection with stagnant character."""
        arc = CharacterArc(
            character_name="Bob",
            episode_goals={1: "Bang Zhu Peng You", 2: "Bang Zhu Peng You", 3: "Bang Zhu Peng You"},
            episode_states={1: "loyal", 2: "loyal", 3: "loyal"},
        )
        assert arc.has_progression() is False

    def test_has_progression_insufficient_data(self) -> None:
        """Test progression with insufficient data."""
        arc = CharacterArc(
            character_name="Carol",
            episode_goals={1: "Tan Suo Shi Jie"},
        )
        # Not enough data to judge, default to True
        assert arc.has_progression() is True


class TestForeshadowingItem:
    """Tests for ForeshadowingItem dataclass."""

    def test_resolved_item(self) -> None:
        """Test resolved foreshadowing item."""
        item = ForeshadowingItem(
            setup_id="test_1",
            setup_description="mysterious Xin Jian",
            setup_episode=1,
            payoff_episode=5,
            is_resolved=True,
        )
        assert item.is_resolved
        assert item.payoff_episode == 5

    def test_unresolved_item(self) -> None:
        """Test unresolved foreshadowing item."""
        item = ForeshadowingItem(
            setup_id="test_2",
            setup_description="Yin Cang Bao Zang",
            setup_episode=2,
        )
        assert not item.is_resolved
        assert item.payoff_episode is None


class TestEpisodeQualityResult:
    """Tests for EpisodeQualityResult dataclass."""

    def test_to_dict_minimal(self) -> None:
        """Test serialization with minimal data."""
        result = EpisodeQualityResult(passed=True)
        d = result.to_dict()
        assert d["passed"] is True
        assert d["issues"] == []
        assert d["character_arcs"] == {}

    def test_to_dict_with_arcs(self) -> None:
        """Test serialization with character arcs."""
        result = EpisodeQualityResult(
            passed=True,
            character_arcs={
                "Alice": CharacterArc(
                    character_name="Alice",
                    episode_goals={1: "targetA", 2: "targetB"},
                )
            },
        )
        d = result.to_dict()
        assert "Alice" in d["character_arcs"]
        assert d["character_arcs"]["Alice"]["has_progression"] is True


class TestEpisodeQualityValidator:
    """Tests for EpisodeQualityValidator."""

    def test_validate_empty_episodes(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test validation with empty episodes."""
        result = validator.validate([])
        assert result.passed is True
        assert len(result.issues) == 0

    def test_track_character_arcs(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test character arc tracking."""
        episodes = [
            {
                "episode_number": 1,
                "characters": [
                    {"name": "Alice", "goal": "search truth", "status": "Mi Mang"},
                ],
            },
            {
                "episode_number": 2,
                "characters": [
                    {"name": "Alice", "goal": "Tao Li Wei Xian", "status": "Jue Xing"},
                ],
            },
        ]
        story_characters = [{"name": "Alice"}]

        arcs = validator._track_character_arcs(episodes, story_characters)

        assert "Alice" in arcs
        assert arcs["Alice"].episode_goals[1] == "search truth"
        assert arcs["Alice"].episode_goals[2] == "Tao Li Wei Xian"
        assert arcs["Alice"].has_progression()

    def test_track_character_arcs_from_continuity(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test arc tracking from continuity data."""
        episodes = [
            {
                "episode_number": 1,
                "continuity": {
                    "characters": {
                        "Bob": {"goal": "Bao Hu Jia Ren", "status": "tense"},
                    }
                },
            },
        ]

        arcs = validator._track_character_arcs(episodes, [])

        assert "Bob" in arcs
        assert arcs["Bob"].episode_goals[1] == "Bao Hu Jia Ren"

    def test_check_arc_progression_stagnant(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test stagnant arc detection."""
        arcs = {
            "Alice": CharacterArc(
                character_name="Alice",
                episode_goals={1: "Xiang Tong target", 2: "Xiang Tong target", 3: "Xiang Tong target"},
            )
        }
        issues = validator._check_arc_progression(arcs)
        assert len(issues) == 1
        assert issues[0].issue_type == EpisodeQualityIssueType.CHARACTER_ARC_STAGNANT

    def test_analyze_subplot_balance(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test subplot balance analysis."""
        episodes = [
            {"summary": "protagonist He Xin Ren Wu key Tu Po"},
            {"summary": "Lian Ai Gan Qing Xian Fa Zhan，protagonist Yue Hui"},
            {"summary": "Zhu Xian drama Tui Jin，conflict Mao Dun escalate"},
        ]
        ratios = validator._analyze_subplot_balance(episodes)
        assert "main" in ratios
        assert "romance" in ratios
        assert ratios["main"] > 0  # Should have main plot presence

    def test_check_subplot_balance_low_main(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test subplot imbalance detection when main plot is low."""
        ratios = {"main": 0.1, "romance": 0.5, "conflict": 0.2, "mystery": 0.1, "growth": 0.1}
        issues = validator._check_subplot_balance(ratios)
        assert len(issues) == 1
        assert issues[0].issue_type == EpisodeQualityIssueType.SUBPLOT_IMBALANCE
        assert "Zhu Xian" in issues[0].message

    def test_check_subplot_balance_no_subplot(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test subplot imbalance detection when no subplots."""
        ratios = {"main": 0.9, "romance": 0.02, "conflict": 0.02, "mystery": 0.03, "growth": 0.03}
        issues = validator._check_subplot_balance(ratios)
        assert len(issues) == 1
        assert "Zhi Xian" in issues[0].message

    def test_calculate_episode_tension(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test tension score calculation."""
        high_tension_ep = {
            "summary": "crisis Bao Fa，Sheng Si Dui Jue，character Xian Ru Jue Wang Zheng Zha",
            "climax": "Zui Zhong Dui Kang，truth Jie Lu",
        }
        low_tension_ep = {
            "summary": "calm Yi Tian，character Zai Jia Xiu Xi",
        }

        high_score = validator._calculate_episode_tension(high_tension_ep)
        low_score = validator._calculate_episode_tension(low_tension_ep)

        assert high_score > low_score

    def test_analyze_tension_progression(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test tension progression analysis."""
        episodes = [
            {"summary": "calm opening"},
            {"summary": "conflict Chu Xian，Jin Zhang Gan escalate"},
            {"summary": "crisis Bao Fa，climax Dui Jue"},
        ]
        scores = validator._analyze_tension_progression(episodes)
        assert len(scores) == 3
        # Should generally increase
        assert scores[2] >= scores[0]

    def test_check_tension_plateau(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test tension plateau detection."""
        tension_scores = [0.5, 0.5, 0.5, 0.5]
        issues = validator._check_tension_progression(tension_scores)
        plateau_issues = [
            i for i in issues
            if i.issue_type == EpisodeQualityIssueType.TENSION_PLATEAU
        ]
        assert len(plateau_issues) > 0

    def test_check_tension_drop(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test tension drop detection."""
        tension_scores = [0.3, 0.7, 0.3, 0.6]  # Significant drop at position 2
        issues = validator._check_tension_progression(tension_scores)
        drop_issues = [
            i for i in issues
            if i.issue_type == EpisodeQualityIssueType.TENSION_DROP
        ]
        assert len(drop_issues) > 0

    def test_track_foreshadowing_from_ledger(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test foreshadowing tracking from continuity ledger."""
        episodes = [{"episode_number": 1}, {"episode_number": 2}]
        ledger = {
            "open_threads": ["mysterious Ren Wu identity", "Yin Cang Bao Zang Wei Zhi"],
            "resolved_threads": ["Di Yi Ge Mi Tuan"],
        }
        items = validator._track_foreshadowing(episodes, ledger)
        assert len(items) >= 3
        unresolved = [i for i in items if not i.is_resolved]
        resolved = [i for i in items if i.is_resolved]
        assert len(unresolved) >= 2
        assert len(resolved) >= 1

    def test_track_foreshadowing_from_content(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test foreshadowing detection from episode content."""
        episodes = [
            {"episode_number": 1, "summary": "Mai Xia Fu Bi，An Shi mysterious Shi Jian"},
            {"episode_number": 3, "summary": "truth reveal，Yuan Lai is Zhe Yang"},
        ]
        items = validator._track_foreshadowing(episodes, None)
        assert len(items) > 0

    def test_check_foreshadowing_too_many_unresolved(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test detection of too many unresolved setups."""
        items = [
            ForeshadowingItem(
                setup_id=f"test_{i}",
                setup_description=f"Xuan Nian {i}",
                setup_episode=1,
                is_resolved=False,
            )
            for i in range(5)
        ]
        issues = validator._check_foreshadowing(items)
        chekhov_issues = [
            i for i in issues
            if i.issue_type == EpisodeQualityIssueType.UNFIRED_CHEKHOV
        ]
        assert len(chekhov_issues) > 0

    def test_check_foreshadowing_premature_payoff(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test detection of premature payoff."""
        items = [
            ForeshadowingItem(
                setup_id="test_1",
                setup_description="Fu Bi",
                setup_episode=2,
                payoff_episode=2,  # Same episode = premature
                is_resolved=True,
            )
        ]
        issues = validator._check_foreshadowing(items)
        premature_issues = [
            i for i in issues
            if i.issue_type == EpisodeQualityIssueType.PREMATURE_PAYOFF
        ]
        assert len(premature_issues) > 0

    def test_validate_full_episodes_good(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test full validation with good episodes."""
        episodes = [
            {
                "episode_number": 1,
                "summary": "protagonist discover crisis，tense Qi Fen start",
                "characters": [{"name": "Alice", "goal": "Diao Cha truth", "status": "curious"}],
            },
            {
                "episode_number": 2,
                "summary": "He Xin conflict escalate，protagonist Xian Ru Kun Jing",
                "characters": [{"name": "Alice", "goal": "Qiu Sheng", "status": "Kong Ju"}],
            },
            {
                "episode_number": 3,
                "summary": "key Dui Jue，climax Bao Fa，Zhen Xiang Da Bai",
                "characters": [{"name": "Alice", "goal": "Zhan Sheng Di Ren", "status": "Jue Xin"}],
            },
        ]
        story_characters = [{"name": "Alice"}]

        result = validator.validate(episodes, story_characters)

        assert result.passed is True
        assert "Alice" in result.character_arcs
        assert result.character_arcs["Alice"].has_progression()
        assert len(result.tension_scores) == 3

    def test_validate_full_episodes_with_issues(
        self, validator: EpisodeQualityValidator
    ) -> None:
        """Test full validation with problematic episodes."""
        episodes = [
            {
                "episode_number": 1,
                "summary": "calm Yi Tian",
                "characters": [{"name": "Bob", "goal": "Bang Zhu", "status": "loyal"}],
            },
            {
                "episode_number": 2,
                "summary": "You Yi Ge calm Yi Tian",
                "characters": [{"name": "Bob", "goal": "Bang Zhu", "status": "loyal"}],
            },
            {
                "episode_number": 3,
                "summary": "Yi Ran calm",
                "characters": [{"name": "Bob", "goal": "Bang Zhu", "status": "loyal"}],
            },
        ]
        story_characters = [{"name": "Bob"}]

        result = validator.validate(episodes, story_characters)

        # Should have issues for stagnant arc and/or tension
        assert len(result.issues) > 0
