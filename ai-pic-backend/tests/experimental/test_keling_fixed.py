#!/usr/bin/env python3
"""
test repair Hou De Ke LingAIimage generate function

Zhe Ge Jiao Ben Hui test: 
1. Ke LingAIprovider De Chu Shi Hua
2. retry Ji Zhi Shi Fou Sheng Xiao
3. service Fan Mang Shi De handle
4. AIservice Guan Li Qi De integration
"""

import asyncio
import sys
from pathlib import Path

# Tian Jia project Gen Mu Lu toPythonpath
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.services.ai_service import AIService


async def test_keling_with_retries():
 """Ce Shi Ke LingAIDe retry Ji Zhi"""

 print("🚀 test repair Hou De Ke LingAIimage generate function")
 print("=" * 60)

 # check Huan Jing Bian Liang configuration
 if not settings.KELING_API_KEY or not settings.KELING_SECRET_KEY:
 print("❌ Ke LingAIPei Zhi Que Shi")
 print(
 f" KELING_API_KEY: {'✅Yi Pei Zhi' if settings.KELING_API_KEY else '❌Wei Pei Zhi'}"
)
 print(
 f" KELING_SECRET_KEY: {'✅Yi Pei Zhi' if settings.KELING_SECRET_KEY else '❌Wei Pei Zhi'}"
)
 return

 print("✅ Ke LingAIconfiguration check pass")
 print(f" API Key: {settings.KELING_API_KEY[:10]}...****")
 print(f" Secret Key: {settings.KELING_SECRET_KEY[:10]}...****")
 print()

 try:
 # Chu Shi HuaAIservice
 ai_service = AIService()
 print("📦 AIservice Chu Shi Hua complete")

 # checkAIGuan Li Qi status
 if not ai_service.ai_manager:
 print("❌ AIGuan Li Qi not yet Chu Shi Hua")
 return

 print("🤖 AIGuan Li Qi status:")
 try:
 provider_status = ai_service.ai_manager.get_provider_status()
 for provider_name, status in provider_status.items():
 if provider_name == "keling":
 print(
 f" Ke LingAI: {'✅Ke Yong' if status.get('enabled') else '❌unavailable'}"
)
 print(f" Pei Zhi Xiang Qing: {status}")
 except Exception as e:
 print(f" status get failed: {e}")
 print()

 # Ce Shi Yong Li
 test_cases = [
 {
 "name": "Ji Chu Ce Shi",
 "prompt": "Yi Ge Ke Ai De Xiao Nv Hai, Ka Tong Feng Ge, Gao Zhi Liang",
 "style": "cartoon",
 "model": "kling-image",
 },
 {
 "name": "Xian Shi style test",
 "prompt": "modern urban Feng Jing, Ye Jing, Ni Hong Deng",
 "style": "realistic",
 "model": "kling-image",
 },
 ]

 for i, test_case in enumerate(test_cases, 1):
 print(f"🎨 Ce Shi Yong Li {i}: {test_case['name']}")
 print(f" Ti Shi Ci: {test_case['prompt']}")
 print(f" style: {test_case['style']}")
 print(f" model: {test_case['model']}")
 print(" start call Ke LingAI...")

 try:
 # useAIGuan Li Qi Zhi Jie call
 response = await ai_service.ai_manager.generate_image(
 prompt=test_case["prompt"],
 width=1024,
 height=1024,
 style=test_case["style"],
 model=test_case["model"],
 prefer_provider="keling",
)

 print(" 📊 Xiang Ying Jie Guo:")
 print(f" success: {'✅' if response.success else '❌'}")
 print(f" provider: {response.provider}")
 print(f" model: {response.model}")

 if response.success:
 print(" ✅ Sheng Cheng Cheng Gong!")
 if response.data and "images" in response.data:
 images = response.data["images"]
 print(f" generate image count: {len(images)}")
 for j, img_url in enumerate(images):
 print(f" image {j+1}: {str(img_url)[:100]}...")
 else:
 print(f" data: {response.data}")
 else:
 print(f" ❌ Sheng Cheng Shi Bai: {response.error}")

 print(f" Yuan Shu Ju: {response.metadata}")

 except Exception as e:
 print(f" ❌ Ce Shi Yi Chang: {e}")
 import traceback

 traceback.print_exc()

 print()

 # Ce Shi Tong GuoAIFu Wu Degenerate_virtual_ip_imagemethod
 print("🖼️ testAIFu Wu Degenerate_virtual_ip_imagemethod")
 try:
 result = await ai_service.generate_virtual_ip_image(
 ip_name="Ce Shi Jue Se",
 description="a lively and lovely young woman, Chong Man Hao Qi Xin He Mao Xian Jing Shen",
 style="cartoon",
 category="portrait",
 model="kling-image",
 additional_prompts=["Gao Zhi Liang", "Jing Zhi Xi Jie"],
)

 if result:
 print(" ✅ generate_virtual_ip_image Diao Yong Cheng Gong!")
 print(f" Sheng Cheng Fang Fa: {result.get('generation_method', 'N/A')}")
 print(f" provider: {result.get('provider_used', 'N/A')}")
 print(f" model: {result.get('model_used', 'N/A')}")
 print(f" imageURL: {result.get('image_url', 'N/A')}")
 else:
 print(" ❌ generate_virtual_ip_image Diao Yong Shi Bai")

 except Exception as e:
 print(f" ❌ generate_virtual_ip_image exception: {e}")

 except Exception as e:
 print(f"❌ test failed: {e}")
 import traceback

 traceback.print_exc()


async def main():
 """main function"""
 await test_keling_with_retries()
 print("\n✨ Ce Shi Wan Cheng!")


if __name__ == "__main__":
 asyncio.run(main())
