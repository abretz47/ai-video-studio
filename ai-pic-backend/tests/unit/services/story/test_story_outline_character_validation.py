from __future__ import annotations

from app.services.story.story_outline_character_validation import (
 validate_story_outline_characters,
)


def test_story_outline_character_validation_allows_generic_business_roles() -> None:
 result = validate_story_outline_characters(
 {
 "premise": "APreturn discover data Bei Cuan Gai, customer Dang Chang Zhi Yi.",
 "synopsis": (
 "customer: Zhe Fen data Bu Ke Xin.\n"
 "Nei Gui: you Mei You evidence.\n"
 "APreturn Yong phone recording He Tou Ping evidence counterattack, team Cheng Yuan He Jing Zheng Dui Shou company only Zuo Wei Bei Jing Ya Li exists."
),
 "main_characters": [
 {"name": "APreturn-20260618T164912", "description": "project Fu Ze Ren"},
 {"name": "Ke Hu Dai Biao", "description": "Hui Yi Bei Jing Ya Li character"},
 {"name": "Tuan Dui Cheng Yuan", "description": "Bei Jing Ren"},
 {"name": "Jing Zheng Dui Shou company", "description": "not yet Ju Ming Wai Bu Ya Li"},
 ],
 },
 [{"name": "APHui Gui Jue Se-20260618T164912", "description": "project Fu Ze Ren"}],
)

 assert result["character_validation_passed"] is True
 assert result["character_warnings"] == []
