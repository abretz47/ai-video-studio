#!/usr/bin/env python3
"""test approvalAPIrepair"""

import requests

API_BASE_URL = "http://localhost:8000/api/v1"


def test_approval_api():
    """test approvalAPI"""
    print("🔍 test approvalAPIrepair")

    try:
        # 1. login
        login_response = requests.post(
            f"{API_BASE_URL}/auth/login",
            data={"username": "admin", "password": "Ai7dio"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if login_response.status_code != 200:
            print(f"❌ login failed: {login_response.status_code}")
            return False

        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ login Cheng Gong")

        # 2. get user list
        users_response = requests.get(f"{API_BASE_URL}/admin/users", headers=headers)
        if users_response.status_code != 200:
            print(f"❌ get user list failed: {users_response.status_code}")
            return False

        users_data = users_response.json()
        users = users_data.get("users", [])
        print(f"✅ get to {len(users)} Ge user")

        # 3. Zhao Yi Ge Wei approval user
        pending_user = None
        for user in users:
            if not user.get("is_approved"):
                pending_user = user
                break

        if not pending_user:
            print("⚠️  Mei You Dai approval user，Tiao Guo approval test")
            return True

        user_id = pending_user["id"]
        print(f"✅ Zhao Dao Dai approval user: {pending_user['username']} (ID: {user_id})")

        # 4. test approvalAPI - use correct format
        approval_data = {"action": "approve", "reason": "APIrepair test - Zi Dong approval"}

        approval_response = requests.put(
            f"{API_BASE_URL}/admin/users/{user_id}/approval",
            headers={**headers, "Content-Type": "application/json"},
            json=approval_data,
        )

        if approval_response.status_code == 200:
            print("✅ approvalAPInormal work")
            result = approval_response.json()
            print(
                f"   user {result.get('username')} approval status: {'already approval' if result.get('is_approved') else 'Wei approval'}"
            )
            return True
        else:
            print(f"❌ approvalAPIfailed: {approval_response.status_code}")
            print(f"   error details: {approval_response.text}")
            return False

    except Exception as e:
        print(f"❌ test failed: {e}")
        return False


def main():
    print("🚀 approvalAPIrepair validate")
    print("=" * 40)

    if test_approval_api():
        print("\n✅ approvalAPIrepair Cheng Gong")
        print("Xian Zai frontend approval function Ying Gai Ke Yi normal work")
    else:
        print("\n❌ approvalAPIReng have issue")

    print("\n💡 Jian Yi:")
    print("  1. Chong Xin login frontend system Qing Chu Jiutoken")
    print("  2. test approval Mo Tai Kuang function")
    print("  3. check Liu Lan Qi Kong Zhi Tai error")


if __name__ == "__main__":
    main()
