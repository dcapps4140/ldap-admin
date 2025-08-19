import pytest
from unittest.mock import patch

@pytest.fixture
def disable_rate_limits(app):
    """Disable rate limits for testing."""
    original_enabled = app.config.get('RATELIMIT_ENABLED', True)
    app.config['RATELIMIT_ENABLED'] = False
    yield
    app.config['RATELIMIT_ENABLED'] = original_enabled

@pytest.fixture
def with_rate_limits(app):
    """Ensure rate limits are enabled for testing."""
    original_enabled = app.config.get('RATELIMIT_ENABLED', True)
    app.config['RATELIMIT_ENABLED'] = True
    yield
    app.config['RATELIMIT_ENABLED'] = original_enabled
