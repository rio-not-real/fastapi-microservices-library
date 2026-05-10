"""Reusable pagination, sorting, and filtering models."""

from enum import StrEnum
from math import ceil
from typing import Annotated, Generic, Self, TypeVar

from pydantic import Field, NonNegativeInt, PositiveInt, computed_field

from fml.models import CustomBaseModel


class SortOrder(StrEnum):
    """Sort direction for query results."""

    asc = "asc"
    desc = "desc"


class PaginationParams(CustomBaseModel):
    """Query parameters for offset-based pagination."""

    page: Annotated[
        PositiveInt,
        Field(ge=1, description="Page number (1-indexed)."),
    ] = 1
    size: Annotated[
        PositiveInt,
        Field(
            ge=1,
            le=100,
            description="Number of items per page.",
        ),
    ] = 20

    @computed_field
    @property
    def offset(self) -> NonNegativeInt:
        """Zero-based offset for database queries."""
        return (self.page - 1) * self.size


class SortParams(CustomBaseModel):
    """Query parameters for single-field sorting."""

    sort_by: Annotated[
        str,
        Field(
            min_length=1,
            max_length=128,
            description="Field name to sort by.",
        ),
    ]
    sort_order: Annotated[
        SortOrder,
        Field(
            description="Sort direction.",
            examples=["asc", "desc"],
        ),
    ]

    def __str__(self) -> str:
        """String representation for use in SQL ORDER BY clauses."""
        return f"{self.sort_by} {self.sort_order}"


class PaginationMeta(CustomBaseModel):
    """Pagination metadata included in paginated responses."""

    page: Annotated[
        PositiveInt,
        Field(ge=1, description="Current page number (1-indexed)."),
    ]
    size: Annotated[
        NonNegativeInt,
        Field(ge=0, description="Number of items per page."),
    ]
    total_items: Annotated[
        NonNegativeInt,
        Field(ge=0, description="Total number of items across all pages."),
    ]
    total_pages: Annotated[
        NonNegativeInt,
        Field(ge=0, description="Total number of pages."),
    ]
    has_next: Annotated[
        bool,
        Field(description="Whether a next page exists."),
    ]
    has_previous: Annotated[
        bool,
        Field(description="Whether a previous page exists."),
    ]

    @classmethod
    def from_params(
        cls,
        page: int,
        size: int,
        total_items: int,
    ) -> Self:
        """Create metadata from page number, page size, and total count."""
        total_pages: int = ceil(total_items / size) if size > 0 else 0
        return cls(
            page=page,
            size=size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )


T = TypeVar("T")


class Page(CustomBaseModel, Generic[T]):
    """Generic paginated response wrapper.

    Parameterize with an 'item' model to get typed responses::

        @app.get("/books", response_model=Page[Book])
        async def list_books(...) -> Page[Book]:
            ...
    """

    items: Annotated[list[T], Field(description="The items on the current page.")]
    pagination: Annotated[PaginationMeta, Field(description="Pagination metadata.")]

    @classmethod
    def create(
        cls,
        items: list[T],
        page: int,
        size: int,
        total_items: int,
    ) -> Self:
        """Build a paginated response from items and pagination info."""
        return cls(
            items=items,
            pagination=PaginationMeta.from_params(
                page=page, size=size, total_items=total_items
            ),
        )
