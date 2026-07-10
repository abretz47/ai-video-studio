from __future__ import annotations

import pytest

from app.services.storyboard.storyboard_audio_prompt_builder import (
 build_visual_prompt_description,
)


def _assert_common_short_drama_shape(prompt: str) -> None:
 assert "main subject:" in prompt
 assert "Biao Yan Dong Zuo:" in prompt
 assert "Chang Jing Guang Xian:" in prompt
 assert "Gou Tu Lian Xu Xing:" in prompt
 assert "Jin Zhi Xiang:" in prompt
 assert "Shu Ping Duan Ju" in prompt
 assert "Dan Fu Hua Mian" in prompt
 assert "no subtitles" in prompt
 assert "Wu Ke Du Wen Zi" in prompt
 assert "Duo Ge Man Hua" in prompt


@pytest.mark.parametrize(
 ("text", "expected_intent", "expected_detail"),
 [
 ("you Dao Di Xiang Zen Me Yang?", "Yi Wen/Zhui Wen", "Yan Shen Zhui Wen"),
 ("Wo Shou Gou Le!", "Qing Xu Ji Lie", "Qing Xu Wai Lu"),
 ],
)
def test_dialogue_prompt_is_visual_only_and_rich(
 text: str,
 expected_intent: str,
 expected_detail: str,
) -> None:
 prompt = build_visual_prompt_description(
 beat_type="dialogue",
 speaker_name="Lin Wan",
 text=text,
)

 _assert_common_short_drama_shape(prompt)
 assert "Kai Kou Shuo Hua" in prompt
 assert f"Yu Qi{expected_intent}" in prompt
 assert expected_detail in prompt
 assert text not in prompt


def test_voiceover_prompt_uses_silent_reaction() -> None:
 prompt = build_visual_prompt_description(
 beat_type="dialogue",
 speaker_name="Lin Wan",
 text="Wo Bu Neng Rang Ta Men Kan Chu Lai.",
 dialogue_action="Nei Xin Du Bai",
)

 _assert_common_short_drama_shape(prompt)
 assert "Chen Mo Fan Ying" in prompt
 assert "Bu Kai Kou Shuo Hua" in prompt
 assert "Wo Bu Neng Rang Ta Men Kan Chu Lai" not in prompt


def test_document_read_prompt_hides_screen_text() -> None:
 prompt = build_visual_prompt_description(
 beat_type="dialogue",
 speaker_name="Chen Zhe",
 text="Ta Kan Jian「Li Hun Xie Yi」Si Ge Zi, Shou suddenly Ting Zhu.",
)

 _assert_common_short_drama_shape(prompt)
 assert "screen/Zhi Mian content Zhi Neng Mo Hu Cheng Xian" in prompt
 assert "Wu Ke Du Wen Zi" in prompt
 assert "Li Hun Xie Yi" not in prompt


def test_action_prompt_preserves_action_without_dialogue_text() -> None:
 prompt = build_visual_prompt_description(
 beat_type="action",
 speaker_name=None,
 text="Tui Kai Men Chong Jin living room, 「don't move」",
)

 _assert_common_short_drama_shape(prompt)
 assert "Tui Kai Men Chong Jin living room" in prompt
 assert "don't move" not in prompt
 assert "action You Ming Que Mu Di" in prompt


def test_pause_prompt_adds_reaction_rhythm() -> None:
 prompt = build_visual_prompt_description(
 beat_type="pause",
 speaker_name=None,
 text=None,
)

 _assert_common_short_drama_shape(prompt)
 assert "drama pause Shun Jian" in prompt
 assert "Wei Biao Qing" in prompt
