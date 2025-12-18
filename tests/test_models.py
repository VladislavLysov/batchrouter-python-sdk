"""Tests for Models operations."""

import pytest
from unittest.mock import patch

from batchrouter import BatchRouter, Model, ModelProvider


class TestModels:
    """Test model operations."""

    @pytest.fixture
    def client(self, mock_client):
        """Create a client with mocked HTTP."""
        return BatchRouter(api_key="br_test_key_123")

    def test_list_models(self, client):
        """Test listing all models."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = [
                {
                    "name": "gpt-4o",
                    "display_name": "GPT-4o",
                    "description": "OpenAI's latest model",
                    "context_window": 128000,
                    "max_output_tokens": 4096,
                    "capabilities": ["chat", "vision"],
                    "providers": [
                        {
                            "id": "prov_1",
                            "name": "openai",
                            "batch_input_price_per_1m": 1.25,
                            "batch_output_price_per_1m": 5.0,
                            "is_batch_supported": True,
                        },
                        {
                            "id": "prov_2",
                            "name": "together",
                            "batch_input_price_per_1m": 1.0,
                            "batch_output_price_per_1m": 4.0,
                            "is_batch_supported": True,
                        },
                    ],
                },
                {
                    "name": "claude-3.5-sonnet",
                    "display_name": "Claude 3.5 Sonnet",
                    "context_window": 200000,
                    "providers": [
                        {
                            "id": "prov_3",
                            "name": "anthropic",
                            "batch_input_price_per_1m": 1.5,
                            "batch_output_price_per_1m": 7.5,
                        },
                    ],
                },
            ]

            result = client.models.list()

            assert len(result) == 2
            assert all(isinstance(m, Model) for m in result)

            # Check first model
            gpt4o = result[0]
            assert gpt4o.name == "gpt-4o"
            assert gpt4o.display_name == "GPT-4o"
            assert gpt4o.context_window == 128000
            assert "vision" in gpt4o.capabilities
            assert len(gpt4o.providers) == 2

            # Check providers
            openai_provider = gpt4o.providers[0]
            assert isinstance(openai_provider, ModelProvider)
            assert openai_provider.name == "openai"
            assert openai_provider.batch_input_price_per_1m == 1.25

    def test_list_models_empty(self, client):
        """Test listing models when none available."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = []

            result = client.models.list()

            assert result == []

    def test_get_model(self, client):
        """Test getting a specific model."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "name": "gpt-4o",
                "display_name": "GPT-4o",
                "description": "OpenAI's flagship model",
                "context_window": 128000,
                "max_output_tokens": 4096,
                "capabilities": ["chat", "vision", "function_calling"],
                "is_deprecated": False,
                "providers": [
                    {
                        "id": "prov_1",
                        "name": "openai",
                        "batch_input_price_per_1m": 1.25,
                        "batch_output_price_per_1m": 5.0,
                    },
                ],
            }

            result = client.models.get("gpt-4o")

            assert isinstance(result, Model)
            assert result.name == "gpt-4o"
            assert result.context_window == 128000
            assert not result.is_deprecated
            mock_request.assert_called_once_with("GET", "/v1/routing/models/gpt-4o")

    def test_get_model_not_found(self, client):
        """Test getting a model that doesn't exist."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = None

            result = client.models.get("nonexistent-model")

            assert result is None

    def test_model_provider_fields(self, client):
        """Test that model provider has all expected fields."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = [
                {
                    "name": "test-model",
                    "providers": [
                        {
                            "id": "prov_1",
                            "name": "test-provider",
                            "batch_input_price_per_1m": 2.5,
                            "batch_output_price_per_1m": 10.0,
                            "is_batch_supported": True,
                        },
                    ],
                },
            ]

            result = client.models.list()
            provider = result[0].providers[0]

            assert provider.id == "prov_1"
            assert provider.name == "test-provider"
            assert provider.batch_input_price_per_1m == 2.5
            assert provider.batch_output_price_per_1m == 10.0
            assert provider.is_batch_supported is True
