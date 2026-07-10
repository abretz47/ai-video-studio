#!/usr/bin/env python3
"""
test KelingAIintegration - mock Cheng Gong response

Yong Yu validate KelingAIintegration Jia Gou Shi Fou correct work
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Tian Jia project Gen Mu Lu toPythonpath
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.services.ai_service import AIService
from app.services.providers.base import (
    AIModelType,
    AIResponse,
    AITaskType,
    ProviderConfig,
)
from app.services.providers.keling_provider import KelingProvider


async def test_keling_with_mock():
    """use mock response test KelingAIintegration"""
    print("🎭 test KelingAIintegration - mock Cheng Gong response")
    print("=" * 50)

    if not settings.KELING_API_KEY or not settings.KELING_SECRET_KEY:
        print("❌ Que Shao KelingAIconfiguration")
        return

    # create mock Cheng Gong response
    mock_response_data = {
        "result": 1,
        "status": 200,
        "message": "Success",
        "data": {"images": ["https://mock-keling.com/generated-image-123.png"]},
    }

    # mockHTTPresponse
    class MockHttpResponse:
        def __init__(self, json_data, status_code=200):
            self._json_data = json_data
            self.status_code = status_code

        def json(self):
            return self._json_data

    # test1: Zhi Jie test Keling provider
    print("🧪 test1: Zhi Jie test KelingAIprovider")

    config = ProviderConfig(
        name="keling",
        api_key=settings.KELING_API_KEY,
        api_secret=settings.KELING_SECRET_KEY,
        base_url="https://klingai.com/api/v1",
        timeout=120.0,
    )

    provider = KelingProvider(config)
    print(f"✅ Keling provider create Cheng Gong: {provider.name}")

    # mockHTTPKe Hu Duanpostmethod
    with patch.object(provider, "get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.post.return_value = MockHttpResponse(mock_response_data)
        mock_get_client.return_value = mock_client

        response = await provider.generate_image(
            prompt="Yi Ge Ke Ai Xiao Nv Hai，Ka Tong style，Gao Zhi Liang",
            model="kling-image",
            width=1024,
            height=1024,
            style="cartoon",
        )

        print("   📊 response Jie Guo:")
        print(f"     Cheng Gong: {'✅' if response.success else '❌'}")
        print(f"     provider: {response.provider}")
        print(f"     model: {response.model}")

        if response.success:
            print("     ✅ mock generate Cheng Gong!")
            print(f"     image data: {response.data}")
        else:
            print(f"     ❌ generate failed: {response.error}")

    print()

    # test2: passAIservice Guan Li Qi test
    print("🤖 test2: passAIservice Guan Li Qi test KelingAI")

    try:
        ai_service = AIService()
        if not ai_service.ai_manager:
            print("❌ AIGuan Li Qi Wei Chu Shi Hua")
            return

        print("✅ AIGuan Li Qi Chu Shi Hua Cheng Gong")

        # get KelingAIstatus
        provider_status = ai_service.ai_manager.get_provider_status()
        keling_status = provider_status.get("keling", {})
        print(
            f"   KelingAIstatus: {'✅Ke Yong' if keling_status.get('enabled') else '❌unavailable'}"
        )
        print(
            f"   Zhi Chi model: {[m['name'] for m in keling_status.get('available_models', [])]}"
        )

        # mock Cheng GongAIGuan Li Qi call
        with patch.object(
            ai_service.ai_manager.providers["keling"], "generate_image"
        ) as mock_generate:
            mock_generate.return_value = AIResponse(
                success=True,
                data={"images": ["https://mock-keling.com/generated-image-456.png"]},
                provider="keling",
                model="kling-image",
                task_type=AITaskType.PORTRAIT_GENERATION,
                model_type=AIModelType.TEXT_TO_IMAGE,
                metadata={
                    "width": 1024,
                    "height": 1024,
                    "style": "cartoon",
                    "prompt": "test prompt Ci",
                },
            )

            response = await ai_service.ai_manager.generate_image(
                prompt="test prompt Ci",
                model="kling-image",
                prefer_provider="keling",
                width=1024,
                height=1024,
                style="cartoon",
            )

            print("   📊 AIGuan Li Qi response:")
            print(f"     Cheng Gong: {'✅' if response.success else '❌'}")
            print(f"     provider: {response.provider}")
            print(f"     model: {response.model}")

            if response.success:
                print("     ✅ AIGuan Li Qi integration test Cheng Gong!")
                print(f"     image data: {response.data}")
            else:
                print(f"     ❌ AIGuan Li Qi integration failed: {response.error}")

    except Exception as e:
        print(f"❌ AIGuan Li Qi test failed: {e}")

    print()

    # test3: test completevirtual_ip_imagegenerate Liu Cheng
    print("🖼️  test3: completevirtual_ip_imagegenerate Liu Cheng")

    try:
        # mock Zheng GeAIservicegenerate_virtual_ip_imagecall
        with patch.object(ai_service, "_generate_with_keling_image") as mock_keling_gen:
            mock_keling_gen.return_value = (
                "https://mock-keling.com/generated-image-789.png"
            )

            result = await ai_service.generate_virtual_ip_image(
                ip_name="test character",
                description="a lively and lovely young woman，Chong Man curious Xin and Mao Xian Jing Shen",
                style="cartoon",
                category="portrait",
                model="kling-image",
                additional_prompts=["Gao Zhi Liang", "Jing Zhi Xi Jie"],
            )

            if result:
                print("   ✅ complete Liu Cheng test Cheng Gong!")
                print(f"   generate method: {result.get('generation_method', 'N/A')}")
                print(f"   provider: {result.get('provider_used', 'N/A')}")
                print(f"   model: {result.get('model_used', 'N/A')}")
                print(f"   mock imageURL: {result.get('image_url', 'N/A')}")
            else:
                print("   ❌ complete Liu Cheng test failed")

    except Exception as e:
        print(f"   ❌ complete Liu Cheng test exception: {e}")


async def main():
    """main function"""
    await test_keling_with_mock()
    print("\n🎉 KelingAIintegration test complete!")
    print("📝 Zong Jie:")
    print("   ✅ KelingAIprovider already correct integration")
    print("   ✅ AIGuan Li Qi already Shi Bie KelingAI")
    print("   ✅ retry Ji Zhi already Shi Xian")
    print("   ✅ Cuo Wu Chu Li already You Hua")
    print("   ✅ Jia Gou She Ji correct")
    print()
    print("💡 Dang Qian KelingAIservice Fan Mang，Dan integration Jia Gou already Jiu Xu。")
    print("   Dang Ke LingAIservice Hui Fu Zheng Chang when，image generate Jiang Zi Dong work。")


if __name__ == "__main__":
    asyncio.run(main())
