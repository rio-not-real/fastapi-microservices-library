"""Reusable FastAPI type annotations."""

from typing import Annotated

from fastapi import Depends
from fastapi.params import Header

from fml.pagination import PaginationParams, SortParams

RequestIdHeader = Annotated[str | None, Header(alias="X-Request-ID")]

PaginationQuery = Annotated[PaginationParams, Depends()]
SortQuery = Annotated[SortParams, Depends()]
