from typing import Annotated

from fastapi.params import Header

RequestIdHeader = Annotated[str | None, Header(alias="X-Request-ID")]
