import pytest
from app.prompts.manager import prompt_manager
from app.prompts.templates import PromptTemplate


def test_virtual_ip_creation_template_includes_constraints():
    prompt = prompt_manager.render_prompt(
        PromptTemplate.VIRTUAL_IP_CREATION.value,
        {
            "name": "test character",
            "description": "35Sui Shang Hai Jin Rong Hang YefemaleHe Huo Ren，Wai Biao calm Li Luo，Nei Xin Zhong Qing Yi；Zheng Ti Xie Shi modern；Ju Jue Kua Zhang in Er Yu Qi。",
            "age": None,
            "gender": None,
            "personality_traits": None,
            "style_preference": None,
            "target_audience": None,
            "content_type": None,
        },
    )

    assert "Zhong Yao Yue Shu" in prompt
    assert "Bu Yao in Ren He Zi Duan in Ti Ji“virtualIP" in prompt
    assert "Bu Yao Yi“test character is Yi Ge" in prompt


def test_virtual_ip_style_prompt_template_renders():
    prompt = prompt_manager.render_prompt(
        PromptTemplate.VIRTUAL_IP_STYLE_PROMPT.value,
        {
            "name": "test character",
            "description": "Duan Fa，Zhi Ye Zhuang，calm Li Luo",
            "biography": "Jin Rong Hang Ye He Huo Ren，Ke Zhi Li Xing Dan Zhong Qing Yi",
            "image_category": "portrait",
        },
    )

    assert "only output Zhong Wen prompt Ci" in prompt
    assert "virtual ip" not in prompt.lower()


@pytest.mark.asyncio
async def test_virtual_ip_style_prompt_template_is_registered():
    # PromptTemplate Mei Ju exists Ji Dai Biao template Ming already Zhu Ce；Ci Chu Bi Mian be Zhong Gou Wu Shan
    assert PromptTemplate.VIRTUAL_IP_STYLE_PROMPT.value == "virtual_ip_style_prompt"
