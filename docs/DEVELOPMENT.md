# Development Guide

This document provides information for developers working on the Jules Agent SDK.

## Project Structure

```
jules-api-python-sdk/
├── src/
│   └── jules_agent_sdk/
│       ├── __init__.py           # Package exports
│       ├── base.py               # Sync HTTP client
│       ├── async_base.py         # Async HTTP client
│       ├── client.py             # Main sync client
│       ├── async_client.py       # Main async client
│       ├── exceptions.py         # Custom exceptions
│       ├── models.py             # Data models
│       ├── sessions.py           # Sessions API
│       ├── activities.py         # Activities API
│       └── sources.py            # Sources API
├── tests/
│   ├── test_client.py            # Sync client tests
│   ├── test_async_client.py      # Async client tests
│   └── test_models.py            # Model tests
├── examples/
│   ├── basic_usage.py            # Basic example
│   ├── async_example.py          # Async example
│   └── plan_approval_example.py  # Plan approval workflow
├── docs/
│   ├── README.md                 # Main documentation
│   └── DEVELOPMENT.md            # This file
├── setup.py                      # Setup script
├── pyproject.toml                # Project metadata
└── LICENSE                       # MIT License

```

## Setup Development Environment

1. Clone the repository:
```bash
git clone https://github.com/jules/jules-agent-sdk.git
cd jules-agent-sdk
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode with all dependencies:
```bash
pip install -e ".[dev]"
```

## Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=jules_agent_sdk --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_client.py -v
```

Run specific test:
```bash
pytest tests/test_client.py::TestJulesClient::test_client_initialization -v
```

## Code Quality

### Formatting

Format code with Black:
```bash
black src tests
```

Check formatting:
```bash
black --check src tests
```

### Type Checking

Run mypy for type checking:
```bash
mypy src
```

### Linting

Run flake8:
```bash
flake8 src tests
```

## Adding New Features

### 1. Add API Endpoint

If adding a new API endpoint:

1. Update the appropriate module in `src/jules_agent_sdk/` (e.g., `sessions.py`)
2. Add method with proper type hints and docstrings
3. Add corresponding async method in `async_client.py`
4. Update tests

Example:
```python
def new_method(self, param: str) -> ModelType:
    """Description of the method.

    Args:
        param: Description

    Returns:
        Description

    Example:
        >>> client.resource.new_method("value")
    """
    response = self.client.get(f"resource/{param}")
    return ModelType.from_dict(response)
```

### 2. Add Data Model

If adding a new data model:

1. Add dataclass in `src/jules_agent_sdk/models.py`
2. Implement `from_dict()` and `to_dict()` methods
3. Add type hints
4. Add tests in `tests/test_models.py`

Example:
```python
@dataclass
class NewModel:
    """Description of the model."""

    field1: str
    field2: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NewModel":
        """Create from API response dictionary."""
        return cls(
            field1=data.get("field1", ""),
            field2=data.get("field2", 0),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request dictionary."""
        return {
            "field1": self.field1,
            "field2": self.field2,
        }
```

### 3. Add Exception Type

If adding a new exception type:

1. Add class in `src/jules_agent_sdk/exceptions.py`
2. Inherit from appropriate base exception
3. Update error handling in `base.py` if needed

## Publishing to PyPI

### Test PyPI (recommended for testing)

1. Build the package:
```bash
python -m build
```

2. Upload to Test PyPI:
```bash
twine upload --repository testpypi dist/*
```

3. Test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ jules-agent-sdk
```

### Production PyPI

1. Ensure version is updated in `pyproject.toml` and `setup.py`
2. Build:
```bash
python -m build
```

3. Upload:
```bash
twine upload dist/*
```

## Version Numbering

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Update version in:
- `pyproject.toml`
- `setup.py`
- `src/jules_agent_sdk/__init__.py`

## Documentation

### Docstrings

Follow Google-style docstrings:

```python
def function(param1: str, param2: int) -> bool:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ExceptionType: When this exception is raised

    Example:
        >>> result = function("test", 42)
        >>> print(result)
        True
    """
```

### README Updates

When adding features, update:
- `docs/README.md` - Main user documentation
- Example files in `examples/`

## Continuous Integration

The project uses GitHub Actions for CI/CD:

- Run tests on multiple Python versions
- Check code formatting
- Run type checking
- Generate coverage reports

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed in development mode:
```bash
pip install -e .
```

### Test Failures

If async tests fail, ensure pytest-asyncio is installed:
```bash
pip install pytest-asyncio
```

### Type Checking Errors

If mypy fails, check:
- All functions have type hints
- Return types are specified
- Optional types use `Optional[T]`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and code quality checks
5. Submit a pull request

## Support

For questions or issues:
- GitHub Issues: https://github.com/jules/jules-agent-sdk/issues
- Email: support@jules.ai
