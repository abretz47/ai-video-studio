#!/usr/bin/env python3
"""
AI image generation feature demo script
Shows how to use AI services to generate images for virtual IPs
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.ai_service import ai_service


async def demo_virtual_ip_generation():
    """Demo virtual IP image generation"""
    print("🎭 Virtual IP AI image generation demo")
    print("=" * 60)

    # Example virtual IPs
    virtual_ips = [
        {
            "name": "Sakura the Magical Girl",
            "description": "A girl with powerful magical abilities, cheerful and lively, who loves collecting magic cards, with long pink hair and cute outfits",
            "style": "anime",
            "category": "portrait",
            "additional_prompts": ["magical", "cute", "pink hair", "school uniform"],
        },
        {
            "name": "Future Warrior Arno",
            "description": "A mechanical warrior from the future with powerful combat abilities, a cold appearance, and high-tech armor",
            "style": "realistic",
            "category": "full_body",
            "additional_prompts": ["cyborg", "armor", "futuristic", "serious"],
        },
        {
            "name": "Bobby the Cute Bear",
            "description": "A fluffy little bear with a gentle and friendly personality who loves honey and adventure, perfect for children's content",
            "style": "cartoon",
            "category": "emotion",
            "additional_prompts": ["cute", "friendly", "honey", "adventure"],
        },
    ]

    for i, ip in enumerate(virtual_ips, 1):
        print(f"\n🎨 Demo {i}: {ip['name']}")
        print(f"   Description: {ip['description']}")
        print(f"   Style: {ip['style']}")
        print(f"   Category: {ip['category']}")
        print(f"   Additional prompts: {', '.join(ip['additional_prompts'])}")

        try:
            print("   🔄 Generating image...")
            result = await ai_service.generate_virtual_ip_image(
                ip_name=ip["name"],
                description=ip["description"],
                style=ip["style"],
                category=ip["category"],
                additional_prompts=ip["additional_prompts"],
            )

            if result:
                print("   ✅ Generation succeeded!")
                print(f"   Image path: {result['image_url']}")
                print(f"   Generation method: {result['generation_method']}")
                print(f"   Optimized prompt: {result['prompt'][:120]}...")
            else:
                print("   ❌ Generation failed")

        except Exception as e:
            print(f"   ❌ Generation error: {e}")

        print("-" * 40)


async def demo_style_variations():
    """Demo image generation in different styles"""
    print("\n🎨 风格变化演示")
    print("=" * 60)

    test_ip = {
        "name": "Mystic Witch",
        "description": "A witch with powerful magic, wearing robes and holding a magic staff",
    }

    styles = ["realistic", "anime", "cartoon"]
    categories = ["portrait", "full_body"]

    for style in styles:
        for category in categories:
            print(f"\n🔮 生成 {style} 风格的 {category}")

            try:
                result = await ai_service.generate_virtual_ip_image(
                    ip_name=test_ip["name"],
                    description=test_ip["description"],
                    style=style,
                    category=category,
                    additional_prompts=["mystical", "magical staff", "robes"],
                )

                if result:
                    print(f"   ✅ Successfully generated a {style} style image")
                    print(f"   Path: {result['image_url']}")
                else:
                    print("   ❌ Generation failed")

            except Exception as e:
                print(f"   ❌ Generation error: {e}")


async def demo_prompt_optimization():
    """Demo prompt optimization"""
    print("\n🔧 提示词优化演示")
    print("=" * 60)

    test_cases = [
        {
            "name": "Simple description",
            "description": "A girl",
            "expected": "Should automatically add style and quality enhancement terms",
        },
        {
            "name": "Detailed description",
            "description": "A beautiful girl in a red dress, smiling in a garden",
            "expected": "Should keep the original description and add style terms",
        },
        {
            "name": "Professional description",
            "description": "A model portrait photographed by a professional photographer using natural light with a blurred background",
            "expected": "Should be optimized into an AI-friendly prompt",
        },
    ]

    for case in test_cases:
        print(f"\n📝 测试: {case['name']}")
        print(f"   Original description: {case['description']}")
        print(f"   Expected effect: {case['expected']}")

        try:
            result = await ai_service.generate_virtual_ip_image(
                ip_name="Test Character",
                description=case["description"],
                style="realistic",
                category="portrait",
                additional_prompts=[],
            )

            if result:
                print("   ✅ Optimized prompt:")
                print(f"   {result['prompt']}")
            else:
                print("   ❌ Optimization failed")

        except Exception as e:
            print(f"   ❌ Optimization error: {e}")


def main():
    """Main function"""
    print("🚀 AI image generation feature demo")
    print("Please make sure the AI service API key is configured")
    print("=" * 60)

    # Check configuration
    if not any(
        [
            os.getenv("OPENAI_API_KEY"),
            os.getenv("STABILITY_API_KEY"),
            os.getenv("AI_API_KEY"),
        ]
    ):
        print("⚠️  Warning: No AI service API key configuration detected")
        print("Please configure one of the following environment variables:")
        print("  - OPENAI_API_KEY")
        print("  - STABILITY_API_KEY")
        print("  - AI_SERVICE_URL + AI_API_KEY")
        print("\n演示将继续，但可能无法成功生成图像")

    # Ensure the upload directory exists
    os.makedirs("uploads", exist_ok=True)

    # Run the demos
    asyncio.run(demo_virtual_ip_generation())
    asyncio.run(demo_style_variations())
    asyncio.run(demo_prompt_optimization())

    print("\n" + "=" * 60)
    print("🎉 Demo complete!")
    print("\n💡 提示:")
    print("- Generated images are saved in the uploads/ directory")
    print("- You can inspect the generated prompts to understand the optimization results")
    print("- Different AI services may produce different generation results")
    print("- Try different combinations of styles and categories")


if __name__ == "__main__":
    main()
