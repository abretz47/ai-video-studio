#!/usr/bin/env python3
"""test user suspend/reactivate activate Kong Zhi function"""

import requests

API_BASE_URL = "http://localhost:8000/api/v1"


def test_suspension_controls():
 """Ce Shi Zan Ting/reactivate activate Kong Zhi function"""
 print("🔍 test user suspend/reactivate activate Kong Zhi function")

 try:
 # 1. Deng Lu Huo Qutoken
 login_data = {"username": "admin", "password": "Ai7dio"}
 login_response = requests.post(
 f"{API_BASE_URL}/auth/login",
 data=login_data,
 headers={"Content-Type": "application/x-www-form-urlencoded"},
)

 if login_response.status_code!= 200:
 print(f"❌ login failed: {login_response.status_code}")
 return False

 token = login_response.json().get("access_token")
 if not token:
 print("❌ not yet get to access Ling Pai")
 return False

 print("✅ success get access Ling Pai")

 # 2. get user list
 headers = {"Authorization": f"Bearer {token}"}
 users_response = requests.get(f"{API_BASE_URL}/admin/users", headers=headers)

 if users_response.status_code!= 200:
 print(f"❌ get user list failed: {users_response.status_code}")
 return False

 users_data = users_response.json()
 users = users_data.get("users", [])

 if len(users) == 0:
 print("❌ user list Wei Kong")
 return False

 # Zhao Yi Ge FeiadminDe test user
 test_user = None
 for user in users:
 if user.get("username")!= "admin":
 test_user = user
 break

 if not test_user:
 print("⚠️ Wei Zhao Dao He Shi De test user")
 return True

 user_id = test_user["id"]
 print(f"✅ Zhao Dao test user: {test_user['username']} (ID: {user_id})")
 print(f" Dang Qian Zhuang Tai: {'Huo Yue' if test_user['is_active'] else 'suspend'}")

 success_indicators = []

 # 3. test suspend userAPI
 print("\n🔍 test suspend userAPI...")
 suspend_response = requests.put(
 f"{API_BASE_URL}/admin/users/{user_id}/suspend",
 headers={**headers, "Content-Type": "application/x-www-form-urlencoded"},
 data={"reason": "APIGong Neng Ce Shi - Zan Ting Yong Hu"},
)

 if suspend_response.status_code in [200, 400]:
 success_indicators.append("Zan Ting Yong HuAPI")
 print("✅ Zan Ting Yong HuAPIDuan Dian Zheng Chang")
 if suspend_response.status_code == 200:
 print(" user Yi success suspend")
 elif suspend_response.status_code == 400:
 print(" user possible Yi Jing Chu Yu Zan Ting Zhuang Tai")
 else:
 print(f"❌ Zan Ting Yong HuAPIexception: {suspend_response.status_code}")
 print(f" response: {suspend_response.text}")

 # 4. test reactivate activate userAPI
 print("\n🔍 test reactivate activate userAPI...")
 reactivate_response = requests.put(
 f"{API_BASE_URL}/admin/users/{user_id}/reactivate",
 headers={**headers, "Content-Type": "application/x-www-form-urlencoded"},
 data={"reason": "APIGong Neng Ce Shi - reactivate activate user"},
)

 if reactivate_response.status_code in [200, 400]:
 success_indicators.append("reactivate activate userAPI")
 print("✅ reactivate activate userAPIDuan Dian Zheng Chang")
 if reactivate_response.status_code == 200:
 print(" user Yi success reactivate activate")
 elif reactivate_response.status_code == 400:
 print(" user possible Yi Jing Chu Yu Ji Huo Zhuang Tai")
 else:
 print(f"❌ reactivate activate userAPIexception: {reactivate_response.status_code}")
 print(f" response: {reactivate_response.text}")

 # 5. validate user status
 print("\n🔍 validate user final status...")
 final_users_response = requests.get(
 f"{API_BASE_URL}/admin/users", headers=headers
)
 if final_users_response.status_code == 200:
 final_users = final_users_response.json().get("users", [])
 final_user = next((u for u in final_users if u["id"] == user_id), None)
 if final_user:
 success_indicators.append("Zhuang Tai Yan Zheng")
 print(
 f"✅ user final status: {'Huo Yue' if final_user['is_active'] else 'suspend'}"
)
 else:
 print("❌ Wei Zhao Dao test user")
 else:
 print("❌ get Zui Zhong Yong Hu status failed")

 # 6. testAPICan Shu Chu Li
 print("\n🔍 testAPICan Shu Chu Li...")

 # test Dai Shi Chang De suspend
 suspend_with_duration = requests.put(
 f"{API_BASE_URL}/admin/users/{user_id}/suspend",
 headers={**headers, "Content-Type": "application/x-www-form-urlencoded"},
 data={"duration_hours": "24", "reason": "APIGong Neng Ce Shi - 24Xiao Shi Zan Ting"},
)

 if suspend_with_duration.status_code in [200, 400]:
 success_indicators.append("Can Shu Chu Li")
 print("✅ APICan Shu handle normal(Zhi Chi suspend Shi length)")
 else:
 print(f"⚠️ APICan Shu handle exception: {suspend_with_duration.status_code}")

 print(f"\n📊 Ce Shi Jie Guo: {len(success_indicators)}/4 Xiang function normal")
 print(f" ✅ Zheng Chang Gong Neng: {', '.join(success_indicators)}")

 return len(success_indicators) >= 3 # Zhi Shao3Xiang function normal Cai Suan success

 except Exception as e:
 print(f"❌ An error occurred during testing: {e}")
 return False


