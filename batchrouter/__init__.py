"""BatchRouter Python SDK - Cost-optimized batch LLM inference routing."""

from batchrouter.client import BatchRouter
from batchrouter.exceptions import (
    AuthenticationError,
    BatchRouterError,
    NotFoundError,
    ServerError,
    ValidationError,
)
from batchrouter.types import (
    BatchCreateResponse,
    BatchJob,
    Dataset,
    DatasetUploadResponse,
    Model,
    ModelProvider,
)

__version__ = "0.1.0"

__all__ = [
    # Client
    "BatchRouter",
    # Types
    "Dataset",
    "DatasetUploadResponse",
    "Model",
    "ModelProvider",
    "BatchJob",
    "BatchCreateResponse",
    # Exceptions
    "BatchRouterError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "ServerError",
]
