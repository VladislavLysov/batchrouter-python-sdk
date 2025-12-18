"""Tests for BatchRouter client initialization."""

import os
import pytest
from unittest.mock import patch, MagicMock

from batchrouter import BatchRouter
from batchrouter.exceptions import AuthenticationError


class TestClientInit:
    """Test client initialization."""

    def test_init_with_api_key(self, mock_client):
        """Test initialization with explicit API key."""
        client = BatchRouter(api_key="br_test_key_123")
        assert client._api_key == "br_test_key_123"
        assert client._base_url == "https://api.batchrouter.ai"

    def test_init_with_env_var(self, mock_client):
        """Test initialization with environment variable."""
        with patch.dict(os.environ, {"BATCHROUTER_API_KEY": "br_env_key_456"}):
            client = BatchRouter()
            assert client._api_key == "br_env_key_456"

    def test_init_without_api_key_raises(self, mock_client):
        """Test that missing API key raises AuthenticationError."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove the env var if it exists
            os.environ.pop("BATCHROUTER_API_KEY", None)
            with pytest.raises(AuthenticationError) as exc_info:
                BatchRouter()
            assert "API key is required" in str(exc_info.value)

    def test_init_with_invalid_key_format(self, mock_client):
        """Test that invalid key format raises AuthenticationError."""
        with pytest.raises(AuthenticationError) as exc_info:
            BatchRouter(api_key="invalid_key_without_prefix")
        assert "should start with 'br_'" in str(exc_info.value)

    def test_init_with_custom_base_url(self, mock_client):
        """Test initialization with custom base URL."""
        client = BatchRouter(
            api_key="br_test_key_123",
            base_url="https://custom.api.com",
        )
        assert client._base_url == "https://custom.api.com"

    def test_init_with_custom_timeout(self, mock_client):
        """Test initialization with custom timeout."""
        client = BatchRouter(
            api_key="br_test_key_123",
            timeout=120.0,
        )
        assert client._timeout == 120.0

    def test_client_has_resources(self, mock_client):
        """Test that client has all resource classes."""
        client = BatchRouter(api_key="br_test_key_123")
        assert hasattr(client, "datasets")
        assert hasattr(client, "batches")
        assert hasattr(client, "models")

    def test_context_manager(self, mock_client):
        """Test client works as context manager."""
        with BatchRouter(api_key="br_test_key_123") as client:
            assert client._api_key == "br_test_key_123"
        # close() should have been called
        mock_client.close.assert_called_once()


class TestClientHeaders:
    """Test client headers."""

    def test_get_headers(self, mock_client):
        """Test that headers are correctly generated."""
        client = BatchRouter(api_key="br_test_key_123")
        headers = client._get_headers()

        assert headers["Authorization"] == "Bearer br_test_key_123"
        assert headers["Content-Type"] == "application/json"
        assert "User-Agent" in headers
        assert "batchrouter-python" in headers["User-Agent"]
