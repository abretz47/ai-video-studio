"""
Tests for centralized exception hierarchy.
"""

from app.core.exceptions import (
 ConfigurationError,
 ConflictError,
 DomainError,
 DuplicateError,
 ExternalServiceError,
 ForbiddenError,
 GenerationFailedError,
 InvalidFormatError,
 MissingFieldError,
 NotFoundError,
 ServiceError,
 UnauthorizedError,
 ValidationError,
)


class TestDomainError:
 """Test base DomainError class."""

 def test_basic_error(self):
 error = DomainError("test error")
 assert error.message == "test error"
 assert error.status_code == 500
 assert error.error_code == "INTERNAL_ERROR"
 assert error.context == {}

 def test_error_with_context(self):
 error = DomainError("test error", context={"key": "value"})
 assert error.context == {"key": "value"}

 def test_error_with_custom_code(self):
 error = DomainError("test error", error_code="CUSTOM_ERROR")
 assert error.error_code == "CUSTOM_ERROR"

 def test_to_dict(self):
 error = DomainError("test error", context={"user_id": 123})
 result = error.to_dict()
 assert result == {
 "error": "INTERNAL_ERROR",
 "message": "test error",
 "context": {"user_id": 123},
 }


class TestNotFoundError:
 """Test NotFoundError class."""

 def test_basic_not_found(self):
 error = NotFoundError("user", 123)
 assert error.message == "user Bu exists: 123"
 assert error.status_code == 404
 assert error.context["resource_id"] == 123
 assert error.context["resource_type"] == "user"

 def test_not_found_without_id(self):
 error = NotFoundError("virtualIP")
 assert error.message == "virtualIPBu Cun Zai"
 assert "resource_id" not in error.context

 def test_not_found_custom_message(self):
 error = NotFoundError("Jiao Ben", 456, message="Zhao Bu Dao Zhi Ding Jiao Ben")
 assert error.message == "Zhao Bu Dao Zhi Ding Jiao Ben"
 assert error.context["resource_id"] == 456

 def test_user_factory(self):
 error = NotFoundError.user(123)
 assert error.message == "user Bu exists: 123"
 assert error.status_code == 404

 def test_virtual_ip_factory(self):
 error = NotFoundError.virtual_ip("vip_123")
 assert error.message == "virtualIPBu Cun Zai: vip_123"

 def test_script_factory(self):
 error = NotFoundError.script(456)
 assert error.message == "Jiao Ben Bu exists: 456"


class TestValidationError:
 """Test ValidationError and subclasses."""

 def test_basic_validation_error(self):
 error = ValidationError("virtualIPname Yi exists")
 assert error.message == "virtualIPname Yi exists"
 assert error.status_code == 400
 assert error.error_code == "VALIDATION_ERROR"

 def test_validation_error_with_field(self):
 error = ValidationError("format Bu correct", field="email")
 assert error.context["field"] == "email"

 def test_missing_field_error(self):
 error = MissingFieldError("user_id")
 assert error.message == "Que Shao Bi Tian character Duan: user_id"
 assert error.status_code == 400
 assert error.context["field"] == "user_id"

 def test_missing_field_custom_message(self):
 error = MissingFieldError("prompt", "Bi Xu provide prompt text")
 assert error.message == "Bi Xu provide prompt text"

 def test_invalid_format_error(self):
 error = InvalidFormatError("scene_numbers")
 assert error.message == "character Duan format Bu correct: scene_numbers"
 assert error.context["field"] == "scene_numbers"

 def test_invalid_format_custom_message(self):
 error = InvalidFormatError("date", "Ri Qi format Bi Xu WeiYYYY-MM-DD")
 assert error.message == "Ri Qi format Bi Xu WeiYYYY-MM-DD"

 def test_duplicate_error(self):
 error = DuplicateError("virtualIPname", "Ce Shi Ming Cheng")
 assert error.message == "virtualIPname Yi exists: Ce Shi Ming Cheng"
 assert error.context["value"] == "Ce Shi Ming Cheng"
 assert error.context["field"] == "virtualIPname"


class TestAuthErrors:
 """Test authentication and authorization errors."""

 def test_unauthorized_error(self):
 error = UnauthorizedError("Ling Pai Yi Guo Qi")
 assert error.message == "Ling Pai Yi Guo Qi"
 assert error.status_code == 401
 assert error.error_code == "UNAUTHORIZED"

 def test_forbidden_error(self):
 error = ForbiddenError("Mei You permission access Ci Zi Yuan")
 assert error.message == "Mei You permission access Ci Zi Yuan"
 assert error.status_code == 403
 assert error.error_code == "FORBIDDEN"

 def test_conflict_error(self):
 error = ConflictError("Zi Yuan Zheng Zai Bei use")
 assert error.message == "Zi Yuan Zheng Zai Bei use"
 assert error.status_code == 409


class TestServiceErrors:
 """Test server-side errors."""

 def test_service_error(self):
 error = ServiceError("Nei Bu Cuo Wu")
 assert error.status_code == 500

 def test_generation_failed_basic(self):
 error = GenerationFailedError("image", "APItimeout")
 assert error.message == "image generate failed: APItimeout"
 assert error.context["generation_type"] == "image"
 assert error.context["reason"] == "APItimeout"

 def test_generation_failed_no_reason(self):
 error = GenerationFailedError("video")
 assert error.message == "video generate failed"

 def test_generation_failed_image_factory(self):
 error = GenerationFailedError.image("model return error")
 assert error.message == "image generate failed: model return error"

 def test_generation_failed_factories(self):
 assert GenerationFailedError.video().message == "video generate failed"
 assert GenerationFailedError.script().message == "Jiao Ben generate failed"
 assert GenerationFailedError.story().message == "story generate failed"
 assert GenerationFailedError.audio().message == "Yin Pin generate failed"

 def test_configuration_error(self):
 error = ConfigurationError("OSSservice not yet configuration")
 assert error.message == "OSSservice not yet configuration"
 assert error.status_code == 500

 def test_external_service_error(self):
 error = ExternalServiceError("OpenAI", "connection timeout")
 assert error.message == "Wai Bu Fu Wu OpenAI unavailable: connection timeout"
 assert error.status_code == 503
 assert error.context["service_name"] == "OpenAI"
 assert error.context["reason"] == "connection timeout"

 def test_external_service_no_reason(self):
 error = ExternalServiceError("Keling")
 assert error.message == "Wai Bu Fu Wu Keling unavailable"


class TestExceptionToDict:
 """Test exception serialization."""

 def test_simple_exception_to_dict(self):
 error = NotFoundError.user(123)
 result = error.to_dict()
 assert result["error"] == "user_NOT_FOUND"
 assert result["message"] == "user Bu exists: 123"
 assert result["context"]["resource_id"] == 123

 def test_exception_without_context(self):
 error = ValidationError("test error")
 result = error.to_dict()
 # Context is only included if not empty
 if "context" in result:
 assert result["context"] == {}

 def test_exception_with_rich_context(self):
 error = GenerationFailedError(
 "image", "APIerror", context={"provider": "openai", "attempt": 3}
)
 result = error.to_dict()
 assert result["context"]["provider"] == "openai"
 assert result["context"]["attempt"] == 3
 assert result["context"]["generation_type"] == "image"
