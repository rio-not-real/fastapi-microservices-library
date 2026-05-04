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
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id: str = request.headers.get("X-Request-ID", uuid.uuid4().hex)
        request.state.request_id: str = request_id
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time: int | float = time.perf_counter()
        request.state.request_start_time: int | float = start_time
        response: Response = await call_next(request)
        process_time: int | float = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.6f}"
        return response


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            response: Response = await call_next(request)
        except Exception:
            logger.exception("Unexpected error occur")
            _exc = InternalServerError()
            return ProblemDetailResponse(
                status=_exc.status_code,
                title=_exc.title,
                detail=_exc.detail,
            )
        return response
