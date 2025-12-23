import logging
import time
import uuid
from typing import Awaitable, Callable

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware as CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware as GZipMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fml.constants import HTTP_500_DETAIL, HTTP_500_TITLE
from fml.exceptions import ProblemDetailsResponse

logger = logging.getLogger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        response: Response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.perf_counter()
        response: Response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.6f}"
        return response


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.exception(exc)
            return ProblemDetailsResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                title=HTTP_500_TITLE,
                detail=HTTP_500_DETAIL,
            )
        else:
            return response
