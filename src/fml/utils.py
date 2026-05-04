from datetime import UTC, datetime
from typing import Annotated

from fastapi.params import Header
from starlette.requests import Request

RequestIdHeader = Annotated[str | None, Header()]

CorrelationIdHeader = Annotated[str | None, Header()]


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_now_str() -> str:
    return utc_now().isoformat()


def dt_to_utc_str(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    else:
        dt = dt.astimezone(UTC)
    return dt.isoformat()


def get_request_id(request: Request) -> str | None:
    return request.headers.get(
        "x-request-id", getattr(request.state, "request_id", None)
    )
