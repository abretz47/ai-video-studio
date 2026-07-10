"""
migration Zhong Jian Jian

in Ying Yong Qi Dong when check database migration status, and in need when Ti Xing administrator
"""

import logging
from typing import Callable

from app.core.config import settings
from app.core.migrations import migration_manager
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class MigrationCheckMiddleware(BaseHTTPMiddleware):
    """migration check Zhong Jian Jian"""

    def __init__(
        self, app, check_on_startup: bool = True, require_up_to_date: bool = False
    ):
        super().__init__(app)
        self.check_on_startup = check_on_startup
        self.require_up_to_date = require_up_to_date
        self._migration_status_checked = False
        self._migration_status = None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """process request"""

        # in Shou Ci request whenCheck migration status
        if not self._migration_status_checked and self.check_on_startup:
            await self._check_migration_status()

        # Ru Guo requirement database Bi Xu Shi Zui Xin, Qie Bu Shi Zui Xin, then Zu Zhi access
        if (
            self.require_up_to_date
            and self._migration_status
            and not self._migration_status.get("is_up_to_date", True)
        ):

            # Yun Xu access migration relatedAPIDuan Dian
            if request.url.path.startswith(f"{settings.API_V1_STR}/migrations"):
                return await call_next(request)

            # Yun Xu access Jian Kang Jian Cha Duan Dian
            if request.url.path in ["/health", "/", f"{settings.API_V1_STR}/health"]:
                return await call_next(request)

            # return database need escalate error
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "database need escalate",
                    "migration_status": self._migration_status,
                    "migration_endpoint": f"{settings.API_V1_STR}/migrations/status",
                },
            )

        # in response Tou in Tian Jia migration status Xin Xi
        response = await call_next(request)

        if self._migration_status:
            response.headers["X-Migration-Status"] = (
                "up-to-date"
                if self._migration_status.get("is_up_to_date")
                else "needs-upgrade"
            )
            if self._migration_status.get("current_revision"):
                response.headers["X-Migration-Current"] = self._migration_status[
                    "current_revision"
                ]

        return response

    async def _check_migration_status(self):
        """Check migration status"""
        try:
            self._migration_status = migration_manager.check_migration_status()
            self._migration_status_checked = True

            if not self._migration_status.get("database_exists"):
                logger.warning("database not Cun Zai or unable to connection")
            elif not self._migration_status.get("is_up_to_date"):
                pending_count = self._migration_status.get("pending_count", 0)
                logger.warning(f"数据库需要升级，有 {pending_count} 个待应用的迁移")
            else:
                logger.info("database migration status Zheng Chang")

        except Exception as e:
            logger.error(f"检查迁移状态失败: {e}")
            self._migration_status = {
                "error": str(e),
                "database_exists": False,
                "is_up_to_date": False,
            }
            self._migration_status_checked = True


class DatabaseHealthMiddleware(BaseHTTPMiddleware):
    """database Jian Kang Jian Cha Zhong Jian Jian"""

    def __init__(self, app, health_check_interval: int = 300):  # 5minutes check Yi Ci
        super().__init__(app)
        self.health_check_interval = health_check_interval
        self._last_health_check = 0
        self._database_healthy = True

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """process request"""
        import time

        current_time = time.time()

        # Ding Qi Jian Cha database Jian Kang status
        if current_time - self._last_health_check > self.health_check_interval:
            await self._check_database_health()
            self._last_health_check = current_time

        # Ru Guo database not Jian Kang, return503error
        if not self._database_healthy:
            # Yun Xu access Jian Kang Jian Cha Duan Dian
            if request.url.path in [
                "/health",
                "/",
                f"{settings.API_V1_STR}/migrations/health",
            ]:
                return await call_next(request)

            return JSONResponse(
                status_code=503,
                content={
                    "detail": "database connection not allowed Yong",
                    "health_check_endpoint": f"{settings.API_V1_STR}/migrations/health",
                },
            )

        response = await call_next(request)
        response.headers["X-Database-Health"] = (
            "healthy" if self._database_healthy else "unhealthy"
        )

        return response

    async def _check_database_health(self):
        """check database Jian Kang status"""
        try:
            status = migration_manager.check_migration_status()
            self._database_healthy = status.get("database_exists", False)

            if not self._database_healthy:
                logger.warning("database Jian Kang Jian Cha failed")

        except Exception as e:
            logger.error(f"数据库健康检查异常: {e}")
            self._database_healthy = False
