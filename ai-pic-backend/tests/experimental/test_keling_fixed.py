#!/usr/bin/env python3
"""
test repair after KelingAIimage generate function

Zhe Ge Jiao Ben Hui test：
1. KelingAIprovider Chu Shi Hua
2. retry Ji Zhi Shi Fou Sheng Xiao
3. service Fan Mang when handle
4. AIservice Guan Li Qi integration
"""

import asyncio
import sys
from pathlib import Path

# Tian Jia project Gen Mu Lu toPythonpath
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.services.ai_service import AIService


async def test_keling_with_retries():
    """test KelingAIretry Ji Zhi"""

    print("🚀 test repair after KelingAIimage generate function")
    print("=" * 60)

    # check Huan Jing Bian Liang configuration
    if not settings.KELING_API_KEY or not settings.KELING_SECRET_KEY:
        print("❌ KelingAIconfiguration Que Shi")
        print(
            f"   KELING_API_KEY: {'✅already configuration' if settings.KELING_API_KEY else '❌Wei configuration'}"
        )
        print(
            f"   KELING_SECRET_KEY: {'✅already configuration' if settings.KELING_SECRET_KEY else '❌Wei configuration'}"
        )
        return

    print("✅ KelingAIconfiguration check pass")
    print(f"   API Key: {settings.KELING_API_KEY[:10]}...****")
    print(f"   Secret Key: {settings.KELING_SECRET_KEY[:10]}...****")
    print()

    try:
        # Chu Shi HuaAIservice
        ai_service = AIService()
        print("📦 AIservice Chu Shi Hua complete")

        # checkAIGuan Li Qi status
        if not ai_service.ai_manager:
            print("❌ AIGuan Li Qi Wei Chu Shi Hua")
            return

        print("🤖 AIGuan Li Qi status:")
        try:
            provider_status = ai_service.ai_manager.get_provider_status()
            for provider_name, status in provider_status.items():
                if provider_name == "keling":
                    print(
                        f"   KelingAI: {'✅Ke Yong' if status.get('enabled') else '❌unavailable'}"
                    )
                    print(f"   configuration details: {status}")
        except Exception as e:
            print(f"   status get failed: {e}")
        print()

        # Ce Shi Yong Li
        test_cases = [
            {
                "name": "Ji Chu test",
                "prompt": "Yi Ge Ke Ai Xiao Nv Hai，Ka Tong style，Gao Zhi Liang",
                "style": "cartoon",
                "model": "kling-image",
            },
            {
                "name": "Xian Shi style test",
                "prompt": "modern urban Feng Jing，Ye Jing，Ni Hong Deng",
                "style": "realistic",
                "model": "kling-image",
            },
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"🎨 Ce Shi Yong Li {i}: {test_case['name']}")
            print(f"   prompt: {test_case['prompt']}")
            print(f"   style: {test_case['style']}")
            print(f"   model: {test_case['model']}")
            print("   start call KelingAI...")

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

                print("   📊 response Jie Guo:")
                print(f"     Cheng Gong: {'✅' if response.success else '❌'}")
                print(f"     provider: {response.provider}")
                print(f"     model: {response.model}")

                if response.success:
                    print("     ✅ generate Cheng Gong!")
                    if response.data and "images" in response.data:
                        images = response.data["images"]
                        print(f"     generate image count: {len(images)}")
                        for j, img_url in enumerate(images):
                            print(f"     image {j+1}: {str(img_url)[:100]}...")
                    else:
                        print(f"     data: {response.data}")
                else:
                    print(f"     ❌ generate failed: {response.error}")

                print(f"     Yuan data: {response.metadata}")

            except Exception as e:
                print(f"   ❌ test exception: {e}")
                import traceback

                traceback.print_exc()

            print()

        # Ce Shi Tong GuoAIservicegenerate_virtual_ip_imagemethod
        print("🖼️  testAIservicegenerate_virtual_ip_imagemethod")
        try:
            result = await ai_service.generate_virtual_ip_image(
                ip_name="test character",
                description="a lively and lovely young woman，Chong Man curious Xin and Mao Xian Jing Shen",
                style="cartoon",
                category="portrait",
                model="kling-image",
                additional_prompts=["Gao Zhi Liang", "Jing Zhi Xi Jie"],
            )

            if result:
                print("   ✅ generate_virtual_ip_image call Cheng Gong!")
                print(f"   generate method: {result.get('generation_method', 'N/A')}")
                print(f"   provider: {result.get('provider_used', 'N/A')}")
                print(f"   model: {result.get('model_used', 'N/A')}")
                print(f"   imageURL: {result.get('image_url', 'N/A')}")
            else:
                print("   ❌ generate_virtual_ip_image call failed")

        except Exception as e:
            print(f"   ❌ generate_virtual_ip_image exception: {e}")

    except Exception as e:
        print(f"❌ test failed: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """main function"""
    await test_keling_with_retries()
    print("\n✨ test complete!")


if __name__ == "__main__":
    asyncio.run(main())
