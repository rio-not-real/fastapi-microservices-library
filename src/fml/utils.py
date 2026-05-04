from datetime import UTC, datetime

from starlette.requests import Request


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_now_str() -> str:
    return utc_now().isoformat()


def dt_to_utc_str(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt: datetime = dt.replace(tzinfo=UTC)
    else:
        dt: datetime = dt.astimezone(UTC)
    return dt.isoformat()


def get_request_id(request: Request) -> str | None:
    return request.headers.get(
        "x-request-id", getattr(request.state, "request_id", None)
    )
