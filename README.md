# Jules Agent SDK for Python

> **Disclaimer**: This is an open source implementation of Jules API SDK wrapper in Python and does not have any association with Google. For the official API, please visit: https://developers.google.com/jules/api/

A Python SDK for the Jules API. Simple interface for working with Jules sessions, activities, and sources.

![Jules](jules.png)

## Quick Start

### Installation

```bash
pip install jules-agent-sdk
```

### Basic Usage

```python
from jules_agent_sdk import JulesClient

# Initialize with your API key
client = JulesClient(api_key="your-api-key")

# List sources
sources = client.sources.list_all()
print(f"Found {len(sources)} sources")

# Create a session
session = client.sessions.create(
    prompt="Add error handling to the authentication module",
    source=sources[0].name,
    starting_branch="main"
)

print(f"Session created: {session.id}")
print(f"View at: {session.url}")

client.close()
```

## Configuration

Set your API key as an environment variable:

```bash
export JULES_API_KEY="your-api-key-here"
```

Get your API key from the [Jules dashboard](https://jules.google.com).

## Features

### API Coverage
- **Sessions**: create, get, list, approve plans, send messages, wait for completion
- **Activities**: get, list with automatic pagination
- **Sources**: get, list with automatic pagination


## Documentation

- **[Quick Start](docs/QUICKSTART.md)** - Get started guide
- **[Full Documentation](docs/README.md)** - Complete API reference
- **[Development Guide](docs/DEVELOPMENT.md)** - For contributors

## Usage Examples

### Context Manager (Recommended)

```python
from jules_agent_sdk import JulesClient

with JulesClient(api_key="your-api-key") as client:
    sources = client.sources.list_all()

    session = client.sessions.create(
        prompt="Fix authentication bug",
        source=sources[0].name,
        starting_branch="main"
    )

    print(f"Created: {session.id}")
```

### Async/Await Support

```python
import asyncio
from jules_agent_sdk import AsyncJulesClient

async def main():
    async with AsyncJulesClient(api_key="your-api-key") as client:
        sources = await client.sources.list_all()

        session = await client.sessions.create(
            prompt="Add unit tests",
            source=sources[0].name,
            starting_branch="main"
        )

        # Wait for completion
        completed = await client.sessions.wait_for_completion(session.id)
        print(f"Done: {completed.state}")

asyncio.run(main())
```

### Error Handling

```python
from jules_agent_sdk import JulesClient
from jules_agent_sdk.exceptions import (
    JulesAuthenticationError,
    JulesNotFoundError,
    JulesValidationError,
    JulesRateLimitError
)

try:
    client = JulesClient(api_key="your-api-key")
    session = client.sessions.create(
        prompt="My task",
        source="sources/invalid-id"
    )
except JulesAuthenticationError:
    print("Invalid API key")
except JulesNotFoundError:
    print("Source not found")
except JulesValidationError as e:
    print(f"Validation error: {e.message}")
except JulesRateLimitError as e:
    retry_after = e.response.get("retry_after_seconds", 60)
    print(f"Rate limited. Retry after {retry_after} seconds")
finally:
    client.close()
```

### Custom Configuration

```python
client = JulesClient(
    api_key="your-api-key",
    timeout=60,              # Request timeout in seconds (default: 30)
    max_retries=5,           # Max retry attempts (default: 3)
    retry_backoff_factor=2.0 # Backoff multiplier (default: 1.0)
)
```

Retries happen automatically for:
- Network errors (connection issues, timeouts)
- Server errors (5xx status codes)

No retries for:
- Client errors (4xx status codes)
- Authentication errors

## API Reference

### Sessions

```python
# Create session
session = client.sessions.create(
    prompt="Task description",
    source="sources/source-id",
    starting_branch="main",
    title="Optional title",
    require_plan_approval=False
)

# Get session
session = client.sessions.get("session-id")

# List sessions
result = client.sessions.list(page_size=10)
sessions = result["sessions"]

# Approve plan
client.sessions.approve_plan("session-id")

# Send message
client.sessions.send_message("session-id", "Additional instructions")

# Wait for completion
completed = client.sessions.wait_for_completion(
    "session-id",
    poll_interval=5,
    timeout=600
)
```

### Activities

```python
# Get activity
activity = client.activities.get("session-id", "activity-id")

# List activities (paginated)
result = client.activities.list("session-id", page_size=20)

# List all activities (auto-pagination)
all_activities = client.activities.list_all("session-id")
```

### Sources

```python
# Get source
source = client.sources.get("source-id")

# List sources (paginated)
result = client.sources.list(page_size=10)

# List all sources (auto-pagination)
all_sources = client.sources.list_all()
```

## Logging

Enable logging to see request details:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jules_agent_sdk")
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=jules_agent_sdk

# Run specific test
pytest tests/test_client.py -v
```

## Project Structure

```
jules-api-python-sdk/
├── src/jules_agent_sdk/
│   ├── client.py              # Main client
│   ├── async_client.py        # Async client
│   ├── base.py                # HTTP client with retries
│   ├── models.py              # Data models
│   ├── sessions.py            # Sessions API
│   ├── activities.py          # Activities API
│   ├── sources.py             # Sources API
│   └── exceptions.py          # Custom exceptions
├── tests/                     # Test suite
├── examples/                  # Usage examples
│   ├── simple_test.py         # Quick start
│   ├── interactive_demo.py    # Full demo
│   ├── async_example.py       # Async usage
│   └── plan_approval_example.py
├── docs/                      # Documentation
└── README.md
```

## Contributing

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: See [docs/](docs/) folder
- **Examples**: See [examples/](examples/) folder
- **Issues**: Open a GitHub issue

## Next Steps

1. Run `python examples/simple_test.py` to try it out
2. Read [docs/QUICKSTART.md](docs/QUICKSTART.md) for more details
3. Check [examples/](examples/) folder for more use cases
