#!/usr/bin/env python3
"""
Zhi Jie test Ke LingAIprovider

Rao GuoAIservice Guan Li Qi, Zhi Jie test Ke LingAIprovider
"""

import asyncio
import sys
from pathlib import Path

# Tian Jia project Gen Mu Lu toPythonpath
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.services.providers.base import ProviderConfig
from app.services.providers.keling_provider import KelingProvider


async def test_keling_provider_directly():
 """Zhi Jie test Ke LingAIprovider"""
 print("🔧 Zhi Jie test Ke LingAIprovider")
 print("=" * 50)

 if not settings.KELING_API_KEY or not settings.KELING_SECRET_KEY:
 print("❌ Que Shao Ke LingAIconfiguration")
 return

 # create Ke Ling provider configuration
 config = ProviderConfig(
 name="keling",
 api_key=settings.KELING_API_KEY,
 api_secret=settings.KELING_SECRET_KEY,
 base_url="https://klingai.com/api/v1",
 timeout=120.0,
)

 # create Ke Ling provider Shi Li
 provider = KelingProvider(config)
 print("✅ Ke Ling provider create success")
 print(f" name: {provider.name}")
 print(f" basicURL: {provider.base_url}")
 print()

 # test image generate(use repair Hou De retry Ji Zhi)
 print("🎨 test image generate...")
 test_prompt = "Yi Ge Ke Ai De Xiao Nv Hai, Ka Tong Feng Ge, Gao Zhi Liang"
 print(f"Ti Shi Ci: {test_prompt}")
 print("start call Ke LingAI API(Zhi Chi Zhong Shi)...")

 try:
 response = await provider.generate_image(
 prompt=test_prompt,
 model="kling-image",
 width=1024,
 height=1024,
 style="cartoon",
)

 print("\n📊 APIresponse:")
 print(f" success: {response.success}")
 print(f" provider: {response.provider}")
 print(f" model: {response.model}")

 if response.success:
 print(" ✅ Sheng Cheng Cheng Gong!")
 print(f" data: {response.data}")
 if response.data and "images" in response.data:
 images = response.data["images"]
 print(f" Tu Xiang Shu Liang: {len(images)}")
 for i, img_url in enumerate(images):
 print(f" image {i+1}: {img_url}")
 else:
 print(f" ❌ Sheng Cheng Shi Bai: {response.error}")

 print(f" Yuan Shu Ju: {response.metadata}")

 except Exception as e:
 print(f"❌ provider test failed: {e}")
 import traceback

 traceback.print_exc()


async def main():
 """main function"""
 await test_keling_provider_directly()
 print("\n✨ Ce Shi Wan Cheng!")


if __name__ == "__main__":
 asyncio.run(main())