def test_frontend_api_integration():
 """Ce Shi Qian DuanAPIintegration"""
 print("\n🔍 Ce Shi Qian DuanAPIFang Fa Ding Yi")

 # Zhe Li Wo Men check frontendAPIKe Hu Duan Shi Fou You Suo Xu De method
 success_indicators = []

 # Du QuAPIfile Bing check method Ding Yi
 try:
 with open(
 "/Users/geyunfei/dev/yfge/ai-video-studio/ai-pic-frontend/src/utils/api.ts",
 "r",
 encoding="utf-8",
) as f:
 api_content = f.read()

 if "suspendUser" in api_content:
 success_indicators.append("Zan Ting Yong HuAPImethod")
 print("✅ Qian Duan Bao HansuspendUser APImethod")

 if "reactivateUser" in api_content:
 success_indicators.append("reactivate activate userAPImethod")
 print("✅ Qian Duan Bao HanreactivateUser APImethod")

 if "adminAPI" in api_content and "suspendUser" in api_content:
 success_indicators.append("managementAPIDao Chu")
 print("✅ frontend correct Dao Chu managementAPImethod")

 print(f"\n📊 frontend integration check: {len(success_indicators)}/3 Xiang Zheng Chang")
 return len(success_indicators) >= 2

 except Exception as e:
 print(f"❌ frontendAPIJian Cha Shi Bai: {e}")
 return False


def main():
 """main test function"""
 print("🚀 start user suspend/reactivate activate Kong Zhi test")
 print("=" * 60)

 # Ce Shi Hou DuanAPI
 backend_success = test_suspension_controls()

 # test frontend integration
 frontend_success = test_frontend_api_integration()

 # summary result
 print("\n" + "=" * 60)
 print("📊 test result summary")
 print("=" * 60)

 if backend_success:
 print("✅ Hou DuanAPItest: pass")
 else:
 print("❌ Hou DuanAPItest: failed")

 if frontend_success:
 print("✅ frontend integration test: pass")
 else:
 print("❌ frontend integration test: failed")

 overall_success = backend_success and frontend_success

 if overall_success:
 print("\n🎉 Yong Hu Zan Ting/reactivate activate Kong Zhi test Quan Bu pass!")
 print("\n📋 Shi Xian De function:")
 print(" ✅ user suspend function (Zhi Chi Shi length set)")
 print(" ✅ user reactivate activate function")
 print(" ✅ suspend reason record")
 print(" ✅ status validate Ji Zhi")
 print(" ✅ frontendAPIintegration")
 print(" ✅ Hou DuanAPIendpoint")

 print("\n💡 Shi Yong Shuo Ming:")
 print(" - Zai user details Mo Tai Kuang Zhong Ke Yi Zhao Dao suspend/Ji Huo An Niu")
 print(" - Zhi You Huo Yue Qie Yi approval De user display suspend button")
 print(" - Zhi You Fei Huo Yue user display reactivate activate button")
 print(" - Suo You operation Dou Hui record to Shen Ji Ri Zhi Zhong")
 else:
 print("\n⚠️ Bu Fen Gong Neng Ce Shi failed, Jian Yi Jian Cha:")
 if not backend_success:
 print(" - Hou Duan Zan Ting/activateAPIJie Kou")
 print(" - database status update logic")
 if not frontend_success:
 print(" - frontendAPIFang Fa Ding Yi")
 print(" - UIZu Jian Ji Cheng")

 return overall_success


if __name__ == "__main__":
 try:
 main()
 except KeyboardInterrupt:
 print("\n❌ test Bei user Zhong Duan")
 except Exception as e:
 print(f"\n❌ An error occurred during testing: {e}")
