import logging
import os
import socket
import uuid
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

import colorlog
import pytz
import requests
from app.core.json_logging import JsonlLogHandler
from app.core.log_context import get_log_context, reset_log_context, set_log_context
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestFormatter(logging.Formatter):
    """Zi Ding Yi log Ge Shi Hua Qi, support request Zhui Zong"""

    def formatTime(self, record, datefmt=None):
        """Ge Shi Hua time as Beijing time"""
        bj_time = pytz.timezone("Asia/Shanghai")
        ct = datetime.fromtimestamp(record.created, bj_time)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            try:
                s = ct.isoformat(timespec="milliseconds")
            except TypeError:
                s = ct.isoformat()
        return s

    def format(self, record):
        """Tian Jia request context Xin Xi to log Ji Lu"""
        for key, value in get_log_context().items():
            setattr(record, key, value)
        return super().format(record)


class FeishuLogHandler(logging.Handler):
    """Fei ShuWebhooklog Chu Li Qi, Yong Yu error Tong Zhi"""

    def __init__(self, webhook_url: str):
        super().__init__(level=logging.ERROR)
        self.webhook_url = webhook_url

    def emit(self, record):
        """Fa Song error log to Fei Shu"""
        log_entry = self.format(record)
        payload = {
            "msg_type": "text",
            "content": {"text": f"AIvideo Gong Zuo Shi Hou Duan Chu Cuo！\n{log_entry}\n"},
        }
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # avoid Xun Huan log, directlyprinterror
            print(f"Failed to send log to Feishu: {e}")


class ColoredRequestFormatter(RequestFormatter, colorlog.ColoredFormatter):
    """Cai Se log Ge Shi Hua Qi"""

    def __init__(self, fmt, **kwargs):
        super().__init__(fmt, **kwargs)


class LoggingMiddleware(BaseHTTPMiddleware):
    """FastAPIlog Zhong Jian Jian"""

    async def dispatch(self, request: Request, call_next):
        request_id = (
            request.headers.get("X-Client-Request-ID")
            or request.headers.get("X-Request-ID")
            or uuid.uuid4().hex
        )
        run_id = request.headers.get("X-Harness-Run-ID", "no-run-id")
        client_ip = self._get_client_ip(request)
        set_log_context(
            request_id=request_id,
            run_id=run_id,
            url=str(request.url),
            route=request.url.path,
            client_ip=client_ip,
            status="started",
            latency_ms="0",
        )

        logger = logging.getLogger("ai-video-studio")
        body_bytes = b""
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                body_bytes = await request.body()
        except Exception as e:
            logger.warning(f"Failed to read request body for logging: {e}")

        await self._log_request_with_body(request, logger, body_bytes)

        async def receive() -> dict:
            return {"type": "http.request", "body": body_bytes, "more_body": False}

        request = Request(request.scope, receive)
        start_time = datetime.now()
        try:
            response = await call_next(request)
            process_time = (datetime.now() - start_time).total_seconds()
            await self._log_response(response, logger, process_time)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Harness-Run-ID"] = run_id
            return response
        finally:
            reset_log_context()

    def _get_client_ip(self, request: Request) -> str:
        """get client Zhen ShiIP"""
        # Chang Shi Cong Dai Li Tou get Zhen ShiIP
        if "X-Forwarded-For" in request.headers:
            return request.headers["X-Forwarded-For"].split(",")[0].strip()
        elif "X-Real-IP" in request.headers:
            return request.headers["X-Real-IP"]
        else:
            return request.client.host if request.client else "unknown"

    async def _log_request_with_body(
        self, request: Request, logger: logging.Logger, body: bytes
    ):
        """Ji Lu request Xin Xi(Shi Yong readbody, avoid Chong Fu read)"""
        method = request.method
        url = str(request.url)
        logger.info(f"Request started: {method} {url}")
        if method in ["POST", "PUT", "PATCH"]:
            try:
                content_type = request.headers.get("content-type", "")
                if "multipart/form-data" in content_type:
                    logger.info("Request body: <multipart form data>")
                elif "application/json" in content_type and body:
                    payload = body.decode("utf-8", errors="ignore")
                    if len(payload) > 1000:
                        payload = payload[:1000] + "..."
                    logger.info("Request body: %s", payload)
                elif "application/x-www-form-urlencoded" in content_type:
                    logger.info("Request body: <form data>")
                else:
                    logger.info(f"Request body: <{content_type}>")
            except Exception as e:
                logger.error(f"Failed to log request body: {e}")

    async def _log_response(
        self, response: Response, logger: logging.Logger, process_time: float
    ):
        """Ji Lu response Xin Xi"""
        status_code = response.status_code

        # Gen Ju status Ma Xuan Ze log Ji Bie
        if status_code >= 500:
            log_level = logging.ERROR
        elif status_code >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO

        set_log_context(status=str(status_code), latency_ms=int(process_time * 1000))
        logger.log(
            log_level,
            "Request completed: %s in %.3fs",
            status_code,
            process_time,
            extra={"status": status_code, "latency_ms": int(process_time * 1000)},
        )


