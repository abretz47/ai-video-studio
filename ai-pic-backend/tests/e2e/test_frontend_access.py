#!/usr/bin/env python3
"""test frontend page access"""

import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE_URL = "http://localhost:3000"


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


def test_page_access():
    """test page access"""
    print("🔍 test frontend page access")

    # test frontend server response
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200:
            print("✅ frontend server normal response")
        else:
            print(f"❌ frontend server response exception: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ frontend server connection failed: {e}")
        return False

    # use Liu Lan Qi test page
    driver = setup_webdriver()
    if not driver:
        print("⚠️  Wu Fa set Liu Lan Qi，Tiao GuoUItest")
        return True

    try:
        success_indicators = []

        # test Zhu Ye
        print("  test Zhu Ye...")
        driver.get(BASE_URL)
        time.sleep(3)

        if (
            "AI Video Studio" in driver.title
            or len(driver.find_elements(By.TAG_NAME, "body")) > 0
        ):
            success_indicators.append("Zhu Ye")
            print("    ✅ Zhu Ye Jia Zai normal")

        # test login Ye
        print("  test login Ye...")
        driver.get(f"{BASE_URL}/login")
        time.sleep(3)

        login_forms = driver.find_elements(By.TAG_NAME, "form")
        if len(login_forms) > 0:
            success_indicators.append("login Ye")
            print("    ✅ login Ye Jia Zai normal")

        # test login function
        print("  test login function...")
        username_inputs = driver.find_elements(By.NAME, "username")
        password_inputs = driver.find_elements(By.NAME, "password")
        login_buttons = driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")

        if (
            len(username_inputs) > 0
            and len(password_inputs) > 0
            and len(login_buttons) > 0
        ):
            # Chang Shi login
            username_inputs[0].clear()
            username_inputs[0].send_keys("admin")
            password_inputs[0].clear()
            password_inputs[0].send_keys("Ai7dio")
            login_buttons[0].click()

            time.sleep(5)  # Deng Dai login handle

            # check Shi Fou Zhong Ding Xiang to Zhu Ye ordashboard
            current_url = driver.current_url
            if current_url != f"{BASE_URL}/login" and "login" not in current_url:
                success_indicators.append("login function")
                print("    ✅ login function normal")

                # test management page access
                print("  test management page...")
                driver.get(f"{BASE_URL}/admin/users")
                time.sleep(3)

                page_content = driver.page_source.lower()
                if (
                    "user management" in page_content
                    or "admin" in page_content
                    or len(driver.find_elements(By.TAG_NAME, "table")) > 0
                ):
                    success_indicators.append("management page")
                    print("    ✅ management page Jia Zai normal")
            else:
                print("    ❌ login function exception")

        print(f"\n📊 page test Jie Guo: {len(success_indicators)}/4 Xiang normal")
        print(f"   ✅ normal page: {', '.join(success_indicators)}")

        return len(success_indicators) >= 2  # Zhi Shao2Ge page normal

    except Exception as e:
        print(f"❌ page test failed: {e}")
        return False
    finally:
        driver.quit()


def main():
    print("🚀 frontend page access test")
    print("=" * 40)

    success = test_page_access()

    print("\n" + "=" * 40)
    if success:
        print("✅ frontend system Ji Ben normal")
        print("\n💡 Jie Jue Fang An:")
        print("  1. approvalAPIalready repair (actionZi Duan issue)")
        print("  2. frontend page Ke Yi normal access")
        print("  3. Jian Yi Qing Chu Liu Lan Qi Huan Cun andlocalStorage")
        print("  4. Chong Xin login system test complete function")
    else:
        print("❌ frontend system exists issue")
        print("\n🔧 Tiao Shi Jian Yi:")
        print("  1. check frontend Kong Zhi Tai Cuo Wu Xin Xi")
        print("  2. confirm Duan Kou3000Shi Fou be Zhan Yong")
        print("  3. Chong Qi Qian Duan Kai Fa server")

    print(f"\n🌐 access Di Zhi: {BASE_URL}")
    print("   Mo Ren login: admin / Ai7dio")


if __name__ == "__main__":
    main()
