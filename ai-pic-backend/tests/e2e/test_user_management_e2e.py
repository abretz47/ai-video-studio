"""user Guan Li Xi Tong Duan Dao Duan test Jiao Ben

test complete De user Guan Li Gong Zuo Liu Cheng: 
1. Yong Hu Zhu Ce(Mo Ren Wei Ji Huo)
2. administrator approval user
3. user login validate
4. permission Kong Zhi test
"""

import pytest
import requests

pytestmark = pytest.mark.skip(
 reason="manual e2e script (requires running backend at localhost:8000)"
)

BASE_URL = "http://localhost:8000/api/v1"


def test_user_registration():
 """test Yong Hu Zhu Ce - Ying Gai create Wei Ji Huo user"""
 print("🔍 test 1: Yong Hu Zhu Ce")

 # Zhu Ce new user
 registration_data = {
 "username": "testuser123",
 "email": "testuser123@example.com",
 "password": "testpass123",
 "full_name": "Test User 123",
 }

 response = requests.post(f"{BASE_URL}/auth/register", json=registration_data)

 if response.status_code == 200:
 user_data = response.json()
 print(f"✅ Yong Hu Zhu Ce success: {user_data['username']}")
 print(f" - is_active: {user_data['is_active']} (Ying Wei False)")
 print(f" - is_approved: {user_data['is_approved']} (Ying Wei False)")
 print(f" - email_verified: {user_data['email_verified']} (Ying Wei False)")
 return user_data
 else:
 print(f"❌ Zhu Ce Shi Bai: {response.status_code} - {response.text}")
 return None


def test_inactive_user_login(username: str):
 """test Wei Ji Huo user login - Ying Gai Shi Bai"""
 print(f"🔍 test 2: Wei Ji Huo user login ({username})")

 login_data = {"username": username, "password": "testpass123"}

 response = requests.post(f"{BASE_URL}/auth/login", data=login_data)

 if response.status_code == 403:
 print("✅ Wei Ji Huo user login Bei correct Ju Jue")
 print(f" Cuo Wu Xin Xi: {response.json()['detail']}")
 return True
 else:
 print(f"❌ Wei Ji Huo user login test failed: {response.status_code}")
 return False


def get_admin_token():
 """get administrator Ling Pai"""
 print("🔍 get administrator Ling Pai")

 # use Xian You DeadminZhang Hu
 login_data = {"username": "admin", "password": "Ai7dio"}

 response = requests.post(f"{BASE_URL}/auth/login", data=login_data)

 if response.status_code == 200:
 token = response.json()["access_token"]
 print("✅ administrator login success")
 return token
 else:
 print(f"❌ administrator login failed: {response.status_code} - {response.text}")
 return None


def test_admin_user_list(admin_token: str):
 """test administrator get user list"""
 print("🔍 test 3: administrator get user list")

 headers = {"Authorization": f"Bearer {admin_token}"}
 response = requests.get(f"{BASE_URL}/admin/users", headers=headers)

 if response.status_code == 200:
 data = response.json()
 print(f"✅ get user list success, Gong {data['total']} Ge Yong Hu")
 print(f" Dang Qian Ye: {data['page']}, Mei Ye: {data['size']}")

 # Cha Zhao Wo Men Gang Zhu Ce De user
 test_user = None
 for user in data["users"]:
 if user["username"] == "testuser123":
 test_user = user
 break

 if test_user:
 print(f"✅ Zhao Dao test user: {test_user['username']}")
 print(f" - ID: {test_user['id']}")
 print(
 f" - status: activate={test_user['is_active']}, approval={test_user['is_approved']}"
)
 return test_user["id"]
 else:
 print("❌ Wei Zhao Dao test user")
 return None
 else:
 print(f"❌ get user list failed: {response.status_code} - {response.text}")
 return None


