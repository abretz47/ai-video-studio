#!/usr/bin/env python3
"""
AIimage generate Gong Neng Ce Shi Jiao Ben
Yong Yu test virtualIPimage generate function Shi Fou normal work
"""

import asyncio
import os
import sys
from pathlib import Path

# Tian Jia project Gen Mu Lu toPythonpath
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.services.ai_service import ai_service


async def test_ai_generation():
 """testAIimage generate function"""
 print("🤖 AIimage generate Gong Neng Ce Shi")
 print("=" * 50)

 # Jian Cha Pei Zhi
 print("📋 checkAIFu Wu Pei Zhi...")
 if (
 not settings.OPENAI_API_KEY
 and not settings.STABILITY_API_KEY
 and not settings.AI_API_KEY
):
 print("❌ not yet configuration Ren HeAIserviceAPI Key")
 print("please configuration Yi Xia Huan Jing Bian Liang Zhi Yi: ")
 print(" - OPENAI_API_KEY (Tui Jian)")
 print(" - STABILITY_API_KEY")
 print(" - AI_SERVICE_URL + AI_API_KEY")
 return False

 if settings.OPENAI_API_KEY:
 print("✅ OpenAI API Key Yi Pei Zhi")
 if settings.STABILITY_API_KEY:
 print("✅ Stability AI API Key Yi Pei Zhi")
 if settings.AI_SERVICE_URL and settings.AI_API_KEY:
 print("✅ Zi Ding YiAIservice Yi configuration")

 # test image generate
 print("\n🎨 test image generate...")

 test_cases = [
 {
 "name": "Xie Shi style Xiao Xiang",
 "style": "realistic",
 "category": "portrait",
 "additional_prompts": "smiling, professional lighting",
 },
 {
 "name": "Dong Man style Quan Shen Xiang",
 "style": "anime",
 "category": "full_body",
 "additional_prompts": "vibrant colors, dynamic pose",
 },
 {
 "name": "Ka Tong style Biao Qing",
 "style": "cartoon",
 "category": "emotion",
 "additional_prompts": "happy, bright background",
 },
 ]

 for i, test_case in enumerate(test_cases, 1):
 print(f"\n📸 test {i}: {test_case['name']}")
 print(f" style: {test_case['style']}")
 print(f" Lei Bie: {test_case['category']}")
 print(f" E Wai Ti Shi: {test_case['additional_prompts']}")

 try:
 result = await ai_service.generate_virtual_ip_image(
 ip_name="Ce Shi Xu NiIP",
 description="Zhe Shi Yi Ge Yong Yu test De virtualIPcharacter",
 style=test_case["style"],
 category=test_case["category"],
 additional_prompts=[test_case["additional_prompts"]],
)

 if result:
 print(" ✅ Sheng Cheng Cheng Gong!")
 print(f" Tu Xiang Lu Jing: {result['image_url']}")
 print(f" Sheng Cheng Fang Fa: {result['generation_method']}")
 print(f" use prompt text: {result['prompt'][:100]}...")
 else:
 print(" ❌ Sheng Cheng Shi Bai")

 except Exception as e:
 print(f" ❌ Sheng Cheng Chu Cuo: {e}")

 print("\n" + "=" * 50)
 print("🎉 Ce Shi Wan Cheng!")
 return True


async def test_prompt_optimization():
 """test prompt text You Hua function"""
 print("\n🔧 test prompt text You Hua...")

 test_ip = {
 "name": "Mo Fa Shao Nv Xiao Ying",
 "description": "Yi Wei Yong You Qiang Da Mo Fa Neng Li De Shao Nv, Xing Ge Huo Po Kai Lang, Xi Huan Shou Ji Mo Fa Ka Pai",
 }

 styles = ["realistic", "anime", "cartoon"]
 categories = ["portrait", "full_body", "scene"]

 for style in styles:
 for category in categories:
 print(f"\n📝 test {style} + {category} prompt text You Hua:")

 result = await ai_service.generate_virtual_ip_image(
 ip_name=test_ip["name"],
 description=test_ip["description"],
 style=style,
 category=category,
 additional_prompts=["magical", "cute"],
)

 if result:
 print(f" You Hua Hou prompt text: {result['prompt']}")
 else:
 print(" ❌ prompt text You Hua failed")


def main():
 """main function"""
 print("🚀 Qi DongAIimage generate test...")

 # Que Bao upload Mu Lu exists
 os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

 # Yun Xing Ce Shi
 asyncio.run(test_ai_generation())
 asyncio.run(test_prompt_optimization())


if __name__ == "__main__":
 main()
