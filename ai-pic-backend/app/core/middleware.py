"""Zhong Jian Jian module

Ti Gong user Ren Zheng, permission Kong Zhi, request log, exception process Deng Zhong Jian Jian
"""

import logging
from datetime import datetime
from typing import Callable

from app.core.database import get_db
from app.core.exceptions import DomainError
from app.core.security import verify_token
from app.models.user import User
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class UserPermissionLevel:
    """user permission Ji Bie Mei Ju"""

    BASIC_AUTH = "basic_auth"  # basic Ren Zheng(only Deng Lu)
    ACTIVE_USER = "active_user"  # Huo Yue user(Ji Huo+Shen Pi)
    ADMIN = "admin"  # administrator permission
    SUPERUSER = "superuser"  # Chao Ji user permission


def get_current_user_basic(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """basic user Ren Zheng - only validationtokenYou Xiao Xing"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="unable to validation Ping Ju",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user_basic),
) -> User:
    """get current Huo Yue user - need through Shen Pi Qie account Ji Huo"""
    # check account Shi Fou lock
    if current_user.is_account_locked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="account lock, Qing Lian Xi administrator or Shao Hou Zai Shi",
        )

    # Jian Cha Yong Hu Shi FouCanDeng Lu
    if not current_user.can_login:
        # specific Cuo Wu Xin Xi
        if not current_user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You Xiang not validation, Qing first validation You Xiang"
            )
        elif not current_user.is_approved:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="account pending administrator Shen Pi, Qing Nai Xin waiting",
            )
        elif not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="account Ting Yong, Qing Lian Xi administrator",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="account status exception, Qing Lian Xi administrator",
            )

    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """get current administrator user"""
    if not current_user.is_admin and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="need administrator permission"
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """get current Chao Ji user"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="need Chao Ji user permission"
        )
    return current_user


def require_permission(permission_level: str) -> Callable:
    """permission Zhuang Shi Qi Gong Chang"""
    permission_functions = {
        UserPermissionLevel.BASIC_AUTH: get_current_user_basic,
        UserPermissionLevel.ACTIVE_USER: get_current_active_user,
        UserPermissionLevel.ADMIN: get_current_admin_user,
        UserPermissionLevel.SUPERUSER: get_current_superuser,
    }

    if permission_level not in permission_functions:
        raise ValueError(f"未知的权限级别: {permission_level}")

    return permission_functions[permission_level]


# Bie Ming function, Fang Bian Shi Yong
def require_basic_auth() -> User:
    """requirement basic Ren Zheng"""
    return Depends(get_current_user_basic)


def require_active_user() -> User:
    """requirement Huo Yue user"""
    return Depends(get_current_active_user)


def require_admin() -> User:
    """requirement administrator permission"""
    return Depends(get_current_admin_user)


def require_superuser() -> User:
    """requirement Chao Ji user permission"""
    return Depends(get_current_superuser)


def record_user_login(user: User, db: Session, success: bool = True):
    """Ji Lu user Deng Lu"""
    if success:
        user.last_login_at = datetime.utcnow()
        user.failed_login_attempts = 0  # successful Deng Lu when Zhong Zhi failed Ci Shu
    else:
        user.failed_login_attempts += 1
        # Chao Guo5Ci failed Chang Shi, lock account1Xiao Shi
        if user.failed_login_attempts >= 5:
            from datetime import timedelta

            user.account_locked_until = datetime.utcnow() + timedelta(hours=1)

    db.commit()
    db.refresh(user)


async def domain_exception_handler(request: Request, exc: DomainError) -> JSONResponse:
    """
    Exception handler for domain exceptions.

    This handler catches all DomainError exceptions raised in the application
    and converts them to structured JSON HTTP responses. It enables clean
    separation between business logic (which raises domain exceptions) and
    HTTP layer (which returns HTTP responses).

    Args:
        request: Incoming HTTP request
        exc: Domain exception that was raised

    Returns:
        JSONResponse with structured error format

    Features:
        - Automatic conversion of domain exceptions to HTTP responses
        - Structured error response format (error, message, context)
        - Logging of all domain errors for monitoring
        - Preserves status codes and error codes from domain exceptions
    """
    # Log the domain error with context
    logger.warning(
        f"Domain error occurred: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "error_message": exc.message,  # Use 'error_message' to avoid conflict with log record 'message'
            "error_context": exc.context,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
        },
    )

    # Convert domain exception to JSON response
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )
