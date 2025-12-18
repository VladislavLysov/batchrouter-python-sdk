"""Batch operations for BatchRouter SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING

from batchrouter.types import BatchCreateResponse, BatchJob

if TYPE_CHECKING:
    from batchrouter.client import BatchRouter


class Batches:
    """Batch job operations."""

    def __init__(self, client: "BatchRouter"):
        self._client = client

    def create(
        self,
        dataset_name: str,
        model: str = "auto",
        provider: str | None = None,
        description: str | None = None,
    ) -> BatchCreateResponse:
        """Create a new batch job.

        Args:
            dataset_name: Name of the dataset to process
            model: Model to use (default "auto" for cheapest routing)
            provider: Optional specific provider (e.g., "openai", "anthropic")
            description: Optional job description

        Returns:
            BatchCreateResponse with job id, status, and cost estimate
        """
        payload: dict[str, str | None] = {
            "dataset_name": dataset_name,
            "model": model,
        }
        if provider:
            payload["provider"] = provider
        if description:
            payload["description"] = description

        response = self._client._request("POST", "/v1/batches", json=payload)
        return BatchCreateResponse(**response)

    def list(self, page: int = 1, page_size: int = 20) -> list[BatchJob]:
        """List all batch jobs.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            List of BatchJob objects
        """
        response = self._client._request(
            "GET",
            "/v1/batches",
            params={"page": page, "page_size": page_size},
        )
        return [BatchJob(**b) for b in response.get("data", [])]

    def get(self, batch_id: str) -> BatchJob:
        """Get a batch job by ID.

        Args:
            batch_id: The batch job ID

        Returns:
            BatchJob object with current status and progress
        """
        response = self._client._request("GET", f"/v1/batches/{batch_id}")
        return BatchJob(**response)

    def cancel(self, batch_id: str) -> BatchJob:
        """Cancel a batch job.

        Args:
            batch_id: The batch job ID to cancel

        Returns:
            Updated BatchJob object
        """
        response = self._client._request("POST", f"/v1/batches/{batch_id}/cancel")
        return BatchJob(**response)

    def download_results(self, batch_id: str) -> bytes:
        """Download batch job results as JSONL.

        Args:
            batch_id: The batch job ID

        Returns:
            JSONL content as bytes
        """
        return self._client._request_raw("GET", f"/v1/batches/{batch_id}/results")

    def download_errors(self, batch_id: str) -> bytes:
        """Download batch job errors as JSONL.

        Args:
            batch_id: The batch job ID

        Returns:
            JSONL content as bytes (may be empty if no errors)
        """
        return self._client._request_raw("GET", f"/v1/batches/{batch_id}/errors")
