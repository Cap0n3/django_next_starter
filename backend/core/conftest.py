"""Project-wide pytest fixtures."""

import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _clear_cache():
    """
    allauth rate limits and DRF throttles count against the cache, which is
    not reset between tests the way the database is. Clear it so one test's
    signup does not rate-limit the next test's verification email.
    """
    cache.clear()
    yield
    cache.clear()
