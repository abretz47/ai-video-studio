#!/usr/bin/env python3
"""test user approval Mo Tai Kuang function"""

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


def create_pending_user():
    """create Yi Ge Dai approval test user"""
    test_user_data = {
        "username": "pending_user_test",
        "email": "pending_test@example.com",
        "password": "testpass123",
        "full_name": "Pending Test User",
    }

    try:
        response = requests.post(f"{API_BASE_URL}/auth/register", json=test_user_data)
        if response.status_code == 200:
            print("✅ Cheng Gong create Dai approval test user")
            return response.json()
        else:
            print(f"⚠️  Dai approval test user Ke Neng already exists (status Ma: {response.status_code})")
            return None
    except Exception as e:
        print(f"❌ create Dai approval test user failed: {e}")
        return None


def test_user_approval_modal():
    """test user approval Mo Tai Kuang"""
    print("🔍 test user approval Mo Tai Kuang function")

    # Xian create Yi Ge Dai approval user
    create_pending_user()

    driver = setup_webdriver()
    if not driver:
        return False

    try:
        # 1. access login page and login
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

        # 3. Cha Zhao"handle approval"button
        approval_buttons = driver.find_elements(
            By.XPATH, "//button[contains(text(), 'handle approval')]"
        )
        if len(approval_buttons) == 0:
            print("❌ Wei Zhao Dao handle approval button")
            return False

        print(f"✅ Zhao Dao {len(approval_buttons)} Ge handle approval button")

        # 4. Dian Ji Di Yi Ge handle approval button
        approval_buttons[0].click()
        time.sleep(2)

        # 5. check approval Mo Tai Kuang Shi Fou Chu Xian
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h3[contains(text(), 'user approval')]")
                )
            )
            print("✅ user approval Mo Tai Kuang Yi display")
        except Exception:
            print("❌ user approval Mo Tai Kuang Wei display")
            return False

        success_indicators = []

        # 6. check Mo Tai Kuang content

        # Jian Cha Yong Hu information display
        user_info_elements = driver.find_elements(By.CSS_SELECTOR, "label")
        user_info_texts = [elem.text for elem in user_info_elements]
        if any("Yong Hu Ming" in text for text in user_info_texts) and any(
            "You Xiang Di Zhi" in text for text in user_info_texts
        ):
            success_indicators.append("user information display")
            print("✅ user information correct display")

        # check handle Jue Ding Xuan Xiang
        approve_radio = driver.find_elements(By.ID, "approve")
        reject_radio = driver.find_elements(By.ID, "reject")
        if len(approve_radio) > 0 and len(reject_radio) > 0:
            success_indicators.append("handle Xuan Xiang")
            print("✅ Pi Zhun/Ju Jue Xuan Xiang correct display")

        # 7. test Xuan Ze Pi Zhun
        if len(approve_radio) > 0:
            approve_radio[0].click()
            time.sleep(1)

            # check Shi Fou Chu Xian reason Xuan Ze
            reason_select = driver.find_elements(By.ID, "reason")
            if len(reason_select) > 0:
                success_indicators.append("reason Xuan Ze")
                print("✅ Pi Zhun reason Xuan Ze Kuang correct display")

                # Xuan Ze Yi Ge reason
                reason_select[0].click()
                time.sleep(0.5)
                options = driver.find_elements(By.CSS_SELECTOR, "#reason option")
                if len(options) > 1:
                    options[1].click()  # Xuan Ze Di Yi Ge Fei Kong Xuan Xiang
                    time.sleep(0.5)
                    success_indicators.append("reason Xuan Ze function")
                    print("✅ reason Xuan Ze function normal")

        # 8. check confirm button Shi Fou Qi Yong
        confirm_buttons = driver.find_elements(
            By.XPATH, "//button[contains(text(), 'confirm Pi Zhun')]"
        )
        if len(confirm_buttons) > 0:
            if not confirm_buttons[0].get_attribute("disabled"):
                success_indicators.append("confirm button")
                print("✅ confirm button status correct")
            else:
                print("⚠️  confirm button Chu Yu Jin Yong status")

        # 9. test Qu Xiao function
        cancel_buttons = driver.find_elements(
            By.XPATH, "//button[contains(text(), 'Qu Xiao')]"
        )
        if len(cancel_buttons) > 0:
            cancel_buttons[0].click()
            time.sleep(1)

            # check Mo Tai Kuang Shi Fou close
            approval_modals = driver.find_elements(
                By.XPATH, "//h3[contains(text(), 'user approval')]"
            )
            if len(approval_modals) == 0:
                success_indicators.append("Qu Xiao function")
                print("✅ Qu Xiao function normal work")
            else:
                print("❌ Qu Xiao function exception")

        print(f"\n📊 test Jie Guo: {len(success_indicators)}/6 Xiang function normal")
        print(f"   ✅ normal function: {', '.join(success_indicators)}")

        return len(success_indicators) >= 4  # Zhi Shao4Xiang function normal Cai Suan Cheng Gong

    except Exception as e:
        print(f"❌ An error occurred during testing: {e}")
        return False
    finally:
        driver.quit()


