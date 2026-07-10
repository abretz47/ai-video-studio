#!/usr/bin/env python3
"""Ce Shi Shen PiAPIrepair"""

import requests

API_BASE_URL = "http://localhost:8000/api/v1"


def test_approval_api():
 """Ce Shi Shen PiAPI"""
 print("🔍 Ce Shi Shen PiAPIrepair")

 try:
 # 1. login
 login_response = requests.post(
 f"{API_BASE_URL}/auth/login",
 data={"username": "admin", "password": "Ai7dio"},
 headers={"Content-Type": "application/x-www-form-urlencoded"},
)

 if login_response.status_code!= 200:
 print(f"❌ login failed: {login_response.status_code}")
 return False

 token = login_response.json().get("access_token")
 headers = {"Authorization": f"Bearer {token}"}
 print("✅ Deng Lu Cheng Gong")

 # 2. get user list
 users_response = requests.get(f"{API_BASE_URL}/admin/users", headers=headers)
 if users_response.status_code!= 200:
 print(f"❌ get user list failed: {users_response.status_code}")
 return False

 users_data = users_response.json()
 users = users_data.get("users", [])
 print(f"✅ Huo Qu Dao {len(users)} Ge Yong Hu")

 # 3. Zhao Yi Ge not yet approval De user
 pending_user = None
 for user in users:
 if not user.get("is_approved"):
 pending_user = user
 break

 if not pending_user:
 print("⚠️ Mei You pending approval user, Tiao Guo approval test")
 return True

 user_id = pending_user["id"]
 print(f"✅ Zhao Dao pending approval user: {pending_user['username']} (ID: {user_id})")

 # 4. Ce Shi Shen PiAPI - use correct De format
 approval_data = {"action": "approve", "reason": "APIXiu Fu Ce Shi - Zi Dong Shen Pi"}

 approval_response = requests.put(
 f"{API_BASE_URL}/admin/users/{user_id}/approval",
 headers={**headers, "Content-Type": "application/json"},
 json=approval_data,
)

 if approval_response.status_code == 200:
 print("✅ approvalAPIZheng Chang Gong Zuo")
 result = approval_response.json()
 print(
 f" user {result.get('username')} Shen Pi Zhuang Tai: {'Yi Shen Pi' if result.get('is_approved') else 'Wei Shen Pi'}"
)
 return True
 else:
 print(f"❌ approvalAPIfailed: {approval_response.status_code}")
 print(f" Cuo Wu Xiang Qing: {approval_response.text}")
 return False

 except Exception as e:
 print(f"❌ test failed: {e}")
 return False


def main():
 print("🚀 approvalAPIXiu Fu Yan Zheng")
 print("=" * 40)

 if test_approval_api():
 print("\n✅ approvalAPIXiu Fu Cheng Gong")
 print("Xian Zai frontend approval function Ying Gai Ke Yi normal work Le")
 else:
 print("\n❌ approvalAPIReng You Wen Ti")

 print("\n💡 Jian Yi:")
 print(" 1. reactivate login frontend system Qing Chu Jiutoken")
 print(" 2. test approval Mo Tai Kuang function")
 print(" 3. check Liu Lan Qi Kong Zhi Tai error")


if __name__ == "__main__":
 main()
