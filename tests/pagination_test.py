import pytest
from pydantic import ValidationError

from fml.models import CustomBaseModel
from fml.pagination import (
    Page,
    PaginationMeta,
    PaginationParams,
    SortOrder,
    SortParams,
)
from fml.types import PaginationQuery, SortQuery

# -- SortOrder --


def test_sort_order_values():
    assert SortOrder.asc == "asc"
    assert SortOrder.desc == "desc"


def test_sort_order_is_str():
    assert isinstance(SortOrder.asc, str)
    assert isinstance(SortOrder.desc, str)


# -- PaginationParams --


def test_pagination_params_defaults():
    params = PaginationParams()
    assert params.page == 1
    assert params.size == 20


def test_pagination_params_offset():
    assert PaginationParams(page=1, size=10).offset == 0
    assert PaginationParams(page=3, size=10).offset == 20
    assert PaginationParams(page=2, size=50).offset == 50


def test_pagination_params_page_min():
    with pytest.raises(ValidationError):
        PaginationParams(page=0)


def test_pagination_params_size_min():
    with pytest.raises(ValidationError):
        PaginationParams(size=0)


def test_pagination_params_size_max():
    with pytest.raises(ValidationError):
        PaginationParams(size=101)


@pytest.mark.parametrize(
    ("page", "size"),
    [(1, 1), (1, 100), (5, 25), (100, 10)],
)
def test_pagination_params_valid(page, size):
    params = PaginationParams(page=page, size=size)
    assert params.page == page
    assert params.size == size


# -- SortParams --


def test_sort_params_required_fields():
    with pytest.raises(ValidationError):
        SortParams()  # ty:ignore[missing-argument]


def test_sort_params_valid():
    params = SortParams(sort_by="created_at", sort_order=SortOrder.desc)
    assert params.sort_by == "created_at"
    assert params.sort_order is SortOrder.desc


def test_sort_params_sort_by_empty_string():
    with pytest.raises(ValidationError):
        SortParams(sort_by="")  # ty:ignore[missing-argument]


# -- PaginationMeta --


def test_from_params_single_page():
    meta = PaginationMeta.from_params(page=1, size=20, total_items=5)
    assert meta.page == 1
    assert meta.size == 20
    assert meta.total_items == 5
    assert meta.total_pages == 1
    assert meta.has_next is False
    assert meta.has_previous is False


def test_from_params_multiple_pages():
    meta = PaginationMeta.from_params(page=2, size=20, total_items=50)
    assert meta.total_pages == 3
    assert meta.has_next is True
    assert meta.has_previous is True


def test_from_params_last_page():
    meta = PaginationMeta.from_params(page=3, size=20, total_items=50)
    assert meta.has_next is False
    assert meta.has_previous is True


def test_from_params_zero_items():
    meta = PaginationMeta.from_params(page=1, size=20, total_items=0)
    assert meta.total_pages == 0
    assert meta.has_next is False
    assert meta.has_previous is False


def test_from_params_exact_division():
    meta = PaginationMeta.from_params(page=1, size=20, total_items=40)
    assert meta.total_pages == 2


def test_from_params_partial_last_page():
    meta = PaginationMeta.from_params(page=1, size=20, total_items=41)
    assert meta.total_pages == 3


# -- Page --


class _Item(CustomBaseModel):
    id: int
    name: str


def test_page_create():
    items = [_Item(id=1, name="a"), _Item(id=2, name="b")]
    page = Page.create(items=items, page=1, size=20, total_items=2)
    assert page.items == items
    assert page.pagination.page == 1
    assert page.pagination.total_items == 2
    assert page.pagination.total_pages == 1


def test_page_empty_items():
    page = Page.create(items=[], page=1, size=20, total_items=0)
    assert page.items == []
    assert page.pagination.total_items == 0
    assert page.pagination.total_pages == 0


def test_page_generic_serialization():
    items = [_Item(id=1, name="a")]
    page = Page[_Item].create(items=items, page=1, size=10, total_items=1)
    data = page.model_dump()
    assert data["items"] == [{"id": 1, "name": "a"}]
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["total_items"] == 1


# -- Integration: FastAPI endpoint --


def test_pagination_query_params_in_endpoint(app, client):
    @app.get("/items")
    async def list_items(
        pagination: PaginationQuery,
        sort: SortQuery,
    ):
        return {
            "page": pagination.page,
            "size": pagination.size,
            "offset": pagination.offset,
            "sort_by": sort.sort_by,
            "sort_order": sort.sort_order,
        }

    response = client.get("/items")
    assert response.status_code == 422

    response = client.get("/items?sort_by=name&sort_order=asc")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 20
    assert data["offset"] == 0
    assert data["sort_by"] == "name"
    assert data["sort_order"] == "asc"

    response = client.get("/items?page=3&size=10&sort_by=name&sort_order=desc")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 3
    assert data["size"] == 10
    assert data["offset"] == 20
    assert data["sort_by"] == "name"
    assert data["sort_order"] == "desc"


def test_page_response_model_in_endpoint(app, client):
    @app.get("/items", response_model=Page[_Item])
    async def list_items(pagination: PaginationQuery):
        items = [_Item(id=i, name=f"item-{i}") for i in range(1, 4)]
        return Page.create(
            items=items,
            page=pagination.page,
            size=pagination.size,
            total_items=25,
        )

    response = client.get("/items?page=2&size=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["items"][0] == {"id": 1, "name": "item-1"}
    assert data["pagination"]["page"] == 2
    assert data["pagination"]["size"] == 3
    assert data["pagination"]["total_items"] == 25
    assert data["pagination"]["total_pages"] == 9
    assert data["pagination"]["has_next"] is True
    assert data["pagination"]["has_previous"] is True
