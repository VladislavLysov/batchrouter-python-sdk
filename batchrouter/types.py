"""Type definitions for BatchRouter SDK."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class Dataset(BaseModel):
    """A dataset containing JSONL data for batch processing."""

    id: str
    name: str
    description: str | None = None
    file_size: int | None = None
    record_count: int | None = None
    status: str
    validation_error: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class DatasetUploadResponse(BaseModel):
    """Response when uploading a new dataset."""

    id: str
    name: str
    status: str


class ModelProvider(BaseModel):
    """A provider offering a specific model."""

    id: str
    name: str
    batch_input_price_per_1m: float | None = None
    batch_output_price_per_1m: float | None = None
    is_batch_supported: bool = True


class Model(BaseModel):
    """An LLM model available for batch processing."""

    name: str
    display_name: str | None = None
    description: str | None = None
    context_window: int | None = None
    max_output_tokens: int | None = None
    capabilities: list[str] = []
    is_deprecated: bool = False
    release_date: str | None = None
    providers: list[ModelProvider] = []


class BatchJob(BaseModel):
    """A batch job for processing LLM requests."""

    id: str
    dataset_id: str
    dataset_name: str | None = None
    model: str
    provider_id: str | None = None
    provider_name: str | None = None
    status: str
    description: str | None = None
    error_message: str | None = None
    request_count: int | None = None
    completed_count: int | None = None
    failed_count: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    estimated_cost: float | None = None
    actual_cost: float | None = None
    has_results: bool = False
    has_errors: bool = False
    created_at: datetime
    submitted_at: datetime | None = None
    completed_at: datetime | None = None


class BatchCreateRequest(BaseModel):
    """Request to create a new batch job."""

    dataset_name: str
    model: str = "auto"
    provider: str | None = None
    description: str | None = None


class BatchCreateResponse(BaseModel):
    """Response when creating a new batch job."""

    id: str
    status: str
    model: str
    provider_id: str | None = None
    provider_name: str | None = None
    estimated_cost: float | None = None


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""

    data: list[Any]
    total: int
    page: int
    page_size: int
    has_more: bool
