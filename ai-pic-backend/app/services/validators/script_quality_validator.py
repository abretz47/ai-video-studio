"""Script quality validator for dialogue authenticity and narrative techniques.

This module provides validation for:
- Dialogue authenticity scoring (natural conversation detection)
- Show-don't-tell detection (excessive exposition warnings)
- Dialogue-action ratio check (avoid talking heads)
- Subtext analysis (what characters say vs what they mean)
- Scene emotional arc validation (entry emotion → exit emotion)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ScriptQualityIssueType(Enum):
    """Types of script quality issues."""

    UNNATURAL_DIALOGUE = "unnatural_dialogue"
    EXCESSIVE_EXPOSITION = "excessive_exposition"
    TALKING_HEADS = "talking_heads"
    MISSING_SUBTEXT = "missing_subtext"
    EMOTIONAL_ARC_FLAT = "emotional_arc_flat"
    EMOTIONAL_ARC_JUMP = "emotional_arc_jump"
    REPETITIVE_DIALOGUE = "repetitive_dialogue"


class ScriptQualitySeverity(Enum):
    """Severity levels for script quality issues."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ScriptQualityIssue:
    """Represents a single script quality issue."""

    issue_type: ScriptQualityIssueType
    severity: ScriptQualitySeverity
    message: str
    scene_number: Optional[int] = None
    dialogue_index: Optional[int] = None
    details: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "scene_number": self.scene_number,
            "dialogue_index": self.dialogue_index,
            "details": self.details,
            "suggestions": self.suggestions,
        }


@dataclass
class SceneEmotionalArc:
    """Tracks emotional progression within a scene."""

    scene_number: int
    entry_emotion: Optional[str] = None
    exit_emotion: Optional[str] = None
    emotion_sequence: List[str] = field(default_factory=list)
    has_progression: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_number": self.scene_number,
            "entry_emotion": self.entry_emotion,
            "exit_emotion": self.exit_emotion,
            "emotion_sequence": self.emotion_sequence,
            "has_progression": self.has_progression,
        }


@dataclass
class ScriptQualityResult:
    """Result of script quality validation."""

    passed: bool = True
    issues: List[ScriptQualityIssue] = field(default_factory=list)
    dialogue_authenticity_score: float = 0.0
    exposition_ratio: float = 0.0
    dialogue_action_ratio: float = 0.0
    scene_emotional_arcs: List[SceneEmotionalArc] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "issues": [issue.to_dict() for issue in self.issues],
            "dialogue_authenticity_score": self.dialogue_authenticity_score,
            "exposition_ratio": self.exposition_ratio,
            "dialogue_action_ratio": self.dialogue_action_ratio,
            "scene_emotional_arcs": [
                arc.to_dict() for arc in self.scene_emotional_arcs
            ],
        }


