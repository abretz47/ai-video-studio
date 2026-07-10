from app.core.database import Base
from app.models.base import SoftDeleteBusinessMixin
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime


class User(SoftDeleteBusinessMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ux_users_email_is_deleted", "email", "is_deleted", unique=True),
        Index("ux_users_username_is_deleted", "username", "is_deleted", unique=True),
    )

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), index=True, nullable=False)
    email = Column(String(255), index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)

    # basic Zhuang Tai Zi Duan
    is_active = Column(Boolean, default=False, comment="account Shi Fou Ji Huo(default Wei Ji Huo)")
    is_superuser = Column(Boolean, default=False, comment="Shi Fou as Chao Ji user")
    is_admin = Column(Boolean, default=False, comment="Shi Fou as administrator")

    # user Shen Pi related
    is_approved = Column(Boolean, default=False, comment="Shi Fou Shen Pi through")
    approved_at = Column(DateTime(timezone=True), nullable=True, comment="Shen Pi time")
    approved_by_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, comment="Shen Pi RenID"
    )

    # You Xiang validation related
    email_verified = Column(Boolean, default=False, comment="You Xiang Shi Fou validation")
    activation_token = Column(String(255), nullable=True, comment="Ji Huo Ling Pai")
    activation_token_expires = Column(
        DateTime(timezone=True), nullable=True, comment="Ji Huo Ling Pai Guo Qi time"
    )

    # Deng Lu related
    last_login_at = Column(
        DateTime(timezone=True), nullable=True, comment="Zui Hou Deng Lu time"
    )
    failed_login_attempts = Column(Integer, default=0, comment="failed Deng Lu Ci Shu")
    account_locked_until = Column(
        DateTime(timezone=True), nullable=True, comment="account lock Dao Qi time"
    )

    # user Pian Hao
    language = Column(String(10), default="zh-CN", comment="user Yu Yan Pian Hao")
    timezone = Column(String(50), default="Asia/Shanghai", comment="user when Qu")

    # time Chuo
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="create time"
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), comment="update time"
    )

    # relationship
    images = relationship("Image", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    approved_by = relationship("User", remote_side=[id], backref="approved_users")
    virtual_ips = relationship("VirtualIP", backref="owner")
    stories = relationship("Story", backref="owner")
    environments = relationship("Environment", backref="owner")

    @property
    def can_login(self):
        """Jian Cha Yong Hu Shi FouCanDeng Lu"""
        return (
            self.is_active
            and self.is_approved
            and self.email_verified
            and (
                self.account_locked_until is None
                or self.account_locked_until < datetime.utcnow()
            )
        )

    @property
    def is_account_locked(self):
        """check account Shi Fou lock"""
        return (
            self.account_locked_until is not None
            and self.account_locked_until > datetime.utcnow()
        )

    def __str__(self) -> str:
        return self.username


class UserAuditLog(SoftDeleteBusinessMixin, Base):
    """user Cao Zuo Shen Ji log"""

    __tablename__ = "user_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, comment="Cao Zuo userID"
    )
    admin_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, comment="Cao Zuo administratorID"
    )
    action = Column(String(50), nullable=False, comment="Cao Zuo type")
    old_values = Column(Text, nullable=True, comment="Cao Zuo Qian Zhi(JSON)")
    new_values = Column(Text, nullable=True, comment="Cao Zuo after Zhi(JSON)")
    ip_address = Column(String(45), nullable=True, comment="IPDi Zhi")
    user_agent = Column(String(500), nullable=True, comment="user Dai Li")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="Cao Zuo time"
    )

    # relationship
    user = relationship("User", foreign_keys=[user_id], backref="audit_logs")
    admin_user = relationship(
        "User", foreign_keys=[admin_user_id], backref="admin_actions"
    )
