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

    # check configuration
    print("📋 checkAIservice configuration...")
    if (
        not settings.OPENAI_API_KEY
        and not settings.STABILITY_API_KEY
        and not settings.AI_API_KEY
    ):
        print("❌ Wei configuration Ren HeAIserviceAPI Key")
        print("please configuration Yi Xia Huan Jing Bian Liang Zhi Yi：")
        print("  - OPENAI_API_KEY (Tui Jian)")
        print("  - STABILITY_API_KEY")
        print("  - AI_SERVICE_URL + AI_API_KEY")
        return False

    if settings.OPENAI_API_KEY:
        print("✅ OpenAI API Key already configuration")
    if settings.STABILITY_API_KEY:
        print("✅ Stability AI API Key already configuration")
    if settings.AI_SERVICE_URL and settings.AI_API_KEY:
        print("✅ Zi Ding YiAIservice already configuration")

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
        print(f"   style: {test_case['style']}")
        print(f"   Lei Bie: {test_case['category']}")
        print(f"   additional prompt: {test_case['additional_prompts']}")

        try:
            result = await ai_service.generate_virtual_ip_image(
                ip_name="test virtualIP",
                description="Zhe Shi Yi Ge Yong Yu test virtualIPcharacter",
                style=test_case["style"],
                category=test_case["category"],
                additional_prompts=[test_case["additional_prompts"]],
            )

            if result:
                print("   ✅ generate Cheng Gong!")
                print(f"   image path: {result['image_url']}")
                print(f"   generate method: {result['generation_method']}")
                print(f"   use prompt Ci: {result['prompt'][:100]}...")
            else:
                print("   ❌ generate failed")

        except Exception as e:
            print(f"   ❌ generate Chu Cuo: {e}")

    print("\n" + "=" * 50)
    print("🎉 test complete!")
    return True


async def test_prompt_optimization():
    """test prompt Ci You Hua function"""
    print("\n🔧 test prompt Ci You Hua...")

    test_ip = {
        "name": "Mo Fa Shao Nv Xiao Ying",
        "description": "Yi Wei Yong You Qiang Da Mo Fa Neng Li Shao Nv，Xing Ge lively Kai Lang，Xi Huan Shou Ji Mo Fa Ka Pai",
    }

    styles = ["realistic", "anime", "cartoon"]
    categories = ["portrait", "full_body", "scene"]

    for style in styles:
        for category in categories:
            print(f"\n📝 test {style} + {category} prompt Ci You Hua:")

            result = await ai_service.generate_virtual_ip_image(
                ip_name=test_ip["name"],
                description=test_ip["description"],
                style=style,
                category=category,
                additional_prompts=["magical", "cute"],
            )

            if result:
                print(f"   You Hua after prompt Ci: {result['prompt']}")
            else:
                print("   ❌ prompt Ci You Hua failed")


def main():
    """main function"""
    print("🚀 Qi DongAIimage generate test...")

    # Que Bao upload Mu Lu exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # run test
    asyncio.run(test_ai_generation())
    asyncio.run(test_prompt_optimization())


if __name__ == "__main__":
    main()
