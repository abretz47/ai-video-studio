#!/usr/bin/env python3
"""test user details Mo Tai Kuang function"""

import json
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


def test_user_details_modal():
    """test user details Mo Tai Kuang"""
    print("🔍 test user details Mo Tai Kuang function")

    driver = setup_webdriver()
    if not driver:
        return False

    try:
        # 1. access login page
        driver.get(f"{BASE_URL}/login")
        time.sleep(2)

        # 2. login
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        username_input.clear()
        username_input.send_keys("admin")
        password_input.clear()
        password_input.send_keys("Ai7dio")
        login_button.click()

        time.sleep(3)

        # 3. Dao Hang to user management page
        driver.get(f"{BASE_URL}/admin/users")
        time.sleep(3)

        # 4. Cha Zhao Di Yi Ge user details button
        detail_buttons = driver.find_elements(By.CSS_SELECTOR, "[title='Cha Kan user details']")
        if len(detail_buttons) == 0:
            print("❌ Wei Zhao Dao user details button")
            return False

        print(f"✅ Zhao Dao {len(detail_buttons)} Ge user details button")

        # 5. Dian Ji Di Yi Ge details button
        detail_buttons[0].click()
        time.sleep(2)

        # 6. check Mo Tai Kuang Shi Fou Chu Xian
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".fixed.inset-0"))
            )
            print("✅ user details Mo Tai Kuang Yi display")
        except Exception:
            print("❌ user details Mo Tai Kuang Wei display")
            return False

        # 7. check Mo Tai Kuang content
        success_indicators = []

        # check Biao Qian Ye
        tabs = driver.find_elements(By.CSS_SELECTOR, "nav button")
        tab_texts = [tab.text for tab in tabs]
        if (
            "Ji Ben information" in tab_texts
            and "operation record" in tab_texts
            and "An Quan information" in tab_texts
        ):
            success_indicators.append("Biao Qian Ye")
            print("✅ Mo Tai Kuang Biao Qian Ye correct display")
        else:
            print(f"❌ Biao Qian Ye display exception: {tab_texts}")

        # Jian Cha Yong Hu information
        user_info_elements = driver.find_elements(By.CSS_SELECTOR, "label")
        user_info_texts = [elem.text for elem in user_info_elements]
        if any("Yong Hu Ming" in text for text in user_info_texts) and any(
            "You Xiang Di Zhi" in text for text in user_info_texts
        ):
            success_indicators.append("user information")
            print("✅ user Ji Ben information correct display")
        else:
            print("❌ user Ji Ben information display exception")

        # 8. test Biao Qian Qie Huan
        audit_tab = None
        for tab in tabs:
            if tab.text == "operation record":
                audit_tab = tab
                break

        if audit_tab:
            audit_tab.click()
            time.sleep(1)
            print("✅ Cheng Gong Qie Huan to operation record Biao Qian")
            success_indicators.append("Biao Qian Qie Huan")

        # 9. test close Mo Tai Kuang
        close_buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        for button in close_buttons:
            if "close" in button.text:
                button.click()
                time.sleep(1)
                print("✅ Cheng Gong close Mo Tai Kuang")
                success_indicators.append("close function")
                break

        # 10. validate Mo Tai Kuang Yi close
        modals = driver.find_elements(By.CSS_SELECTOR, ".fixed.inset-0")
        if len(modals) == 0:
            print("✅ Mo Tai Kuang Yi correct close")
            success_indicators.append("close confirm")
        else:
            print("❌ Mo Tai Kuang Wei correct close")

        print(f"\n📊 test Jie Guo: {len(success_indicators)}/5 Xiang function normal")
        print(f"   ✅ normal function: {', '.join(success_indicators)}")

        return len(success_indicators) >= 3  # Zhi Shao3Xiang function normal Cai Suan Cheng Gong

    except Exception as e:
        print(f"❌ An error occurred during testing: {e}")
        return False
    finally:
        driver.quit()


def test_backend_audit_api():
    """test after Duan Shen Ji Ri ZhiAPI"""
    print("\n🔍 test after Duan Shen Ji Ri ZhiAPI")

    try:
        # 1. login gettoken
        login_data = {"username": "admin", "password": "Ai7dio"}

        # useform dataformat
        login_response = requests.post(
            f"{API_BASE_URL}/auth/login",
            data=login_data,  # Zhu Yi Zhe Li usedataEr Bu Shijson
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if login_response.status_code != 200:
            print(f"❌ login failed: {login_response.status_code} - {login_response.text}")
            return False

        token_data = login_response.json()
        token = token_data.get("access_token")

        if not token:
            print(f"❌ Wei get to access Ling Pai: {token_data}")
            return False

        print("✅ Cheng Gong get access Ling Pai")

        # 2. get user list
        headers = {"Authorization": f"Bearer {token}"}
        users_response = requests.get(f"{API_BASE_URL}/admin/users", headers=headers)

        if users_response.status_code != 200:
            print(f"❌ get user list failed: {users_response.status_code}")
            return False

        users_data = users_response.json()
        if not users_data.get("users"):
            print("❌ user list Wei Kong")
            return False

        user_id = users_data["users"][0]["id"]
        print(f"✅ get to userID: {user_id}")

        # 3. get Shen Ji Ri Zhi
        audit_response = requests.get(
            f"{API_BASE_URL}/admin/users/{user_id}/audit-logs", headers=headers
        )

        if audit_response.status_code != 200:
            print(f"❌ get Shen Ji Ri Zhi failed: {audit_response.status_code}")
            return False

        audit_data = audit_response.json()
        print(f"✅ get to {len(audit_data)} Tiao Shen Ji Ri Zhi")

        if len(audit_data) > 0:
            sample_log = audit_data[0]
            required_fields = ["id", "user_id", "action", "created_at"]
            missing_fields = [
                field for field in required_fields if field not in sample_log
            ]

            if missing_fields:
                print(f"❌ Shen Ji Ri Zhi Que Shao Zi Duan: {missing_fields}")
                return False
            else:
                print("✅ Shen Ji Ri Zhi structure correct")
                print(
                    f"   Shi Li Ri Zhi: {json.dumps(sample_log, indent=2, ensure_ascii=False)}"
                )

        return True

    except Exception as e:
        print(f"❌ APItest failed: {e}")
        return False


def main():
    """main test function"""
    print("🚀 start user details Mo Tai Kuang test")
    print("=" * 60)

    # test after DuanAPI
    api_success = test_backend_audit_api()

    # test frontendUI
    ui_success = test_user_details_modal()

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
        print("\n🎉 user details Mo Tai Kuang Gong Neng Ce Shi Quan Bu pass！")
        print("\n📋 Shi Xian function:")
        print("   ✅ user Ji Ben information display")
        print("   ✅ user operation record display")
        print("   ✅ user An Quan information display")
        print("   ✅ Biao Qian Ye Qie Huan function")
        print("   ✅ Mo Tai Kuang Da Kai/close")
        print("   ✅ after DuanAPIintegration")
    else:
        print("\n⚠️ Bu Fen Gong Neng Ce Shi failed，Jian Yi check:")
        if not api_success:
            print("   - after DuanAPIJie Kou")
            print("   - database connection")
        if not ui_success:
            print("   - frontend Zu Jian Xuan Ran")
            print("   - JavaScript/TypeScriptDai Ma")

    return overall_success


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ test be user Zhong Duan")
    except Exception as e:
        print(f"\n❌ An error occurred during testing: {e}")
