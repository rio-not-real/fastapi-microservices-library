from typing import Any

from pydantic import BaseModel, TypeAdapter
from pydantic_core import PydanticSerializationError
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse as _JSONResponse

from fml.models import ProblemDetail

try:
    import orjson
except ImportError:
    orjson = None  # ty:ignore[invalid-assignment]


class JSONResponse(_JSONResponse):
    def render(self, content: Any) -> bytes:
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
        headers = headers or {}
        headers.update({"Content-Type": "application/problem+json"})

        super().__init__(
            content=self.problem_detail,
            status_code=self.problem_detail.status,
            headers=headers,
            media_type=self.media_type,
            background=background,
        )

    def render(self, content: BaseModel) -> bytes:
        return content.model_dump_json(exclude_none=True).encode("utf-8")
