"""
Centralized exception hierarchy for domain-level errors.

This module provides a structured exception system that replaces scattered
HTTPException raises throughout the codebase. Domain exceptions are converted
to HTTP responses by exception middleware.

Usage:
    from app.core.exceptions import NotFoundError

    if not user:
 raise NotFoundError("user", user_id)

The middleware will automatically convert this to:
 HTTPException(status_code=404, detail="User not found: {user_id}")
"""

from typing import Any, Dict, Optional


class DomainError(Exception):
    """
    Base class for all domain-level exceptions.

    Attributes:
        message: Human-readable error message
        status_code: HTTP status code (default: 500)
        error_code: Machine-readable error code for API clients
        context: Additional context data for debugging
    """

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ):
        self.message = message
        self.context = context or {}
        if error_code:
            self.error_code = error_code
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        result = {
            "error": self.error_code,
            "message": self.message,
        }
        if self.context:
            result["context"] = self.context
        return result


# ============================================================================
# 4xx Client Errors
# ============================================================================


class NotFoundError(DomainError):
    """
    Resource not found error (404).

    Usage:
 raise NotFoundError("user", user_id)
 raise NotFoundError("Xu NiIP", virtual_ip_id)
        raise NotFoundError.user(user_id)
    """

    status_code = 404
    error_code = "NOT_FOUND"

    def __init__(
        self,
        resource_type: str,
        resource_id: Any = None,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            if resource_id is not None:
                message = f"{resource_type}not found: {resource_id}"
            else:
                message = f"{resource_type}not found"

        context = context or {}
        if resource_id is not None:
            context["resource_id"] = resource_id
        context["resource_type"] = resource_type

        super().__init__(message, context, f"{resource_type.upper()}_NOT_FOUND")

    # Convenience factory methods for common resources
    @classmethod
    def user(cls, user_id: Any) -> "NotFoundError":
        return cls("user", user_id)

    @classmethod
    def virtual_ip(cls, virtual_ip_id: Any) -> "NotFoundError":
        return cls("Xu NiIP", virtual_ip_id)

    @classmethod
    def script(cls, script_id: Any) -> "NotFoundError":
        return cls("Jiao Ben", script_id)

    @classmethod
    def episode(cls, episode_id: Any) -> "NotFoundError":
        return cls("episode", episode_id)

    @classmethod
    def story(cls, story_id: Any) -> "NotFoundError":
        return cls("story", story_id)

    @classmethod
    def scene(cls, scene_id: Any) -> "NotFoundError":
        return cls("scene", scene_id)

    @classmethod
    def shot(cls, shot_id: Any) -> "NotFoundError":
        return cls("shot", shot_id)

    @classmethod
    def beat(cls, beat_id: Any) -> "NotFoundError":
        return cls("Jie Pai", beat_id)

    @classmethod
    def environment(cls, env_id: Any) -> "NotFoundError":
        return cls("environment", env_id)

    @classmethod
    def image(cls, image_id: Any) -> "NotFoundError":
        return cls("image", image_id)


class ValidationError(DomainError):
    """
    Input validation error (400).

    Usage:
 raise ValidationError("Xu NiIPname Cun Zai")
 raise ValidationError("Bi Xu Ti Gongpromptorimage_url", field="prompt")
    """

    status_code = 400
    error_code = "VALIDATION_ERROR"

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        context = context or {}
        if field:
            context["field"] = field
        super().__init__(message, context)


class MissingFieldError(ValidationError):
    """
    Required field missing error (400).

    Usage:
        raise MissingFieldError("user_id")
 raise MissingFieldError("prompt", "Bi Xu Ti Gong prompt Ci")
    """

    error_code = "MISSING_FIELD"

    def __init__(
        self,
        field: str,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"missing required field: {field}"
        super().__init__(message, field, context)


class InvalidFormatError(ValidationError):
    """
    Invalid format error (400).

    Usage:
 raise InvalidFormatError("scene_numbers", "Bi Xu Shi Shu Zu format")
    """

    error_code = "INVALID_FORMAT"

    def __init__(
        self,
        field: str,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"invalid field format: {field}"
        super().__init__(message, field, context)


class DuplicateError(ValidationError):
    """
    Duplicate resource error (400).

    Usage:
 raise DuplicateError("Xu NiIPname", name)
    """

    error_code = "DUPLICATE"

    def __init__(
        self,
        resource_type: str,
        value: Any,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"{resource_type}already exists: {value}"
        context = context or {}
        context["value"] = value
        super().__init__(message, resource_type, context)


class UnauthorizedError(DomainError):
    """
    Authentication required error (401).

    Usage:
 raise UnauthorizedError("Ling Pai Yi Guo Qi")
    """

    status_code = 401
    error_code = "UNAUTHORIZED"


class ForbiddenError(DomainError):
    """
    Permission denied error (403).

    Usage:
 raise ForbiddenError("missing permission access Ci Zi Yuan")
    """

    status_code = 403
    error_code = "FORBIDDEN"


class ConflictError(DomainError):
    """
    Resource conflict error (409).

    Usage:
 raise ConflictError("Zi Yuan Zheng Zai Qi Ta Cao Zuo Shi Yong")
    """

    status_code = 409
    error_code = "CONFLICT"


# ============================================================================
# 5xx Server Errors
# ============================================================================


class ServiceError(DomainError):
    """
    Internal service error (500).

    Base class for server-side errors.
    """

    status_code = 500
    error_code = "SERVICE_ERROR"


class GenerationFailedError(ServiceError):
    """
    AI generation failed error (500).

    Usage:
 raise GenerationFailedError("image Sheng Cheng", "APIreturn error")
 raise GenerationFailedError.image("model Chao Shi")
    """

    error_code = "GENERATION_FAILED"

    def __init__(
        self,
        generation_type: str,
        reason: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        message = f"{generation_type}generation failed"
        if reason:
            message += f": {reason}"

        context = context or {}
        context["generation_type"] = generation_type
        if reason:
            context["reason"] = reason

        super().__init__(message, context)

    @classmethod
    def image(cls, reason: Optional[str] = None) -> "GenerationFailedError":
        return cls("image", reason)

    @classmethod
    def video(cls, reason: Optional[str] = None) -> "GenerationFailedError":
        return cls("video", reason)

    @classmethod
    def script(cls, reason: Optional[str] = None) -> "GenerationFailedError":
        return cls("Jiao Ben", reason)

    @classmethod
    def story(cls, reason: Optional[str] = None) -> "GenerationFailedError":
        return cls("story", reason)

    @classmethod
    def audio(cls, reason: Optional[str] = None) -> "GenerationFailedError":
        return cls("audio", reason)


class ConfigurationError(ServiceError):
    """
    Service configuration error (500).

    Usage:
 raise ConfigurationError("OSS servicenot configuration")
    """

    error_code = "CONFIGURATION_ERROR"


class ExternalServiceError(DomainError):
    """
    External service unavailable error (503).

    Usage:
 raise ExternalServiceError("OpenAI", "APIChao Shi")
    """

    status_code = 503
    error_code = "EXTERNAL_SERVICE_ERROR"

    def __init__(
        self,
        service_name: str,
        reason: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        message = f"external service {service_name} unavailable"
        if reason:
            message += f": {reason}"

        context = context or {}
        context["service_name"] = service_name
        if reason:
            context["reason"] = reason

        super().__init__(message, context)
