import orjson
import pytest
from fastapi.responses import ORJSONResponse
from starlette.background import BackgroundTask
from starlette.exceptions import HTTPException

from fml.exceptions import CustomHTTPException, ProblemDetailsResponse, Unauthorized


class TestCustomHTTPException:
    @pytest.fixture
    def exc(self):
        return CustomHTTPException(detail=None, headers=None)

    def test_raise(self, exc: CustomHTTPException):
        with pytest.raises(HTTPException):
            raise exc

    def test_init_default(self, exc):
        _detail = "The server encountered an unexpected error"

        assert exc.status_code == 500
        assert exc._title == "Server Error"
        assert exc.detail == _detail
        assert exc.type == "https://problems-registry.smartbear.com/server-error/"
        assert repr(exc) == (
            "CustomHTTPException(status_code=500, "
            f"title='Server Error', detail='{_detail}')"
        )
        assert str(exc) == f"500 Server Error: {_detail}"

    @pytest.mark.parametrize(
        "detail",
        [
            "something went wrong",
            None,
        ],
    )
    def test_init_detail(self, detail: str | None):
        exc = CustomHTTPException(detail=detail, headers=None)

        assert exc.detail is not None
        assert isinstance(exc.detail, str)

        if detail is not None:
            assert exc.detail == detail
        else:
            assert exc.detail == "The server encountered an unexpected error"

    @pytest.mark.parametrize(
        "headers",
        [
            None,
            {},
            {"meaning_of_life": 42},
            {"meaning_of_life": 42, "foo": "bar"},
        ],
    )
    def test_init(self, headers: dict[str, str] | None):
        exc = CustomHTTPException(detail=None, headers=headers)

        if headers is None:
            assert exc.headers is None
        else:
            assert exc.headers is not None
            assert all(k.lower() in exc.headers.keys() for k in headers.keys())
            assert all(exc.headers[k.lower()] == v for k, v in headers.items())


class TestUnauthorized:
    @pytest.fixture
    def exc(self):
        return Unauthorized(headers=None)

    def test_raise(self, exc: Unauthorized):
        with pytest.raises(CustomHTTPException):
            raise exc

    def test_init_default(self, exc):
        assert exc.status_code == 401
        assert exc.detail == "The client request missed or malformed its credentials"
        assert exc._title == "Unauthorized"

    @pytest.mark.parametrize(
        "headers",
        [
            {"meaning_of_life": 42},
            {"foo": "bar", "WWW-Authenticate": "Bearer"},
            {},
            None,
        ],
    )
    def test_init_header(self, headers: dict[str, str] | None):
        exc = Unauthorized(headers=headers)

        assert isinstance(exc.headers, dict)
        assert exc.headers["WWW-Authenticate"] == "Bearer"


class TestProblemDetailsResponse:
    @pytest.fixture
    def res(self):
        return ProblemDetailsResponse(title="default")

    def test_init_default(self, res: ProblemDetailsResponse):
        assert isinstance(res, ORJSONResponse)
        assert res.media_type == "application/json"
        assert res.headers["Content-Type"] == "application/problem+json"

        body = orjson.loads(res.body)
        assert isinstance(body, dict)
        assert body["type"] == "about:blank"
        assert body["status"] == 500
        assert body["title"] == "default"

    @pytest.mark.parametrize(
        "headers",
        [
            None,
            {},
            {"foo": "bar"},
            {"meaning_of_life": "42", "foo": "bar"},
        ],
    )
    def test_init_headers(self, headers: dict[str, str] | None):
        kwargs: dict[str, str] = {"title": "default"}
        res = ProblemDetailsResponse(
            headers=headers,
            background=None,
            **kwargs,
        )

        if headers is not None:
            assert all(k.lower() in res.headers.keys() for k in headers.keys())
            assert all(res.headers[k.lower()] == v for k, v in headers.items())
        assert res.headers["Content-Type"] == "application/problem+json"

    @staticmethod
    async def _async_callable() -> None:
        import asyncio

        await asyncio.sleep(1)

    @pytest.mark.parametrize(
        "background",
        [
            None,
            BackgroundTask(lambda: None),
            BackgroundTask(_async_callable),
        ],
    )
    def test_init_background(self, background: BackgroundTask | None):
        kwargs: dict[str, str] = {"title": "default"}
        res = ProblemDetailsResponse(
            headers=None,
            background=background,
            **kwargs,
        )

        if background is not None:
            assert res.background is not None
            assert res.background == background
        else:
            assert res.background is None
