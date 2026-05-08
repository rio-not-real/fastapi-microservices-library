"""Middleware classes for common API concerns."""

import logging
import time
import uuid
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware as CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware as GZipMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fml.errors import InternalServerError
from fml.exception_handlers import ProblemDetailResponse

logger = logging.getLogger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Propagate or create an X-Request-ID header."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Attach the request ID to request state and X-Request-ID."""

        request_id: str = request.headers.get("X-Request-ID", uuid.uuid4().hex)
        request.state.request_id: str = request_id
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """Measure request processing time."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Track request start time and set X-Process-Time."""

        start_time: int | float = time.perf_counter()
        request.state.request_start_time: int | float = start_time
        response: Response = await call_next(request)
        process_time: int | float = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.6f}"
        return response


class ExceptionMiddleware(BaseHTTPMiddleware):
    """Convert unexpected exceptions into generic problem responses."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Handle downstream exceptions without exposing implementation details."""

        try:
            response: Response = await call_next(request)
        except Exception:
            logger.exception("Unexpected error occurred")
            _exc = InternalServerError()
            return ProblemDetailResponse(
                status=_exc.status_code,
                title=_exc.title,
                detail=_exc.detail,
            )
        return response
