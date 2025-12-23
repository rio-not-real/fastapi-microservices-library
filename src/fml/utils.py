from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Annotated

from fastapi.params import Header
from starlette.requests import Request

RequestIdHeader = Annotated[str | None, Header()]

CorrelationIdHeader = Annotated[str | None, Header()]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_str() -> str:
    return utc_now().isoformat()


def dt_to_utc_str(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat()


def get_correlation_id(
    request: Request | None,
    ctx_var: ContextVar[str | None] | None = None,
) -> str | None:
    correlation_id: str | None = None

    if request is None and ctx_var is None:
        return None

    correlation_id = None
    if request is not None:
        correlation_id = (
            str(request.state.correlation_id)
            if hasattr(request.state, "correlation_id")
            else request.headers.get("X-Correlation-ID")
        )
        if correlation_id is not None:
            return correlation_id

    if ctx_var is not None:
        correlation_id = ctx_var.get()

    return correlation_id


def get_request_id(
    request: Request | None,
    ctx_var: ContextVar[str | None] | None = None,
) -> str | None:
    request_id: str | None = None

    if request is None and ctx_var is None:
        return None

    request_id = None
    if request is not None:
        request_id = (
            str(request.state.request_id)
            if hasattr(request.state, "request_id")
            else request.headers.get("X-Request-ID")
        )
        if request_id is not None:
            return request_id

    if ctx_var is not None:
        request_id = ctx_var.get()

    return request_id
