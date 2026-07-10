import pytest
from app.prompts.manager import prompt_manager
from app.prompts.templates import PromptTemplate


def test_virtual_ip_creation_template_includes_constraints():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.VIRTUAL_IP_CREATION.value,
 {
 "name": "Ce Shi Jue Se",
 "description": "35Sui Shang Hai Jin Rong Hang YefemaleHe Huo Ren, Wai Biao calm Li Luo, Nei Xin Zhong Qing Yi; Zheng Ti Xie Shi modern; Ju Jue Kua Zhang Zhong Er Yu Qi.",
 "age": None,
 "gender": None,
 "personality_traits": None,
 "style_preference": None,
 "target_audience": None,
 "content_type": None,
 },
)

 assert "Zhong Yao Yue Shu" in prompt
 assert "Bu Yao Zai Ren He Zi Duan Zhong Ti Ji"virtualIP" in prompt
 assert "Bu Yao Yi"test character Shi Yi Ge" in prompt


def test_virtual_ip_style_prompt_template_renders():
 prompt = prompt_manager.render_prompt(
 PromptTemplate.VIRTUAL_IP_STYLE_PROMPT.value,
 {
 "name": "Ce Shi Jue Se",
 "description": "Duan Fa, Zhi Ye Zhuang, Leng Jing Li Luo",
 "biography": "Jin Rong Hang Ye He Huo Ren, Ke Zhi Li Xing Dan Zhong Qing Yi",
 "image_category": "portrait",
 },
)

 assert "only output Zhong Wen prompt text" in prompt
 assert "virtual ip" not in prompt.lower()


@pytest.mark.asyncio
async def test_virtual_ip_style_prompt_template_is_registered():
 # PromptTemplate Mei Ju exists Ji Dai Biao template Ming Yi Zhu Ce; Ci Chu Bi Mian Bei Zhong Gou Wu Shan
 assert PromptTemplate.VIRTUAL_IP_STYLE_PROMPT.value == "virtual_ip_style_prompt"
