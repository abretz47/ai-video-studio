import json
from types import SimpleNamespace

import pytest
from app.services.virtual_ip_ai_service import (
 VIRTUAL_IP_CONTENT_FILL_MODEL,
 VIRTUAL_IP_CONTENT_FILL_PROVIDER,
 VirtualIPAIService,
)


class RecordingAIManager:
 def __init__(self) -> None:
 self.calls = []

 async def generate_text(self, **kwargs):
 self.calls.append(kwargs)
 if "only output Zhong Wen prompt text" in kwargs["prompt"]:
 return SimpleNamespace(
 data="film Gan Xiao Xiang, Leng Se Diao office Guang Xian, Zhi Ye Zhuang, Mian Bu Xi Jie Qing Xi",
 model=kwargs["model"],
 usage={"total_tokens": 12},
)

 payload = {
 "detailed_description": "Duan FafemaleHe Huo Ren, Zhi Ye Zhuang, Shen Qing calm Ke Zhi.",
 "background_story": "from Ji Ceng Yi Lu Cheng Zhang Wei He Huo Ren, Xi Guan Yong Shi Shi Jie Jue crisis.",
 "personality": "Li Xing, Ke Zhi, Zhong Qing Yi",
 "skills": "Tan Pan, Feng Kong, Kuai Su Jue Ce",
 "relationships": "Yu team keep Yan Ge Dan Ke Kao De Huo Ban Guan Xi",
 "lifestyle": "Gao Qiang Du work, Zhong Shi Chang Qi Cheng Nuo",
 "signature_traits": "Hei Se Xi Zhuang Yu calm Mu Guang",
 "development_potential": "Shi He modern Shang Zhan Yu Fu Chou Cheng Zhang Xian",
 "suggested_tags": ["modern", "Jin Rong", "He Huo Ren"],
 }
 return SimpleNamespace(
 data=json.dumps(payload, ensure_ascii=False),
 model=kwargs["model"],
 usage={"total_tokens": 88},
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_virtual_ip_content_fill_uses_deepseek_v4_flash():
 service = VirtualIPAIService()
 manager = RecordingAIManager()
 service.ai_manager = manager

 result = await service.generate_complete_ip_with_details(
 name="Lin Jing",
 basic_info="35Sui Shang Hai Jin Rong Hang YefemaleHe Huo Ren",
)
 style_prompt = await service.generate_style_prompt(
 name="Lin Jing",
 description=result["content"]["description"],
 biography=result["content"]["biography"],
)

 assert result["generation_details"]["model"] == VIRTUAL_IP_CONTENT_FILL_MODEL
 assert style_prompt == "film Gan Xiao Xiang, Leng Se Diao office Guang Xian, Zhi Ye Zhuang, Mian Bu Xi Jie Qing Xi"
 assert [call["model"] for call in manager.calls] == [
 VIRTUAL_IP_CONTENT_FILL_MODEL,
 VIRTUAL_IP_CONTENT_FILL_MODEL,
 ]
 assert [call["prefer_provider"] for call in manager.calls] == [
 VIRTUAL_IP_CONTENT_FILL_PROVIDER,
 VIRTUAL_IP_CONTENT_FILL_PROVIDER,
 ]
