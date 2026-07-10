"""user Guan Li service

Ti Gong user Ji Huo, Shen Pi, character Guan Li Deng core Ye Wu Luo Ji
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.models.user import User, UserAuditLog
from app.schemas.user import UserApprovalRequest, UserStatsResponse
from fastapi import HTTPException
from sqlalchemy import and_, desc, or_
from sqlalchemy.orm import Session


class UserManagementService:
    """user Guan Li service Lei"""

    def __init__(self, db: Session):
        self.db = db

    def get_users_list(
        self,
        page: int = 1,
        size: int = 20,
        status_filter: Optional[str] = None,
        role_filter: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[User], int]:
        """get user list"""
        query = self.db.query(User).filter(User.is_deleted == False)  # noqa: E712

        # status Shai Xuan
        if status_filter == "pending":
            query = query.filter(
                and_(User.is_active == False, User.is_approved == False)
            )
        elif status_filter == "approved":
            query = query.filter(User.is_approved == True)
        elif status_filter == "suspended":
            query = query.filter(User.is_active == False)
        elif status_filter == "locked":
            query = query.filter(User.account_locked_until > datetime.utcnow())

        # character Shai Xuan
        if role_filter == "admin":
            query = query.filter(User.is_admin == True)
        elif role_filter == "superuser":
            query = query.filter(User.is_superuser == True)
        elif role_filter == "user":
            query = query.filter(
                and_(User.is_admin == False, User.is_superuser == False)
            )

        # Sou Suo
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_term),
                    User.email.ilike(search_term),
                    User.full_name.ilike(search_term),
                )
            )

        # get Zong Shu
        total = query.count()

        # Fen Ye
        offset = (page - 1) * size
        users = query.order_by(desc(User.created_at)).offset(offset).limit(size).all()

        return users, total

    def approve_user(
        self,
        user_id: int,
        admin_user: User,
        approval_data: UserApprovalRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> User:
        """Shen Pi user"""
        user = (
            self.db.query(User)
            .filter(User.id == user_id, User.is_deleted == False)  # noqa: E712
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        old_values = {
            "is_approved": user.is_approved,
            "is_active": user.is_active,
            "approved_at": user.approved_at,
            "approved_by_user_id": user.approved_by_user_id,
        }

        if approval_data.action == "approve":
            user.is_approved = True
            user.is_active = True
            user.approved_at = datetime.utcnow()
            user.approved_by_user_id = admin_user.id
            action = "USER_APPROVED"
        elif approval_data.action == "reject":
            user.is_approved = False
            user.is_active = False
            action = "USER_REJECTED"
        else:
            raise HTTPException(status_code=400, detail="Wu Xiao Cao Zuo type")

        new_values = {
            "is_approved": user.is_approved,
            "is_active": user.is_active,
            "approved_at": user.approved_at,
            "approved_by_user_id": user.approved_by_user_id,
            "reason": approval_data.reason,
        }

        # Record audit log
        self._create_audit_log(
            user_id=user_id,
            admin_user_id=admin_user.id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.commit()
        self.db.refresh(user)

        return user

    def update_user_role(
        self,
        user_id: int,
        admin_user: User,
        is_admin: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> User:
        """update user character"""
        user = (
            self.db.query(User)
            .filter(User.id == user_id, User.is_deleted == False)  # noqa: E712
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Fang Zhi Jiang Ji Zi Ji permission
        if user.id == admin_user.id:
            raise HTTPException(status_code=400, detail="cannot Xiu Gai Zi Ji permission")

        old_values = {"is_admin": user.is_admin, "is_superuser": user.is_superuser}

        if is_admin is not None:
            user.is_admin = is_admin
        if is_superuser is not None:
            user.is_superuser = is_superuser

        new_values = {"is_admin": user.is_admin, "is_superuser": user.is_superuser}

        # Record audit log
        self._create_audit_log(
            user_id=user_id,
            admin_user_id=admin_user.id,
            action="ROLE_UPDATED",
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.commit()
        self.db.refresh(user)

        return user

    def suspend_user(
        self,
        user_id: int,
        admin_user: User,
        duration_hours: Optional[int] = None,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> User:
        """Zan Ting user"""
        user = (
            self.db.query(User)
            .filter(User.id == user_id, User.is_deleted == False)  # noqa: E712
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Fang Zhi Zan Ting Zi Ji
        if user.id == admin_user.id:
            raise HTTPException(status_code=400, detail="cannot Zan Ting Zi Ji account")

        old_values = {
            "is_active": user.is_active,
            "account_locked_until": user.account_locked_until,
        }

        user.is_active = False
        if duration_hours:
            user.account_locked_until = datetime.utcnow() + timedelta(
                hours=duration_hours
            )

        new_values = {
            "is_active": user.is_active,
            "account_locked_until": user.account_locked_until,
            "reason": reason,
            "duration_hours": duration_hours,
        }

        # Record audit log
        self._create_audit_log(
            user_id=user_id,
            admin_user_id=admin_user.id,
            action="USER_SUSPENDED",
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.commit()
        self.db.refresh(user)

        return user

    def reactivate_user(
        self,
        user_id: int,
        admin_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> User:
        """retry Ji Huo user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        old_values = {
            "is_active": user.is_active,
            "account_locked_until": user.account_locked_until,
            "failed_login_attempts": user.failed_login_attempts,
        }

        user.is_active = True
        user.account_locked_until = None
        user.failed_login_attempts = 0

        new_values = {
            "is_active": user.is_active,
            "account_locked_until": user.account_locked_until,
            "failed_login_attempts": user.failed_login_attempts,
        }

        # Record audit log
        self._create_audit_log(
            user_id=user_id,
            admin_user_id=admin_user.id,
            action="USER_REACTIVATED",
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.commit()
        self.db.refresh(user)

        return user

    def delete_user(
        self,
        user_id: int,
        admin_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """delete user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Fang Zhi delete Zi Ji
        if user.id == admin_user.id:
            raise HTTPException(status_code=400, detail="cannot delete Zi Ji account")

        # Ji Lu delete before user Xin Xi
        user_info = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

        # Record audit log
        self._create_audit_log(
            user_id=user_id,
            admin_user_id=admin_user.id,
            action="USER_DELETED",
            old_values=user_info,
            new_values=None,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.delete(user)
        self.db.commit()

        return True

    def get_user_stats(self) -> UserStatsResponse:
        """get user Tong Ji Xin Xi"""
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        pending_approval = (
            self.db.query(User)
            .filter(and_(User.is_approved == False, User.is_active == False))
            .count()
        )
        suspended_users = self.db.query(User).filter(User.is_active == False).count()
        admin_users = self.db.query(User).filter(User.is_admin == True).count()

        # Zui Jin7Tian Zhu Ce Yong Hu Shu
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_registrations = (
            self.db.query(User).filter(User.created_at >= seven_days_ago).count()
        )

        return UserStatsResponse(
            total_users=total_users,
            active_users=active_users,
            pending_approval=pending_approval,
            suspended_users=suspended_users,
            admin_users=admin_users,
            recent_registrations=recent_registrations,
        )

    def generate_activation_token(self, user_id: int) -> str:
        """Sheng Cheng user Ji Huo Ling Pai"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        token = str(uuid.uuid4())
        user.activation_token = token
        user.activation_token_expires = datetime.utcnow() + timedelta(hours=24)

        self.db.commit()

        return token

    def verify_activation_token(self, token: str) -> Optional[User]:
        """validation Ji Huo Ling Pai"""
        user = (
            self.db.query(User)
            .filter(
                and_(
                    User.activation_token == token,
                    User.activation_token_expires > datetime.utcnow(),
                )
            )
            .first()
        )

        if user:
            user.email_verified = True
            user.activation_token = None
            user.activation_token_expires = None
            self.db.commit()
            self.db.refresh(user)

        return user

    def reset_failed_login_attempts(self, user_id: int) -> User:
        """Zhong Zhi failed Deng Lu Ci Shu"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.failed_login_attempts = 0
            user.account_locked_until = None
            self.db.commit()
            self.db.refresh(user)
        return user

    def increment_failed_login_attempts(self, user_id: int) -> User:
        """increase failed Deng Lu Ci Shu"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.failed_login_attempts += 1
            # Chao Guo5Ci failed Chang Shi, lock account1Xiao Shi
            if user.failed_login_attempts >= 5:
                user.account_locked_until = datetime.utcnow() + timedelta(hours=1)
            self.db.commit()
            self.db.refresh(user)
        return user

    def _create_audit_log(
        self,
        user_id: int,
        admin_user_id: Optional[int],
        action: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserAuditLog:
        """create Shen Ji log"""
        audit_log = UserAuditLog(
            user_id=user_id,
            admin_user_id=admin_user_id,
            action=action,
            old_values=json.dumps(old_values, default=str) if old_values else None,
            new_values=json.dumps(new_values, default=str) if new_values else None,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.add(audit_log)
        self.db.flush()  # Que BaoIDFen Pei Dan not submit Shi Wu

        return audit_log

    def get_user_audit_logs(
        self, user_id: int, page: int = 1, size: int = 20
    ) -> Tuple[List[UserAuditLog], int]:
        """get user Shen Ji log"""
        query = self.db.query(UserAuditLog).filter(UserAuditLog.user_id == user_id)
        total = query.count()

        offset = (page - 1) * size
        logs = (
            query.order_by(desc(UserAuditLog.created_at))
            .offset(offset)
            .limit(size)
            .all()
        )

        return logs, total
