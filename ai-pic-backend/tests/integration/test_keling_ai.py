#!/usr/bin/env python3
"""
test KelingAIimage generate function

You Yu KelingAIXu Yao Zhen ShiAPIMi Yao，Zhe Ge Jiao Ben use mock data Jin Xing test。
actual use when Xu Yao configuration Zhen ShiKELING_API_KEYandKELING_SECRET_KEY。
"""

import asyncio
import sys
from pathlib import Path

# Tian Jia project Gen Mu Lu toPythonpath
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.services.ai_service import AIService


async def test_keling_ai():
    """test KelingAIimage generate function"""

    print("🧪 test KelingAIimage generate function")
    print("=" * 50)

    # check Huan Jing Bian Liang configuration
    if not settings.KELING_API_KEY or not settings.KELING_SECRET_KEY:
        print("❌ KelingAIconfiguration Que Shi:")
        print(
            f"   KELING_API_KEY: {'✅already configuration' if settings.KELING_API_KEY else '❌Wei configuration'}"
        )
        print(
            f"   KELING_SECRET_KEY: {'✅already configuration' if settings.KELING_SECRET_KEY else '❌Wei configuration'}"
        )
        print("")
        print("💡 Yao test KelingAI，please in.envfile in configuration:")
        print("   KELING_API_KEY=your-keling-api-key")
        print("   KELING_SECRET_KEY=your-keling-secret-key")
        print("")
        print("🔧 mock test Mo Shi:")
        print("   You Yu Que Shao Zhen ShiAPIMi Yao，Jiang run mock test")
        await simulate_keling_test()
        return

    # Zhen ShiAPItest
    print("✅ KelingAIconfiguration already Zhao Dao")
    print(f"   API Key: {settings.KELING_API_KEY[:10]}...")
    print(f"   Secret Key: {settings.KELING_SECRET_KEY[:10]}...")
    print("")

    try:
        # Chu Shi HuaAIservice
        ai_service = AIService()
        print("📦 AIservice Chu Shi Hua complete")

        # checkAIGuan Li Qi status
        if not ai_service.ai_manager:
            print("❌ AIGuan Li Qi Wei Chu Shi Hua")
            return

        print("📋 AIGuan Li Qi status:")
        provider_status = ai_service.ai_manager.get_provider_status()
        for provider_name, status in provider_status.items():
            if provider_name == "keling":
                print(f"   KelingAI: {'✅Ke Yong' if status.get('enabled') else '❌unavailable'}")

        # test image generate
        print("\n🎨 start test KelingAIimage generate...")

        test_cases = [
            {
                "prompt": "Yi Ge Ke Ai Xiao Nv Hai，Ka Tong style",
                "style": "cartoon",
                "model": "keling-kolors",
            },
            {
                "prompt": "modern urban Feng Jing，Ye Jing",
                "style": "realistic",
                "model": "kling-image",
            },
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\nCe Shi Yong Li {i}:")
            print(f"   prompt: {test_case['prompt']}")
            print(f"   style: {test_case['style']}")
            print(f"   model: {test_case['model']}")

            result = await ai_service.generate_virtual_ip_image(
                ip_name="test character",
                description="test description",
                style=test_case["style"],
                category="portrait",
                model=test_case["model"],
                additional_prompts=[test_case["prompt"]],
            )

            if result:
                print("   ✅ generate Cheng Gong!")
                print(f"   📁 file path: {result.get('local_file_path', 'N/A')}")
                print(f"   🌐 imageURL: {result.get('image_url', 'N/A')}")
                print(f"   📝 generate method: {result.get('generation_method', 'N/A')}")
            else:
                print("   ❌ generate failed")

    except Exception as e:
        print(f"❌ test failed: {e}")


async def simulate_keling_test():
    """mock KelingAItest（Dang Mei You Zhen ShiAPIMi Yao when）"""
    print("🎭 run KelingAImock test")
    print("")

    # mock KelingAIresponse
    mock_response = {
        "success": True,
        "data": {"images": ["https://mock-keling-api.com/generated-image-123.png"]},
        "provider": "keling",
        "model": "keling-kolors",
        "metadata": {
            "width": 1024,
            "height": 1024,
            "style": "realistic",
            "prompt": "Yi Ge Ke Ai Xiao Nv Hai，Chong Man curious Xin",
        },
    }

    print("📊 mock KelingAIresponse:")
    print(f"   status: {'✅Cheng Gong' if mock_response['success'] else '❌failed'}")
    print(f"   provider: {mock_response['provider']}")
    print(f"   model: {mock_response['model']}")
    print(f"   image count: {len(mock_response['data']['images'])}")
    print(f"   imageURL: {mock_response['data']['images'][0]}")
    print("")

    # mockAIservice integration test
    print("🔧 mockAIservice integration:")
    try:
        ai_service = AIService()
        print(f"   AIGuan Li Qi Chu Shi Hua: {'✅Cheng Gong' if ai_service.ai_manager else '❌failed'}")

        if ai_service.ai_manager:
            # check Keling provider Shi Fou in configuration in
            from app.services.providers.keling_provider import KelingProvider

            print("   Keling provider Lei: ✅already import")
            print(f"   Zhi Chi model type: {KelingProvider.__doc__ or 'video and image generate'}")

    except Exception as e:
        print(f"   ❌ mock test failed: {e}")

    print("")
    print("💡 Yao Jin Xing Zhen Shi test，please:")
    print("   1. Zhu Ce KelingAIZhang Hao: https://klingai.com/")
    print("   2. getAPIMi Yao")
    print("   3. in.envfile in configurationKELING_API_KEYandKELING_SECRET_KEY")
    print("   4. Chong Xin run Ci test Jiao Ben")


async def main():
    """main function"""
    print("🚀 KelingAIimage generate test Jiao Ben")
    print("📅 Ban Ben: 1.0")
    print("🎯 target: test KelingAIintegration function")
    print("")

    await test_keling_ai()

    print("")
    print("✨ test complete!")


if __name__ == "__main__":
    asyncio.run(main())
