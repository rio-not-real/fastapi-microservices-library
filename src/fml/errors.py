"""RFC 9457 Problem Details exception classes based on the SmartBear registry.

ref: https://problems-registry.smartbear.com/
"""

import logging
from typing import Mapping

from starlette import status

logger = logging.getLogger(__name__)


class InternalServerError(Exception):
    """Base RFC problem detail exception for API error responses."""

    title: str = "Server Error"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    _detail: str = "The server encountered an unexpected error"
    _problems_registry: str = "https://problems-registry.smartbear.com/{problem}/"

    def __init__(
        self,
        detail: str | None = None,
        headers: Mapping[str, str] | None = None,
        type: str | None = None,
    ) -> None:
        self.detail: str = detail or self._detail
        self.headers: Mapping[str, str] | None = headers
        self.type: str | None = type or self._problems_registry.format(
            problem=self.title.lower().replace(" ", "-")
        )

    def __str__(self) -> str:
        return f"{self.status_code} {self.title}: {self.detail}"

    def __repr__(self) -> str:
        class_name: str = self.__class__.__name__
        return (
            f"{class_name}(status_code={self.status_code!r},"
            f" title={self.title!r}, detail={self.detail!r})"
        )


class AlreadyExists(InternalServerError):
    """Raised when a resource already exists."""

    title = "Already Exists"
    status_code = status.HTTP_409_CONFLICT
    _detail = "The resource being created already exists."


class MissingBodyProperty(InternalServerError):
    """Raised when a required request body property is missing."""

    title = "Missing Body Property"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request is missing an expected body property."


class MissingRequestHeader(InternalServerError):
    """Raised when a required request header is missing."""

    title = "Missing Request Header"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request is missing an expected HTTP request header."


class MissingRequestParameter(InternalServerError):
    """Raised when a required query or path parameter is missing."""

    title = "Missing Request Parameter"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request is missing an expected query or path parameter."


class InvalidBodyPropertyFormat(InternalServerError):
    """Raised when a request body property is malformed."""

    title = "Invalid Body Property Format"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request body contains a malformed property."


class InvalidRequestParameterFormat(InternalServerError):
    """Raised when a query or path parameter is malformed."""

    title = "Invalid Request Parameter Format"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request contains a malformed query parameter."


class InvalidRequestHeaderFormat(InternalServerError):
    """Raised when a request header is malformed."""

    title = "Invalid Request Header Format"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request contains a malformed request header parameter."


class InvalidBodyPropertyValue(InternalServerError):
    """Raised when a request body property value is invalid."""

    title = "Invalid Body Property Value"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request body contains an invalid body property value."


class InvalidRequestParameterValue(InternalServerError):
    """Raised when a query or path parameter value is invalid."""

    title = "Invalid Request Parameter Value"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request body contains an invalid request parameter value."


class ValidationError(InternalServerError):
    """Raised when a request is unprocessable."""

    title = "Validation Error"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    _detail = "The request is not valid."


class BusinessRuleViolation(InternalServerError):
    """Raised when a request violates a business rule."""

    title = "Business Rule Violation"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    _detail = "The request body is invalid and not meeting business rules."


class NotFound(InternalServerError):
    """Raised when a requested resource does not exist."""

    title = "Not Found"
    status_code = status.HTTP_404_NOT_FOUND
    _detail = "The requested resource was not found"


class Unauthorized(InternalServerError):
    """Raised when authentication credentials are missing or invalid."""

    title = "Unauthorized"
    status_code = status.HTTP_401_UNAUTHORIZED
    _detail = "Access token not set or invalid, and the requested resource could not be returned."


class Forbidden(InternalServerError):
    """Raised when the authenticated client is not authorized."""

    title = "Forbidden"
    status_code = status.HTTP_403_FORBIDDEN
    _detail = "The resource could not be returned as the requestor is not authorized."


class BadRequest(InternalServerError):
    """Raised when a request is invalid or malformed."""

    title = "Bad Request"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request is invalid or malformed."


class InvalidParameters(InternalServerError):
    """Raised when request parameters are invalid or malformed."""

    title = "Invalid Parameters"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request contained invalid, or malformed parameters (path or header or query)."


class ServiceUnavailable(InternalServerError):
    """Raised when the service is not ready to handle the request."""

    title = "Service Unavailable"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    _detail = "The service is currently unavailable."
