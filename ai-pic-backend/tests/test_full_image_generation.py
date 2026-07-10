import os
import sys
from pathlib import Path

import pytest

# Tian Jia project Gen Mu Lu toPythonpath
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ai_service import AIService


@pytest.mark.openai
@pytest.mark.external
@pytest.mark.asyncio
async def test_full_image_generation_workflow(skip_if_no_openai):
    """test complete image generate work Liu Cheng"""

    # Chu Shi HuaAIservice
    ai_service = AIService()

    # test Can Shu
    ip_name = "Mia"
    description = "a lively and lovely young woman，Chong Man curious Xin and Mao Xian Jing Shen"
    style = "realistic"
    category = "portrait"
    model = "dall-e-3"
    additional_prompts = ["test image generation"]

    print("\n🧪 test complete image generate work Liu Cheng")
    print(f"   virtualIP: {ip_name}")
    print(f"   description: {description}")
    print(f"   style: {style}")
    print(f"   Lei Bie: {category}")
    print(f"   model: {model}")

    # call complete image generate method
    result = await ai_service.generate_virtual_ip_image(
        ip_name=ip_name,
        description=description,
        style=style,
        category=category,
        model=model,
        additional_prompts=additional_prompts,
    )

    print(f"   Jie Guo: {result is not None}")
    if result:
        print(f"   return Zi Duan: {list(result.keys())}")
        if "local_file_path" in result:
            local_path = result["local_file_path"]
            print(f"   Ben Di file: {local_path}")
            print(f"   file exists: {os.path.exists(local_path) if local_path else False}")
            if local_path and os.path.exists(local_path):
                file_size = os.path.getsize(local_path)
                print(f"   Wen Jian Da Xiao: {file_size} bytes")

        if "oss_upload" in result:
            oss_result = result["oss_upload"]
            print(f"   OSSupload: {oss_result}")
    else:
        print("   ❌ generate_virtual_ip_imagereturnNone")

    # Duan Yan
    assert result is not None, "generate_virtual_ip_image should return result"
    assert "image_url" in result, "Result should contain image_url"
    assert "local_file_path" in result, "Result should contain local_file_path"
    assert "prompt" in result, "Result should contain prompt"

    # check Ben Di file
    local_path = result["local_file_path"]
    assert local_path is not None, "local_file_path should not be None"
    assert os.path.exists(local_path), f"Local file should exist: {local_path}"
    assert (
        os.path.getsize(local_path) > 1000
    ), "Generated image file should be substantial"
