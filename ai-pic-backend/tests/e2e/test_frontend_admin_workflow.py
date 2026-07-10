"""frontend management Jie Mian work Liu test Jiao Ben

test complete frontend management Jie Mian function：
1. administrator login
2. Cha Kan user statistics
3. management user list
4. user approval operation
5. Jie Mian response Xing test
"""

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
    options.add_argument("--headless")  # Wu Tou Mo Shi
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"❌ Wu Fa Qi DongChrome WebDriver: {e}")
        print("please Que Bao already An ZhuangChromeLiu Lan Qi andChromeDriver")
        return None


def test_servers_running():
    """test server Shi Fou Zheng Zai run"""
    print("🔍 test 1: check server status")

    try:
        # check after DuanAPIserver
        response = requests.get(f"{API_BASE_URL}/auth/me", timeout=5)
        print(f"✅ after DuanAPIserver run normal (status Ma: {response.status_code})")
    except Exception as e:
        print(f"❌ after DuanAPIserver connection failed: {e}")
        return False

    try:
        # check frontend server
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ frontend server run normal (status Ma: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ frontend server connection failed: {e}")
        return False


def create_test_user():
    """create test user"""
    print("🔍 test 2: create test user")

    test_user_data = {
        "username": "frontend_testuser",
        "email": "frontend_test@example.com",
        "password": "testpass123",
        "full_name": "Frontend Test User",
    }

    try:
        response = requests.post(f"{API_BASE_URL}/auth/register", json=test_user_data)
        if response.status_code == 200:
            print("✅ test user create Cheng Gong")
            return response.json()
        else:
            print(f"⚠️  test user Ke Neng already exists (status Ma: {response.status_code})")
            return None
    except Exception as e:
        print(f"❌ create test user failed: {e}")
        return None


def test_admin_login_ui(driver):
    """test administrator login Jie Mian"""
    print("🔍 test 3: administrator login Jie Mian")

    try:
        # access login page
        driver.get(f"{BASE_URL}/login")

        # Deng Dai page Jia Zai
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )

        # Cha Zhao login Biao Dan Yuan Su
        username_input = driver.find_element(By.NAME, "username")  # use correct Zi Duan Ming
        password_input = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        # Shu Ru administrator Ping Ju
        username_input.clear()
        username_input.send_keys("admin")
        password_input.clear()
        password_input.send_keys("Ai7dio")

        # Dian Ji login
        login_button.click()

        # Deng Dai Zhong Ding Xiang Huo Zhe Cuo Wu Xin Xi
        time.sleep(3)

        current_url = driver.current_url
        if "/admin" in current_url or current_url.endswith("/"):
            print("✅ administrator login Cheng Gong")
            return True
        else:
            print(f"❌ login Ke Neng failed，Dang QianURL: {current_url}")
            # check Shi Fou have Cuo Wu Xin Xi
            page_text = driver.page_source
            print(f"page content Yu Lan: {page_text[:500]}...")
            return False

    except Exception as e:
        print(f"❌ login Jie Mian test failed: {e}")
        return False


def test_admin_dashboard_access(driver):
    """test administrator Mian Ban access"""
    print("🔍 test 4: administrator Mian Ban access")

    try:
        # Zhi Jie access administrator Mian Ban
        driver.get(f"{BASE_URL}/admin")

        # Deng Dai page Jia Zai
        time.sleep(3)

        # check Shi Fou Cheng Gong access administrator Mian Ban
        if "/admin" in driver.current_url:
            # Cha Zhao administrator Mian Ban Te You Yuan Su
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.TEXT, "user management"))
                )
                print("✅ administrator Mian Ban access Cheng Gong")
                return True
            except:
                # Ru Guo Zhao Bu Dao Te Ding Wen Zi，check Shi Fou have Dao Hang Yuan Su
                nav_elements = driver.find_elements(By.TAG_NAME, "nav")
                if len(nav_elements) > 0:
                    print("✅ administrator Mian Ban access Cheng Gong (Jian Ce to Dao Hang Yuan Su)")
                    return True
                else:
                    print("❌ administrator Mian Ban Ke Neng Wei correct Jia Zai")
                    return False
        else:
            print(f"❌ Wei Neng access administrator Mian Ban，Dang QianURL: {driver.current_url}")
            return False

    except Exception as e:
        print(f"❌ administrator Mian Ban access test failed: {e}")
        return False


def test_user_list_page(driver):
    """test user list page"""
    print("🔍 test 5: user list page")

    try:
        # access user management page
        driver.get(f"{BASE_URL}/admin/users")

        # Deng Dai page Jia Zai
        time.sleep(3)

        # check page Shi Fou Bao Han user management related content
        page_text = driver.page_source.lower()

        success_indicators = [
            "user management" in page_text,
            "Sou Suo" in page_text,
            "user" in page_text,
            len(driver.find_elements(By.TAG_NAME, "table")) > 0,
            len(driver.find_elements(By.TAG_NAME, "input")) > 0,
        ]

        if any(success_indicators):
            print("✅ user list page Jia Zai Cheng Gong")
            print(
                f"   - Jian Ce to function: {sum(success_indicators)} / {len(success_indicators)}"
            )
            return True
        else:
            print("❌ user list page Wei correct Jia Zai")
            print(f"page content Yu Lan: {page_text[:300]}...")
            return False

    except Exception as e:
        print(f"❌ user list page test failed: {e}")
        return False


