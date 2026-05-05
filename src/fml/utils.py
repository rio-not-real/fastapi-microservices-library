"""Utility functions for datetime and request metadata handling."""

from datetime import UTC, datetime

from starlette.requests import Request


def utc_now() -> datetime:
    """Return the current UTC datetime."""

    return datetime.now(UTC)


def utc_now_str() -> str:
    """Return the current UTC datetime as an ISO 8601 string."""

    return utc_now().isoformat()


def dt_to_utc_str(dt: datetime) -> str:
    """Convert a datetime to an ISO 8601 UTC string."""

    if dt.tzinfo is None:
        dt: datetime = dt.replace(tzinfo=UTC)
    else:
        dt: datetime = dt.astimezone(UTC)
    return dt.isoformat()


def get_request_id(request: Request) -> str | None:
    """Return the request ID from headers or request state."""

    return request.headers.get(
        "x-request-id", getattr(request.state, "request_id", None)
    )
