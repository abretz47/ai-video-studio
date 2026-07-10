"""user Guan Li Xi Tong test

Quan Mian test Yong Hu Zhu Ce、approval、permission management etc function
"""

from datetime import datetime, timedelta

import pytest
from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.user import User, UserAuditLog
from app.services.user_management_service import UserManagementService
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def client(db_session: Session):
    """FastAPI test client with DB dependency override (no auth overrides)."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)


class TestUserRegistration:
    """Yong Hu Zhu Ce test"""

    def test_register_creates_inactive_user(self, db_session: Session, client):
        """test Zhu Ce create Wei Ji Huo user"""
        # Shou user create administrator，Xian clean up
        db_session.query(User).delete()
        db_session.commit()

        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User",
        }

        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        data = response.json()
        assert data["username"] == "testuser"
        # Shou Ge user Zi Dong Jin Sheng Wei administrator and activate
        assert data["is_active"] is True
        assert data["is_approved"] is True
        assert data["email_verified"] is True
        assert data["is_admin"] is True
        assert data["is_superuser"] is True

    def test_register_subsequent_user_is_pending(self, db_session: Session, client):
        """test Di Er Ge user keep Dai approval status"""
        db_session.query(User).delete()
        db_session.commit()

        # Shou Ge user -> administrator
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "adminuser",
                "email": "admin@example.com",
                "password": "pass123",
            },
        )

        # Di Er Ge user
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "user2",
                "email": "user2@example.com",
                "password": "pass123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["is_approved"] is False
        assert data["email_verified"] is False
        assert data["is_admin"] is False
        assert data["is_superuser"] is False

    def test_register_duplicate_username(self, db_session: Session, client):
        """test Chong Fu Yong Hu Ming Zhu Ce"""
        db_session.query(User).delete()
        db_session.commit()
        # create Di Yi Ge user
        user1_data = {
            "username": "duplicate",
            "email": "user1@example.com",
            "password": "pass123",
        }
        client.post("/api/v1/auth/register", json=user1_data)

        # Chang Shi Yong Xiang general-purpose Hu Ming create Di Er Ge user
        user2_data = {
            "username": "duplicate",
            "email": "user2@example.com",
            "password": "pass123",
        }

        response = client.post("/api/v1/auth/register", json=user2_data)
        assert response.status_code == 400
        assert "Yong Hu Ming already exists" in response.json()["detail"]

    def test_register_duplicate_email(self, db_session: Session, client):
        """test Chong Fu You Xiang Zhu Ce"""
        db_session.query(User).delete()
        db_session.commit()
        user1_data = {
            "username": "user1",
            "email": "duplicate@example.com",
            "password": "pass123",
        }
        client.post("/api/v1/auth/register", json=user1_data)

        user2_data = {
            "username": "user2",
            "email": "duplicate@example.com",
            "password": "pass123",
        }

        response = client.post("/api/v1/auth/register", json=user2_data)
        assert response.status_code == 400
        assert "You Xiang already exists" in response.json()["detail"]


class TestUserLogin:
    """user login test"""

    def create_approved_user(self, db: Session, username: str = "activeuser"):
        """create already approval test user"""
        user = User(
            username=username,
            email=f"{username}@example.com",
            hashed_password=get_password_hash("testpass123"),
            is_active=True,
            is_approved=True,
            email_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def create_pending_user(self, db: Session, username: str = "pendinguser"):
        """create Dai approval test user"""
        user = User(
            username=username,
            email=f"{username}@example.com",
            hashed_password=get_password_hash("testpass123"),
            is_active=False,
            is_approved=False,
            email_verified=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def test_login_approved_user_success(self, db_session: Session, client):
        """test already approval user login Cheng Gong"""
        user = self.create_approved_user(db_session)

        response = client.post(
            "/api/v1/auth/login",
            data={"username": user.username, "password": "testpass123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_pending_user_fails(self, db_session: Session, client):
        """test Dai approval user login failed"""
        user = self.create_pending_user(db_session)

        response = client.post(
            "/api/v1/auth/login",
            data={"username": user.username, "password": "testpass123"},
        )

        assert response.status_code == 403
        assert (
            "You Xiang" in response.json()["detail"] or "approval" in response.json()["detail"]
        )

    def test_login_invalid_credentials(self, db_session: Session, client):
        """test error Ping Zheng login"""
        user = self.create_approved_user(db_session)

        response = client.post(
            "/api/v1/auth/login",
            data={"username": user.username, "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "Yong Hu Ming or Mi Ma error" in response.json()["detail"]

    def test_login_increments_failed_attempts(self, db_session: Session, client):
        """test failed login Zeng Jia failed Ci Shu"""
        user = self.create_approved_user(db_session)

        # Lian Xu failed login
        for i in range(3):
            client.post(
                "/api/v1/auth/login",
                data={"username": user.username, "password": "wrongpassword"},
            )

        db_session.refresh(user)
        assert user.failed_login_attempts == 3

    def test_account_locks_after_five_failures(self, db_session: Session, client):
        """test5Ci failed after Zhang Hu Suo Ding"""
        user = self.create_approved_user(db_session)

        # Lian Xu5Ci failed login
        for i in range(5):
            client.post(
                "/api/v1/auth/login",
                data={"username": user.username, "password": "wrongpassword"},
            )

        db_session.refresh(user)
        assert user.failed_login_attempts == 5
        assert user.account_locked_until is not None
        assert user.account_locked_until > datetime.utcnow()


class TestUserManagementService:
    """user management service test"""

    def create_admin_user(self, db_session: Session):
        """create administrator user"""
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("adminpass"),
            is_active=True,
            is_approved=True,
            email_verified=True,
            is_admin=True,
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
        return admin

    def create_test_user(self, db_session: Session, username: str = "testuser"):
        """create test user"""
        user = User(
            username=username,
            email=f"{username}@example.com",
            hashed_password=get_password_hash("testpass"),
            is_active=False,
            is_approved=False,
            email_verified=False,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def test_approve_user_success(self, db_session: Session):
        """test user approval Cheng Gong"""
        admin = self.create_admin_user(db_session)
        user = self.create_test_user(db_session)
        service = UserManagementService(db_session)

        from app.schemas.user import UserApprovalRequest

        approval_data = UserApprovalRequest(action="approve", reason="Test approval")

        result = service.approve_user(
            user_id=user.id, admin_user=admin, approval_data=approval_data
        )

        assert result.is_approved is True
        assert result.is_active is True
        assert result.approved_at is not None
        assert result.approved_by_user_id == admin.id

    def test_reject_user_success(self, db_session: Session):
        """test user Ju Jue Cheng Gong"""
        admin = self.create_admin_user(db_session)
        user = self.create_test_user(db_session)
        service = UserManagementService(db_session)

        from app.schemas.user import UserApprovalRequest

        approval_data = UserApprovalRequest(action="reject", reason="Test rejection")

        result = service.approve_user(
            user_id=user.id, admin_user=admin, approval_data=approval_data
        )

        assert result.is_approved is False
        assert result.is_active is False

    def test_update_user_role(self, db_session: Session):
        """test update user character"""
        admin = self.create_admin_user(db_session)
        user = self.create_test_user(db_session)
        service = UserManagementService(db_session)

        result = service.update_user_role(
            user_id=user.id, admin_user=admin, is_admin=True
        )

        assert result.is_admin is True

    def test_suspend_user(self, db_session: Session):
        """test suspend user"""
        admin = self.create_admin_user(db_session)
        user = self.create_test_user(db_session)
        service = UserManagementService(db_session)

        result = service.suspend_user(
            user_id=user.id,
            admin_user=admin,
            duration_hours=24,
            reason="Test suspension",
        )

        assert result.is_active is False
        assert result.account_locked_until is not None

    def test_reactivate_user(self, db_session: Session):
        """test Chong Xin activate user"""
        admin = self.create_admin_user(db_session)
        user = self.create_test_user(db_session)
        service = UserManagementService(db_session)

        # Xian suspend user
        service.suspend_user(user_id=user.id, admin_user=admin)

        # Zai Chong Xin activate
        result = service.reactivate_user(user_id=user.id, admin_user=admin)

        assert result.is_active is True
        assert result.account_locked_until is None
        assert result.failed_login_attempts == 0

    def test_get_user_stats(self, db_session: Session):
        """test get user statistics"""
        # create Bu Tong status user
        self.create_admin_user(db_session)

        # create Ji Ge Bu Tong status user Yong Yu statistics
        for i in range(3):
            user = User(
                username=f"active_user_{i}",
                email=f"active_{i}@example.com",
                hashed_password=get_password_hash("pass"),
                is_active=True,
                is_approved=True,
                email_verified=True,
            )
            db_session.add(user)

        for i in range(2):
            user = User(
                username=f"pending_user_{i}",
                email=f"pending_{i}@example.com",
                hashed_password=get_password_hash("pass"),
                is_active=False,
                is_approved=False,
                email_verified=False,
            )
            db_session.add(user)

        db_session.commit()

        service = UserManagementService(db_session)
        stats = service.get_user_stats()

        assert stats.total_users >= 6  # admin + 3 active + 2 pending
        assert stats.active_users >= 4  # admin + 3 active
        assert stats.pending_approval >= 2
        assert stats.admin_users >= 1

    def test_audit_log_creation(self, db_session: Session):
        """test Shen Ji Ri Zhi create"""
        admin = self.create_admin_user(db_session)
        user = self.create_test_user(db_session)
        service = UserManagementService(db_session)

        from app.schemas.user import UserApprovalRequest

        approval_data = UserApprovalRequest(action="approve", reason="Test")

        service.approve_user(
            user_id=user.id,
            admin_user=admin,
            approval_data=approval_data,
            ip_address="127.0.0.1",
            user_agent="TestClient",
        )

        # check Shen Ji Ri Zhi
        audit_log = (
            db_session.query(UserAuditLog)
            .filter(
                UserAuditLog.user_id == user.id, UserAuditLog.action == "USER_APPROVED"
            )
            .first()
        )

        assert audit_log is not None
        assert audit_log.admin_user_id == admin.id
        assert audit_log.ip_address == "127.0.0.1"
        assert audit_log.user_agent == "TestClient"
        assert audit_log.old_values is not None
        assert audit_log.new_values is not None


class TestAdminAPI:
    """administratorAPItest"""

    def create_admin_user(self, db_session: Session):
        """create administrator user"""
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("adminpass"),
            is_active=True,
            is_approved=True,
            email_verified=True,
            is_admin=True,
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
        return admin

    def create_regular_user(self, db_session: Session):
        """create Pu general-purpose Hu"""
        user = User(
            username="regularuser",
            email="regular@example.com",
            hashed_password=get_password_hash("userpass"),
            is_active=True,
            is_approved=True,
            email_verified=True,
            is_admin=False,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def get_admin_token(self, admin_user: User) -> str:
        """get administratortoken"""
        return create_access_token(data={"sub": admin_user.username})

    def test_admin_can_access_user_list(self, db_session: Session, client):
        """test administrator Ke Yi access user list"""
        admin = self.create_admin_user(db_session)
        token = self.get_admin_token(admin)

        response = client.get(
            "/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert "page" in data

    def test_regular_user_cannot_access_admin_endpoints(
        self, db_session: Session, client
    ):
        """test Pu general-purpose Hu Wu Fa Fang Wen administrator Jie Kou"""
        user = self.create_regular_user(db_session)
        token = self.get_admin_token(user)

        response = client.get(
            "/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert "administrator permission" in response.json()["detail"]

    def test_admin_can_approve_user(self, db_session: Session, client):
        """test administrator Ke Yi approval user"""
        admin = self.create_admin_user(db_session)
        token = self.get_admin_token(admin)

        # create Dai approval user
        pending_user = User(
            username="pending",
            email="pending@example.com",
            hashed_password=get_password_hash("pass"),
            is_active=False,
            is_approved=False,
            email_verified=True,
        )
        db_session.add(pending_user)
        db_session.commit()
        db_session.refresh(pending_user)

        response = client.put(
            f"/api/v1/admin/users/{pending_user.id}/approval",
            headers={"Authorization": f"Bearer {token}"},
            json={"action": "approve", "reason": "Test approval"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_approved"] is True
        assert data["is_active"] is True

    def test_admin_can_get_user_stats(self, db_session: Session, client):
        """test administrator Ke Yi get user statistics"""
        admin = self.create_admin_user(db_session)
        token = self.get_admin_token(admin)

        response = client.get(
            "/api/v1/admin/stats", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "active_users" in data
        assert "pending_approval" in data
        assert "admin_users" in data

    def test_admin_can_suspend_user(self, db_session: Session, client):
        """test administrator Ke Yi suspend user"""
        admin = self.create_admin_user(db_session)
        user = self.create_regular_user(db_session)
        token = self.get_admin_token(admin)

        response = client.put(
            f"/api/v1/admin/users/{user.id}/suspend",
            headers={"Authorization": f"Bearer {token}"},
            params={"duration_hours": 24, "reason": "Test suspension"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False


class TestEmailVerification:
    """You Xiang validate test"""

    def test_generate_activation_token(self, db_session: Session):
        """test generate activate Ling Pai"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("pass"),
            email_verified=False,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        service = UserManagementService(db_session)
        token = service.generate_activation_token(user.id)

        assert token is not None
        db_session.refresh(user)
        assert user.activation_token == token
        assert user.activation_token_expires is not None

    def test_verify_activation_token_success(self, db_session: Session):
        """test validate activate Ling Pai Cheng Gong"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("pass"),
            email_verified=False,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        service = UserManagementService(db_session)
        token = service.generate_activation_token(user.id)

        result = service.verify_activation_token(token)

        assert result is not None
        assert result.email_verified is True
        assert result.activation_token is None

    def test_verify_expired_token_fails(self, db_session: Session):
        """test validate Guo Qi Ling Pai failed"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("pass"),
            email_verified=False,
            activation_token="expired_token",
            activation_token_expires=datetime.utcnow() - timedelta(hours=1),
        )
        db_session.add(user)
        db_session.commit()

        service = UserManagementService(db_session)
        result = service.verify_activation_token("expired_token")

        assert result is None