def test_approve_user(admin_token: str, user_id: int):
 """test administrator approval user"""
 print(f"🔍 test 4: administrator approval user (ID: {user_id})")

 headers = {"Authorization": f"Bearer {admin_token}"}
 approval_data = {"action": "approve", "reason": "Zi Dong Hua test approval"}

 response = requests.put(
 f"{BASE_URL}/admin/users/{user_id}/approval",
 headers=headers,
 json=approval_data,
)

 if response.status_code == 200:
 user_data = response.json()
 print("✅ user approval success")
 print(f" - is_active: {user_data['is_active']} (Xian Zai Ying Wei True)")
 print(f" - is_approved: {user_data['is_approved']} (Xian Zai Ying Wei True)")
 return True
 else:
 print(f"❌ user approval failed: {response.status_code} - {response.text}")
 return False


def test_approved_user_login():
 """test Yi approval user login - Xu Yao You Xiang validate"""
 print("🔍 test 5: Yi approval user login")

 login_data = {"username": "testuser123", "password": "testpass123"}

 response = requests.post(f"{BASE_URL}/auth/login", data=login_data)

 if response.status_code == 403:
 error_msg = response.json()["detail"]
 if "validate" in error_msg:
 print("✅ user Xu Yao You Xiang validate Cai Neng login - correct De Xing Wei")
 print(f" Cuo Wu Xin Xi: {error_msg}")
 return True
 else:
 print(f"❌ Yi Wai De Cuo Wu Xin Xi: {error_msg}")
 return False
 elif response.status_code == 200:
 print("❌ not yet validate You Xiang De user Bu Ying Gai Neng Gou login")
 return False
 else:
 print(f"❌ login test failed: {response.status_code} - {response.text}")
 return False


def test_admin_verify_email(admin_token: str, user_id: int):
 """test administrator Shou Dong validate user You Xiang"""
 print(f"🔍 test 6: administrator Shou Dong validate You Xiang (ID: {user_id})")

 headers = {"Authorization": f"Bearer {admin_token}"}
 update_data = {"email_verified": True}

 response = requests.put(
 f"{BASE_URL}/admin/users/{user_id}", headers=headers, json=update_data
)

 if response.status_code == 200:
 user_data = response.json()
 print("✅ You Xiang validate status update success")
 print(f" - email_verified: {user_data['email_verified']} (Xian Zai Ying Wei True)")
 return True
 else:
 print(f"❌ You Xiang validate update failed: {response.status_code} - {response.text}")
 return False


def test_fully_activated_user_login():
 """test Wan Quan activate user login - Ying Gai Cheng Gong"""
 print("🔍 test 7: Wan Quan activate user login")

 login_data = {"username": "testuser123", "password": "testpass123"}

 response = requests.post(f"{BASE_URL}/auth/login", data=login_data)

 if response.status_code == 200:
 token_data = response.json()
 print("✅ Wan Quan activate user login success")
 print(f" - Huo De access Ling Pai: {token_data['access_token'][:20]}...")
 return token_data["access_token"]
 else:
 print(f"❌ login failed: {response.status_code} - {response.text}")
 return None


def test_regular_user_cannot_access_admin(user_token: str):
 """test Pu Tong Yong Hu Wu Fa Fang Wen administrator Jie Kou"""
 print("🔍 test 8: Pu Tong Yong Hu access administrator Jie Kou")

 headers = {"Authorization": f"Bearer {user_token}"}
 response = requests.get(f"{BASE_URL}/admin/users", headers=headers)

 if response.status_code == 403:
 print("✅ Pu Tong Yong Hu correct Bei Zu Zhi access administrator Jie Kou")
 print(f" Cuo Wu Xin Xi: {response.json()['detail']}")
 return True
 else:
 print(f"❌ Pu Tong Yong Hu permission Kong Zhi failed: {response.status_code}")
 return False


def test_user_can_access_protected_routes(user_token: str):
 """test user Ke Yi access Shou Bao Hu De general Lu You"""
 print("🔍 test 9: user access Shou Bao Hu Lu You")

 headers = {"Authorization": f"Bearer {user_token}"}
 response = requests.get(f"{BASE_URL}/auth/me", headers=headers)

 if response.status_code == 200:
 user_data = response.json()
 print("✅ user Ke Yi access Shou Bao Hu De Lu You")
 print(f" - Yong Hu Ming: {user_data['username']}")
 print(f" - You Xiang: {user_data['email']}")
 return True
 else:
 print(f"❌ user access Shou Bao Hu Lu You failed: {response.status_code} - {response.text}")
 return False


