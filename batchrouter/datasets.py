"""Dataset operations for BatchRouter SDK."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

from batchrouter.types import Dataset, DatasetUploadResponse

if TYPE_CHECKING:
    from batchrouter.client import BatchRouter


class Datasets:
    """Dataset operations."""

    def __init__(self, client: "BatchRouter"):
        self._client = client

    def upload(
        self,
        file: str | Path | BinaryIO,
        name: str | None = None,
        description: str | None = None,
    ) -> DatasetUploadResponse:
        """Upload a new dataset.

        Args:
            file: Path to JSONL file or file-like object
            name: Optional name for the dataset (defaults to filename)
            description: Optional description

        Returns:
            DatasetUploadResponse with id, name, and status
        """
        if isinstance(file, (str, Path)):
            file_path = Path(file)
            if name is None:
                name = file_path.name
            with open(file_path, "rb") as f:
                return self._upload_file(f, name, description)
        else:
            if name is None:
                raise ValueError("name is required when uploading from file-like object")
            return self._upload_file(file, name, description)

    def _upload_file(
        self,
        file: BinaryIO,
        name: str,
        description: str | None,
    ) -> DatasetUploadResponse:
        """Internal method to upload a file."""
        files = {"file": (name, file, "application/jsonl")}
        data = {"name": name}
        if description:
            data["description"] = description

        response = self._client._request(
            "POST",
            "/v1/datasets",
            files=files,
            data=data,
        )
        return DatasetUploadResponse(**response)

    def list(self, page: int = 1, page_size: int = 20) -> list[Dataset]:
        """List all datasets.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            List of Dataset objects
        """
        response = self._client._request(
            "GET",
            "/v1/datasets",
            params={"page": page, "page_size": page_size},
        )
        return [Dataset(**d) for d in response.get("data", [])]

    def get(self, dataset_id: str) -> Dataset:
        """Get a dataset by ID.

        Args:
            dataset_id: The dataset ID

        Returns:
            Dataset object
        """
        response = self._client._request("GET", f"/v1/datasets/{dataset_id}")
        return Dataset(**response)

    def get_by_name(self, name: str) -> Dataset | None:
        """Get a dataset by name.

        Args:
            name: The dataset name

        Returns:
            Dataset object or None if not found
        """
        datasets = self.list(page_size=100)
        for dataset in datasets:
            if dataset.name == name:
                return dataset
        return None

    def delete(self, dataset_id: str) -> None:
        """Delete a dataset.

        Args:
            dataset_id: The dataset ID to delete
        """
        self._client._request("DELETE", f"/v1/datasets/{dataset_id}")
