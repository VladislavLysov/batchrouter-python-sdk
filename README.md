# BatchRouter Python SDK

Python SDK for [BatchRouter](https://batchrouter.ai) - Cost-optimized batch LLM inference routing.

BatchRouter automatically routes your batch LLM jobs to the cheapest available provider (OpenAI, Anthropic, Together.AI, Fireworks.AI) with up to 50% savings from batch API discounts.

## Installation

```bash
pip install batchrouter
```

## Quick Start

```python
from batchrouter import BatchRouter

# Initialize with your API key
client = BatchRouter(api_key="br_...")
# Or set BATCHROUTER_API_KEY environment variable

# Upload a dataset
dataset = client.datasets.upload("data.jsonl", name="my-dataset")

# Create a batch job (auto-routes to cheapest provider)
batch = client.batches.create(
    dataset_name="my-dataset",
    model="gpt-4o",  # or "auto" for cheapest model
)

print(f"Batch created: {batch.id}")
print(f"Estimated cost: ${batch.estimated_cost:.4f}")

# Check job status
status = client.batches.get(batch.id)
print(f"Status: {status.status}")
print(f"Progress: {status.completed_count}/{status.request_count}")

# Download results when complete
if status.status == "completed":
    results = client.batches.download_results(batch.id)
    with open("results.jsonl", "wb") as f:
        f.write(results)
```

## Dataset Format

BatchRouter uses a unified JSONL format:

```jsonl
{"custom_id": "req-1", "messages": [{"role": "user", "content": "Hello!"}], "max_tokens": 100}
{"custom_id": "req-2", "messages": [{"role": "system", "content": "Be helpful."}, {"role": "user", "content": "Hi!"}]}
```

Each line must have:
- `custom_id`: Unique identifier for the request
- `messages`: Array of message objects with `role` and `content`

Optional fields: `max_tokens`, `temperature`, `top_p`, `stop`, `model`

## API Reference

### Datasets

```python
# Upload a dataset
dataset = client.datasets.upload(
    file="data.jsonl",           # Path or file-like object
    name="my-dataset",           # Optional, defaults to filename
    description="Test dataset",  # Optional
)

# List datasets
datasets = client.datasets.list(page=1, page_size=20)

# Get dataset by ID
dataset = client.datasets.get("dataset-id")

# Get dataset by name
dataset = client.datasets.get_by_name("my-dataset")

# Delete dataset
client.datasets.delete("dataset-id")
```

### Batches

```python
# Create a batch job
batch = client.batches.create(
    dataset_name="my-dataset",
    model="gpt-4o",              # Model name or "auto"
    provider="openai",           # Optional: specific provider
    description="My batch job",  # Optional
)

# List batch jobs
batches = client.batches.list(page=1, page_size=20)

# Get batch job status
batch = client.batches.get("batch-id")

# Cancel a batch job
batch = client.batches.cancel("batch-id")

# Download results (JSONL bytes)
results = client.batches.download_results("batch-id")

# Download errors (JSONL bytes)
errors = client.batches.download_errors("batch-id")
```

### Models

```python
# List available models
models = client.models.list()

for model in models:
    print(f"{model.name}: {len(model.providers)} providers")
    for provider in model.providers:
        print(f"  - {provider.name}: ${provider.batch_input_price_per_1m}/1M input tokens")

# Get specific model
model = client.models.get("gpt-4o")
```

## Batch Job Status

Jobs progress through these statuses:
- `pending` - Job created, waiting to be submitted
- `submitted` - Submitted to provider
- `processing` - Provider is processing requests
- `completed` - All requests processed successfully
- `failed` - Job failed (check `error_message`)
- `cancelled` - Job was cancelled

## Error Handling

```python
from batchrouter import (
    BatchRouter,
    BatchRouterError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
)

try:
    client = BatchRouter(api_key="br_...")
    batch = client.batches.get("invalid-id")
except AuthenticationError:
    print("Invalid API key")
except NotFoundError:
    print("Batch not found")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except BatchRouterError as e:
    print(f"API error: {e.message}")
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `BATCHROUTER_API_KEY` | Your BatchRouter API key |

## License

MIT License - see [LICENSE](LICENSE) for details.
