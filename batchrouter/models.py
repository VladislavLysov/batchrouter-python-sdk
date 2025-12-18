"""Model operations for BatchRouter SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING

from batchrouter.types import Model

if TYPE_CHECKING:
    from batchrouter.client import BatchRouter


class Models:
    """Model listing and information."""

    def __init__(self, client: "BatchRouter"):
        self._client = client

    def list(self) -> list[Model]:
        """List all available models.

        Returns:
            List of Model objects with provider information
        """
        response = self._client._request("GET", "/v1/routing/models")
        return [Model(**m) for m in response]

    def get(self, name: str) -> Model | None:
        """Get a model by name.

        Args:
            name: Model name (e.g., "gpt-4o", "claude-3.5-sonnet")

        Returns:
            Model object or None if not found
        """
        response = self._client._request("GET", f"/v1/routing/models/{name}")
        if response:
            return Model(**response)
        return None
