"""
Diagnostic API endpoints

Provides diagnostic and testing capabilities for the AI image generation system
"""

from typing import Any, Dict

from app.core.middleware import get_current_active_user
from app.models.user import User
from app.services.diagnostic_service import diagnostic_service
from fastapi import APIRouter, Depends, Header, HTTPException

router = APIRouter()


@router.get("/health")
async def quick_health_check():
    """Quick health check"""
    try:
        result = await diagnostic_service.quick_health_check()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.post("/full")
async def run_full_diagnostic(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Run the full diagnostic suite (administrator privileges required)"""
    try:
        result = await diagnostic_service.run_full_diagnostic()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full diagnostic run failed: {str(e)}")


@router.post("/openai")
async def test_openai_api(
    authorization: str | None = Header(None, alias="Authorization"),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Test OpenAI API connection"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        success = await diagnostic_service.test_openai_api()
        return {
            "success": success,
            "test_result": diagnostic_service.test_results.get("OpenAI API", {}),
        }
    except Exception as e:
        return {"success": False, "error": f"OpenAI API test failed: {str(e)}"}


@router.post("/oss")
async def test_oss_service(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Test OSS service"""
    try:
        success = await diagnostic_service.test_oss_service()
        return {
            "success": success,
            "test_result": diagnostic_service.test_results.get("OSS service", {}),
        }
    except Exception as e:
        return {"success": False, "error": f"OSS service test failed: {str(e)}"}


@router.post("/oss-image")
async def test_oss_image_upload(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Test OSS image upload (using a 1x1 PNG to simulate the virtual IP image upload path)"""
    try:
        success = await diagnostic_service.test_oss_image_upload()
        return {
            "success": success,
            "test_result": diagnostic_service.test_results.get("OSS image upload", {}),
        }
    except Exception as e:
        return {"success": False, "error": f"OSS image upload test failed: {str(e)}"}


@router.post("/database")
async def test_database_connection(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Test database connection"""
    try:
        success = await diagnostic_service.test_database_connection()
        return {
            "success": success,
            "test_result": diagnostic_service.test_results.get("Database connection", {}),
        }
    except Exception as e:
        return {"success": False, "error": f"Database test failed: {str(e)}"}


@router.post("/filesystem")
async def test_file_system(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Test file system"""
    try:
        success = await diagnostic_service.test_file_system()
        return {
            "success": success,
            "test_result": diagnostic_service.test_results.get("File system", {}),
        }
    except Exception as e:
        return {"success": False, "error": f"File system test failed: {str(e)}"}


@router.post("/end-to-end")
async def test_end_to_end_generation(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Test end-to-end image generation"""
    try:
        success = await diagnostic_service.test_end_to_end_image_generation()
        return {
            "success": success,
            "test_result": diagnostic_service.test_results.get("End-to-end test", {}),
        }
    except Exception as e:
        return {"success": False, "error": f"End-to-end test failed: {str(e)}"}