class ScriptQualityValidator:
    """Validates script quality across multiple dimensions."""

    # Keywords indicating unnatural/expository dialogue (Chinese)
    EXPOSITION_KEYWORDS = [
        "Zheng Ru you Suo Zhi",
        "you Zhi Dao",
        "Zhong Suo Zhou Zhi",
        "Wo Lai Gao Su you",
        "Rang I Jie Shi",
        "Shi Qing Shi Zhe Yang",
        "you Ke Neng not Zhi Dao",
        "I Bi Xu Gao Su you",
        "Qi Shi",
        "Yuan Lai",
        "Huan Ju Hua Shuo",
        "Ye Jiu Shi Shuo",
        "Jian Dan Lai Shuo",
        "Zong Er Yan Zhi",
        "Chang Hua Duan Shuo",
        "Shi Shi Shang",
        "Shi Ji Shang",
        "Shuo Shi Hua",
    ]

    # Keywords indicating natural dialogue patterns
    NATURAL_DIALOGUE_PATTERNS = [
        r"\.{3}",
        r"！",
        r"？",
        r"…",  # Hesitation, emotion, questions
        r"N",
        r"A",
        r"O",
        r"E",  # Interjections
        r"Bu Shi Ma",
        r"Dui Ba",
        r"Shi Ma",  # Tag questions
        r"you Shuo Ne",
        r"Zen Me Yang",  # Seeking opinion
    ]

    # Emotion categories for arc analysis (ordered: intense checked first for priority)
    EMOTION_CATEGORIES = {
        "intense": ["shocked", "angry", "Kuang Xi", "fear", "Jue Wang", "excited", "Beng Kui", "eruption"],
        "positive": ["happy", "happy", "excited", "pleasant", "Man Zu", "Gan Dong", "Wen Nuan", "Qi Dai"],
        "negative": ["sad", "anxious", "worried", "Tong Ku", "Shi Wang", "sad", "frustrated", "sad"],
        "neutral": ["calm", "calm", "thoughtful", "Chen Mo", "Yi Huo", "Hao Qi", "You Yu", "Jiu Jie"],
    }

    # Keywords for subtext detection (surface vs underlying)
    SUBTEXT_PATTERNS = {
        "surface_positive": ["Mei Shi", "Hen Hao", "Bu Yao Jin", "Mei Guan Xi", "Ting Hao"],
        "surface_negative": ["Ke Neng", "Ye Xu", "Huo Xu", "not Yi Ding", "Shuo Bu Zhun"],
        "underlying_tension": ["Dan Shi", "Bu Guo", "Ran Er", "Ke Xi", "Zhi Shi"],
    }

    def __init__(self) -> None:
        """Initialize the validator."""
        pass

    def validate(
        self,
        content: Dict[str, Any],
        characters: Optional[List[Dict[str, Any]]] = None,
    ) -> ScriptQualityResult:
        """
        Validate script quality across multiple dimensions.

        Args:
            content: Script content with scenes, dialogues, stage_directions
            characters: Optional list of character definitions

        Returns:
            ScriptQualityResult with validation results
        """
        result = ScriptQualityResult()

        dialogues = content.get("dialogues", [])
        scenes = content.get("scenes", [])
        stage_directions = content.get("stage_directions", [])

        if not dialogues:
            return result

        # Calculate dialogue authenticity score
        result.dialogue_authenticity_score = self._score_dialogue_authenticity(
            dialogues
        )
        if result.dialogue_authenticity_score < 0.5:
            result.issues.append(
                ScriptQualityIssue(
                    issue_type=ScriptQualityIssueType.UNNATURAL_DIALOGUE,
                    severity=ScriptQualitySeverity.WARNING,
                    message="dialogue Zheng Ti Zi Ran Du Pian Di, Ke Neng Guo Yu Shu Mian Hua",
                    details={"score": result.dialogue_authenticity_score},
                    suggestions=[
                        "increase Kou Yu Hua Biao Da",
                        "Tian Jia Ting Dun and Yu Qi Ci",
                        "Jian Shao Chang Ju, increase Dui Hua Gan",
                    ],
                )
            )

        # Check for excessive exposition
        result.exposition_ratio = self._calculate_exposition_ratio(dialogues)
        exposition_issues = self._check_exposition(dialogues)
        result.issues.extend(exposition_issues)

        # Check dialogue-action ratio
        result.dialogue_action_ratio = self._calculate_dialogue_action_ratio(
            dialogues, stage_directions
        )
        ratio_issues = self._check_dialogue_action_ratio(
            result.dialogue_action_ratio, scenes
        )
        result.issues.extend(ratio_issues)

        # Analyze scene emotional arcs
        result.scene_emotional_arcs = self._analyze_emotional_arcs(scenes, dialogues)
        arc_issues = self._check_emotional_arcs(result.scene_emotional_arcs)
        result.issues.extend(arc_issues)

        # Check for subtext presence
        subtext_issues = self._check_subtext(dialogues)
        result.issues.extend(subtext_issues)

        # Check for repetitive dialogue
        repetition_issues = self._check_repetitive_dialogue(dialogues)
        result.issues.extend(repetition_issues)

        # Determine overall pass/fail
        error_count = sum(
            1
            for issue in result.issues
            if issue.severity == ScriptQualitySeverity.ERROR
        )
        result.passed = error_count == 0

        return result

    def _score_dialogue_authenticity(self, dialogues: List[Dict[str, Any]]) -> float:
        """Score how natural/authentic the dialogues sound."""
        if not dialogues:
            return 0.5  # Neutral default

        total_score = 0.0
        scored_count = 0

        for dlg in dialogues:
            if not isinstance(dlg, dict):
                continue
            content = dlg.get("content", "")
            if not content:
                continue

            score = self._score_single_dialogue(content)
            total_score += score
            scored_count += 1

        return round(total_score / scored_count, 2) if scored_count > 0 else 0.5

    def _score_single_dialogue(self, content: str) -> float:
        """Score authenticity of a single dialogue line."""
        score = 0.5  # Base score

        # Check for natural patterns (bonus)
        for pattern in self.NATURAL_DIALOGUE_PATTERNS:
            if re.search(pattern, content):
                score += 0.05

        # Penalize very long sentences (unnatural in speech)
        avg_sentence_length = len(content) / (content.count("。") + 1)
        if avg_sentence_length > 50:
            score -= 0.1
        elif avg_sentence_length < 20:
            score += 0.1

        # Penalize exposition keywords
        for keyword in self.EXPOSITION_KEYWORDS:
            if keyword in content:
                score -= 0.05

        # Bonus for questions (interactive dialogue)
        question_count = content.count("？")
        if question_count > 0:
            score += min(0.1, question_count * 0.03)

        return max(0.0, min(1.0, score))

    def _calculate_exposition_ratio(self, dialogues: List[Dict[str, Any]]) -> float:
        """Calculate the ratio of expository dialogue."""
        if not dialogues:
            return 0.0

        expository_count = 0
        total_count = 0

        for dlg in dialogues:
            if not isinstance(dlg, dict):
                continue
            content = dlg.get("content", "")
            if not content:
                continue

            total_count += 1
            if self._is_expository(content):
                expository_count += 1

        return round(expository_count / total_count, 2) if total_count > 0 else 0.0

    def _is_expository(self, content: str) -> bool:
        """Check if a dialogue line is primarily expository."""
        # Count exposition keywords
        keyword_count = sum(1 for kw in self.EXPOSITION_KEYWORDS if kw in content)

        # Consider expository if multiple keywords or long explanation-style
        if keyword_count >= 2:
            return True

        # Check for explanation patterns
        if len(content) > 100 and "Shi" in content and "Yin Wei" in content:
            return True

        return False

    def _check_exposition(
        self, dialogues: List[Dict[str, Any]]
    ) -> List[ScriptQualityIssue]:
        """Check for excessive show-don't-tell violations."""
        issues = []

        # Group by scene
        scene_expositions: Dict[int, List[int]] = {}

        for idx, dlg in enumerate(dialogues):
            if not isinstance(dlg, dict):
                continue
            content = dlg.get("content", "")
            scene_num = dlg.get("scene_number", 0)

            if self._is_expository(content):
                if scene_num not in scene_expositions:
                    scene_expositions[scene_num] = []
                scene_expositions[scene_num].append(idx)

        # Report issues for scenes with too much exposition
        for scene_num, exp_indices in scene_expositions.items():
            if len(exp_indices) >= 3:
                issues.append(
                    ScriptQualityIssue(
                        issue_type=ScriptQualityIssueType.EXCESSIVE_EXPOSITION,
                        severity=ScriptQualitySeverity.WARNING,
                        message=f"场景 {scene_num} 存在过多解说性对白 ({len(exp_indices)} 处)",
                        scene_number=scene_num,
                        details={"exposition_indices": exp_indices},
                        suggestions=[
                            "through action and Biao Qing Zhan Shi, Er Fei directly Jiang Shu",
                            "Xin Xi Rong Ru Zi Ran Dui Hua in",
                            "Fen San Xin Xi to Duo Ge scene",
                        ],
                    )
                )

        return issues

    def _calculate_dialogue_action_ratio(
        self,
        dialogues: List[Dict[str, Any]],
        stage_directions: List[Dict[str, Any]],
    ) -> float:
        """Calculate ratio of dialogue to action/stage directions."""
        dialogue_count = len([d for d in dialogues if isinstance(d, dict)])
        action_count = len([s for s in stage_directions if isinstance(s, dict)])

        if action_count == 0:
            return float("inf") if dialogue_count > 0 else 1.0

        return round(dialogue_count / action_count, 2)

    def _check_dialogue_action_ratio(
        self,
        ratio: float,
        scenes: List[Dict[str, Any]],
    ) -> List[ScriptQualityIssue]:
        """Check if dialogue-action ratio is balanced."""
        issues = []

        if ratio > 5.0:
            issues.append(
                ScriptQualityIssue(
                    issue_type=ScriptQualityIssueType.TALKING_HEADS,
                    severity=ScriptQualitySeverity.WARNING,
                    message=f"对白与动作比例失衡 ({ratio:.1f}:1)，存在'说话头'风险",
                    details={"ratio": ratio},
                    suggestions=[
                        "increase character action Miao Xie",
                        "in Dui Hua Jian Chuan Cha Fan Ying shot",
                        "Tian Jia environment Jiao Hu",
                    ],
                )
            )
        elif ratio < 0.5:
            issues.append(
                ScriptQualityIssue(
                    issue_type=ScriptQualityIssueType.TALKING_HEADS,
                    severity=ScriptQualitySeverity.INFO,
                    message=f"动作描写较多，对白较少 ({ratio:.1f}:1)",
                    details={"ratio": ratio},
                    suggestions=["Que Bao key Qing Gan through dialogue Chuan Da"],
                )
            )

        return issues

    def _analyze_emotional_arcs(
        self,
        scenes: List[Dict[str, Any]],
        dialogues: List[Dict[str, Any]],
    ) -> List[SceneEmotionalArc]:
        """Analyze emotional progression within each scene."""
        arcs = []

        # Group dialogues by scene
        scene_dialogues: Dict[int, List[Dict[str, Any]]] = {}
        for dlg in dialogues:
            if not isinstance(dlg, dict):
                continue
            scene_num = dlg.get("scene_number", 0)
            if scene_num not in scene_dialogues:
                scene_dialogues[scene_num] = []
            scene_dialogues[scene_num].append(dlg)

        for scene in scenes:
            if not isinstance(scene, dict):
                continue
            scene_num = scene.get("scene_number", 0)
            scene_dlgs = scene_dialogues.get(scene_num, [])

            arc = SceneEmotionalArc(scene_number=scene_num)

            # Extract emotions from dialogues
            for dlg in scene_dlgs:
                emotion = dlg.get("emotion")
                if emotion:
                    arc.emotion_sequence.append(emotion)

            if arc.emotion_sequence:
                arc.entry_emotion = arc.emotion_sequence[0]
                arc.exit_emotion = arc.emotion_sequence[-1]
                # Check if there's meaningful progression
                unique_emotions = set(arc.emotion_sequence)
                arc.has_progression = len(unique_emotions) > 1

            arcs.append(arc)

        return arcs

    def _check_emotional_arcs(
        self, arcs: List[SceneEmotionalArc]
    ) -> List[ScriptQualityIssue]:
        """Check emotional arc validity."""
        issues = []

        for arc in arcs:
            # Check for flat emotion (same throughout)
            if arc.emotion_sequence and not arc.has_progression:
                issues.append(
                    ScriptQualityIssue(
                        issue_type=ScriptQualityIssueType.EMOTIONAL_ARC_FLAT,
                        severity=ScriptQualitySeverity.INFO,
                        message=f"场景 {arc.scene_number} 情绪变化单一",
                        scene_number=arc.scene_number,
                        details={
                            "emotion": arc.entry_emotion,
                            "count": len(arc.emotion_sequence),
                        },
                        suggestions=["consider in scene in She ZhiEmotionZhuan Zhe Dian"],
                    )
                )

            # Check for unreasonable jumps
            if arc.entry_emotion and arc.exit_emotion:
                entry_cat = self._categorize_emotion(arc.entry_emotion)
                exit_cat = self._categorize_emotion(arc.exit_emotion)

                # Jumping from positive to intense negative without transition
                if entry_cat == "positive" and exit_cat == "intense":
                    issues.append(
                        ScriptQualityIssue(
                            issue_type=ScriptQualityIssueType.EMOTIONAL_ARC_JUMP,
                            severity=ScriptQualitySeverity.WARNING,
                            message=f"场景 {arc.scene_number} 情绪跳跃过大: {arc.entry_emotion} → {arc.exit_emotion}",
                            scene_number=arc.scene_number,
                            details={
                                "entry": arc.entry_emotion,
                                "exit": arc.exit_emotion,
                            },
                            suggestions=["increase Guo DuEmotion", "ForeshadowingEmotionZhuan Bian Yuan Yin"],
                        )
                    )

        return issues

    def _categorize_emotion(self, emotion: str) -> str:
        """Categorize an emotion into broad categories."""
        emotion_lower = emotion.lower()
        for category, keywords in self.EMOTION_CATEGORIES.items():
            for kw in keywords:
                if kw in emotion_lower:
                    return category
        return "neutral"

    def _check_subtext(
        self, dialogues: List[Dict[str, Any]]
    ) -> List[ScriptQualityIssue]:
        """Check for subtext presence in dialogues."""
        issues = []

        # Count dialogues with potential subtext
        subtext_count = 0
        total_dialogues = 0

        for dlg in dialogues:
            if not isinstance(dlg, dict):
                continue
            content = dlg.get("content", "")
            if not content:
                continue

            total_dialogues += 1

            # Check for subtext indicators
            has_surface = any(
                p in content
                for p in self.SUBTEXT_PATTERNS["surface_positive"]
                + self.SUBTEXT_PATTERNS["surface_negative"]
            )
            has_tension = any(
                p in content for p in self.SUBTEXT_PATTERNS["underlying_tension"]
            )

            if has_surface and has_tension:
                subtext_count += 1
            elif has_tension:
                subtext_count += 0.5

        subtext_ratio = subtext_count / total_dialogues if total_dialogues > 0 else 0

        if total_dialogues > 10 and subtext_ratio < 0.1:
            issues.append(
                ScriptQualityIssue(
                    issue_type=ScriptQualityIssueType.MISSING_SUBTEXT,
                    severity=ScriptQualitySeverity.INFO,
                    message="dialogue Qian Tai Ci Jiao Shao, character Biao Da Guo Yu Zhi Bai",
                    details={"subtext_ratio": round(subtext_ratio, 2)},
                    suggestions=[
                        "Rang character Shuo and Xiang not Wan Quan Yi Zhi",
                        "through Xing Wei An Shi Zhen Shi Xiang Fa",
                        "Shi Yong Jian Jie Biao Da increase Ceng Ci",
                    ],
                )
            )

        return issues

    def _check_repetitive_dialogue(
        self, dialogues: List[Dict[str, Any]]
    ) -> List[ScriptQualityIssue]:
        """Check for repetitive dialogue patterns."""
        issues = []

        # Normalize and count dialogue patterns
        pattern_counts: Dict[str, List[int]] = {}

        for idx, dlg in enumerate(dialogues):
            if not isinstance(dlg, dict):
                continue
            content = dlg.get("content", "")
            if not content or len(content) < 5:
                continue

            # Create normalized pattern (first 10 chars or key phrases)
            normalized = content[:20].strip()

            if normalized not in pattern_counts:
                pattern_counts[normalized] = []
            pattern_counts[normalized].append(idx)

        # Report highly repeated patterns
        for pattern, indices in pattern_counts.items():
            if len(indices) >= 3:
                issues.append(
                    ScriptQualityIssue(
                        issue_type=ScriptQualityIssueType.REPETITIVE_DIALOGUE,
                        severity=ScriptQualitySeverity.WARNING,
                        message=f"对白模式重复 {len(indices)} 次: '{pattern[:15]}...'",
                        details={
                            "pattern": pattern,
                            "occurrences": len(indices),
                        },
                        suggestions=[
                            "Shi Yong Bu Tong Biao Da Fang Shi",
                            "Fu Yu character Du Te Yu Yan style",
                        ],
                    )
                )

        return issues
