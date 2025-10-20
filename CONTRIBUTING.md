# Contributing to Jules Agent SDK

Thank you for your interest in contributing to the Jules Agent SDK for Python! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and considerate in all interactions.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip (Python package installer)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/jules-agent-sdk-python.git
   cd jules-agent-sdk-python
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/sashimikun/jules-agent-sdk-python.git
   ```

## Development Setup

### 1. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs the package in editable mode along with all development dependencies:
- pytest (testing framework)
- pytest-asyncio (async testing support)
- black (code formatter)
- mypy (type checker)
- flake8 (linter)

### 3. Verify Installation

```bash
# Run tests to verify setup
pytest

# Check code style
black --check src/ tests/
flake8 src/ tests/
mypy src/
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/` - for new features
- `fix/` - for bug fixes
- `docs/` - for documentation updates
- `refactor/` - for code refactoring

### 2. Make Your Changes

- Write clear, concise code
- Add tests for new functionality
- Update documentation as needed
- Follow the code style guidelines

### 3. Keep Your Branch Updated

```bash
git fetch upstream
git rebase upstream/main
```

## Code Style Guidelines

### Python Code Style

We follow PEP 8 with some modifications configured in `pyproject.toml`:

- **Line length**: 100 characters
- **Target Python versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Formatter**: Black
- **Linter**: Flake8
- **Type checker**: mypy

### Formatting

Format your code with Black before committing:

```bash
black src/ tests/ examples/
```

### Type Hints

- Use type hints for all function signatures
- All functions must have return type annotations
- Use `Optional[T]` for nullable types
- Example:
  ```python
  def create_session(
      self,
      prompt: str,
      source: str,
      starting_branch: Optional[str] = None
  ) -> Session:
      ...
  ```

### Linting

Check for style issues with Flake8:

```bash
flake8 src/ tests/ examples/
```

### Type Checking

Verify type correctness with mypy:

```bash
mypy src/
```

### Docstrings

Use Google-style docstrings:

```python
def wait_for_completion(
    self,
    session_id: str,
    poll_interval: int = 5,
    timeout: int = 600
) -> Session:
    """Wait for a session to complete.

    Args:
        session_id: The ID of the session to wait for
        poll_interval: Seconds between status checks (default: 5)
        timeout: Maximum seconds to wait (default: 600)

    Returns:
        The completed Session object

    Raises:
        JulesTimeoutError: If the session doesn't complete within timeout
        JulesAPIError: If an API error occurs
    """
    ...
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::test_create_session

# Run with coverage
pytest --cov=jules_agent_sdk --cov-report=html
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test names that explain what is being tested
- Test both success and error cases
- Mock external API calls

Example test structure:

```python
import pytest
from jules_agent_sdk import JulesClient
from jules_agent_sdk.exceptions import JulesValidationError


def test_create_session_success(mock_api):
    """Test successful session creation"""
    client = JulesClient(api_key="test-key")
    session = client.sessions.create(
        prompt="Test task",
        source="sources/test-source"
    )
    assert session.id == "session-123"


def test_create_session_validation_error(mock_api):
    """Test session creation with invalid parameters"""
    client = JulesClient(api_key="test-key")
    with pytest.raises(JulesValidationError):
        client.sessions.create(prompt="", source="")
```

### Async Tests

For async code, use `pytest-asyncio`:

```python
import pytest


@pytest.mark.asyncio
async def test_async_create_session(mock_api):
    """Test async session creation"""
    async with AsyncJulesClient(api_key="test-key") as client:
        session = await client.sessions.create(
            prompt="Test task",
            source="sources/test-source"
        )
        assert session.id == "session-123"
```

## Submitting Changes

### Before Submitting

1. **Run all checks**:
   ```bash
   black src/ tests/ examples/
   flake8 src/ tests/ examples/
   mypy src/
   pytest
   ```

2. **Update documentation** if needed:
   - Update README.md for user-facing changes
   - Update docs/ for detailed documentation
   - Add docstrings to new functions

3. **Update CHANGELOG** (if applicable):
   - Add entry describing your changes
   - Follow existing format

### Commit Messages

Write clear, descriptive commit messages:

```
Add support for session cancellation

- Add cancel() method to SessionsClient
- Add CANCELLED state to SessionState enum
- Add tests for cancellation flow
- Update documentation with cancellation examples
```

Format:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description with bullet points if needed

### Creating a Pull Request

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a pull request on GitHub

3. Fill out the PR template with:
   - Description of changes
   - Related issue numbers (if applicable)
   - Testing performed
   - Documentation updates

4. Wait for review and address feedback

### PR Review Process

- All PRs require at least one review
- CI checks must pass (tests, linting, type checking)
- Address all review comments
- Keep PR scope focused and manageable

## Reporting Issues

### Bug Reports

When reporting bugs, include:
- Python version
- SDK version
- Minimal code to reproduce the issue
- Expected behavior
- Actual behavior
- Error messages and stack traces

### Feature Requests

When requesting features, include:
- Use case and motivation
- Proposed API design (if applicable)
- Alternative solutions considered

### Security Issues

For security vulnerabilities, please email security@example.com instead of opening a public issue.

## Project Structure

```
jules-agent-sdk-python/
├── src/jules_agent_sdk/    # Main package code
│   ├── client.py           # Sync client
│   ├── async_client.py     # Async client
│   ├── base.py             # HTTP base client
│   ├── async_base.py       # Async HTTP base client
│   ├── sessions.py         # Sessions API
│   ├── activities.py       # Activities API
│   ├── sources.py          # Sources API
│   ├── models.py           # Data models
│   ├── exceptions.py       # Custom exceptions
│   └── config.py           # Configuration
├── tests/                  # Test suite
├── examples/               # Usage examples
├── docs/                   # Documentation
└── pyproject.toml          # Project configuration
```

## Additional Resources

- [Development Guide](docs/DEVELOPMENT.md) - Detailed development information
- [Quick Start](docs/QUICKSTART.md) - Getting started guide
- [Official Jules API Documentation](https://developers.google.com/jules/api/)

## Questions?

Feel free to open an issue for questions or reach out to the maintainers.

Thank you for contributing to Jules Agent SDK!
