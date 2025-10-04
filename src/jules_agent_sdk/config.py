"""Configuration management for Jules Agent SDK."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ClientConfig:
    """Configuration for Jules API client.

    Attributes:
        api_key: Jules API key for authentication
        base_url: Base URL for the Jules API
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts for failed requests
        retry_backoff_factor: Exponential backoff factor for retries
        max_backoff: Maximum backoff time between retries in seconds
        verify_ssl: Whether to verify SSL certificates
    """

    api_key: str
    base_url: str = "https://jules.googleapis.com/v1alpha"
    timeout: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 1.0
    max_backoff: float = 10.0
    verify_ssl: bool = True

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.api_key:
            raise ValueError("API key is required")

        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")

        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")

        if self.retry_backoff_factor <= 0:
            raise ValueError("Retry backoff factor must be positive")


# Default constants
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_POLL_INTERVAL = 5
DEFAULT_SESSION_TIMEOUT = 600
DEFAULT_RETRY_BACKOFF_FACTOR = 1.0
DEFAULT_MAX_BACKOFF = 10.0
