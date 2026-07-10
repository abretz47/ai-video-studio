"""
Zhen DuanAPIendpoint test

test Zhen Duan relatedAPIendpoint function
"""

from unittest.mock import patch

import pytest


@pytest.mark.api
@pytest.mark.diagnostic
class TestDiagnosticEndpoints:
    """Zhen DuanAPIendpoint test Lei"""

    def test_health_check_endpoint(self, client):
        """test Kuai Su Jian Kang Jian Cha endpoint"""
        response = client.get("/api/v1/diagnostic/health")

        assert response.status_code == 200
        data = response.json()

        assert "healthy" in data
        assert "checks" in data
        assert "timestamp" in data

    def test_openai_test_endpoint_requires_auth(self, client):
        """testOpenAItest endpoint Xu Yao Ren Zheng"""
        response = client.post("/api/v1/diagnostic/openai")

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_openai_test_endpoint_with_auth(self, client, auth_headers):
        """test Dai Ren ZhengOpenAItest endpoint"""
        with patch(
            "app.services.diagnostic_service.diagnostic_service.test_openai_api"
        ) as mock_test:
            mock_test.return_value = True
            mock_result = {
                "success": True,
                "details": "APInormal，usetokens: 10",
                "error": "",
                "timestamp": "2023-01-01T00:00:00",
            }

            # Mock global diagnostic_service.test_results used by the endpoint.
            with patch(
                "app.services.diagnostic_service.diagnostic_service.test_results",
                new={"OpenAI API": mock_result},
            ):
                response = client.post("/api/v1/diagnostic/openai", headers=auth_headers)

        if auth_headers:  # Zhi You in have You Xiao Ren Zheng Tou Shi Cai test
            assert response.status_code == 200
            data = response.json()

            assert "success" in data
            assert "test_result" in data

    def test_oss_test_endpoint_with_auth(self, client, auth_headers):
        """testOSSservice test endpoint"""
        with patch(
            "app.services.diagnostic_service.diagnostic_service.test_oss_service"
        ) as mock_test:
            mock_test.return_value = True

            response = client.post("/api/v1/diagnostic/oss", headers=auth_headers)

        if auth_headers:
            assert response.status_code == 200
            data = response.json()

            assert "success" in data
            assert "test_result" in data

    def test_database_test_endpoint_with_auth(self, client, auth_headers):
        """test database connection test endpoint"""
        response = client.post("/api/v1/diagnostic/database", headers=auth_headers)

        if auth_headers:
            assert response.status_code == 200
            data = response.json()

            assert "success" in data
            assert "test_result" in data

    def test_filesystem_test_endpoint_with_auth(self, client, auth_headers):
        """test Wen Jian Xi Tong test endpoint"""
        response = client.post("/api/v1/diagnostic/filesystem", headers=auth_headers)

        if auth_headers:
            assert response.status_code == 200
            data = response.json()

            assert "success" in data
            assert "test_result" in data

    def test_end_to_end_test_endpoint_with_auth(self, client, auth_headers):
        """test Duan Dao Duan test endpoint"""
        with patch(
            "app.services.diagnostic_service.diagnostic_service.test_end_to_end_image_generation"
        ) as mock_test:
            mock_test.return_value = True

            response = client.post(
                "/api/v1/diagnostic/end-to-end", headers=auth_headers
            )

        if auth_headers:
            assert response.status_code == 200
            data = response.json()

            assert "success" in data
            assert "test_result" in data

    def test_full_diagnostic_endpoint_with_auth(self, client, auth_headers):
        """test complete Zhen Duan endpoint"""
        with patch(
            "app.services.diagnostic_service.diagnostic_service.run_full_diagnostic"
        ) as mock_diagnostic:
            mock_diagnostic.return_value = {
                "summary": {
                    "overall_status": "PASS",
                    "total_tests": 5,
                    "passed_tests": 5,
                    "failed_tests": 0,
                    "success_rate": "100.0%",
                    "timestamp": "2023-01-01T00:00:00",
                },
                "test_results": {},
                "errors": [],
                "recommendations": ["🎉 Suo You Ce Shi Tong Guo！AIimage generate function Ying Gai normal work"],
            }

            response = client.post("/api/v1/diagnostic/full", headers=auth_headers)

        if auth_headers:
            assert response.status_code == 200
            data = response.json()

            assert "summary" in data
            assert "test_results" in data
            assert "errors" in data
            assert "recommendations" in data


@pytest.mark.api
@pytest.mark.diagnostic
@pytest.mark.integration
class TestDiagnosticEndpointsIntegration:
    """Zhen DuanAPIendpoint integration test"""

    @pytest.mark.asyncio
    async def test_health_check_endpoint_real(self, client):
        """test Zhen Shi Jian Kang Jian Cha endpoint"""
        response = client.get("/api/v1/diagnostic/health")

        assert response.status_code == 200
        data = response.json()

        # validate return Shu Ju Jie Gou
        assert isinstance(data["healthy"], bool)
        assert isinstance(data["checks"], dict)

        # validate Bi Yao check Xiang
        expected_checks = [
            "openai_configured",
            "oss_configured",
            "upload_dir_exists",
            "upload_dir_writable",
            "database_accessible",
        ]

        for check in expected_checks:
            assert check in data["checks"]
            assert isinstance(data["checks"][check], bool)

    def test_error_handling(self, client, auth_headers):
        """test Cuo Wu Chu Li"""
        with patch(
            "app.services.diagnostic_service.diagnostic_service.test_openai_api"
        ) as mock_test:
            # MockPao Chu exception
            mock_test.side_effect = Exception("test exception")

            response = client.post("/api/v1/diagnostic/openai", headers=auth_headers)

        if auth_headers:
            assert response.status_code == 200  # Ying Gai return200DansuccessforFalse
            data = response.json()

            assert data["success"] is False
            assert "error" in data
            assert "test exception" in data["error"]
