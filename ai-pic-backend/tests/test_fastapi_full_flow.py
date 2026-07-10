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
 """testFastAPIYing Yong De complete image generate Liu Cheng"""

 print("\n🧪 testFastAPIcomplete image generate Liu Cheng")

 # 0. create test user He virtualIP
 print(" create Ce Shi Shu Ju...")

 # Chuang Jian Yong Hu
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
 print(f" Chuang Jian Yong Hu: {test_user.username}")

 # Chuang Jian Xu NiIP
 test_virtual_ip = VirtualIP(
 name="Mia",
 description="a lively and lovely young woman, Chong Man Hao Qi Xin He Mao Xian Jing Shen",
 tags=["test", "ai"],
 background_story="Zhe Shi Yi Ge test Yong De virtualIPcharacter",
 style_prompt="realistic, professional",
 is_active=True,
 is_public=False,
)
 db_session.add(test_virtual_ip)
 db_session.commit()
 db_session.refresh(test_virtual_ip)
 print(f" Chuang Jian Xu NiIP: {test_virtual_ip.name} (ID: {test_virtual_ip.id})")

 # 1. login get Ren Zheng Tou
 login_data = {"username": "admin", "password": "Ai7dio"}
 response = client.post("/api/v1/auth/login", data=login_data)
 print(f" Yong Hu Deng Lu: {response.status_code}")
 assert response.status_code == 200, f"login failed: {response.text}"

 token = response.json()["access_token"]
 auth_headers = {"Authorization": f"Bearer {token}"}

 virtual_ip_id = test_virtual_ip.id

 # 2. check generate Qian De image count
 initial_count = (
 db_session.query(VirtualIPImage)
.filter(VirtualIPImage.virtual_ip_id == virtual_ip_id)
.count()
)
 print(f" generate Qian image count: {initial_count}")

 # 3. call image generateAPI
 generation_data = {
 "style": "realistic",
 "category": "portrait",
 "model": "dall-e-3",
 "additional_prompts": "test image generation",
 "is_default": False,
 }

 print(" start call image generateAPI...")
 print(f" Can Shu: {generation_data}")

 response = client.post(
 f"/api/v1/virtual-ips/{virtual_ip_id}/images/generate",
 data=generation_data,
 headers=auth_headers,
 timeout=120, # set120Miao Chao Shi
)

 print(f" APIXiang Ying Zhuang Tai: {response.status_code}")

 if response.status_code!= 200:
 print(f" APICuo Wu Xiang Ying: {response.text}")
 # Ru Guo Shi500error, Bu Yao Zhi Jie failed, Er Shi display Xiang Xi Xin Xi
 if response.status_code == 500:
 error_detail = response.json().get("detail", "Wei Zhi Cuo Wu")
 print(f" Cuo Wu Xiang Qing: {error_detail}")

 assert (
 response.status_code == 200
), f"APIDiao Yong Shi Bai: {response.status_code} - {response.text}"

 result = response.json()
 print(f" APIXiang Ying Zi Duan: {list(result.keys())}")

 # 4. validate response data
 assert "id" in result, "response Ying Bao Han imageID"
 assert "file_path" in result, "response Ying Bao Han file path"
 assert "filename" in result, "response Ying Bao Han Wen Jian Ming"

 image_id = result["id"]
 file_path = result["file_path"]
 filename = result["filename"]

 print(f" generate De imageID: {image_id}")
 print(f" Wen Jian Lu Jing: {file_path}")
 print(f" Wen Jian Ming: {filename}")

 # 5. check database Zhong De record
 final_count = (
 db_session.query(VirtualIPImage)
.filter(VirtualIPImage.virtual_ip_id == virtual_ip_id)
.count()
)
 print(f" generate Hou image count: {final_count}")
 assert final_count == initial_count + 1, "database Zhong Ying Gai Xin Zeng Yi Tiao image record"

 # 6. check Ju Ti De database record
 db_image = (
 db_session.query(VirtualIPImage).filter(VirtualIPImage.id == image_id).first()
)

 assert db_image is not None, "database Zhong Ying Gai Zhao Dao Dui Ying De image record"
 print(f" database record: ID={db_image.id}, path={db_image.file_path}")
 print(f" Ti Shi Ci: {db_image.prompt[:100]}...")
 print(f" AImodel: {db_image.ai_model}")
 print(f" Wen Jian Da Xiao: {db_image.file_size} bytes")

 # 7. check Ben Di file Shi Fou exists
 if file_path.startswith("/uploads/"):
 # Xiang Dui Lu Jing, Pin Jie complete path
 full_file_path = os.path.join("./uploads", filename)
 else:
 full_file_path = file_path

 print(f" check Ben Di file: {full_file_path}")
 file_exists = os.path.exists(full_file_path)
 print(f" Wen Jian Cun Zai: {file_exists}")

 if file_exists:
 file_size = os.path.getsize(full_file_path)
 print(f" actual Wen Jian Da Xiao: {file_size} bytes")
 assert file_size > 1000, "generate De Tu Xiang Wen Jian Ying Gai You Shi Zhi content"
 assert (
 file_size == db_image.file_size
), "database record De Wen Jian Da Xiao Ying Yu actual Wen Jian Da Xiao Pi Pei"
 else:
 print(" ⚠️ Ben Di file Bu exists, Dan database You record")

 # 8. checkOSSShang Chuan Zhuang Tai(Ru Guo Youmetadata)
 if db_image.metadata and "oss_upload" in db_image.metadata:
 oss_result = db_image.metadata["oss_upload"]
 print(f" OSSShang Chuan Jie Guo: {oss_result}")

 print(" ✅ Quan Liu Cheng test complete")
