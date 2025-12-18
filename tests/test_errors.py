"""Tests for error handling."""

import pytest
from unittest.mock import patch, MagicMock
import httpx

from batchrouter import BatchRouter
from batchrouter.exceptions import (
    AuthenticationError,
    NotFoundError,
    ValidationError,
    ServerError,
    BatchRouterError,
)


class TestErrorHandling:
    """Test error handling."""

    @pytest.fixture
    def client(self, mock_client):
        """Create a client with mocked HTTP."""
        return BatchRouter(api_key="br_test_key_123")

    def _make_response(self, status_code: int, json_data: dict | None = None, text: str = ""):
        """Create a mock httpx Response."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = status_code
        response.is_success = 200 <= status_code < 300
        response.text = text
        if json_data:
            response.json.return_value = json_data
        else:
            response.json.side_effect = Exception("No JSON")
        return response

    def test_authentication_error(self, client, mock_client):
        """Test 401 raises AuthenticationError."""
        mock_client.request.return_value = self._make_response(
            401, {"detail": "Invalid API key"}
        )

        with pytest.raises(AuthenticationError) as exc_info:
            client._request("GET", "/v1/test")

        assert "Invalid API key" in str(exc_info.value)
        assert exc_info.value.status_code == 401

    def test_not_found_error(self, client, mock_client):
        """Test 404 raises NotFoundError."""
        mock_client.request.return_value = self._make_response(
            404, {"detail": "Batch not found"}
        )

        with pytest.raises(NotFoundError) as exc_info:
            client._request("GET", "/v1/batches/nonexistent")

        assert "Batch not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404

    def test_validation_error(self, client, mock_client):
        """Test 422 raises ValidationError."""
        mock_client.request.return_value = self._make_response(
            422, {"detail": "Invalid dataset format"}
        )

        with pytest.raises(ValidationError) as exc_info:
            client._request("POST", "/v1/datasets")

        assert "Invalid dataset format" in str(exc_info.value)
        assert exc_info.value.status_code == 422

    def test_server_error(self, client, mock_client):
        """Test 500+ raises ServerError."""
        mock_client.request.return_value = self._make_response(
            500, {"detail": "Internal server error"}
        )

        with pytest.raises(ServerError) as exc_info:
            client._request("GET", "/v1/test")

        assert exc_info.value.status_code == 500

    def test_server_error_502(self, client, mock_client):
        """Test 502 raises ServerError."""
        mock_client.request.return_value = self._make_response(
            502, text="Bad Gateway"
        )

        with pytest.raises(ServerError):
            client._request("GET", "/v1/test")

    def test_generic_error(self, client, mock_client):
        """Test other status codes raise BatchRouterError."""
        mock_client.request.return_value = self._make_response(
            429, {"detail": "Rate limited"}
        )

        with pytest.raises(BatchRouterError) as exc_info:
            client._request("GET", "/v1/test")

        assert "Rate limited" in str(exc_info.value)
        assert exc_info.value.status_code == 429

    def test_error_without_json(self, client, mock_client):
        """Test error handling when response has no JSON."""
        response = self._make_response(500, text="Internal Server Error")
        response.json.side_effect = Exception("No JSON")
        mock_client.request.return_value = response

        with pytest.raises(ServerError) as exc_info:
            client._request("GET", "/v1/test")

        assert "Internal Server Error" in str(exc_info.value)

    def test_error_with_empty_response(self, client, mock_client):
        """Test error handling with empty response."""
        response = self._make_response(500, text="")
        response.json.side_effect = Exception("No JSON")
        mock_client.request.return_value = response

        with pytest.raises(ServerError) as exc_info:
            client._request("GET", "/v1/test")

        assert "HTTP 500" in str(exc_info.value)


class TestExceptionAttributes:
    """Test exception attributes."""

    def test_batch_router_error_attributes(self):
        """Test BatchRouterError has correct attributes."""
        error = BatchRouterError("Test error", status_code=400)

        assert error.message == "Test error"
        assert error.status_code == 400
        assert str(error) == "Test error"

    def test_authentication_error_default(self):
        """Test AuthenticationError default message."""
        error = AuthenticationError()

        assert "Invalid or missing API key" in error.message
        assert error.status_code == 401

    def test_not_found_error_default(self):
        """Test NotFoundError default message."""
        error = NotFoundError()

        assert "not found" in error.message.lower()
        assert error.status_code == 404

    def test_validation_error_default(self):
        """Test ValidationError default message."""
        error = ValidationError()

        assert "validation" in error.message.lower()
        assert error.status_code == 422

    def test_server_error_default(self):
        """Test ServerError default message."""
        error = ServerError()

        assert "server error" in error.message.lower()
        assert error.status_code == 500