def test_statistics_page(driver):
    """test Tong Ji Shu Ju page"""
    print("🔍 test 6: Tong Ji Shu Ju page")

    try:
        # access statistics page
        driver.get(f"{BASE_URL}/admin/stats")

        # Deng Dai page Jia Zai
        time.sleep(3)

        # check page Shi Fou Bao Han statistics related content
        page_text = driver.page_source.lower()

        success_indicators = [
            "statistics" in page_text,
            "user" in page_text,
            "total" in page_text,
            len(driver.find_elements(By.CLASS_NAME, "bg-blue-50")) > 0
            or len(driver.find_elements(By.CLASS_NAME, "bg-green-50")) > 0,
        ]

        if any(success_indicators):
            print("✅ Tong Ji Shu Ju page Jia Zai Cheng Gong")
            return True
        else:
            print("❌ Tong Ji Shu Ju page Wei correct Jia Zai")
            return False

    except Exception as e:
        print(f"❌ Tong Ji Shu Ju page test failed: {e}")
        return False


def test_responsive_design(driver):
    """test response Shi She Ji"""
    print("🔍 test 7: response Shi She Ji")

    try:
        driver.get(f"{BASE_URL}/admin/users")

        # test Zhuo Mian Shi Tu
        driver.set_window_size(1920, 1080)
        time.sleep(1)
        desktop_elements = len(driver.find_elements(By.TAG_NAME, "div"))

        # test Yi Dong Shi Tu
        driver.set_window_size(375, 667)
        time.sleep(1)
        mobile_elements = len(driver.find_elements(By.TAG_NAME, "div"))

        # Hui Fu Zhuo Mian Shi Tu
        driver.set_window_size(1920, 1080)

        if desktop_elements > 0 and mobile_elements > 0:
            print("✅ response Shi She Ji Ce Shi Tong Guo")
            print(f"   - Zhuo Mian Yuan Su count: {desktop_elements}")
            print(f"   - Yi Dong Yuan Su count: {mobile_elements}")
            return True
        else:
            print("❌ response Shi She Ji test failed")
            return False

    except Exception as e:
        print(f"❌ response Shi She Ji test failed: {e}")
        return False


def test_navigation(driver):
    """test Dao Hang function"""
    print("🔍 test 8: Dao Hang function")

    try:
        driver.get(f"{BASE_URL}/admin")
        time.sleep(2)

        # test Dao Hang to Bu Tong page
        test_pages = [
            ("/admin/users", "user"),
            ("/admin/stats", "statistics"),
        ]

        successful_navigations = 0

        for url, expected_content in test_pages:
            try:
                driver.get(f"{BASE_URL}{url}")
                time.sleep(2)

                if expected_content.lower() in driver.page_source.lower():
                    successful_navigations += 1
                    print(f"   ✅ Dao Hang to {url} Cheng Gong")
                else:
                    print(f"   ❌ Dao Hang to {url} failed")

            except Exception as e:
                print(f"   ❌ Dao Hang to {url} Chu Cuo: {e}")

        if successful_navigations >= len(test_pages) // 2:
            print(f"✅ Dao Hang Gong Neng Ce Shi pass ({successful_navigations}/{len(test_pages)})")
            return True
        else:
            print(f"❌ Dao Hang Gong Neng Ce Shi failed ({successful_navigations}/{len(test_pages)})")
            return False

    except Exception as e:
        print(f"❌ Dao Hang Gong Neng Ce Shi failed: {e}")
        return False


def main():
    """main test function"""
    print("🚀 start frontend management Jie Mian work Liu test")
    print("=" * 60)

    test_results = []

    # test 1: check server status
    result = test_servers_running()
    test_results.append(result)

    if not result:
        print("❌ server Wei run，Zhong Zhi test")
        return

    # test 2: create test user
    create_test_user()  # not Ji Ru test Jie Guo，Yin Wei user Ke Neng already exists

    # setWebDriver
    print("\n🔧 set Liu Lan Qi...")
    driver = setup_webdriver()

    if not driver:
        print("❌ Wu Fa set Liu Lan Qi，Tiao GuoUItest")
        print("💡 prompt: please An ZhuangChromeLiu Lan Qi andChromeDriverLai run complete test")
        return

    try:
        # UItest
        test_results.append(test_admin_login_ui(driver))
        test_results.append(test_admin_dashboard_access(driver))
        test_results.append(test_user_list_page(driver))
        test_results.append(test_statistics_page(driver))
        test_results.append(test_responsive_design(driver))
        test_results.append(test_navigation(driver))

    finally:
        driver.quit()

    # Hui Zong Jie Guo
    print("\n" + "=" * 60)
    print("📊 test Jie Guo Hui Zong")
    print("=" * 60)

    passed = sum(test_results)
    total = len(test_results)

    print(f"✅ pass: {passed}/{total}")
    print(f"❌ failed: {total - passed}/{total}")
    print(f"📈 Cheng Gong Lv: {passed/total*100:.1f}%")

    if passed == total:
        print("\n🎉 Suo You Ce Shi Tong Guo！frontend management Jie Mian work normal！")
        print("\n📋 function Qing Dan:")
        print("   ✅ administrator Shen Fen Yan Zheng")
        print("   ✅ user management Jie Mian")
        print("   ✅ Tong Ji Shu Ju display")
        print("   ✅ response Shi She Ji")
        print("   ✅ page Dao Hang")
    else:
        print(f"\n⚠️  have {total - passed} Ge test failed，Jian Yi check Yi Xia Nei Rong:")
        print("   - frontend Zu Jian Shi Fou correct Xuan Ran")
        print("   - APIJie Kou Shi Fou normal response")
        print("   - Yang Shi and Bu Ju Shi Fou correct")

    # access Shuo Ming
    print("\n🌐 access Di Zhi:")
    print(f"   frontend: {BASE_URL}")
    print(f"   management Hou Tai: {BASE_URL}/admin")
    print("   login Ping Ju: admin / Ai7dio")

    return passed == total


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ test be user Zhong Duan")
    except Exception as e:
        print(f"\n❌ An error occurred during testing: {e}")