class TestMiddleware:
    """Zhong Jian Jian test"""

    def test_require_active_user_blocks_inactive(self, db_session: Session, client):
        """test Huo Yue user Zhong Jian Jian Zu Zhi Fei Huo Yue user"""
        # create Wei Ji Huo user
        user = User(
            username="inactive",
            email="inactive@example.com",
            hashed_password=get_password_hash("pass"),
            is_active=False,
            is_approved=False,
            email_verified=False,
        )
        db_session.add(user)
        db_session.commit()

        token = create_access_token(data={"sub": user.username})

        # Chang Shi access Xu Yao Huo Yue user permission Jie Kou
        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert (
            "approval" in response.json()["detail"] or "validate" in response.json()["detail"]
        )

    def test_require_admin_blocks_regular_user(self, db_session: Session, client):
        """test administrator Zhong Jian Jian Zu Zhi Pu general-purpose Hu"""
        user = User(
            username="regular",
            email="regular@example.com",
            hashed_password=get_password_hash("pass"),
            is_active=True,
            is_approved=True,
            email_verified=True,
            is_admin=False,
        )
        db_session.add(user)
        db_session.commit()

        token = create_access_token(data={"sub": user.username})

        response = client.get(
            "/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert "administrator permission" in response.json()["detail"]
