"""JSON response classes for API and problem detail payloads."""

from typing import Any

from pydantic import BaseModel, TypeAdapter
from pydantic_core import PydanticSerializationError
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse as _JSONResponse

from fml.models import ProblemDetail

try:
    import orjson  # ty:ignore[unresolved-import]
except ModuleNotFoundError:
    orjson = None  # ty: ignore[invalid-assignment, unused-ignore-comment, unused-ignore-comment]


class JSONResponse(_JSONResponse):
    """JSON response that serializes Pydantic models and common Python values."""

    def render(self, content: Any) -> bytes:
        """Render response content to JSON bytes."""

        if isinstance(content, BaseModel):
            return content.model_dump_json().encode("utf-8")

        try:
            return TypeAdapter(type(content)).dump_json(content)
        except PydanticSerializationError:
            if orjson is not None:
                return orjson.dumps(
                    content, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY
                )

        return super().render(content)


class ProblemDetailResponse(JSONResponse):
    """Response that renders an RFC 9457 problem detail body."""

    def __init__(
        self,
        headers: dict[str, str] | None = None,
        background: BackgroundTask | None = None,
        problem_detail: ProblemDetail | None = None,
        **kwargs,
    ) -> None:
        self.problem_detail: ProblemDetail = (
            problem_detail or ProblemDetail.model_validate(kwargs, extra="ignore")
        )
        headers: dict[str, str] = {
            key: value
            for key, value in (headers or {}).items()
            if key.lower() != "content-type"
        }
        headers["Content-Type"] = "application/problem+json"

        super().__init__(
            content=self.problem_detail,
            status_code=self.problem_detail.status,
            headers=headers,
            media_type=self.media_type,
            background=background,
        )

    def render(self, content: BaseModel) -> bytes:
        """Render problem detail content without null fields."""

        return content.model_dump_json(exclude_none=True).encode("utf-8")
