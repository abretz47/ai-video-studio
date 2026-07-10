"""Episode quality validator for cross-episode consistency and dramatic structure.

This module provides validation for:
- Character arc tracking (goal/relationship/status evolution across episodes)
- Subplot balance (main plot vs subplots screen time ratio)
- Dramatic tension progression (stakes escalation across episodes)
- Foreshadowing/payoff tracking (setup in Ep N, payoff in Ep N+M)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EpisodeQualityIssueType(Enum):
    """Types of episode quality issues."""

    CHARACTER_ARC_STAGNANT = "character_arc_stagnant"
    CHARACTER_ARC_INCONSISTENT = "character_arc_inconsistent"
    SUBPLOT_IMBALANCE = "subplot_imbalance"
    TENSION_PLATEAU = "tension_plateau"
    TENSION_DROP = "tension_drop"
    UNFIRED_CHEKHOV = "unfired_chekhov"
    PREMATURE_PAYOFF = "premature_payoff"
    MISSING_SETUP = "missing_setup"


class EpisodeQualitySeverity(Enum):
    """Severity levels for episode quality issues."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class EpisodeQualityIssue:
    """Represents a single episode quality issue."""

    issue_type: EpisodeQualityIssueType
    severity: EpisodeQualitySeverity
    message: str
    episode_number: Optional[int] = None
    character_name: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "episode_number": self.episode_number,
            "character_name": self.character_name,
            "details": self.details,
            "suggestions": self.suggestions,
        }


@dataclass
class CharacterArc:
    """Tracks a character's evolution across episodes."""

    character_name: str
    episode_goals: Dict[int, str] = field(default_factory=dict)
    episode_states: Dict[int, str] = field(default_factory=dict)
    relationship_changes: List[Dict[str, Any]] = field(default_factory=list)
    growth_events: List[Dict[str, Any]] = field(default_factory=list)

    def has_progression(self) -> bool:
        """Check if character shows meaningful progression."""
        if len(self.episode_goals) < 2 and len(self.episode_states) < 2:
            return True  # Not enough data to judge
        goals = list(self.episode_goals.values())
        states = list(self.episode_states.values())
        # Check if all goals/states are identical (stagnant)
        if goals and len(set(goals)) == 1:
            return False
        if states and len(set(states)) == 1:
            return False
        return True


@dataclass
class ForeshadowingItem:
    """Tracks a setup/payoff pair."""

    setup_id: str
    setup_description: str
    setup_episode: int
    payoff_episode: Optional[int] = None
    payoff_description: Optional[str] = None
    is_resolved: bool = False


@dataclass
class EpisodeQualityResult:
    """Result of episode quality validation."""

    passed: bool = True
    issues: List[EpisodeQualityIssue] = field(default_factory=list)
    character_arcs: Dict[str, CharacterArc] = field(default_factory=dict)
    foreshadowing_items: List[ForeshadowingItem] = field(default_factory=list)
    tension_scores: List[float] = field(default_factory=list)
    subplot_ratios: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "issues": [issue.to_dict() for issue in self.issues],
            "character_arcs": {
                name: {
                    "episode_goals": arc.episode_goals,
                    "episode_states": arc.episode_states,
                    "has_progression": arc.has_progression(),
                }
                for name, arc in self.character_arcs.items()
            },
            "foreshadowing_items": [
                {
                    "setup_id": item.setup_id,
                    "setup_episode": item.setup_episode,
                    "is_resolved": item.is_resolved,
                    "payoff_episode": item.payoff_episode,
                }
                for item in self.foreshadowing_items
            ],
            "tension_scores": self.tension_scores,
            "subplot_ratios": self.subplot_ratios,
        }