def setup_logging(
    app_name: str = "ai-video-studio",
    log_level: str = "INFO",
    log_dir: str = "logs",
    enable_file_logging: bool = True,
    enable_console_logging: bool = True,
    enable_jsonl_logging: bool = True,
    feishu_webhook_url: Optional[str] = None,
    jsonl_log_path: str = "logs/ai-video-studio.jsonl",
    backup_count: int = 7,
) -> logging.Logger:
    """
 She Zhi Ying Yong log configuration

    Args:
 app_name: Ying Yong name
 log_level: log Ji Bie
 log_dir: log Mu Lu
 enable_file_logging: Shi Fou Qi Yong file log
 enable_console_logging: Shi Fou Qi Yong Kong Zhi Tai log
 enable_jsonl_logging: Shi Fou Qi Yong JSONL log
 feishu_webhook_url: Fei ShuWebhook URL(can Xuan)
 jsonl_log_path: JSONL log file path
 backup_count: log backup Shu Liang

    Returns:
 configuration Haologgerinstance
    """
    # createlogger
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Qing Chu existing Chu Li Qi
    logger.handlers.clear()

    # get Zhu Ji Ming
    host_name = socket.gethostname()

    # log format
    log_format = (
        "%(asctime)s [%(levelname)s] ai-video-studio.com/ai-video-studio "
        + host_name
        + " %(client_ip)s %(route)s %(request_id)s %(run_id)s %(funcName)s %(process)d %(message)s"
    )
    formatter = RequestFormatter(log_format)

    # Cai Se Kong Zhi Tai log format
    color_log_format = (
        "%(log_color)s%(asctime)s [%(levelname)s] ai-video-studio.com/ai-video-studio "
        + host_name
        + " %(client_ip)s %(route)s %(request_id)s %(run_id)s %(funcName)s %(process)d %(message)s"
    )
    color_formatter = ColoredRequestFormatter(
        color_log_format,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    # file log Chu Li Qi
    if enable_file_logging:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(log_dir, f"{app_name}.log")
        file_handler = TimedRotatingFileHandler(
            log_file, when="midnight", backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Kong Zhi Tai log Chu Li Qi
    if enable_console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(color_formatter)
        logger.addHandler(console_handler)

    if enable_jsonl_logging:
        logger.addHandler(JsonlLogHandler(jsonl_log_path))

    # Fei Shu log Chu Li Qi(only error Ji Bie)
    if feishu_webhook_url:
        feishu_handler = FeishuLogHandler(feishu_webhook_url)
        feishu_handler.setFormatter(formatter)
        logger.addHandler(feishu_handler)
        logger.info("Feishu error notification enabled")
    else:
        logger.info("Feishu error notification disabled")

    # Jin Zhi log Chuan Bo to Genlogger
    logger.propagate = False

    logger.info(f"Logging initialized for {app_name}")
    return logger


def get_logger(name: str = "ai-video-studio") -> logging.Logger:
    """get Ying Yongloggerinstance"""
    return logging.getLogger(name)
