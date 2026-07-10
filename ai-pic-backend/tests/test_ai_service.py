import sys
from pathlib import Path

import pytest

# Tian Jia project Gen Mu Lu toPythonpath
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ai_service import AIService


@pytest.mark.asyncio
async def test_openai_dalle_generation(skip_if_no_openai):
 """testOpenAI DALL-Eimage generate method"""

 # Chu Shi HuaAIservice(Jiu Xiang Zai complete Ying Yong Zhong Yi Yang)
 ai_service = AIService()

 # Ce Shi Can Shu
 prompt = "A simple test image"
 style = "realistic"
 category = "portrait"

 print("\n🧪 testOpenAI DALL-ETu Xiang Sheng Cheng")
 print(f" Ti Shi Ci: {prompt}")
 print(f" style: {style}")
 print(f" Lei Bie: {category}")

 # Zhi Jie Ce ShiAIservice De method
 result = await ai_service._generate_with_openai_dalle(prompt, style, category)

 print(f" Jie Guo Lei Xing: {type(result)}")
 if result:
 if result.startswith("data:image/png;base64,"):
 print(f" format: base64 (Chang Du: {len(result)})")
 else:
 print(f" format: URL ({result[:50]}...)")

 # Duan Yan
 assert result is not None, "OpenAI DALL-E should return result"
 assert isinstance(result, str), "Result should be a string"

 # check Shi Fou Shibase64format
 if result.startswith("data:image/png;base64,"):
 assert len(result) > 1000, "Base64 image data should be substantial"
 else:
 assert result.startswith("http"), "Should be URL if not base64"