class EpisodeQualityValidator:
    """Validates episode quality across multiple dimensions."""

    # Keywords indicating high tension/stakes (Chinese)
    TENSION_KEYWORDS = [
        "crisis", "Wei Xian", "Sheng Si", "Jin Ji", "key", "Jue Zhan", "Dui Jue", "climax",
        "eruption", "conflict", "Dui Kang", "threat", "Jue Wang", "Zheng Zha", "Bi Po", "Xian Jing",
        "Bei Pan", "truth", "expose", "secret", "shocked", "Zhuan Zhe", "Tu Bian", "escalate",
    ]

    # Keywords indicating setup/foreshadowing
    SETUP_KEYWORDS = [
        "An Shi", "Fu Bi", "Yu Shi", "Foreshadowing", "Mai below", "Yin Cang", "An Cang",
        "Ti Ji", "clue", "Zheng Zhao", "Yu Zhao", "An Xian", "suspense", "Mi Tuan",
    ]

    # Keywords indicating payoff/resolution
    PAYOFF_KEYWORDS = [
        "reveal", "expose", "Zhen Xiang Da Bai", "Shui Luo Shi Chu", "Hui Shou", "Hu Ying",
        "Yuan Lai", "Jing Ran", "Huang Ran", "Jie Kai", "Po Jie", "Zhong Yu", "Da An",
    ]

    # Subplot indicators
    SUBPLOT_KEYWORDS = {
        "main": ["Zhu Xian", "Zhu Jue", "core", "Zhong Xin", "key"],
        "romance": ["Ai Qing", "Gan Qing", "Lian Ai", "Ai Mei", "Biao Bai", "Yue Hui"],
        "conflict": ["Conflict", "Dui Li", "Di Dui", "Zheng Zhi", "conflict"],
        "mystery": ["Mi Tuan", "Xuan Yi", "Diao Cha", "truth", "secret"],
        "growth": ["Cheng Zhang", "Tui Bian", "Ling Wu", "Xue Xi", "Jin Bu"],
    }

    def __init__(self) -> None:
        """Initialize the validator."""
        pass

    def validate(
        self,
        episodes: List[Dict[str, Any]],
        story_characters: Optional[List[Dict[str, Any]]] = None,
        continuity_ledger: Optional[Dict[str, Any]] = None,
    ) -> EpisodeQualityResult:
        """
        Validate episode quality across multiple dimensions.

        Args:
            episodes: List of episode dictionaries
            story_characters: Optional list of character definitions
            continuity_ledger: Optional continuity ledger for context

        Returns:
            EpisodeQualityResult with validation results
        """
        result = EpisodeQualityResult()

        if not episodes:
            return result

        # Track character arcs
        result.character_arcs = self._track_character_arcs(
            episodes, story_characters or []
        )

        # Check arc progression
        arc_issues = self._check_arc_progression(result.character_arcs)
        result.issues.extend(arc_issues)

        # Analyze subplot balance
        result.subplot_ratios = self._analyze_subplot_balance(episodes)
        subplot_issues = self._check_subplot_balance(result.subplot_ratios)
        result.issues.extend(subplot_issues)

        # Analyze tension progression
        result.tension_scores = self._analyze_tension_progression(episodes)
        tension_issues = self._check_tension_progression(result.tension_scores)
        result.issues.extend(tension_issues)

        # Track foreshadowing and payoffs
        result.foreshadowing_items = self._track_foreshadowing(
            episodes, continuity_ledger
        )
        foreshadow_issues = self._check_foreshadowing(result.foreshadowing_items)
        result.issues.extend(foreshadow_issues)

        # Determine overall pass/fail
        error_count = sum(
            1 for issue in result.issues
            if issue.severity == EpisodeQualitySeverity.ERROR
        )
        result.passed = error_count == 0

        return result

    def _track_character_arcs(
        self,
        episodes: List[Dict[str, Any]],
        story_characters: List[Dict[str, Any]],
    ) -> Dict[str, CharacterArc]:
        """Track character evolution across episodes."""
        arcs: Dict[str, CharacterArc] = {}

        # Initialize arcs from story characters
        for char in story_characters:
            name = char.get("name")
            if name:
                arcs[name] = CharacterArc(character_name=name)

        # Process each episode
        for episode in episodes:
            ep_num = episode.get("episode_number", 0)

            # Extract character states from episode
            ep_chars = episode.get("characters", [])
            if isinstance(ep_chars, list):
                for char in ep_chars:
                    if isinstance(char, dict):
                        name = char.get("name") or char.get("character_name")
                        if not name:
                            continue

                        if name not in arcs:
                            arcs[name] = CharacterArc(character_name=name)

                        arc = arcs[name]

                        # Track goals
                        goal = char.get("goal") or char.get("objective")
                        if goal:
                            arc.episode_goals[ep_num] = goal

                        # Track states
                        state = char.get("status") or char.get("state")
                        if state:
                            arc.episode_states[ep_num] = state

                        # Track relationship changes
                        relationships = char.get("relationships", {})
                        if relationships:
                            arc.relationship_changes.append({
                                "episode": ep_num,
                                "relationships": relationships,
                            })

            # Also extract from continuity data if present
            continuity = episode.get("continuity", {})
            if isinstance(continuity, dict):
                char_states = continuity.get("characters", {})
                for name, state_data in char_states.items():
                    if name not in arcs:
                        arcs[name] = CharacterArc(character_name=name)
                    arc = arcs[name]

                    if isinstance(state_data, dict):
                        if state_data.get("goal"):
                            arc.episode_goals[ep_num] = state_data["goal"]
                        if state_data.get("status"):
                            arc.episode_states[ep_num] = state_data["status"]

        return arcs

    def _check_arc_progression(
        self, arcs: Dict[str, CharacterArc]
    ) -> List[EpisodeQualityIssue]:
        """Check if character arcs show meaningful progression."""
        issues = []

        for name, arc in arcs.items():
            if not arc.has_progression():
                issues.append(
                    EpisodeQualityIssue(
                        issue_type=EpisodeQualityIssueType.CHARACTER_ARC_STAGNANT,
                        severity=EpisodeQualitySeverity.WARNING,
                        message=f"character '{name}' Zai Duo Ji Zhong status/Mu Biao Wu Ming Xian Bian Hua",
                        character_name=name,
                        suggestions=[
                            f"Wei '{name}' She Ji Ming Que De Cheng Zhang Hu Xian",
                            "in key plot Dian She Zhi target or status change",
                        ],
                    )
                )

        return issues

    def _analyze_subplot_balance(
        self, episodes: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Analyze the balance between main plot and subplots."""
        subplot_counts: Dict[str, int] = {key: 0 for key in self.SUBPLOT_KEYWORDS}
        total_content_length = 0

        for episode in episodes:
            # Gather all text content
            content_parts = []
            if episode.get("summary"):
                content_parts.append(episode["summary"])
            if episode.get("description"):
                content_parts.append(episode["description"])
            if episode.get("plot_points"):
                content_parts.extend(str(p) for p in episode["plot_points"] if p)

            content = "\n".join(content_parts)
            total_content_length += len(content)

            # Count subplot keywords
            for subplot_type, keywords in self.SUBPLOT_KEYWORDS.items():
                for keyword in keywords:
                    subplot_counts[subplot_type] += content.count(keyword)

        # Calculate ratios
        total_keywords = sum(subplot_counts.values()) or 1
        ratios = {
            subplot_type: count / total_keywords
            for subplot_type, count in subplot_counts.items()
        }

        return ratios

    def _check_subplot_balance(
        self, ratios: Dict[str, float]
    ) -> List[EpisodeQualityIssue]:
        """Check if subplot distribution is balanced."""
        issues = []

        main_ratio = ratios.get("main", 0)

        # Main plot should dominate but not overwhelm
        if main_ratio < 0.3:
            issues.append(
                EpisodeQualityIssue(
                    issue_type=EpisodeQualityIssueType.SUBPLOT_IMBALANCE,
                    severity=EpisodeQualitySeverity.WARNING,
                    message="Zhu Xian plot Bi Zhong Guo Di, Zhi Xian Ke Neng Xuan Bin Duo Zhu",
                    details={"main_ratio": main_ratio},
                    suggestions=[
                        "increase Zhu Xian related Qing Jie",
                        "Que Bao Mei Ji all advance Zhu Xian plot",
                    ],
                )
            )
        elif main_ratio > 0.8:
            issues.append(
                EpisodeQualityIssue(
                    issue_type=EpisodeQualityIssueType.SUBPLOT_IMBALANCE,
                    severity=EpisodeQualitySeverity.INFO,
                    message="Ji Hu missing Zhi Xian plot, story Ke Neng Xian De Dan Diao",
                    details={"main_ratio": main_ratio},
                    suggestions=[
                        "consider Tian Jia character relationship Zhi Xian",
                        "increase Fu Zhu character Ge Ren story Xian",
                    ],
                )
            )

        return issues

    def _analyze_tension_progression(
        self, episodes: List[Dict[str, Any]]
    ) -> List[float]:
        """Analyze dramatic tension progression across episodes."""
        tension_scores = []

        for episode in episodes:
            score = self._calculate_episode_tension(episode)
            tension_scores.append(score)

        return tension_scores

    def _calculate_episode_tension(self, episode: Dict[str, Any]) -> float:
        """Calculate tension score for a single episode."""
        content_parts = []
        if episode.get("summary"):
            content_parts.append(episode["summary"])
        if episode.get("description"):
            content_parts.append(episode["description"])
        if episode.get("climax"):
            content_parts.append(episode["climax"])
        if episode.get("plot_points"):
            content_parts.extend(str(p) for p in episode["plot_points"] if p)

        content = "\n".join(content_parts)
        if not content:
            return 0.5  # Default neutral score

        # Count tension keywords
        keyword_count = 0
        for keyword in self.TENSION_KEYWORDS:
            keyword_count += content.count(keyword)

        # Normalize to 0-1 range
        content_length = len(content)
        if content_length == 0:
            return 0.5

        # Density-based score with diminishing returns
        density = keyword_count / (content_length / 100)
        score = min(1.0, density / 5.0)  # Cap at 1.0

        return round(score, 2)

    def _check_tension_progression(
        self, tension_scores: List[float]
    ) -> List[EpisodeQualityIssue]:
        """Check if tension progression follows good dramatic structure."""
        issues = []

        if len(tension_scores) < 3:
            return issues  # Not enough data

        # Check for plateau (3+ consecutive similar scores)
        for i in range(len(tension_scores) - 2):
            window = tension_scores[i:i + 3]
            if max(window) - min(window) < 0.1:
                issues.append(
                    EpisodeQualityIssue(
                        issue_type=EpisodeQualityIssueType.TENSION_PLATEAU,
                        severity=EpisodeQualitySeverity.WARNING,
                        message=f"Di {i + 1}-{i + 3} Ji Zhang Li Ping Wen，Que Fa Qi Fu",
                        episode_number=i + 1,
                        details={"scores": window},
                        suggestions=[
                            "in Zhong Jian Ji She Zhi unexpected Zhuan Zhe",
                            "Zhu Bu escalate Dui Kang Qiang Du",
                        ],
                    )
                )
                break  # Only report once

        # Check for premature tension drop (excluding final resolution)
        for i in range(1, len(tension_scores) - 1):
            if tension_scores[i] < tension_scores[i - 1] - 0.2:
                # Significant drop in middle of series
                issues.append(
                    EpisodeQualityIssue(
                        issue_type=EpisodeQualityIssueType.TENSION_DROP,
                        severity=EpisodeQualitySeverity.INFO,
                        message=f"Di {i + 1} Ji Zhang Li Zhou Jiang，Jie Zou Ke Neng Duan Lie",
                        episode_number=i + 1,
                        details={
                            "previous_score": tension_scores[i - 1],
                            "current_score": tension_scores[i],
                        },
                        suggestions=[
                            "Que Bao Zhuan Zhe Dian has Zu GouForeshadowing",
                            "in Di Chao Qi Mai She Xin suspense",
                        ],
                    )
                )

        # Overall trend should be upward (with allowed dips)
        if len(tension_scores) >= 4:
            first_half_avg = sum(tension_scores[: len(tension_scores) // 2]) / (
                len(tension_scores) // 2
            )
            second_half_avg = sum(tension_scores[len(tension_scores) // 2:]) / (
                len(tension_scores) - len(tension_scores) // 2
            )
            if second_half_avg < first_half_avg - 0.1:
                issues.append(
                    EpisodeQualityIssue(
                        issue_type=EpisodeQualityIssueType.TENSION_DROP,
                        severity=EpisodeQualitySeverity.WARNING,
                        message="Zheng Ti Zhang Li Cheng Xia Jiang Qu Shi, Hou Ban Duan Que Fa climax",
                        details={
                            "first_half_avg": round(first_half_avg, 2),
                            "second_half_avg": round(second_half_avg, 2),
                        },
                        suggestions=[
                            "in Hou Ban Duan She Zhi Geng Qiang Dui Kang",
                            "Yu Liu maximum crisis to Dao Shu Ji Ji",
                        ],
                    )
                )

        return issues

    def _track_foreshadowing(
        self,
        episodes: List[Dict[str, Any]],
        continuity_ledger: Optional[Dict[str, Any]],
    ) -> List[ForeshadowingItem]:
        """Track setup and payoff pairs across episodes."""
        items: List[ForeshadowingItem] = []

        # Extract from continuity ledger if available
        if continuity_ledger:
            open_threads = continuity_ledger.get("open_threads", [])
            resolved_threads = continuity_ledger.get("resolved_threads", [])

            for i, thread in enumerate(open_threads):
                items.append(
                    ForeshadowingItem(
                        setup_id=f"thread_{i}",
                        setup_description=thread,
                        setup_episode=1,  # Assume setup in early episodes
                        is_resolved=False,
                    )
                )

            for i, thread in enumerate(resolved_threads):
                items.append(
                    ForeshadowingItem(
                        setup_id=f"resolved_{i}",
                        setup_description=thread,
                        setup_episode=1,
                        payoff_episode=len(episodes),
                        is_resolved=True,
                    )
                )

        # Scan episodes for setup/payoff patterns
        setups: Dict[str, ForeshadowingItem] = {}

        for episode in episodes:
            ep_num = episode.get("episode_number", 0)
            content_parts = []
            if episode.get("summary"):
                content_parts.append(episode["summary"])
            if episode.get("description"):
                content_parts.append(episode["description"])

            content = "\n".join(content_parts)

            # Detect setups
            for keyword in self.SETUP_KEYWORDS:
                if keyword in content:
                    # Extract surrounding context as description
                    match = re.search(rf".{{0,20}}{keyword}.{{0,30}}", content)
                    if match:
                        desc = match.group(0)
                        setup_id = f"ep{ep_num}_{keyword}"
                        if setup_id not in setups:
                            setups[setup_id] = ForeshadowingItem(
                                setup_id=setup_id,
                                setup_description=desc,
                                setup_episode=ep_num,
                            )

            # Detect payoffs and try to match with setups
            for keyword in self.PAYOFF_KEYWORDS:
                if keyword in content:
                    # Try to resolve earlier setups
                    for setup_id, item in setups.items():
                        if not item.is_resolved and item.setup_episode < ep_num:
                            item.is_resolved = True
                            item.payoff_episode = ep_num
                            break

        items.extend(setups.values())
        return items

    def _check_foreshadowing(
        self, items: List[ForeshadowingItem]
    ) -> List[EpisodeQualityIssue]:
        """Check foreshadowing/payoff balance."""
        issues = []

        unresolved = [item for item in items if not item.is_resolved]
        if len(unresolved) > 3:
            issues.append(
                EpisodeQualityIssue(
                    issue_type=EpisodeQualityIssueType.UNFIRED_CHEKHOV,
                    severity=EpisodeQualitySeverity.WARNING,
                    message=f"You {len(unresolved)} Tiao Fu Bi Wei Hui Shou，Guan Zhong Ke Neng Gan Dao Kun Huo",
                    details={
                        "unresolved": [item.setup_description for item in unresolved[:5]]
                    },
                    suggestions=[
                        "in subsequent Ji Zhong An Pai Hui Shou",
                        "delete Bu Bi Yao suspenseForeshadowing",
                    ],
                )
            )

        # Check for premature payoffs (payoff too close to setup)
        for item in items:
            if item.is_resolved and item.payoff_episode:
                gap = item.payoff_episode - item.setup_episode
                if gap <= 0:
                    issues.append(
                        EpisodeQualityIssue(
                            issue_type=EpisodeQualityIssueType.PREMATURE_PAYOFF,
                            severity=EpisodeQualitySeverity.INFO,
                            message=f"Fu Bi '{item.setup_description[:20]}...' Hui Shou Guo Kuai",
                            episode_number=item.setup_episode,
                            details={"gap": gap},
                            suggestions=["consider Yan Chi reveal Yi increase suspense"],
                        )
                    )

        return issues
