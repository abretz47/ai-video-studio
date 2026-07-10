import os
import sys
from pathlib import Path

import pytest

# Tian Jia project Gen Mu Lu toPythonpath
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.security import get_password_hash
from app.models.user import User
from app.models.virtual_ip import VirtualIP, VirtualIPImage


@pytest.mark.asyncio
async def test_fastapi_full_image_generation_flow(client, db_session, mock_ai_service):
    """testFastAPIYing Yong complete image generate Liu Cheng"""

    print("\n🧪 testFastAPIcomplete image generate Liu Cheng")

    # 0. create test user and virtualIP
    print("   create Ce Shi Shu Ju...")

    # create user
    test_user = User(
        username="admin",
        email="admin@test.com",
        hashed_password=get_password_hash("Ai7dio"),
        is_active=True,
        is_approved=True,
        email_verified=True,
        is_admin=True,
        is_superuser=True,
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)
    print(f"   create user: {test_user.username}")

    # create virtualIP
    test_virtual_ip = VirtualIP(
        name="Mia",
        description="a lively and lovely young woman，Chong Man curious Xin and Mao Xian Jing Shen",
        tags=["test", "ai"],
        background_story="Zhe Shi Yi Ge test Yong virtualIPcharacter",
        style_prompt="realistic, professional",
        is_active=True,
        is_public=False,
    )
    db_session.add(test_virtual_ip)
    db_session.commit()
    db_session.refresh(test_virtual_ip)
    print(f"   create virtualIP: {test_virtual_ip.name} (ID: {test_virtual_ip.id})")

    # 1. login get Ren Zheng Tou
    login_data = {"username": "admin", "password": "Ai7dio"}
    response = client.post("/api/v1/auth/login", data=login_data)
    print(f"   user login: {response.status_code}")
    assert response.status_code == 200, f"login failed: {response.text}"

    token = response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    virtual_ip_id = test_virtual_ip.id

    # 2. check generate before image count
    initial_count = (
        db_session.query(VirtualIPImage)
        .filter(VirtualIPImage.virtual_ip_id == virtual_ip_id)
        .count()
    )
    print(f"   generate before image count: {initial_count}")

    # 3. call image generateAPI
    generation_data = {
        "style": "realistic",
        "category": "portrait",
        "model": "dall-e-3",
        "additional_prompts": "test image generation",
        "is_default": False,
    }

    print("   start call image generateAPI...")
    print(f"   Can Shu: {generation_data}")

    response = client.post(
        f"/api/v1/virtual-ips/{virtual_ip_id}/images/generate",
        data=generation_data,
        headers=auth_headers,
        timeout=120,  # set120seconds timeout
    )

    print(f"   APIresponse status: {response.status_code}")

    if response.status_code != 200:
        print(f"   APIerror response: {response.text}")
        # Ru Guo is500error，Bu Yao Zhi Jie failed，Er Shi display Xiang Xi Xin Xi
        if response.status_code == 500:
            error_detail = response.json().get("detail", "Wei Zhi error")
            print(f"   error details: {error_detail}")

    assert (
        response.status_code == 200
    ), f"APIcall failed: {response.status_code} - {response.text}"

    result = response.json()
    print(f"   APIresponse Zi Duan: {list(result.keys())}")

    # 4. validate response data
    assert "id" in result, "response Ying Bao Han imageID"
    assert "file_path" in result, "response Ying Bao Han file path"
    assert "filename" in result, "response Ying Bao Han Wen Jian Ming"

    image_id = result["id"]
    file_path = result["file_path"]
    filename = result["filename"]

    print(f"   generate imageID: {image_id}")
    print(f"   file path: {file_path}")
    print(f"   Wen Jian Ming: {filename}")

    # 5. check database in record
    final_count = (
        db_session.query(VirtualIPImage)
        .filter(VirtualIPImage.virtual_ip_id == virtual_ip_id)
        .count()
    )
    print(f"   generate after image count: {final_count}")
    assert final_count == initial_count + 1, "database in Ying Gai Xin Zeng Yi Tiao image record"

    # 6. check Ju Ti database record
    db_image = (
        db_session.query(VirtualIPImage).filter(VirtualIPImage.id == image_id).first()
    )

    assert db_image is not None, "database in Ying Gai Zhao Dao Dui Ying image record"
    print(f"   database record: ID={db_image.id}, path={db_image.file_path}")
    print(f"   prompt: {db_image.prompt[:100]}...")
    print(f"   AImodel: {db_image.ai_model}")
    print(f"   Wen Jian Da Xiao: {db_image.file_size} bytes")

    # 7. check Ben Di file Shi Fou exists
    if file_path.startswith("/uploads/"):
        # Xiang Dui Lu Jing，Pin Jie complete path
        full_file_path = os.path.join("./uploads", filename)
    else:
        full_file_path = file_path

    print(f"   check Ben Di file: {full_file_path}")
    file_exists = os.path.exists(full_file_path)
    print(f"   file exists: {file_exists}")

    if file_exists:
        file_size = os.path.getsize(full_file_path)
        print(f"   actual Wen Jian Da Xiao: {file_size} bytes")
        assert file_size > 1000, "generate Tu Xiang Wen Jian Ying Gai have Shi Zhi content"
        assert (
            file_size == db_image.file_size
        ), "database record Wen Jian Da Xiao Ying and actual Wen Jian Da Xiao Pi Pei"
    else:
        print("   ⚠️ Ben Di file not exists，Dan database have record")

    # 8. checkOSSupload status（Ru Guo havemetadata）
    if db_image.metadata and "oss_upload" in db_image.metadata:
        oss_result = db_image.metadata["oss_upload"]
        print(f"   OSSupload Jie Guo: {oss_result}")

    print("   ✅ Quan Liu Cheng test complete")
