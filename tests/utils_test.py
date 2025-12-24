from datetime import datetime, timedelta, timezone

import pytest

from fml import utils


def test_utc_now():
    now: datetime = utils.utc_now()

    assert isinstance(now, datetime)
    assert now.tzinfo is not None
    assert now.utcoffset() == timezone.utc.utcoffset(now)


def test_utc_now_str():
    now_str: str = utils.utc_now_str()

    assert isinstance(now_str, str)
    assert now_str.endswith("+00:00")
    assert isinstance(datetime.fromisoformat(now_str), datetime)


@pytest.mark.parametrize(
    "dt, expected",
    [
        (
            datetime(2025, 1, 1, 12, 0, 0),
            "2025-01-01T12:00:00+00:00",
        ),
        (
            datetime(2025, 1, 1, 11, 0, 0, tzinfo=timezone.utc),
            "2025-01-01T11:00:00+00:00",
        ),
        (
            datetime(2025, 1, 1, 5, 0, 0, tzinfo=timezone(timedelta(hours=-5))),
            "2025-01-01T10:00:00+00:00",
        ),
    ],
)
def test_dt_to_utc_str(dt: datetime, expected: str):
    output: str = utils.dt_to_utc_str(dt)

    assert isinstance(output, str)
    assert output == expected
