"""BatchRouter client for interacting with the API."""

from __future__ import annotations

import os
from typing import Any

import httpx

from batchrouter.batches import Batches
from batchrouter.datasets import Datasets
from batchrouter.exceptions import (
    AuthenticationError,
    BatchRouterError,
    NotFoundError,
    ServerError,
    ValidationError,
)
from batchrouter.models import Models

DEFAULT_BASE_URL = "https://api.batchrouter.ai"
DEFAULT_TIMEOUT = 60.0


class BatchRouter:
    """BatchRouter API client.

    Args:
        api_key: Your BatchRouter API key (starts with "br_").
            If not provided, will look for BATCHROUTER_API_KEY env var.
        base_url: API base URL. Defaults to https://api.batchrouter.ai
        timeout: Request timeout in seconds. Defaults to 60.

    Example:
        ```python
        from batchrouter import BatchRouter

        client = BatchRouter(api_key="br_...")

        # Upload a dataset
        dataset = client.datasets.upload("data.jsonl", name="my-dataset")

        # Create a batch job
        batch = client.batches.create(dataset_name="my-dataset", model="gpt-4o")

        # Check status
        status = client.batches.get(batch.id)
        print(f"Status: {status.status}, Progress: {status.completed_count}/{status.request_count}")

        # Download results when complete
        if status.status == "completed":
            results = client.batches.download_results(batch.id)
            with open("results.jsonl", "wb") as f:
                f.write(results)
        ```
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self._api_key = api_key or os.environ.get("BATCHROUTER_API_KEY")
        if not self._api_key:
            raise AuthenticationError(
                "API key is required. Pass api_key parameter or set BATCHROUTER_API_KEY env var."
            )

        if not self._api_key.startswith("br_"):
            raise AuthenticationError("Invalid API key format. API keys should start with 'br_'.")

        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.Client(timeout=timeout)

        # Initialize resource classes
        self.datasets = Datasets(self)
        self.batches = Batches(self)
        self.models = Models(self)

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "User-Agent": "batchrouter-python/0.1.0",
        }

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        try:
            error_data = response.json()
            message = error_data.get("detail", str(error_data))
        except Exception:
            message = response.text or f"HTTP {response.status_code}"

        if response.status_code == 401:
            raise AuthenticationError(message)
        elif response.status_code == 404:
            raise NotFoundError(message)
        elif response.status_code == 422:
            raise ValidationError(message)
        elif response.status_code >= 500:
            raise ServerError(message)
        else:
            raise BatchRouterError(message, status_code=response.status_code)

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
    ) -> Any:
        """Make an API request and return JSON response."""
        url = f"{self._base_url}/api{path}"
        headers = self._get_headers()

        # Don't send Content-Type for multipart file uploads
        if files:
            del headers["Content-Type"]

        response = self._client.request(
            method,
            url,
            headers=headers,
            params=params,
            json=json,
            data=data,
            files=files,
        )

        if not response.is_success:
            self._handle_error(response)

        if response.status_code == 204:
            return None

        return response.json()

    def _request_raw(self, method: str, path: str) -> bytes:
        """Make an API request and return raw bytes (for file downloads)."""
        url = f"{self._base_url}/api{path}"
        headers = self._get_headers()

        response = self._client.request(method, url, headers=headers)

        if not response.is_success:
            self._handle_error(response)

        return response.content

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "BatchRouter":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
