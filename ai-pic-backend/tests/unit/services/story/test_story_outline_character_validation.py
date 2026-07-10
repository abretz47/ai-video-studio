from __future__ import annotations

from app.services.story.story_outline_character_validation import (
    validate_story_outline_characters,
)


def test_story_outline_character_validation_allows_generic_business_roles() -> None:
    result = validate_story_outline_characters(
        {
            "premise": "APreturn discover data be Cuan Gai，client Dang Chang Zhi Yi。",
            "synopsis": (
                "client: Zhe Fen data Bu Ke Xin。\n"
                "INT Gui: Ni Mei You Zheng Ju。\n"
                "APreturn Yong phone recording and Tou Ping Zheng Ju counterattack，team Cheng Yuan and Jing Zheng Dui Shou company only Zuo Wei Bei Jing Ya Li exists。"
            ),
            "main_characters": [
                {"name": "APreturn-20260618T164912", "description": "project Fu Ze Ren"},
                {"name": "client Dai Biao", "description": "Hui Yi Bei Jing Ya Li character"},
                {"name": "team Cheng Yuan", "description": "Bei Jing Ren"},
                {"name": "Jing Zheng Dui Shou company", "description": "Wei Ju Ming Wai Bu Ya Li"},
            ],
        },
        [{"name": "APreturn character-20260618T164912", "description": "project Fu Ze Ren"}],
    )

    assert result["character_validation_passed"] is True
    assert result["character_warnings"] == []
