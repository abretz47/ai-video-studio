"""Administrator API endpoints

Provides administrator features such as user and system management
"""

import math
from typing import List, Optional

from app.core.database import get_db
from app.core.middleware import get_current_active_user
from app.models.user import User
from app.schemas.user import (
    UserAdminResponse,
    UserAdminUpdate,
    UserApprovalRequest,
    UserAuditLogResponse,
    UserListResponse,
    UserStatsResponse,
)
from app.services.user_management_service import UserManagementService
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

router = APIRouter()


def _not_deleted(query, model):
    return query.filter(model.is_deleted.is_(False))


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get the current administrator user"""
    if not current_user.is_admin and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Administrator privileges required"
        )
    return current_user


def get_client_info(request: Request) -> tuple:
    """Get client information"""
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


@router.get("/users", response_model=UserListResponse)
def list_users(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(
        None, description="Status filter: pending, approved, suspended, locked"
    ),
    role_filter: Optional[str] = Query(
        None, description="Role filter: admin, superuser, user"
    ),
    search: Optional[str] = Query(None, description="Search by username, email, or name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get user list"""
    service = UserManagementService(db)
    users, total = service.get_users_list(
        page=page,
        size=size,
        status_filter=status_filter,
        role_filter=role_filter,
        search=search,
    )

    pages = math.ceil(total / size)

    return UserListResponse(users=users, total=total, page=page, size=size, pages=pages)


@router.get("/users/{user_id}", response_model=UserAdminResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get user details"""
    user = _not_deleted(db.query(User), User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")
    return user


@router.put("/users/{user_id}/approval", response_model=UserAdminResponse)
def approve_or_reject_user(
    user_id: int,
    approval_data: UserApprovalRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Approve or reject user"""
    service = UserManagementService(db)
    ip_address, user_agent = get_client_info(request)

    user = service.approve_user(
        user_id=user_id,
        admin_user=current_user,
        approval_data=approval_data,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return user


@router.put("/users/{user_id}/role", response_model=UserAdminResponse)
def update_user_role(
    user_id: int,
    is_admin: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Update user role"""
    # Only superusers can grant administrator privileges
    if is_superuser is not None and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can grant superuser privileges",
        )

    service = UserManagementService(db)
    ip_address, user_agent = get_client_info(request)

    user = service.update_user_role(
        user_id=user_id,
        admin_user=current_user,
        is_admin=is_admin,
        is_superuser=is_superuser,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return user


@router.put("/users/{user_id}/suspend", response_model=UserAdminResponse)
def suspend_user(
    user_id: int,
    duration_hours: Optional[int] = Query(
        None, description="Suspension duration (hours); permanent if not set"
    ),
    reason: Optional[str] = Query(None, description="Suspension reason"),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Suspend user"""
    service = UserManagementService(db)
    ip_address, user_agent = get_client_info(request)

    user = service.suspend_user(
        user_id=user_id,
        admin_user=current_user,
        duration_hours=duration_hours,
        reason=reason,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return user


@router.put("/users/{user_id}/reactivate", response_model=UserAdminResponse)
def reactivate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Reactivate user"""
    service = UserManagementService(db)
    ip_address, user_agent = get_client_info(request)

    user = service.reactivate_user(
        user_id=user_id,
        admin_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Delete user"""
    # Only superusers can delete users
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can delete users"
        )

    service = UserManagementService(db)
    ip_address, user_agent = get_client_info(request)

    success = service.delete_user(
        user_id=user_id,
        admin_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return {"message": "User deleted", "success": success}


@router.get("/users/{user_id}/audit-logs", response_model=List[UserAuditLogResponse])
def get_user_audit_logs(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get user audit logs"""
    service = UserManagementService(db)
    logs, total = service.get_user_audit_logs(user_id, page, size)
    return logs


@router.get("/stats", response_model=UserStatsResponse)
def get_user_stats(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)
):
    """Get user statistics"""
    service = UserManagementService(db)
    return service.get_user_stats()


@router.post("/users/{user_id}/reset-login-attempts", response_model=UserAdminResponse)
def reset_user_login_attempts(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Reset failed login attempts for user"""
    service = UserManagementService(db)
    user = service.reset_failed_login_attempts(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")
    return user


@router.post("/users/{user_id}/generate-activation-token")
def generate_user_activation_token(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Generate user activation token"""
    service = UserManagementService(db)
    token = service.generate_activation_token(user_id)
    return {"activation_token": token, "message": "Activation token generated"}


@router.put("/users/{user_id}", response_model=UserAdminResponse)
def update_user_admin(
    user_id: int,
    user_update: UserAdminUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Administrator updates user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")

    # Record old values
    old_values = {}
    new_values = {}

    # Update fields
    update_fields = user_update.dict(exclude_unset=True)
    for field, value in update_fields.items():
        if hasattr(user, field):
            old_values[field] = getattr(user, field)
            setattr(user, field, value)
            new_values[field] = value

    # Record audit log
    if old_values:
        service = UserManagementService(db)
        ip_address, user_agent = get_client_info(request)
        service._create_audit_log(
            user_id=user_id,
            admin_user_id=current_user.id,
            action="USER_UPDATED",
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    db.commit()
    db.refresh(user)

    return user
