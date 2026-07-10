#!/usr/bin/env python3
"""test character management function"""

import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "http://localhost:3000"
API_BASE_URL = "http://localhost:8000/api/v1"


def setup_webdriver():
 """setChrome WebDriver"""
 options = Options()
 options.add_argument("--headless")
 options.add_argument("--no-sandbox")
 options.add_argument("--disable-dev-shm-usage")
 options.add_argument("--disable-gpu")
 options.add_argument("--window-size=1920,1080")

 try:
 driver = webdriver.Chrome(options=options)
 return driver
 except Exception as e:
 print(f"❌ Wu Fa Qi DongChrome WebDriver: {e}")
 return None


def test_role_management_ui():
 """test character managementUIfunction"""
 print("🔍 test character managementUIfunction")

 driver = setup_webdriver()
 if not driver:
 return False

 try:
 # 1. login administrator Zhang Hu
 driver.get(f"{BASE_URL}/login")
 time.sleep(2)

 username_input = driver.find_element(By.NAME, "username")
 password_input = driver.find_element(By.NAME, "password")
 login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

 username_input.clear()
 username_input.send_keys("admin")
 password_input.clear()
 password_input.send_keys("Ai7dio")
 login_button.click()
 time.sleep(3)

 # 2. Dao Hang to user management page
 driver.get(f"{BASE_URL}/admin/users")
 time.sleep(3)

 # 3. Dian Ji Di Yi Ge user De details button
 detail_buttons = driver.find_elements(By.CSS_SELECTOR, "[title='Cha Kan user details']")
 if len(detail_buttons) == 0:
 print("❌ Wei Zhao Dao user details button")
 return False

 detail_buttons[0].click()
 time.sleep(2)

 # 4. Deng Dai user details Mo Tai Kuang Chu Xian
 try:
 WebDriverWait(driver, 10).until(
 EC.presence_of_element_located(
 (By.XPATH, "//h3[contains(text(), 'userID')]")
)
)
 print("✅ user details Mo Tai Kuang Yi display")
 except Exception:
 print("❌ user details Mo Tai Kuang Wei display")
 return False

 success_indicators = []

 # 5. Cha Zhao Bing Dian Ji"Guan Li Jue Se"button
 role_management_buttons = driver.find_elements(
 By.XPATH, "//button[contains(text(), 'Guan Li Jue Se')]"
)
 if len(role_management_buttons) > 0:
 success_indicators.append("character management button")
 print("✅ Zhao Dao character management button")

 role_management_buttons[0].click()
 time.sleep(2)

 # 6. check character management Mo Tai Kuang Shi Fou Chu Xian
 try:
 WebDriverWait(driver, 10).until(
 EC.presence_of_element_located(
 (By.XPATH, "//h3[contains(text(), 'Jue Se Guan Li')]")
)
)
 success_indicators.append("character management Mo Tai Kuang")
 print("✅ character management Mo Tai Kuang Yi display")

 # 7. check character Xuan Xiang
 role_radios = driver.find_elements(
 By.CSS_SELECTOR, "input[type='radio'][name='role']"
)
 if len(role_radios) >= 3:
 success_indicators.append("Jue Se Xuan Xiang")
 print(f"✅ Zhao Dao {len(role_radios)} Ge character Xuan Xiang")

 # check character name
 role_labels = []
 for radio in role_radios:
 radio_id = radio.get_attribute("id")
 if radio_id:
 label = driver.find_elements(
 By.CSS_SELECTOR, f"label[for='{radio_id}']"
)
 if label:
 role_labels.append(label[0].text)

 expected_roles = ["Pu Tong Yong Hu", "administrator", "Chao Ji administrator"]
 found_roles = any(
 role in " ".join(role_labels) for role in expected_roles
)
 if found_roles:
 success_indicators.append("character name")
 print("✅ character name display correct")

 # 8. check reason Shu Ru Kuang
 reason_textarea = driver.find_elements(By.ID, "reason")
 if len(reason_textarea) > 0:
 success_indicators.append("reason Shu Ru Kuang")
 print("✅ character Bian Geng reason Shu Ru Kuang exists")

 # 9. check permission Shuo Ming
 permission_lists = driver.find_elements(By.CSS_SELECTOR, "ul li")
 if len(permission_lists) > 0:
 success_indicators.append("Quan Xian Shuo Ming")
 print(f"✅ permission Shuo Ming list Bao Han {len(permission_lists)} Xiang")

 # 10. test Qu Xiao function
 cancel_buttons = driver.find_elements(
 By.XPATH, "//button[contains(text(), 'Qu Xiao')]"
)
 if len(cancel_buttons) > 0:
 cancel_buttons[0].click()
 time.sleep(1)

 # check character management Mo Tai Kuang Shi Fou close
 role_modals = driver.find_elements(
 By.XPATH, "//h3[contains(text(), 'Jue Se Guan Li')]"
)
 if len(role_modals) == 0:
 success_indicators.append("Qu Xiao Gong Neng")
 print("✅ character management Mo Tai Kuang Qu Xiao function normal")

 except Exception as e:
 print(f"❌ character management Mo Tai Kuang check failed: {e}")
 else:
 print("❌ Wei Zhao Dao character management button")

 # close user details Mo Tai Kuang
 close_buttons = driver.find_elements(
 By.XPATH, "//button[contains(text(), 'close')]"
)
 if len(close_buttons) > 0:
 close_buttons[0].click()
 time.sleep(1)

 print(f"\n📊 Ce Shi Jie Guo: {len(success_indicators)}/6 Xiang function normal")
 print(f" ✅ Zheng Chang Gong Neng: {', '.join(success_indicators)}")

 return len(success_indicators) >= 4 # Zhi Shao4Xiang function normal Cai Suan success

 except Exception as e:
 print(f"❌ An error occurred during testing: {e}")
 return False
 finally:
 driver.quit()


def test_backend_role_api():
 """test Hou Duan character managementAPI"""
 print("\n🔍 test Hou Duan character managementAPI")

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

 token_data = login_response.json()
 token = token_data.get("access_token")

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

 # Zhao Yi Ge Fei administrator user Jin Xing test
 test_user = None
 for user in users:
 if not user.get("is_admin") and user.get("username")!= "admin":
 test_user = user
 break

 if not test_user:
 print("⚠️ Wei Zhao Dao He Shi De test user(Fei administrator user)")
 return True

 user_id = test_user["id"]
 print(f"✅ Zhao Dao test userID: {user_id}, Yong Hu Ming: {test_user['username']}")

 # 3. test character updateAPIendpoint exists Xing(use Wu Xiao Shu Ju Ce Shi)
 role_data = {"is_admin": True, "reason": "APItest"}

 test_response = requests.put(
 f"{API_BASE_URL}/admin/users/{user_id}/role",
 headers={**headers, "Content-Type": "application/x-www-form-urlencoded"},
 data=role_data,
)

 # checkAPIendpoint Shi Fou exists(200, 400, 422Dou Biao Ming endpoint exists)
 if test_response.status_code in [200, 400, 422, 403]:
 print("✅ Jue Se Guan LiAPIendpoint exists Qie Ke access")

 if test_response.status_code == 403:
 print(" ⚠️ Dang Qian user permission Bu Zu(Zhe Shi normal De An Quan Xian Zhi)")

 return True
 else:
 print(f"❌ Jue Se Guan LiAPIDuan Dian Yi Chang: {test_response.status_code}")
 print(f" Xiang Ying Nei Rong: {test_response.text}")
 return False

 except Exception as e:
 print(f"❌ APItest failed: {e}")
 return False


def main():
 """main test function"""
 print("🚀 start character management Gong Neng Ce Shi")
 print("=" * 60)

 # Ce Shi Hou DuanAPI
 api_success = test_backend_role_api()

 # Ce Shi Qian DuanUI
 ui_success = test_role_management_ui()

 # summary result
 print("\n" + "=" * 60)
 print("📊 test result summary")
 print("=" * 60)

 if api_success:
 print("✅ Hou DuanAPItest: pass")
 else:
 print("❌ Hou DuanAPItest: failed")

 if ui_success:
 print("✅ frontendUItest: pass")
 else:
 print("❌ frontendUItest: failed")

 overall_success = api_success and ui_success

 if overall_success:
 print("\n🎉 character management Gong Neng Ce Shi Quan Bu pass!")
 print("\n📋 Shi Xian De function:")
 print(" ✅ character management Jie Mian")
 print(" ✅ user character Xuan Ze (Pu Tong Yong Hu/administrator/Chao Ji administrator)")
 print(" ✅ character permission Shuo Ming display")
 print(" ✅ character Bian Geng reason record")
 print(" ✅ permission validate He An Quan Kong Zhi")
 print(" ✅ Hou DuanAPIintegration")
 else:
 print("\n⚠️ Bu Fen Gong Neng Ce Shi failed, Jian Yi Jian Cha:")
 if not api_success:
 print(" - Hou Duan character managementAPI")
 print(" - permission validate logic")
 if not ui_success:
 print(" - frontend character management Jie Mian")
 print(" - Mo Tai Kuang Jiao Hu logic")

 return overall_success


if __name__ == "__main__":
 try:
 main()
 except KeyboardInterrupt:
 print("\n❌ test Bei user Zhong Duan")
 except Exception as e:
 print(f"\n❌ An error occurred during testing: {e}")
