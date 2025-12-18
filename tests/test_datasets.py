"""Tests for Datasets operations."""

import io
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from batchrouter import BatchRouter, Dataset, DatasetUploadResponse


class TestDatasets:
    """Test dataset operations."""

    @pytest.fixture
    def client(self, mock_client):
        """Create a client with mocked HTTP."""
        return BatchRouter(api_key="br_test_key_123")

    def test_upload_from_path(self, client, tmp_path):
        """Test uploading a dataset from file path."""
        # Create a temp file
        test_file = tmp_path / "test.jsonl"
        test_file.write_text('{"custom_id": "1", "messages": [{"role": "user", "content": "Hi"}]}')

        # Mock the request
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "id": "ds_123",
                "name": "test.jsonl",
                "status": "pending",
            }

            result = client.datasets.upload(str(test_file))

            assert isinstance(result, DatasetUploadResponse)
            assert result.id == "ds_123"
            assert result.name == "test.jsonl"
            assert result.status == "pending"

    def test_upload_with_custom_name(self, client, tmp_path):
        """Test uploading with custom name."""
        test_file = tmp_path / "test.jsonl"
        test_file.write_text('{"custom_id": "1", "messages": []}')

        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "id": "ds_123",
                "name": "custom-name",
                "status": "pending",
            }

            result = client.datasets.upload(str(test_file), name="custom-name")

            assert result.name == "custom-name"

    def test_upload_from_file_object(self, client):
        """Test uploading from file-like object."""
        file_obj = io.BytesIO(b'{"custom_id": "1", "messages": []}')

        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "id": "ds_123",
                "name": "my-data",
                "status": "pending",
            }

            result = client.datasets.upload(file_obj, name="my-data")

            assert result.id == "ds_123"
            assert result.name == "my-data"

    def test_upload_file_object_requires_name(self, client):
        """Test that file object upload requires name."""
        file_obj = io.BytesIO(b'{"custom_id": "1"}')

        with pytest.raises(ValueError) as exc_info:
            client.datasets.upload(file_obj)
        assert "name is required" in str(exc_info.value)

    def test_list_datasets(self, client):
        """Test listing datasets."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "data": [
                    {
                        "id": "ds_1",
                        "name": "dataset-1",
                        "status": "validated",
                        "record_count": 100,
                        "created_at": "2025-01-01T00:00:00Z",
                    },
                    {
                        "id": "ds_2",
                        "name": "dataset-2",
                        "status": "validated",
                        "record_count": 200,
                        "created_at": "2025-01-02T00:00:00Z",
                    },
                ],
                "total": 2,
            }

            result = client.datasets.list()

            assert len(result) == 2
            assert all(isinstance(d, Dataset) for d in result)
            assert result[0].name == "dataset-1"
            assert result[1].name == "dataset-2"

    def test_list_datasets_with_pagination(self, client):
        """Test listing datasets with pagination."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {"data": [], "total": 0}

            client.datasets.list(page=2, page_size=50)

            mock_request.assert_called_once_with(
                "GET",
                "/v1/datasets",
                params={"page": 2, "page_size": 50},
            )

    def test_get_dataset(self, client):
        """Test getting a dataset by ID."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "id": "ds_123",
                "name": "my-dataset",
                "status": "validated",
                "record_count": 100,
                "file_size": 5000,
                "created_at": "2025-01-01T00:00:00Z",
            }

            result = client.datasets.get("ds_123")

            assert isinstance(result, Dataset)
            assert result.id == "ds_123"
            assert result.name == "my-dataset"
            assert result.record_count == 100
            mock_request.assert_called_once_with("GET", "/v1/datasets/ds_123")

    def test_get_by_name(self, client):
        """Test getting a dataset by name."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "data": [
                    {
                        "id": "ds_1",
                        "name": "other-dataset",
                        "status": "validated",
                        "created_at": "2025-01-01T00:00:00Z",
                    },
                    {
                        "id": "ds_2",
                        "name": "target-dataset",
                        "status": "validated",
                        "created_at": "2025-01-02T00:00:00Z",
                    },
                ],
            }

            result = client.datasets.get_by_name("target-dataset")

            assert result is not None
            assert result.name == "target-dataset"
            assert result.id == "ds_2"

    def test_get_by_name_not_found(self, client):
        """Test getting a dataset by name that doesn't exist."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {"data": []}

            result = client.datasets.get_by_name("nonexistent")

            assert result is None

    def test_delete_dataset(self, client):
        """Test deleting a dataset."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = None

            client.datasets.delete("ds_123")

            mock_request.assert_called_once_with("DELETE", "/v1/datasets/ds_123")
