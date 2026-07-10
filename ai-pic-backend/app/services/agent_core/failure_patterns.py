"""Failure Pattern Library.

Provides pattern matching for common generation failures to enable
intelligent error classification and targeted repair strategies.

This module helps agents learn from common error patterns and apply
appropriate fixes automatically.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Pattern


class PatternCategory(str, Enum):
    """Categories of failure patterns."""

    JSON_SYNTAX = "json_syntax"
    SCHEMA_VIOLATION = "schema_violation"
    CONTENT_LENGTH = "content_length"
    MISSING_FIELD = "missing_field"
    CHARACTER_INCONSISTENCY = "character_inconsistency"
    TIMELINE_ERROR = "timeline_error"
    LOGIC_ERROR = "logic_error"
    FORMAT_ERROR = "format_error"
    API_ERROR = "api_error"


@dataclass
class FailurePattern:
    """A known failure pattern with detection and repair hints."""

    name: str
    category: PatternCategory
    patterns: List[str]  # Regex patterns to match
    description: str
    repair_hints: List[str] = field(default_factory=list)
    example_errors: List[str] = field(default_factory=list)
    severity: str = "medium"  # low, medium, high

    _compiled: List[Pattern] = field(default_factory=list, repr=False)

    def __post_init__(self):
        """Compile regex patterns."""
        self._compiled = [re.compile(p, re.IGNORECASE) for p in self.patterns]

    def matches(self, error_text: str) -> bool:
        """Check if error text matches this pattern."""
        return any(p.search(error_text) for p in self._compiled)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "repair_hints": self.repair_hints,
            "severity": self.severity,
        }


# Common failure patterns library
COMMON_PATTERNS: List[FailurePattern] = [
    # JSON Syntax Errors
    FailurePattern(
        name="unclosed_json_brace",
        category=PatternCategory.JSON_SYNTAX,
        patterns=[r"expecting.*\}", r"unterminated.*object", r"unexpected end of json"],
        description="JSON object not properly closed",
        repair_hints=[
            "Qing Que Bao all { 都有对应的 }",
            "checkJSONstructure Wan Zheng Xing",
        ],
        example_errors=["Expecting '}' delimiter"],
    ),
    FailurePattern(
        name="unclosed_json_array",
        category=PatternCategory.JSON_SYNTAX,
        patterns=[r"expecting.*\]", r"unterminated.*array"],
        description="JSON array not properly closed",
        repair_hints=[
            "Qing Que Bao all [all has Dui Ying]",
            "check Shu Zu Shi Fou complete",
        ],
    ),
    FailurePattern(
        name="trailing_comma",
        category=PatternCategory.JSON_SYNTAX,
        patterns=[r"trailing comma", r"unexpected.*,.*\}", r",\s*[\}\]]"],
        description="Invalid trailing comma in JSON",
        repair_hints=[
            "delete Zui Hou a Yuan Su after Dou Hao",
            "JSONnot Yun Xu Wei Sui Dou Hao",
        ],
    ),
    FailurePattern(
        name="invalid_escape",
        category=PatternCategory.JSON_SYNTAX,
        patterns=[r"invalid.*escape", r"bad.*escape", r"\\[^\"\\\/bfnrtu]"],
        description="Invalid escape sequence in string",
        repair_hints=[
            "Shi Yong You Xiao Zhuan Yi Xu Lie",
            "Dui Te Shu Zi Fu Shi Yong \\\\ Shuang Fan Xie Gang",
        ],
    ),
    # Schema Violations
    FailurePattern(
        name="missing_required_field",
        category=PatternCategory.MISSING_FIELD,
        patterns=[r"required.*field", r"missing.*required", r"field.*required"],
        description="Required field missing from output",
        repair_hints=[
            "Que Bao output Bao Han all Bi Xu character Duan",
            "referenceschemaDing Yi Bi Xu character Duan",
        ],
    ),
    FailurePattern(
        name="wrong_field_type",
        category=PatternCategory.SCHEMA_VIOLATION,
        patterns=[r"expected.*type", r"invalid.*type", r"type.*mismatch"],
        description="Field has wrong data type",
        repair_hints=[
            "check Zi Duan Shu Ju Lei Xing",
            "Shu Zu character Duan need Yong[]Bao Wei",
        ],
    ),
    # Content Length Issues
    FailurePattern(
        name="dialogue_too_long",
        category=PatternCategory.CONTENT_LENGTH,
        patterns=[r"dialogue.*too.*long", r"line.*Chao Guo", r"dialogue.*Guo Chang"],
        description="Dialogue line exceeds maximum length",
        repair_hints=[
            "Jiang Zhang line Chai Fen Wei multiple Ju",
            "Mei Ju dialogue Kong Zhi in15character Yi Nei",
        ],
    ),
    FailurePattern(
        name="output_truncated",
        category=PatternCategory.CONTENT_LENGTH,
        patterns=[r"output.*truncated", r"max.*tokens", r"token.*limit"],
        description="Output was truncated due to length",
        repair_hints=[
            "Jian Shao output content Liang",
            "Fen Pi Sheng Cheng Jiao Zhang content",
        ],
    ),
    # Character Consistency
    FailurePattern(
        name="unknown_character",
        category=PatternCategory.CHARACTER_INCONSISTENCY,
        patterns=[r"unknown.*character", r"unknown.*character", r"character.*not Cun Zai"],
        description="Referenced character not in character list",
        repair_hints=[
            "only Shi Yong Yu Ding Yi character",
            "check character name Pin Xie",
        ],
    ),
    FailurePattern(
        name="character_attribute_conflict",
        category=PatternCategory.CHARACTER_INCONSISTENCY,
        patterns=[r"attribute.*conflict", r"Shu Xing.*Conflict", r"Xing Ge.*not Yi Zhi"],
        description="Character attributes contradict profile",
        repair_hints=[
            "Que Bao Jue Se Xing Wei Fu He setting",
            "check character Xing Ge description",
        ],
    ),
    # Timeline Errors
    FailurePattern(
        name="timeline_inconsistency",
        category=PatternCategory.TIMELINE_ERROR,
        patterns=[r"timeline.*inconsist", r"time Xian.*error", r"Shi Xu.*Conflict"],
        description="Events out of chronological order",
        repair_hints=[
            "check Shi Jian time Shun Xu",
            "Que Bao Yin Guo Guan Xi Zheng Que",
        ],
    ),
    # Format Errors
    FailurePattern(
        name="wrong_format",
        category=PatternCategory.FORMAT_ERROR,
        patterns=[r"format.*incorrect", r"format.*error", r"output.*format"],
        description="Output doesn't match expected format",
        repair_hints=[
            "strict An Zhao Shi Li format output",
            "checkJSONstructure Shi Fou Zheng Que",
        ],
    ),
    # API Errors
    FailurePattern(
        name="rate_limit",
        category=PatternCategory.API_ERROR,
        patterns=[r"rate.*limit", r"too.*many.*requests", r"quota.*exceeded"],
        description="API rate limit exceeded",
        repair_hints=[
            "waiting after retry",
            "Jian Shao request Pin Lv",
        ],
    ),
    FailurePattern(
        name="context_length_exceeded",
        category=PatternCategory.API_ERROR,
        patterns=[r"context.*length", r"max.*context", r"input.*too.*long"],
        description="Input context too long for model",
        repair_hints=[
            "Ya Suo input content",
            "Yi Chu Fei Bi Yao context",
        ],
    ),
]


class FailurePatternMatcher:
    """Matches error text against known failure patterns.

    Usage:
        matcher = FailurePatternMatcher()
        patterns = matcher.match("JSON parse error: expecting '}'")
        for pattern in patterns:
            print(pattern.repair_hints)
    """

    def __init__(self, patterns: Optional[List[FailurePattern]] = None):
        """Initialize with pattern library.

        Args:
            patterns: Custom patterns. Uses COMMON_PATTERNS if not provided.
        """
        self.patterns = patterns or COMMON_PATTERNS

    def match(self, error_text: str) -> List[FailurePattern]:
        """Find all patterns that match the error text.

        Args:
            error_text: Error message or description

        Returns:
            List of matching FailurePattern objects
        """
        return [p for p in self.patterns if p.matches(error_text)]

    def match_first(self, error_text: str) -> Optional[FailurePattern]:
        """Find the first matching pattern.

        Args:
            error_text: Error message or description

        Returns:
            First matching pattern or None
        """
        for p in self.patterns:
            if p.matches(error_text):
                return p
        return None

    def get_repair_hints(self, error_text: str) -> List[str]:
        """Get repair hints for an error.

        Args:
            error_text: Error message or description

        Returns:
            Combined list of repair hints from all matching patterns
        """
        hints = []
        for pattern in self.match(error_text):
            hints.extend(pattern.repair_hints)
        return hints

    def classify_category(self, error_text: str) -> Optional[PatternCategory]:
        """Classify error into a category.

        Args:
            error_text: Error message or description

        Returns:
            PatternCategory or None if no match
        """
        pattern = self.match_first(error_text)
        return pattern.category if pattern else None

    def add_pattern(self, pattern: FailurePattern) -> None:
        """Add a custom pattern to the matcher.

        Args:
            pattern: Pattern to add
        """
        self.patterns.append(pattern)

    def get_patterns_by_category(
        self, category: PatternCategory
    ) -> List[FailurePattern]:
        """Get all patterns in a category.

        Args:
            category: The category to filter by

        Returns:
            List of patterns in that category
        """
        return [p for p in self.patterns if p.category == category]
