import http
import logging

from fastapi.responses import ORJSONResponse
from pydantic import ValidationError as PydanticValidationError
from starlette import status
from starlette.background import BackgroundTask
from starlette.exceptions import HTTPException
from starlette.requests import Request

from fml.constants import ABOUT_BLANK, HTTP_500_DETAIL, HTTP_500_TITLE
from fml.models import ErrorDetails, ProblemDetails

logger = logging.getLogger(__name__)


class CustomHTTPException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "The server encountered an unexpected error"
    _title = "Server Error"
    _problems_registry = "https://problems-registry.smartbear.com/{problem}/"

    def __init__(
        self, detail: str | None = None, headers: dict[str, str] | None = None
    ):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
            headers=headers,
        )

    def __str__(self) -> str:
        return f"{self.status_code} {self._title}: {self.detail}"

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return (
            f"{class_name}(status_code={self.status_code!r},"
            " title={self._title!r}, detail={self.detail!r})"
        )

    @property
    def type(self) -> str:
        problem = self._title.lower().replace(" ", "-")
        return self._problems_registry.format(problem=problem)


class AlreadyExists(CustomHTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = "The request attempted to create a resource that already exists"
    _title = "Already Exists"


class ValidationError(CustomHTTPException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    detail = "The request is invalid and deemed unprocessable"
    _title = "Validation Error"


class BusinessRuleViolation(CustomHTTPException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    detail = "The request is deemed invalid as it failed business rule checks"
    _title = "Business Rule Violation"


class NotFound(CustomHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "The requested resource could not be found"
    _title = "Not Found"


class Unauthorized(CustomHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "The client request missed or malformed its credentials"
    _title = "Unauthorized"

    def __init__(
        self, detail: str | None = None, headers: dict[str, str] | None = None
    ) -> None:
        headers = headers or {}
        headers["WWW-Authenticate"] = "Bearer"
        super().__init__(detail=detail or self.detail, headers=headers)


class Forbidden(CustomHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "The request is not authorized for the resource"
    _title = "Forbidden"


class BadRequest(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "The client request is invalid or malformed"
    _title = "Bad Request"


class ServiceUnavailable(CustomHTTPException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "The requested service is currently unavailable"
    _title = "Service Unavailable"


class ProblemDetailsResponse(ORJSONResponse):
    def __init__(
        self,
        headers: dict[str, str] | None = None,
        background: BackgroundTask | None = None,
        **kwargs,
    ):
        problem_details = ProblemDetails.model_validate(kwargs)
        headers = {"Content-Type": "application/problem+json"}

        super().__init__(
            content=problem_details.model_dump(exclude_none=True),
            status_code=problem_details.status,
            headers=headers,
            media_type=self.media_type,
            background=background,
        )


async def unhandled_exception_handler(
    _: Request, exc: Exception
) -> ProblemDetailsResponse:
    logger.error(exc)
    return ProblemDetailsResponse(
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        title=HTTP_500_TITLE,
        detail=HTTP_500_DETAIL,
    )


async def custom_http_exception_handler(
    _: Request, exc: HTTPException
) -> ProblemDetailsResponse:
    return ProblemDetailsResponse(
        status=exc.status_code,
        title=(
            exc.title
            if hasattr(exc, "title")
            else http.HTTPStatus(exc.status_code).phrase
        ),
        detail=exc.detail,
        type=exc.type if hasattr(exc, "type") else ABOUT_BLANK,
    )


async def pydantic_validation_error_handler(
    _: Request, exc: PydanticValidationError
) -> ProblemDetailsResponse:
    unknown: str = "Unknown"
    errors: list[ErrorDetails] = []

    for err in exc.errors():
        detail = f"[{err.get('type', unknown)}] {err.get('msg', unknown)}"
        pointer = "/".join(
            field for field in err.get("loc", ()) if isinstance(field, str)
        )
        errors.append(
            ErrorDetails(detail=detail, pointer=f"/{pointer}" if pointer else None)
        )

    return ProblemDetailsResponse(
        type="https://problems-registry.smartbear.com/validation-error",
        status=status.HTTP_422_UNPROCESSABLE_CONTENT,
        title="Validation Error",
        detail=str(exc),
        errors=errors,
    )
