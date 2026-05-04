import logging
from typing import Mapping

from starlette import status

logger = logging.getLogger(__name__)


class InternalServerError(Exception):
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


"""
SmartBear Problem Details Registry
ref: https://problems-registry.smartbear.com/
"""


class AlreadyExists(InternalServerError):
    """This problem occurs when the resource being created is found to already exist on the server"""

    title = "Already Exists"
    status_code = status.HTTP_409_CONFLICT
    _detail = "The resource being created already exists."


class MissingBodyProperty(InternalServerError):
    """This problem occurs when the request sent to the API is missing an expected body property"""

    title = "Missing Body Property"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request is missing an expected body property."


class MissingRequestHeader(InternalServerError):
    """This problem occurs when the request sent to the API is missing an expected request header"""

    title = "Missing Request Header"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request is missing an expected HTTP request header."


class MissingRequestParameter(InternalServerError):
    """This problem occurs when the request sent to the API is missing an query or path parameter"""

    title = "Missing Request Parameter"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request is missing an expected query or path parameter."


class InvalidBodyPropertyFormat(InternalServerError):
    """This problem occurs when the request body contain a malformed property"""

    title = "Invalid Body Property Format"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request body contains a malformed property."


class InvalidRequestParameterFormat(InternalServerError):
    """This problem occurs when the request contains a malformed query or path parameter"""

    title = "Invalid Request Parameter Format"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request contains a malformed query parameter."


class InvalidRequestHeaderFormat(InternalServerError):
    """This problem occurs when the request contains a malformed request header"""

    title = "Invalid Request Header Format"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request contains a malformed request header parameter."


class InvalidBodyPropertyValue(InternalServerError):
    """This problem occurs when the request body contains a invalid property value"""

    title = "Invalid Body Property Value"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request body contains an invalid body property value."


class InvalidRequestParameterValue(InternalServerError):
    """This problem occurs when the request contains a invalid query or path parameter value"""

    title = "Invalid Request Parameter Value"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request body contains an invalid request parameter value."


class ValidationError(InternalServerError):
    """This problem occurs when the request is deemed unprocessable"""

    title = "Validation Error"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    _detail = "The request is not valid."


class BusinessRuleViolation(InternalServerError):
    """This problem occurs when the request is deemed invalid as it fails to meet business rule expectations"""

    title = "Business Rule Violation"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    _detail = "The request body is invalid and not meeting business rules."


class NotFound(InternalServerError):
    """This problem occurs when the requested resource could not be found"""

    title = "Not Found"
    status_code = status.HTTP_404_NOT_FOUND
    _detail = "The requested resource was not found"


class Unauthorized(InternalServerError):
    """This problem occurs when the requested resource could not be returned
    as the client request lacked valid authentication credentials
    """

    title = "Unauthorized"
    status_code = status.HTTP_401_UNAUTHORIZED
    _detail = "Access token not set or invalid, and the requested resource could not be returned."


class Forbidden(InternalServerError):
    """This problem occurs when the requested resource (and/or operation combination)
    is not authorized for the requesting client (and or authorization context)
    """

    title = "Forbidden"
    status_code = status.HTTP_403_FORBIDDEN
    _detail = "The resource could not be returned as the requestor is not authorized."


class BadRequest(InternalServerError):
    """The server cannot or will not process the request due to something that is perceived to be a client error
    (for example, malformed request syntax, invalid request message framing, or deceptive request routing)
    """

    title = "Bad Request"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request is invalid or malformed."


class InvalidParameters(InternalServerError):
    """This problem occurs when a client request contains invalid or malformed parameters
    causing the server to reject the request
    """

    title = "Invalid Parameters"
    status_code = status.HTTP_400_BAD_REQUEST
    _detail = "The request contained invalid, or malformed parameters (path or header or query)."


class ServiceUnavailable(InternalServerError):
    """This problem occurs when the service requested is currently unavailable
    and the server is not ready to handle the request
    """

    title = "Service Unavailable"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    _detail = "The service is currently unavailable."
