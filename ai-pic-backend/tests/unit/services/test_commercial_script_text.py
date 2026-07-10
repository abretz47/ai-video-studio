import pytest
from app.services.ai.script_text import build_script_text


@pytest.mark.unit
def test_build_script_text_uses_commercial_vertical_format():
    text = build_script_text(
        scenes=[
            {
                "scene_number": 1,
                "slug_line": "INT. living room - night",
                "summary": "opening hook：Lin Xue Dang Zhong Shuai Chu ledger。",
            }
        ],
        dialogues=[
            {
                "scene_number": 1,
                "character": "Lin Xue",
                "content": "ledger in this，Ni Hai Yao Zhuang Ma？",
                "emotion": "Leng Xiao",
            },
            {
                "scene_number": 1,
                "character": "Chen Mo",
                "content": "Ni Zen Me Hui have it？",
                "emotion": "Huang Luan",
            },
        ],
        stage_directions=[
            {
                "scene_number": 1,
                "timing": "intro",
                "content": "【sound effect】Peng！Men be Chuai Kai，Zhong Ren Hui Tou。",
                "type": "sfx",
            },
            {
                "scene_number": 1,
                "timing": "outro",
                "content": "【close-up】ledger final Yi Ye Lu Chu Mo Sheng signature。",
                "type": "camera",
            },
        ],
        format_type="screenplay",
        language="zh-CN",
        episode_number=1,
        template_style="commercial_vertical_drama",
        target_chars_per_episode=1300,
    )

    assert text.startswith("Di1Ji")
    assert "1-1 INT. living room - night" in text
    assert "Ren Wu： Lin Xue、Chen Mo" in text
    assert "▲【sound effect】Peng！Men be Chuai Kai" in text
    assert "Lin Xue(Leng Xiao)：ledger in this，Ni Hai Yao Zhuang Ma？" in text
    assert "▲【close-up】ledger final Yi Ye Lu Chu Mo Sheng signature。" in text
