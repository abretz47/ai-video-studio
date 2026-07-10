#!/usr/bin/env python3
"""
Simplified AI image generation diagnostic script

Tests core features directly without depending on the full FastAPI app
"""

import asyncio
import base64
import json
import os
from datetime import datetime

import httpx

# Use the same config loading mechanism as FastAPI
try:
    from pydantic_settings import BaseSettings

    class DiagnosticSettings(BaseSettings):
        OPENAI_API_KEY: str = None
        UPLOAD_DIR: str = "./uploads"
        ALIYUN_ACCESS_KEY_ID: str = None
        ALIYUN_ACCESS_KEY_SECRET: str = None
        ALIYUN_OSS_ENDPOINT: str = None
        ALIYUN_OSS_BUCKET: str = None

        class Config:
            env_file = ".env"
            case_sensitive = True
            extra = "ignore"  # Ignore extra environment variables

    config = DiagnosticSettings()
    print("✅ Loaded .env using the FastAPI config mechanism")

except ImportError:
    print("⚠️  pydantic_settings is not installed, using environment variables")
    print("   Install command: pip install pydantic-settings")
    config = None


class SimpleDiagnostic:
    """Simplified diagnostic tool"""

    def __init__(self):
        self.results = {}
        self.errors = []

        if config:
            # Use pydantic config
            self.openai_api_key = config.OPENAI_API_KEY
            self.upload_dir = config.UPLOAD_DIR
            self.oss_access_key = config.ALIYUN_ACCESS_KEY_ID
            self.oss_secret_key = config.ALIYUN_ACCESS_KEY_SECRET
            self.oss_endpoint = config.ALIYUN_OSS_ENDPOINT
            self.oss_bucket = config.ALIYUN_OSS_BUCKET
        else:
            # Fall back to environment variables
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            self.upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
            self.oss_access_key = os.getenv("ALIYUN_ACCESS_KEY_ID")
            self.oss_secret_key = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
            self.oss_endpoint = os.getenv("ALIYUN_OSS_ENDPOINT")
            self.oss_bucket = os.getenv("ALIYUN_OSS_BUCKET")

    def log_result(
        self, test_name: str, success: bool, details: str = "", error: str = ""
    ):
        """Record test result"""
        self.results[test_name] = {
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        }

        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        if error:
            print(f"    Error: {error}")
            self.errors.append(f"{test_name}: {error}")

    async def test_environment_config(self):
        """Test environment config"""
        print("\n🔍 Checking environment config...")

        configs = {
            "OPENAI_API_KEY": self.openai_api_key,
            "UPLOAD_DIR": self.upload_dir,
            "ALIYUN_ACCESS_KEY_ID": self.oss_access_key,
            "ALIYUN_ACCESS_KEY_SECRET": self.oss_secret_key,
            "ALIYUN_OSS_ENDPOINT": self.oss_endpoint,
            "ALIYUN_OSS_BUCKET": self.oss_bucket,
        }

        configured = []
        missing = []

        for name, value in configs.items():
            if value:
                configured.append(name)
            else:
                missing.append(name)

        details = f"Configured: {len(configured)}, Missing: {len(missing)}"
        if missing:
            details += f" (missing: {', '.join(missing)})"

        success = self.openai_api_key is not None  # At least OpenAI config is required
        error = "Missing OPENAI_API_KEY" if not success else ""

        self.log_result("Environment config check", success, details, error)
        return success

    async def test_openai_api(self):
        """Test OpenAI API"""
        print("\n🔍 Test OpenAI API...")

        if not self.openai_api_key:
            self.log_result("OpenAI API", False, error="API key not configured")
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": "Hello"}],
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    usage = result.get("usage", {})
                    details = (
                        f"API OK, tokens used: {usage.get('total_tokens', 'unknown')}"
                    )
                    self.log_result("OpenAI API", True, details)
                    return True
                else:
                    error = (
                        f"API returned error: {response.status_code} - {response.text[:200]}"
                    )
                    self.log_result("OpenAI API", False, error=error)
                    return False

        except Exception as e:
            self.log_result("OpenAI API", False, error=f"Connection error: {str(e)}")
            return False

    async def test_file_system(self):
        """Test file system"""
        print("\n🔍 Test file system...")

        try:
            # Create upload directory
            os.makedirs(self.upload_dir, exist_ok=True)

            # Test write permission
            test_file = os.path.join(self.upload_dir, "test.txt")
            test_content = f"Test at {datetime.now().isoformat()}"

            with open(test_file, "w") as f:
                f.write(test_content)

            # Test read
            with open(test_file, "r") as f:
                read_content = f.read()

            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)

            success = read_content == test_content
            details = (
                f"Directory: {self.upload_dir}, read/write test: {'passed' if success else 'failed'}"
            )

            self.log_result("File system", success, details)
            return success

        except Exception as e:
            self.log_result("File system", False, error=str(e))
            return False

    async def test_image_generation(self):
        """Test image generation"""
        print("\n🔍 Test image generation...")

        if not self.openai_api_key:
            self.log_result("Image generation", False, error="OpenAI API key required")
            return False

        try:
            prompt = "A simple test image"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "dall-e-3",
                        "prompt": prompt,
                        "n": 1,
                        "size": "1024x1024",
                        "quality": "hd",
                        "style": "natural",
                        "response_format": "b64_json",
                    },
                    timeout=60.0,
                )

                if response.status_code == 200:
                    result = response.json()

                    if "b64_json" in result["data"][0]:
                        base64_data = result["data"][0]["b64_json"]

                        # Save image
                        import uuid

                        filename = f"test_{uuid.uuid4().hex}.png"
                        file_path = os.path.join(self.upload_dir, filename)

                        image_bytes = base64.b64decode(base64_data)

                        with open(file_path, "wb") as f:
                            f.write(image_bytes)

                        file_size = os.path.getsize(file_path)
                        details = (
                            f"Image generated successfully, file: {filename}, size: {file_size} bytes"
                        )

                        # Clean up test file
                        try:
                            os.remove(file_path)
                        except:
                            pass

                        self.log_result("Image generation", True, details)
                        return True
                    else:
                        self.log_result("Image generation", False, error="No base64 data received")
                        return False
                else:
                    error = (
                        f"API returned error: {response.status_code} - {response.text[:200]}"
                    )
                    self.log_result("Image generation", False, error=error)
                    return False

        except Exception as e:
            self.log_result("Image generation", False, error=str(e))
            return False

    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting AI image generation diagnostic tests")
        print("=" * 50)

        tests = [
            ("Environment config", self.test_environment_config()),
            ("File system", self.test_file_system()),
            ("OpenAI API", self.test_openai_api()),
            ("Image generation", self.test_image_generation()),
        ]

        for test_name, test_coro in tests:
            try:
                await test_coro
            except Exception as e:
                self.log_result(test_name, False, error=f"Test exception: {str(e)}")

        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 50)
        print("📊 Diagnostic results summary")
        print("=" * 50)

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"Overall status: {'✅ PASS' if failed_tests == 0 else '❌ FAIL'}")
        print(f"Total tests: {total_tests}")
        print(f"Passed tests: {passed_tests}")
        print(f"Failed tests: {failed_tests}")
        print(f"Success rate: {success_rate:.1f}%")

        if self.errors:
            print("\n❌ Issues found:")
            for error in self.errors:
                print(f"  • {error}")

            print("\n🔧 Fix suggestions:")
            if any("OPENAI_API_KEY" in error for error in self.errors):
                print("  • Configure the OPENAI_API_KEY environment variable")
                print("  • Verify OpenAI account balance and API permissions")

            if any("File system" in error for error in self.errors):
                print("  • Check uploads directory permissions")
                print("  • Ensure sufficient disk space")
        else:
            print("\n🎉 All tests passed! AI image generation should work normally")

        # Save report
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "timestamp": datetime.now().isoformat(),
            },
            "results": self.results,
            "errors": self.errors,
        }

        with open("simple_diagnostic_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print("\n💾 Detailed report saved to: simple_diagnostic_report.json")

        return failed_tests == 0


async def main():
    """Main function"""
    diagnostic = SimpleDiagnostic()
    success = await diagnostic.run_all_tests()

    if success:
        print("\n🎉 All tests passed!")
        exit(0)
    else:
        print("\n❌ Some tests failed, please review the report above")
        exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        exit(130)
    except Exception as e:
        print(f"\n💥 Test exception: {e}")
        exit(1)
