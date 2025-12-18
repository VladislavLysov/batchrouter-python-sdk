"""Pytest fixtures for BatchRouter SDK tests."""

import pytest
import httpx
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_client():
    """Create a mock httpx client."""
    with patch("httpx.Client") as mock:
        client_instance = MagicMock()
        mock.return_value = client_instance
        yield client_instance


@pytest.fixture
def api_key():
    """Test API key."""
    return "br_test_key_123456789"
