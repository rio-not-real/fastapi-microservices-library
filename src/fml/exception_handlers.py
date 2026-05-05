"""Exception handlers that return RFC 9457 problem responses."""

import logging

from pydantic import ValidationError as PydanticValidationError
from starlette import status
from starlette.requests import Request

from fml.constants import ABOUT_BLANK
from fml.errors import InternalServerError, Unauthorized
from fml.models import Error
from fml.responses import ProblemDetailResponse

logger = logging.getLogger(__name__)


async def unhandled_exception_handler(
    req: Request, exc: Exception
) -> ProblemDetailResponse:
    """Return a generic problem response for unexpected exceptions."""

    logger.exception("Unexpected error occurred")
    _exc = InternalServerError()
    return ProblemDetailResponse(
        status=_exc.status_code,
        title=_exc.title,
        detail=_exc.detail,
    )


async def fml_exception_handler(
    req: Request, exc: InternalServerError
) -> ProblemDetailResponse:
    """Return a problem response for library-defined exceptions."""

    headers: dict[str, str] = dict(exc.headers or {})
    if isinstance(exc, Unauthorized) and not any(
        key.lower() == "www-authenticate" for key in headers
    ):
        headers["WWW-Authenticate"] = "Bearer"

    return ProblemDetailResponse(
        headers=headers,
        status=exc.status_code,
        title=exc.title,
        detail=exc.detail,
        type=exc.type or ABOUT_BLANK,
    )


def encode_json_pointer(field: str) -> str:
    """Encode a field name as an RFC 6901 JSON Pointer segment."""

    # ref: https://datatracker.ietf.org/doc/html/rfc6901#section-3
    return f"/{field.replace('~', '~0').replace('/', '~1')}"


async def pydantic_validation_error_handler(
    req: Request, exc: PydanticValidationError
) -> ProblemDetailResponse:
    """Return a problem response for Pydantic validation errors."""

    errors: list[Error] = []

    for err in exc.errors():
        pointer: str = "".join(encode_json_pointer(str(field)) for field in err["loc"])
        errors.append(
            Error(
                detail=err["msg"],
                pointer=pointer if pointer else None,
                code=err["type"],
            )
        )

    return ProblemDetailResponse(
        type="https://errors.pydantic.dev/2/v/",
        status=status.HTTP_422_UNPROCESSABLE_CONTENT,
        title="Validation Error",
        detail=str(exc),
        errors=errors,
    )
