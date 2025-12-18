"""Tests for Batches operations."""

import pytest
from unittest.mock import patch

from batchrouter import BatchRouter, BatchJob, BatchCreateResponse


class TestBatches:
    """Test batch operations."""

    @pytest.fixture
    def client(self, mock_client):
        """Create a client with mocked HTTP."""
        return BatchRouter(api_key="br_test_key_123")

    def test_create_batch_minimal(self, client):
        """Test creating a batch with minimal parameters."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "id": "batch_123",
                "status": "pending",
                "model": "gpt-4o",
                "provider_id": "prov_1",
                "provider_name": "openai",
                "estimated_cost": 0.05,
            }

            result = client.batches.create(dataset_name="my-dataset")

            assert isinstance(result, BatchCreateResponse)
            assert result.id == "batch_123"
            assert result.status == "pending"
            assert result.model == "gpt-4o"
            mock_request.assert_called_once_with(
                "POST",
                "/v1/batches",
                json={"dataset_name": "my-dataset", "model": "auto"},
            )

    def test_create_batch_with_model(self, client):
        """Test creating a batch with specific model."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "id": "batch_123",
                "status": "pending",
                "model": "claude-3.5-sonnet",
            }

            result = client.batches.create(
                dataset_name="my-dataset",
                model="claude-3.5-sonnet",
            )

            assert result.model == "claude-3.5-sonnet"
            call_args = mock_request.call_args
            assert call_args[1]["json"]["model"] == "claude-3.5-sonnet"

    def test_create_batch_with_provider(self, client):
        """Test creating a batch with specific provider."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "id": "batch_123",
                "status": "pending",
                "model": "gpt-4o",
                "provider_name": "openai",
            }

            result = client.batches.create(
                dataset_name="my-dataset",
                model="gpt-4o",
                provider="openai",
            )

            call_args = mock_request.call_args
            assert call_args[1]["json"]["provider"] == "openai"

    def test_create_batch_with_description(self, client):
        """Test creating a batch with description."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "id": "batch_123",
                "status": "pending",
                "model": "auto",
            }

            client.batches.create(
                dataset_name="my-dataset",
                description="Test batch job",
            )

            call_args = mock_request.call_args
            assert call_args[1]["json"]["description"] == "Test batch job"

    def test_list_batches(self, client):
        """Test listing batch jobs."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "data": [
                    {
                        "id": "batch_1",
                        "dataset_id": "ds_1",
                        "model": "gpt-4o",
                        "status": "completed",
                        "request_count": 100,
                        "completed_count": 100,
                        "created_at": "2025-01-01T00:00:00Z",
                    },
                    {
                        "id": "batch_2",
                        "dataset_id": "ds_2",
                        "model": "claude-3.5-sonnet",
                        "status": "processing",
                        "request_count": 50,
                        "completed_count": 25,
                        "created_at": "2025-01-02T00:00:00Z",
                    },
                ],
                "total": 2,
            }

            result = client.batches.list()

            assert len(result) == 2
            assert all(isinstance(b, BatchJob) for b in result)
            assert result[0].status == "completed"
            assert result[1].status == "processing"

    def test_list_batches_with_pagination(self, client):
        """Test listing batches with pagination."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {"data": [], "total": 0}

            client.batches.list(page=3, page_size=10)

            mock_request.assert_called_once_with(
                "GET",
                "/v1/batches",
                params={"page": 3, "page_size": 10},
            )

    def test_get_batch(self, client):
        """Test getting a batch by ID."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "id": "batch_123",
                "dataset_id": "ds_123",
                "dataset_name": "my-dataset",
                "model": "gpt-4o",
                "provider_name": "openai",
                "status": "processing",
                "request_count": 100,
                "completed_count": 75,
                "failed_count": 2,
                "input_tokens": 50000,
                "output_tokens": 25000,
                "estimated_cost": 0.05,
                "actual_cost": None,
                "has_results": False,
                "has_errors": True,
                "created_at": "2025-01-01T00:00:00Z",
            }

            result = client.batches.get("batch_123")

            assert isinstance(result, BatchJob)
            assert result.id == "batch_123"
            assert result.status == "processing"
            assert result.completed_count == 75
            assert result.request_count == 100
            mock_request.assert_called_once_with("GET", "/v1/batches/batch_123")

    def test_cancel_batch(self, client):
        """Test cancelling a batch job."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "id": "batch_123",
                "dataset_id": "ds_123",
                "model": "gpt-4o",
                "status": "cancelled",
                "created_at": "2025-01-01T00:00:00Z",
            }

            result = client.batches.cancel("batch_123")

            assert isinstance(result, BatchJob)
            assert result.status == "cancelled"
            mock_request.assert_called_once_with("POST", "/v1/batches/batch_123/cancel")

    def test_download_results(self, client):
        """Test downloading batch results."""
        with patch.object(client, "_request_raw") as mock_request:
            mock_request.return_value = b'{"custom_id": "1", "response": {"content": "Hi!"}}\n'

            result = client.batches.download_results("batch_123")

            assert isinstance(result, bytes)
            assert b"custom_id" in result
            mock_request.assert_called_once_with("GET", "/v1/batches/batch_123/results")

    def test_download_errors(self, client):
        """Test downloading batch errors."""
        with patch.object(client, "_request_raw") as mock_request:
            mock_request.return_value = b'{"custom_id": "1", "error": "Rate limited"}\n'

            result = client.batches.download_errors("batch_123")

            assert isinstance(result, bytes)
            assert b"error" in result
            mock_request.assert_called_once_with("GET", "/v1/batches/batch_123/errors")
