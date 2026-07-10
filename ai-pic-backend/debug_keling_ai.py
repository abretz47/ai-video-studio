#!/usr/bin/env python3
"""
Debug Keling AI image generation

Detailed debugging for Keling AI integration issues
"""

import asyncio
import sys
from pathlib import Path

import httpx

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.services.providers.base import ProviderConfig
from app.services.providers.keling_provider import KelingProvider


async def debug_keling_provider():
    """Debug the Keling provider directly"""
    print("🔍 Directly testing the Keling provider")
    print("=" * 50)

    if not settings.KELING_API_KEY or not settings.KELING_SECRET_KEY:
        print("❌ Missing Keling AI configuration")
        return

    try:
        # Create Keling provider configuration
        config = ProviderConfig(
            name="keling",
            api_key=settings.KELING_API_KEY,
            api_secret=settings.KELING_SECRET_KEY,
            base_url="https://klingai.com/api/v1",
            timeout=120.0,
        )

        # Create Keling provider instance
        provider = KelingProvider(config)
        print("✅ Keling provider created successfully")
        print(f"   Name: {provider.name}")
        print(f"   Base URL: {provider.base_url}")
        print(
            f"   Supported model types: {[mt.value for mt in provider.supported_model_types]}"
        )
        print(f"   Number of available models: {len(provider.available_models)}")

        # Print available models
        print("\n📋 可用模型:")
        for model in provider.available_models:
            print(f"   - {model.model_id}: {model.name}")
            print(f"     Type: {model.model_type.value}")
            print(f"     Capabilities: {model.capabilities}")

        # Test image generation
        print("\n🎨 测试图像生成...")

        test_prompt = "A cute little girl, cartoon style, high quality"

        print(f"Prompt: {test_prompt}")
        print("Starting Keling AI API call...")

        response = await provider.generate_image(
            prompt=test_prompt,
            model="kling-image",
            width=1024,
            height=1024,
            style="cartoon",
        )

        print("\n📊 API响应:")
        print(f"   Success: {response.success}")
        print(f"   Error: {response.error}")
        print(f"   Provider: {response.provider}")
        print(f"   Model: {response.model}")
        print(f"   Data: {response.data}")
        print(f"   Metadata: {response.metadata}")

    except Exception as e:
        print(f"❌ Provider test failed: {e}")
        import traceback

        traceback.print_exc()


async def debug_http_request():
    """Debug HTTP requests directly"""
    print("\n🌐 直接测试HTTP请求")
    print("=" * 50)

    if not settings.KELING_API_KEY:
        print("❌ Missing API key")
        return

    try:
        # Test Keling AI API connectivity
        test_urls = [
            "https://klingai.com/api/v1/images/generate",
            "https://api.klingai.com/v1/images/generate",
            "https://app.klingai.com/api/v1/images/generate",
        ]

        for url in test_urls:
            print(f"\n🔗 测试URL: {url}")

            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    headers = {
                        "Authorization": f"Bearer {settings.KELING_API_KEY}",
                        "Content-Type": "application/json",
                        "User-Agent": "ai-video-studio/1.0",
                    }

                    # Test request data
                    request_data = {
                        "prompt": "A simple test image",
                        "width": 512,
                        "height": 512,
                        "model": "kling-image",
                        "num_outputs": 1,
                    }

                    print(f"   Headers: {headers}")
                    print(f"   Request data: {request_data}")

                    response = await client.post(
                        url, json=request_data, headers=headers
                    )

                    print(f"   Response status: {response.status_code}")
                    print(f"   Response headers: {dict(response.headers)}")

                    if response.status_code == 200:
                        data = response.json()
                        print(f"   ✅ Successful response: {data}")
                    else:
                        print(f"   ❌ Error response: {response.text[:500]}")

            except Exception as e:
                print(f"   ❌ Request failed: {e}")

    except Exception as e:
        print(f"❌ HTTP debugging failed: {e}")


async def debug_ai_manager():
    """Debug AI manager"""
    print("\n🤖 测试AI管理器")
    print("=" * 50)

    try:
        from app.services.ai_service import AIService

        ai_service = AIService()

        if not ai_service.ai_manager:
            print("❌ AI manager is not initialized")
            return

        print("✅ AI manager initialized successfully")

        # Get provider status
        status = ai_service.ai_manager.get_provider_status()

        print("\n📊 提供商状态:")
        for name, provider_status in status.items():
            print(f"   {name}: {provider_status}")

        # Check the Keling provider
        if "keling" in status:
            keling_status = status["keling"]
            print("\n🎯 可灵提供商详情:")
            for key, value in keling_status.items():
                print(f"   {key}: {value}")

        # Test image generation
        print("\n🎨 通过AI管理器测试图像生成...")

        response = await ai_service.ai_manager.generate_image(
            prompt="A test image",
            model="kling-image",
            prefer_provider="keling",
            width=512,
            height=512,
        )

        print(f"   Response: {response}")
        print(f"   Success: {response.success}")
        print(f"   Error: {response.error}")
        print(f"   Data: {response.data}")

    except Exception as e:
        print(f"❌ AI manager debugging failed: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """Main function"""
    print("🔧 Detailed Keling AI debugging script")
    print("🎯 Goal: identify Keling AI integration issues")
    print("")

    # Show configuration status
    print("📋 Environment configuration:")
    print(f"   KELING_API_KEY: {'✅ configured' if settings.KELING_API_KEY else '❌ not configured'}")
    print(
        f"   KELING_SECRET_KEY: {'✅ configured' if settings.KELING_SECRET_KEY else '❌ not configured'}"
    )

    if settings.KELING_API_KEY:
        print(f"   API key prefix: {settings.KELING_API_KEY[:10]}...")

    # Run the debugging steps in sequence
    await debug_keling_provider()
    await debug_http_request()
    await debug_ai_manager()

    print("\n✨ 调试完成!")


if __name__ == "__main__":
    asyncio.run(main())