def test_admin_user_stats(admin_token: str):
 """test administrator get user statistics"""
 print("🔍 test 10: administrator get user statistics")

 headers = {"Authorization": f"Bearer {admin_token}"}
 response = requests.get(f"{BASE_URL}/admin/stats", headers=headers)

 if response.status_code == 200:
 stats = response.json()
 print("✅ get user statistics success")
 print(f" - Zong Yong Hu Shu: {stats['total_users']}")
 print(f" - Huo Yue Yong Hu: {stats['active_users']}")
 print(f" - Dai Shen Pi: {stats['pending_approval']}")
 print(f" - administrator: {stats['admin_users']}")
 return True
 else:
 print(f"❌ get user statistics failed: {response.status_code} - {response.text}")
 return False


def main():
 """main test function"""
 print("🚀 start user Guan Li Xi Tong Duan Dao Duan test")
 print("=" * 50)

 test_results = []

 # test 1: Yong Hu Zhu Ce
 user_data = test_user_registration()
 test_results.append(user_data is not None)

 if not user_data:
 print("❌ Yong Hu Zhu Ce failed, Zhong Zhi Ce Shi")
 return

 # test 2: Wei Ji Huo user login
 result = test_inactive_user_login(user_data["username"])
 test_results.append(result)

 # get administrator Ling Pai
 admin_token = get_admin_token()
 if not admin_token:
 print("❌ Wu Fa get administrator Ling Pai, Zhong Zhi Ce Shi")
 return

 # test 3: administrator get user list
 user_id = test_admin_user_list(admin_token)
 test_results.append(user_id is not None)

 if not user_id:
 print("❌ Wu Fa Zhao Dao test user, Zhong Zhi Ce Shi")
 return

 # test 4: administrator approval user
 result = test_approve_user(admin_token, user_id)
 test_results.append(result)

 # test 5: Yi approval Dan not yet validate You Xiang De user login
 result = test_approved_user_login()
 test_results.append(result)

 # test 6: administrator Shou Dong validate You Xiang
 result = test_admin_verify_email(admin_token, user_id)
 test_results.append(result)

 # test 7: Wan Quan activate user login
 user_token = test_fully_activated_user_login()
 test_results.append(user_token is not None)

 if not user_token:
 print("❌ user Wu Fa Huo De access Ling Pai, Tiao Guo permission test")
 else:
 # test 8: Pu Tong Yong Hu permission Kong Zhi
 result = test_regular_user_cannot_access_admin(user_token)
 test_results.append(result)

 # test 9: user access Shou Bao Hu Lu You
 result = test_user_can_access_protected_routes(user_token)
 test_results.append(result)

 # test 10: administrator statistics
 result = test_admin_user_stats(admin_token)
 test_results.append(result)

 # summary result
 print("\n" + "=" * 50)
 print("📊 test result summary")
 print("=" * 50)

 passed = sum(test_results)
 total = len(test_results)

 print(f"✅ pass: {passed}/{total}")
 print(f"❌ failed: {total - passed}/{total}")
 print(f"📈 Cheng Gong Lv: {passed/total*100:.1f}%")

 if passed == total:
 print("\n🎉 Suo You Ce Shi Tong Guo!user Guan Li Xi Tong work normal!")
 else:
 print(f"\n⚠️ You {total - passed} Ge test failed, please check Xi Tong Pei Zhi")

 return passed == total


if __name__ == "__main__":
 try:
 main()
 except requests.exceptions.ConnectionError:
 print("❌ Wu Fa connection to server, please Que Bao server Yi Qi Dong")
 print(" Qi Dong Ming Ling: uvicorn main:app --host 0.0.0.0 --port 8000")
 except Exception as e:
 print(f"❌ An error occurred during testing: {e}")
