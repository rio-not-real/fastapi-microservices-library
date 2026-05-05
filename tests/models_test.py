from datetime import datetime

from fml.models import HealthCheck
from fml.utils import utc_now


def test_health_check_default_timestamp_is_fresh():
    before: datetime = utc_now()
    health_check = HealthCheck(status="up")
    after: datetime = utc_now()

    assert before <= health_check.timestamp <= after