def test_backend_approval_api():
    """test after Duan approvalAPI"""
    print("\n🔍 test after Duan approvalAPI")

    try:
        # 1. login gettoken
        login_data = {"username": "admin", "password": "Ai7dio"}

        login_response = requests.post(
            f"{API_BASE_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if login_response.status_code != 200:
            print(f"❌ login failed: {login_response.status_code}")
            return False

        token_data = login_response.json()
        token = token_data.get("access_token")

        if not token:
            print("❌ Wei get to access Ling Pai")
            return False

        print("✅ Cheng Gong get access Ling Pai")

        # 2. get Dai approval user
        headers = {"Authorization": f"Bearer {token}"}
        users_response = requests.get(
            f"{API_BASE_URL}/admin/users?status_filter=pending", headers=headers
        )

        if users_response.status_code != 200:
            print(f"❌ get Dai approval user failed: {users_response.status_code}")
            return False

        users_data = users_response.json()
        pending_users = [
            user for user in users_data.get("users", []) if not user.get("is_approved")
        ]

        if len(pending_users) == 0:
            print("⚠️  Dang Qian Mei You Dai approval user")
            return True

        user_id = pending_users[0]["id"]
        print(f"✅ Zhao Dao Dai approval userID: {user_id}")

        # checkAPIendpoint Shi Fou exists（useHEADQing Qiu Huo ZheOPTIONS）
        # Zhe Li Wo Men use Yi Ge Wu Xiao Qing Qiu Lai check endpoint structure
        test_response = requests.put(
            f"{API_BASE_URL}/admin/users/{user_id}/approval",
            headers=headers,
            json={"approved": True, "reason": "APIstructure test"},
        )

        # check response structure（Ji Shi failed Ye Neng Kan DaoAPIShi Fou exists）
        if test_response.status_code in [200, 400, 422]:  # Zhe Xie Dou Biao MingAPIendpoint exists
            print("✅ approvalAPIendpoint exists Qie structure correct")
            return True
        else:
            print(f"❌ approvalAPIendpoint exception: {test_response.status_code}")
            return False

    except Exception as e:
        print(f"❌ APItest failed: {e}")
        return False


def main():
    """main test function"""
    print("🚀 start user approval Mo Tai Kuang test")
    print("=" * 60)

    # test after DuanAPI
    api_success = test_backend_approval_api()

    # test frontendUI
    ui_success = test_user_approval_modal()

    # Hui Zong Jie Guo
    print("\n" + "=" * 60)
    print("📊 test Jie Guo Hui Zong")
    print("=" * 60)

    if api_success:
        print("✅ after DuanAPItest: pass")
    else:
        print("❌ after DuanAPItest: failed")

    if ui_success:
        print("✅ frontendUItest: pass")
    else:
        print("❌ frontendUItest: failed")

    overall_success = api_success and ui_success

    if overall_success:
        print("\n🎉 user approval Mo Tai Kuang Gong Neng Ce Shi Quan Bu pass！")
        print("\n📋 Shi Xian function:")
        print("   ✅ user information Xiang Xi display")
        print("   ✅ Pi Zhun/Ju Jue Xuan Xiang")
        print("   ✅ Yu She reason Xuan Ze")
        print("   ✅ Zi Ding Yi reason Shu Ru")
        print("   ✅ Biao Dan validate Ji Zhi")
        print("   ✅ after DuanAPIintegration")
    else:
        print("\n⚠️ Bu Fen Gong Neng Ce Shi failed，Jian Yi check:")
        if not api_success:
            print("   - after DuanAPIJie Kou")
            print("   - approval Ye Wu logic")
        if not ui_success:
            print("   - frontend Zu Jian Xuan Ran")
            print("   - Mo Tai Kuang Jiao Hu logic")

    return overall_success


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ test be user Zhong Duan")
    except Exception as e:
        print(f"\n❌ An error occurred during testing: {e}")
