"""Temporary Character Extractor.

Extracts information about temporary characters from script content,
including names, dialogues, stage directions, and scene appearances.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from app.core.validators.character_registry import normalize_character_name_token


@dataclass
class TemporaryCharacterInfo:
    """Information about a temporary character extracted from script."""

    character_name: str
    """Normalized character name."""

    dialogues: List[str]
    """All dialogue lines spoken by this character."""

    stage_directions: List[str]
    """Stage directions mentioning this character."""

    scene_appearances: List[int]
    """Scene numbers where this character appears."""

    first_appearance_scene: int
    """First scene number where character appears."""

    last_appearance_scene: int
    """Last scene number where character appears."""

    dialogue_count: int
    """Total number of dialogue lines."""

    appearance_hints: List[str]
    """Appearance descriptions extracted from stage directions."""


def extract_temporary_characters(
    script_content: Dict[str, Any],
    unknown_names: Optional[List[str]] = None,
) -> List[TemporaryCharacterInfo]:
    """Extract temporary character information from script content.

    Args:
        script_content: Script content dictionary with scenes, dialogues, stage_directions
        unknown_names: Optional list of unknown character names to focus on

    Returns:
        List of TemporaryCharacterInfo objects for each temporary character
    """
    if not isinstance(script_content, dict):
        return []

    dialogues = script_content.get("dialogues", [])
    stage_directions = script_content.get("stage_directions", [])

    if unknown_names is None:
        unknown_names = []

    # Normalize unknown names
    unknown_set: Set[str] = {
        normalize_character_name_token(name) or name for name in unknown_names
    }

    # Extract character data from dialogues
    character_data: Dict[str, Dict[str, Any]] = {}

    for dlg in dialogues:
        if not isinstance(dlg, dict):
            continue

        char_name = dlg.get("character") or dlg.get("speaker") or dlg.get("name")
        if not char_name:
            continue

        normalized = normalize_character_name_token(str(char_name))
        if not normalized:
            continue

        # Skip if not in unknown_names (when unknown_names is provided)
        if unknown_set and normalized not in unknown_set:
            continue

        if normalized not in character_data:
            character_data[normalized] = {
                "dialogues": [],
                "scene_appearances": set(),
                "stage_directions": [],
                "appearance_hints": [],
            }

        # Add dialogue
        content = dlg.get("content") or dlg.get("text") or ""
        if content:
            character_data[normalized]["dialogues"].append(str(content))

        # Add scene number
        scene_number = dlg.get("scene_number")
        if scene_number is not None:
            character_data[normalized]["scene_appearances"].add(int(scene_number))

    # Extract character mentions from stage directions
    for sd in stage_directions:
        if not isinstance(sd, dict):
            continue

        content = sd.get("content") or sd.get("text") or ""
        scene_number = sd.get("scene_number")

        if not content:
            continue

        # Check each character for mentions in stage directions
        for char_name in character_data.keys():
            if char_name in content or _fuzzy_match(char_name, content):
                character_data[char_name]["stage_directions"].append(str(content))

                # Extract appearance hints
                appearance_hints = _extract_appearance_hints(content, char_name)
                character_data[char_name]["appearance_hints"].extend(appearance_hints)

                # Add scene appearance
                if scene_number is not None:
                    character_data[char_name]["scene_appearances"].add(
                        int(scene_number)
                    )

    # Build TemporaryCharacterInfo objects
    results: List[TemporaryCharacterInfo] = []

    for char_name, data in character_data.items():
        scene_list = sorted(list(data["scene_appearances"]))

        if not scene_list:
            continue

        results.append(
            TemporaryCharacterInfo(
                character_name=char_name,
                dialogues=data["dialogues"],
                stage_directions=data["stage_directions"],
                scene_appearances=scene_list,
                first_appearance_scene=scene_list[0],
                last_appearance_scene=scene_list[-1],
                dialogue_count=len(data["dialogues"]),
                appearance_hints=data["appearance_hints"],
            )
        )

    # Sort by first appearance scene
    results.sort(key=lambda x: x.first_appearance_scene)

    return results


def _fuzzy_match(char_name: str, text: str) -> bool:
    """Check if character name appears in text with fuzzy matching.

    Handles cases like:
 - "Kuai Di Yuan" in "a Kuai Di Yuan Zou Jin Lai"
 - "Yi Sheng" in "Li Yi Sheng check Bing Ren"
    """
    # Direct substring match
    if char_name in text:
        return True

    # Try with common prefixes/suffixes
    patterns = [
        char_name + "Zou",
        char_name + "Shuo",
        char_name + "Kan",
        char_name + "Zhan",
        "a" + char_name,
        "Yi Wei" + char_name,
        char_name + "Lai",
    ]

    for pattern in patterns:
        if pattern in text:
            return True

    return False


def _extract_appearance_hints(stage_direction: str, char_name: str) -> List[str]:
    """Extract appearance descriptions from stage direction for a character.

    Args:
        stage_direction: Stage direction text
        char_name: Character name to look for

    Returns:
        List of appearance hint strings
    """
    hints: List[str] = []

    # Common appearance patterns
    patterns = [
        r"Chuan Zhe([\u4e00-\u9fa5]+)",  # Chuan Zhe...
        r"Dai Zhe([\u4e00-\u9fa5]+)",  # Dai Zhe...
        r"Bei Zhe([\u4e00-\u9fa5]+)",  # Bei Zhe...
        r"Na Zhe([\u4e00-\u9fa5]+)",  # Na Zhe...
        r"([\u4e00-\u9fa5]{2,6})Zhi Fu",  # ...Zhi Fu
        r"([\u4e00-\u9fa5]{2,6})Zhuang Ban",  # ...Zhuang Ban
        r"(Nian Qing|Nian Zhang|Zhong Nian|Nian Mai)()?([\u4e00-\u9fa5]+)",  # Nian Ling description
    ]

    for pattern in patterns:
        matches = re.findall(pattern, stage_direction)
        for match in matches:
            if isinstance(match, tuple):
                hint = "".join(match).strip()
            else:
                hint = match.strip()

            if hint and hint not in hints:
                hints.append(hint)

    return hints
