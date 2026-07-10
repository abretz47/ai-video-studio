"""user management service Dan Yuan Ce Shi

Zhuan Zhu Yu testUserManagementServiceYe Wu logic
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from app.schemas.user import UserApprovalRequest
from app.services.user_management_service import UserManagementService
from fastapi import HTTPException
from sqlalchemy.orm import Session


class TestUserManagementService:
    """user management service test"""

    def setup_method(self):
        """Mei Ge Ce Shi Fang Fa before set"""
        self.db = Mock(spec=Session)
        self.service = UserManagementService(self.db)

    def create_mock_user(self, **kwargs):
        """create mock user"""
        defaults = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "is_active": False,
            "is_approved": False,
            "email_verified": False,
            "is_admin": False,
            "is_superuser": False,
            "failed_login_attempts": 0,
            "account_locked_until": None,
            "approved_at": None,
            "approved_by_user_id": None,
        }
        defaults.update(kwargs)

        user = Mock()
        for key, value in defaults.items():
            setattr(user, key, value)

        return user

    def create_mock_admin(self, **kwargs):
        """create mock administrator user"""
        defaults = {
            "id": 99,
            "username": "admin",
            "is_admin": True,
            "is_superuser": False,
        }
        defaults.update(kwargs)
        return self.create_mock_user(**defaults)


class TestUserApproval(TestUserManagementService):
    """user approval test"""

    def test_approve_user_success(self):
        """test user approval Cheng Gong"""
        # Zhun Bei
        user = self.create_mock_user()
        admin = self.create_mock_admin()
        self.db.query.return_value.filter.return_value.first.return_value = user

        approval_data = UserApprovalRequest(action="approve", reason="Test approval")

        # Zhi Xing
        result = self.service.approve_user(
            user_id=1, admin_user=admin, approval_data=approval_data
        )

        # validate
        assert result == user
        assert user.is_approved is True
        assert user.is_active is True
        assert user.approved_by_user_id == admin.id
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(user)

    def test_reject_user_success(self):
        """test user Ju Jue Cheng Gong"""
        user = self.create_mock_user()
        admin = self.create_mock_admin()
        self.db.query.return_value.filter.return_value.first.return_value = user

        approval_data = UserApprovalRequest(action="reject", reason="Test rejection")

        result = self.service.approve_user(
            user_id=1, admin_user=admin, approval_data=approval_data
        )

        assert result == user
        assert user.is_approved is False
        assert user.is_active is False

    def test_approve_nonexistent_user_fails(self):
        """test approval not exists user failed"""
        admin = self.create_mock_admin()
        self.db.query.return_value.filter.return_value.first.return_value = None

        approval_data = UserApprovalRequest(action="approve")

        with pytest.raises(HTTPException) as exc_info:
            self.service.approve_user(
                user_id=999, admin_user=admin, approval_data=approval_data
            )

        assert exc_info.value.status_code == 404
        assert "user not exists" in str(exc_info.value.detail)

    def test_invalid_approval_action_fails(self):
        """test Wu Xiao approval operation failed"""
        user = self.create_mock_user()
        admin = self.create_mock_admin()
        self.db.query.return_value.filter.return_value.first.return_value = user

        approval_data = UserApprovalRequest(action="invalid_action")

        with pytest.raises(HTTPException) as exc_info:
            self.service.approve_user(
                user_id=1, admin_user=admin, approval_data=approval_data
            )

        assert exc_info.value.status_code == 400
        assert "Wu Xiao operation type" in str(exc_info.value.detail)


class TestRoleManagement(TestUserManagementService):
    """character management test"""

    def test_update_user_role_success(self):
        """test update user character Cheng Gong"""
        user = self.create_mock_user(id=1)
        admin = self.create_mock_admin(id=2)
        self.db.query.return_value.filter.return_value.first.return_value = user

        result = self.service.update_user_role(
            user_id=1, admin_user=admin, is_admin=True, is_superuser=False
        )

        assert result == user
        assert user.is_admin is True
        assert user.is_superuser is False
        self.db.commit.assert_called_once()

    def test_cannot_modify_own_permissions(self):
        """test Bu Neng Xiu Gai Zi Ji permission"""
        user = self.create_mock_user(id=1)
        self.db.query.return_value.filter.return_value.first.return_value = user

        with pytest.raises(HTTPException) as exc_info:
            self.service.update_user_role(
                user_id=1,
                admin_user=user,  # Tong Yi Ge user
                is_admin=False,
            )

        assert exc_info.value.status_code == 400
        assert "Bu Neng Xiu Gai Zi Ji permission" in str(exc_info.value.detail)


class TestUserSuspension(TestUserManagementService):
    """user suspend test"""

    def test_suspend_user_success(self):
        """test suspend user Cheng Gong"""
        user = self.create_mock_user(id=1, is_active=True)
        admin = self.create_mock_admin(id=2)
        self.db.query.return_value.filter.return_value.first.return_value = user

        result = self.service.suspend_user(
            user_id=1, admin_user=admin, duration_hours=24, reason="Test suspension"
        )

        assert result == user
        assert user.is_active is False
        assert user.account_locked_until is not None
        self.db.commit.assert_called_once()

    def test_cannot_suspend_self(self):
        """test Bu Neng suspend Zi Ji"""
        user = self.create_mock_user(id=1)
        self.db.query.return_value.filter.return_value.first.return_value = user

        with pytest.raises(HTTPException) as exc_info:
            self.service.suspend_user(
                user_id=1,
                admin_user=user,  # Tong Yi Ge user
                duration_hours=24,
            )

        assert exc_info.value.status_code == 400
        assert "Bu Neng suspend Zi Ji Zhang Hu" in str(exc_info.value.detail)

    def test_reactivate_user_success(self):
        """test Chong Xin activate user Cheng Gong"""
        user = self.create_mock_user(
            id=1,
            is_active=False,
            account_locked_until=datetime.utcnow() + timedelta(hours=1),
            failed_login_attempts=3,
        )
        admin = self.create_mock_admin(id=2)
        self.db.query.return_value.filter.return_value.first.return_value = user

        result = self.service.reactivate_user(user_id=1, admin_user=admin)

        assert result == user
        assert user.is_active is True
        assert user.account_locked_until is None
        assert user.failed_login_attempts == 0


class TestUserDeletion(TestUserManagementService):
    """user delete test"""

    def test_delete_user_success(self):
        """test delete user Cheng Gong"""
        user = self.create_mock_user(id=1)
        admin = self.create_mock_admin(id=2)
        self.db.query.return_value.filter.return_value.first.return_value = user

        result = self.service.delete_user(user_id=1, admin_user=admin)

        assert result is True
        self.db.delete.assert_called_once_with(user)
        self.db.commit.assert_called_once()

    def test_cannot_delete_self(self):
        """test Bu Neng delete Zi Ji"""
        user = self.create_mock_user(id=1)
        self.db.query.return_value.filter.return_value.first.return_value = user

        with pytest.raises(HTTPException) as exc_info:
            self.service.delete_user(
                user_id=1,
                admin_user=user,  # Tong Yi Ge user
            )

        assert exc_info.value.status_code == 400
        assert "Bu Neng delete Zi Ji Zhang Hu" in str(exc_info.value.detail)


class TestUserStats(TestUserManagementService):
    """user statistics test"""

    def test_get_user_stats_success(self):
        """test get user statistics Cheng Gong"""
        # mock database Cha Xun Jie Guo：1 Ci Zhi Jie count + 5 Ci filter(...).count()
        base_query = self.db.query.return_value
        filtered_query = base_query.filter.return_value
        base_query.count.return_value = 10
        filtered_query.count.side_effect = [8, 2, 2, 1, 3]

        stats = self.service.get_user_stats()

        assert stats.total_users == 10
        assert stats.active_users == 8
        assert stats.pending_approval == 2
        assert stats.suspended_users == 2
        assert stats.admin_users == 1
        assert stats.recent_registrations == 3


class TestActivationToken(TestUserManagementService):
    """activate Ling Pai test"""

    @patch("app.services.user_management_service.uuid")
    def test_generate_activation_token_success(self, mock_uuid):
        """test generate activate Ling Pai Cheng Gong"""
        mock_uuid.uuid4.return_value = "test-token-123"
        user = self.create_mock_user()
        self.db.query.return_value.filter.return_value.first.return_value = user

        token = self.service.generate_activation_token(user_id=1)

        assert token == "test-token-123"
        assert user.activation_token == "test-token-123"
        assert user.activation_token_expires is not None
        self.db.commit.assert_called_once()

    def test_verify_activation_token_success(self):
        """test validate activate Ling Pai Cheng Gong"""
        user = self.create_mock_user(
            activation_token="valid-token",
            activation_token_expires=datetime.utcnow() + timedelta(hours=1),
        )
        query_mock = self.db.query.return_value.filter.return_value.first
        query_mock.return_value = user

        result = self.service.verify_activation_token("valid-token")

        assert result == user
        assert user.email_verified is True
        assert user.activation_token is None
        assert user.activation_token_expires is None

    def test_verify_expired_token_fails(self):
        """test validate Guo Qi Ling Pai failed"""
        query_mock = self.db.query.return_value.filter.return_value.first
        query_mock.return_value = None  # mock Zhao Bu Dao You Xiao Ling Pai

        result = self.service.verify_activation_token("expired-token")

        assert result is None


class TestLoginAttempts(TestUserManagementService):
    """login Chang Shi test"""

    def test_reset_failed_login_attempts(self):
        """test Zhong Zhi failed login Ci Shu"""
        user = self.create_mock_user(
            failed_login_attempts=3,
            account_locked_until=datetime.utcnow() + timedelta(hours=1),
        )
        self.db.query.return_value.filter.return_value.first.return_value = user

        result = self.service.reset_failed_login_attempts(user_id=1)

        assert result == user
        assert user.failed_login_attempts == 0
        assert user.account_locked_until is None
        self.db.commit.assert_called_once()

    def test_increment_failed_login_attempts(self):
        """test Zeng Jia failed login Ci Shu"""
        user = self.create_mock_user(failed_login_attempts=2)
        self.db.query.return_value.filter.return_value.first.return_value = user

        result = self.service.increment_failed_login_attempts(user_id=1)

        assert result == user
        assert user.failed_login_attempts == 3
        self.db.commit.assert_called_once()

    def test_lock_account_after_five_failures(self):
        """test5Ci failed after Suo Ding Zhang Hu"""
        user = self.create_mock_user(failed_login_attempts=4)
        self.db.query.return_value.filter.return_value.first.return_value = user

        result = self.service.increment_failed_login_attempts(user_id=1)

        assert result == user
        assert user.failed_login_attempts == 5
        assert user.account_locked_until is not None


class TestAuditLog(TestUserManagementService):
    """Shen Ji Ri Zhi test"""

    def test_create_audit_log_success(self):
        """test create Shen Ji Ri Zhi Cheng Gong"""
        old_values = {"is_active": False}
        new_values = {"is_active": True}

        audit_log = self.service._create_audit_log(
            user_id=1,
            admin_user_id=2,
            action="USER_ACTIVATED",
            old_values=old_values,
            new_values=new_values,
            ip_address="192.168.1.1",
            user_agent="TestAgent",
        )

        assert audit_log.user_id == 1
        assert audit_log.admin_user_id == 2
        assert audit_log.action == "USER_ACTIVATED"
        self.db.add.assert_called_once()
        self.db.flush.assert_called_once()

    def test_get_user_audit_logs(self):
        """test get user Shen Ji Ri Zhi"""
        mock_logs = [Mock(), Mock()]
        query_mock = self.db.query.return_value.filter.return_value
        query_mock.count.return_value = 2
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
            mock_logs
        )

        logs, total = self.service.get_user_audit_logs(user_id=1, page=1, size=10)

        assert len(logs) == 2
        assert total == 2


class TestUserSearch(TestUserManagementService):
    """user Sou Suo test"""

    def test_get_users_list_with_filters(self):
        """test Dai Shai Xuan Tiao Jian user list"""
        mock_users = [Mock(), Mock()]
        query_mock = self.db.query.return_value
        query_mock.filter.return_value = query_mock  # Lian Shi call
        query_mock.count.return_value = 2
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
            mock_users
        )

        users, total = self.service.get_users_list(
            page=1, size=10, status_filter="pending", role_filter="admin", search="test"
        )

        assert len(users) == 2
        assert total == 2
        # validate Guo Lv Qi be Ying Yong（Ju Tifiltercall Ci Shu Qu Jue Yu Shi Xian）
        assert query_mock.filter.call_count >= 1
