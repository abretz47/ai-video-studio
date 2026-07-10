from __future__ import annotations

import pytest
from app.core.validators.character_registry import (
    build_alias_to_canonical_map,
    extract_name_aliases,
    normalize_generic_role,
    normalize_to_registered_or_generic,
    preferred_display_name,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("passerby", "passerby"),
        ("Passerby A", "passerby"),
        ("passerby1", "passerby"),
        ("clerk", "clerk"),
        ("clerkA", "clerk"),
        ("voiceover", "voiceover"),
        ("voiceover Jia", None),
        ("Chen Zhe", None),
        (None, None),
        ("", None),
    ],
)
def test_normalize_generic_role(raw: str | None, expected: str | None) -> None:
    assert normalize_generic_role(raw) == expected


@pytest.mark.unit
def test_extract_name_aliases_and_preferred_display_name() -> None:
    raw = "short dramaE2Eheroine-Lin Xue-2026-01-19T03-52-25-958Z"
    aliases = extract_name_aliases(raw)
    assert raw in aliases
    assert "short dramaE2Eheroine" in aliases
    assert "Lin Xue" in aliases
    assert preferred_display_name(raw) == "Lin Xue"


@pytest.mark.unit
def test_normalize_to_registered_or_generic_supports_nickname_suffix_match() -> None:
    alias_to_canonical = build_alias_to_canonical_map(canonical_names=["Lin Xue"])
    assert (
        normalize_to_registered_or_generic(
            "Xiao Xue", alias_to_canonical=alias_to_canonical
        )
        == "Lin Xue"
    )


@pytest.mark.unit
def test_normalize_to_registered_or_generic_avoids_ambiguous_nicknames() -> None:
    alias_to_canonical = build_alias_to_canonical_map(canonical_names=["Lin Xue", "Zhang Xue"])
    assert (
        normalize_to_registered_or_generic(
            "Xiao Xue", alias_to_canonical=alias_to_canonical
        )
        is None
    )
