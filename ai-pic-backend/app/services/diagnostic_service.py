"""
AIimage Sheng Cheng Zhen Duan service

Ti Gong complete Zi Ce Ji Zhi, Yong Yu Zhen Duan and Xiu FuAIimage Sheng Cheng Guo Cheng in Ge Zhong Wen Ti
"""

import os
from datetime import datetime
from typing import Any, Dict

import httpx
from app.core.config import settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.virtual_ip import VirtualIP, VirtualIPImage
from app.services.ai_service import ai_service
from app.services.storage.oss_service import oss_service
from app.utils.model_utils import DEFAULT_OPENAI_IMAGE_MODEL


class DiagnosticService:
    """AIimage Sheng Cheng Zhen Duan service"""

    def __init__(self):
        self.logger = get_logger()
        self.test_results = {}
        self.errors = []

    def _log_test_result(
        self, test_name: str, success: bool, details: str = "", error: str = ""
    ):
        """Ji Lu Ce Shi Jie Guo"""
        self.test_results[test_name] = {
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        }

        if success:
            self.logger.info(f"✅ {test_name}: {details}")
        else:
            self.logger.error(f"❌ {test_name}: {error}")
            self.errors.append(f"{test_name}: {error}")

    async def run_full_diagnostic(self) -> Dict[str, Any]:
        """run complete Zhen Duan Ce Shi"""
        self.logger.info("🚀 Kai Shi Yun Xing completeAIimage Sheng Cheng Zhen Duan Ce Shi")
        self.test_results = {}
        self.errors = []

        # 1. environment configuration check
        await self.test_environment_config()

        # 2. database connection Ce Shi
        await self.test_database_connection()

        # 3. OpenAI APICe Shi
        await self.test_openai_api()

        # 4. OSS serviceCe Shi
        await self.test_oss_service()

        # 5. File systemCe Shi
        await self.test_file_system()

        # 6. Duan Dao Duan image Sheng Cheng Ce Shi
        if len(self.errors) == 0:
            await self.test_end_to_end_image_generation()
        else:
            self._log_test_result(
                "end-to-end test", False, error="Tiao Guoend-to-end test, Yin Wei Qian Zhi Tiao Jian Ce Shi failed"
            )

        # 7. Sheng Cheng Zhen Duan Bao Gao
        report = self.generate_diagnostic_report()

        self.logger.info("🏁 Zhen Duan Ce Shi complete")
        return report

    async def test_environment_config(self) -> bool:
        """Ce Shi Huan Jing configuration"""
        self.logger.info("🔍 Ce Shi Huan Jing configuration...")

        required_configs = [
            ("OPENAI_API_KEY", "OpenAI APIkey"),
            ("UPLOAD_DIR", "Shang Chuan Mu Lu"),
        ]

        optional_configs = [
            ("ALIYUN_ACCESS_KEY_ID", "A Li Yun access keyID"),
            ("ALIYUN_ACCESS_KEY_SECRET", "A Li Yun access key"),
            ("ALIYUN_OSS_ENDPOINT", "A Li YunOSSDuan Dian"),
            ("ALIYUN_OSS_BUCKET", "A Li YunOSSCun Chu Tong"),
        ]

        config_status = {}
        missing_required = []

        # check Bi Xu configuration
        for config_name, description in required_configs:
            value = getattr(settings, config_name, None)
            if value:
                config_status[config_name] = f"✅ Yi configuration ({description})"
            else:
                config_status[config_name] = f"❌ Wei configuration ({description})"
                missing_required.append(config_name)

        # check can Xuan configuration
        for config_name, description in optional_configs:
            value = getattr(settings, config_name, None)
            if value:
                config_status[config_name] = f"✅ Yi configuration ({description})"
            else:
                config_status[config_name] = f"⚠️  Wei configuration ({description}) - Ke Xuan"

        # Te Shu check: AIservice configuration
        if hasattr(ai_service, "openai_api_key") and ai_service.openai_api_key:
            config_status["AI_SERVICE_OPENAI"] = "✅ AIserviceOpenAIconfiguration Zheng Chang"
        else:
            config_status["AI_SERVICE_OPENAI"] = "❌ AIserviceOpenAIconfiguration exception"
            missing_required.append("AI_SERVICE_OPENAI")

        success = len(missing_required) == 0
        details = "\n".join([f"  {k}: {v}" for k, v in config_status.items()])
        error = (
            f"missing Bi Xu configuration: {', '.join(missing_required)}" if missing_required else ""
        )

        self._log_test_result("environment configuration check", success, details, error)
        return success

    async def test_database_connection(self) -> bool:
        """Ce Shi database connection"""
        self.logger.info("🔍 Ce Shi database connection...")

        try:
            db = next(get_db())

            # Ce Shi Cha Xun Xu NiIP
            virtual_ips = db.query(VirtualIP).limit(3).all()
            ip_count = len(virtual_ips)

            # Ce Shi Cha Xun image
            images = db.query(VirtualIPImage).limit(5).all()
            image_count = len(images)

            db.close()

            details = f"Xu NiIPShu Liang: {ip_count}, image Shu Liang: {image_count}"
            self._log_test_result("database connection", True, details)
            return True

        except Exception as e:
            self._log_test_result(
                "database connection", False, error=f"Shu Ju Ku Lian Jie failed: {str(e)}"
            )
            return False

    async def test_openai_api(self) -> bool:
        """Ce ShiOpenAI APIconnection"""
        self.logger.info("🔍 Ce ShiOpenAI API...")

        if not hasattr(ai_service, "openai_api_key") or not ai_service.openai_api_key:
            self._log_test_result("OpenAI API", False, error="OpenAI APIkey not configuration")
            return False

        try:
            # Ce Shi Jian Dan text Sheng Cheng request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {ai_service.openai_api_key}",
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
                        f"APIZheng Chang，Shi Yongtokens: {usage.get('total_tokens', 'unknown')}"
                    )
                    self._log_test_result("OpenAI API", True, details)
                    return True
                else:
                    error_msg = (
                        f"APIFan Hui error: {response.status_code} - {response.text[:200]}"
                    )
                    self._log_test_result("OpenAI API", False, error=error_msg)
                    return False

        except Exception as e:
            self._log_test_result("OpenAI API", False, error=f"APIQing Qiu Yi Chang: {str(e)}")
            return False

    async def test_oss_service(self) -> bool:
        """Ce ShiOSS service"""
        self.logger.info("🔍 Ce ShiOSS service...")

        if not oss_service:
            self._log_test_result(
                "OSS service", False, error="OSS servicenot Chu Shi Hua(configuration Ke Neng not complete)"
            )
            return False

        try:
            # create Ce Shi file content
            test_content = b"This is a test file for OSS diagnostic"
            test_filename = "diagnostic_test.txt"

            # Ce Shi Shang Chuan
            upload_result = await oss_service.upload_file_content(
                file_content=test_content,
                filename=test_filename,
                file_type="text",
                prefix="diagnostic-test",
                metadata={"test": "true", "purpose": "diagnostic"},
            )

            if upload_result.get("success"):
                file_url = upload_result.get("file_url")
                object_key = upload_result.get("object_key")

                # Ce Shi delete(Qing Li)
                try:
                    delete_result = oss_service.delete_object(object_key)
                    cleanup_status = (
                        "Qing Li" if delete_result.get("success") else "Qing Li failed"
                    )
                except Exception:
                    cleanup_status = "Qing Li exception"

                details = f"Shang Chuan Cheng Gong，fileURL: {file_url}, {cleanup_status}"
                self._log_test_result("OSS service", True, details)
                return True
            else:
                error_msg = upload_result.get("error", "Shang Chuan failed, Yuan Yin unknown")
                self._log_test_result("OSS service", False, error=error_msg)
                return False

        except Exception as e:
            self._log_test_result("OSS service", False, error=f"OSSCe Shi Yi Chang: {str(e)}")
            return False

    async def test_oss_image_upload(self) -> bool:
        """Shi YongPNGimage Ce ShiOSSShang Chuan(mock Xu NiIPimage path)"""
        self.logger.info("🔍 Ce ShiOSS image upload...")

        if not oss_service:
            self._log_test_result(
                "OSS image upload", False, error="OSS servicenot Chu Shi Hua(configuration Ke Neng not complete)"
            )
            return False

        try:
            import base64

            # a Zui Xiao 1x1 PNG(Bai Se Xiang Su)
            tiny_png_b64 = (
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMA"
                "ASsJTYQAAAAASUVORK5CYII="
            )
            file_content = base64.b64decode(tiny_png_b64)
            filename = "diagnostic_test.png"

            upload_result = await oss_service.upload_file_content(
                file_content=file_content,
                filename=filename,
                file_type="image",
                prefix="diagnostic-test",
                metadata={
                    "test": "true",
                    "purpose": "diagnostic_image",
                    "provider": "diagnostic",
                    "model": "diagnostic-image",
                },
            )

            if upload_result.get("success"):
                file_url = upload_result.get("file_url")
                object_key = upload_result.get("object_key")

                # Ce Shi delete(Qing Li)
                try:
                    delete_result = oss_service.delete_object(object_key)
                    cleanup_status = (
                        "Qing Li" if delete_result.get("success") else "Qing Li failed"
                    )
                except Exception:
                    cleanup_status = "Qing Li exception"

                details = f"Tu Pian Shang Chuan Cheng Gong，fileURL: {file_url}, {cleanup_status}"
                self._log_test_result("OSS image upload", True, details)
                return True
            else:
                error_msg = upload_result.get("error", "Shang Chuan failed, Yuan Yin unknown")
                self._log_test_result("OSS image upload", False, error=error_msg)
                return False

        except Exception as e:
            self._log_test_result(
                "OSS image upload", False, error=f"OSSTu Pian Ce Shi Yi Chang: {str(e)}"
            )
            return False

    async def test_file_system(self) -> bool:
        """Ce ShiFile systemCao Zuo"""
        self.logger.info("🔍 Ce ShiFile system...")

        try:
            # check Shang Chuan Mu Lu
            upload_dir = settings.UPLOAD_DIR
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir, exist_ok=True)
                creation_status = "create"
            else:
                creation_status = "Cun Zai"

            # Ce Shi write permission
            test_file_path = os.path.join(upload_dir, "diagnostic_test.txt")
            test_content = f"Diagnostic test at {datetime.now().isoformat()}"

            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write(test_content)

            # Ce Shi read
            with open(test_file_path, "r", encoding="utf-8") as f:
                read_content = f.read()

            # Qing Li Ce Shi file
            if os.path.exists(test_file_path):
                os.remove(test_file_path)

            # check permission
            can_read = os.access(upload_dir, os.R_OK)
            can_write = os.access(upload_dir, os.W_OK)
            can_execute = os.access(upload_dir, os.X_OK)

            details = f"Mu Lu: {upload_dir} ({creation_status}), Quan Xian: R({can_read}) W({can_write}) X({can_execute})"
            success = (
                can_read and can_write and can_execute and read_content == test_content
            )

            if success:
                self._log_test_result("File system", True, details)
            else:
                self._log_test_result(
                    "File system", False, error=f"Quan Xian Huo Du Xie Ce Shi failed: {details}"
                )

            return success

        except Exception as e:
            self._log_test_result(
                "File system", False, error=f"file Xi Tong Ce Shi Yi Chang: {str(e)}"
            )
            return False

    async def test_end_to_end_image_generation(self) -> bool:
        """Ce Shi Duan Dao Duan image Sheng Cheng"""
        self.logger.info("🔍 Ce Shi Duan Dao Duan image Sheng Cheng...")

        try:
            # get Ce Shi Yong Xu NiIP
            db = next(get_db())
            test_virtual_ip = db.query(VirtualIP).first()

            if not test_virtual_ip:
                db.close()
                self._log_test_result(
                    "end-to-end test", False, error="missing Zhao Dao Ce Shi Yong Xu NiIP"
                )
                return False

            # callAIimage Sheng Cheng service
            result = await ai_service.generate_virtual_ip_image(
                ip_name=test_virtual_ip.name,
                description=test_virtual_ip.description or "Ce Shi Yong Xu NiIP",
                style="realistic",
                category="portrait",
                model=DEFAULT_OPENAI_IMAGE_MODEL,
                additional_prompts=["diagnostic test"],
            )

            if not result:
                db.close()
                self._log_test_result("end-to-end test", False, error="AIimage Sheng Cheng returnNone")
                return False

            # check Jie Guo Wan Zheng Xing
            local_file_path = result.get("local_file_path")
            image_url = result.get("image_url")
            oss_upload = result.get("oss_upload")

            checks = []

            # check local file
            if local_file_path and os.path.exists(local_file_path):
                file_size = os.path.getsize(local_file_path)
                checks.append(f"✅ Ben Di file: {local_file_path} ({file_size} bytes)")
            else:
                checks.append("❌ local file not Cun Zai")

            # checkOSSShang Chuan
            if oss_upload and oss_upload.get("success"):
                checks.append(f"✅ OSSShang Chuan: {oss_upload.get('file_url')}")
            else:
                oss_error = oss_upload.get("error") if oss_upload else "OSSJie Guo Wei Kong"
                checks.append(f"❌ OSSShang Chuan failed: {oss_error}")

            # check returnURL
            if image_url:
                checks.append(f"✅ Fan HuiURL: {image_url}")
            else:
                checks.append("❌ not return imageURL")

            db.close()

            # Zong He determine
            success = all("✅" in check for check in checks)
            details = "\n".join([f"  {check}" for check in checks])

            if success:
                self._log_test_result("end-to-end test", True, details)

                # Qing Li Ce Shi file
                if local_file_path and os.path.exists(local_file_path):
                    try:
                        os.remove(local_file_path)
                        self.logger.info(f"Yi Qing Li Ce Shi file: {local_file_path}")
                    except Exception as e:
                        self.logger.warning(f"Qing Li Ce Shi file failed: {e}")
            else:
                self._log_test_result(
                    "end-to-end test", False, error=f"Bu Fen Jian Cha failed:\n{details}"
                )

            return success

        except Exception as e:
            self._log_test_result(
                "end-to-end test", False, error=f"Duan Dao Duan Ce Shi Yi Chang: {str(e)}"
            )
            return False

    def generate_diagnostic_report(self) -> Dict[str, Any]:
        """Sheng Cheng Zhen Duan Bao Gao"""
        total_tests = len(self.test_results)
        passed_tests = sum(
            1 for result in self.test_results.values() if result["success"]
        )
        failed_tests = total_tests - passed_tests

        summary = {
            "overall_status": "PASS" if failed_tests == 0 else "FAIL",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (
                f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            ),
            "timestamp": datetime.now().isoformat(),
        }

        recommendations = []

        # Ji Yu error Sheng Cheng suggestion
        for error in self.errors:
            if "OpenAI API" in error:
                recommendations.append("🔧 checkOPENAI_API_KEYHuan Jing Bian Liang configuration")
                recommendations.append("🔧 validationOpenAIaccount Yu E andAPIpermission")
            elif "OSS" in error:
                recommendations.append("🔧 check A Li YunOSSrelated Huan Jing Bian Liang configuration")
                recommendations.append("🔧 validation A Li Yun account permission and Cun Chu Tong She Zhi")
            elif "database" in error:
                recommendations.append("🔧 check database connection configuration")
                recommendations.append("🔧 Que Bao database service Zheng Chang run")
            elif "File system" in error:
                recommendations.append("🔧 checkuploadMu Lu permission She Zhi")
                recommendations.append("🔧 Que Bao Ci Pan Kong Jian Chong Zu")

        if failed_tests == 0:
            recommendations.append("🎉 all Ce Shi Tong Guo!AIimage Sheng Cheng feature Ying Gai Zheng Chang Gong Zuo")

        return {
            "summary": summary,
            "test_results": self.test_results,
            "errors": self.errors,
            "recommendations": recommendations,
        }

    async def quick_health_check(self) -> Dict[str, Any]:
        """quick Jian Kang Jian Cha"""
        self.logger.info("⚡ run quick Jian Kang Jian Cha")

        checks = {}

        # APIkey check
        checks["openai_configured"] = bool(getattr(ai_service, "openai_api_key", None))

        # OSS servicecheck
        checks["oss_configured"] = oss_service is not None

        # Shang Chuan Mu Lu check
        upload_dir = settings.UPLOAD_DIR
        checks["upload_dir_exists"] = os.path.exists(upload_dir)
        checks["upload_dir_writable"] = (
            os.access(upload_dir, os.W_OK) if os.path.exists(upload_dir) else False
        )

        # database check
        try:
            db = next(get_db())
            db.query(VirtualIP).first()
            checks["database_accessible"] = True
            db.close()
        except Exception:
            checks["database_accessible"] = False

        overall_health = all(checks.values())

        return {
            "healthy": overall_health,
            "checks": checks,
            "timestamp": datetime.now().isoformat(),
        }


# create Quan Ju Zhen Duan service instance
diagnostic_service = DiagnosticService()
