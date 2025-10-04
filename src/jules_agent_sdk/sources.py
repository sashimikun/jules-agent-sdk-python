"""Sources API module."""

from typing import Optional, List, Dict, Any
from jules_agent_sdk.models import Source
from jules_agent_sdk.base import BaseClient


class SourcesAPI:
    """API client for managing Jules sources."""

    def __init__(self, client: BaseClient) -> None:
        """Initialize the Sources API.

        Args:
            client: Base HTTP client instance
        """
        self.client = client

    def get(self, source_id: str) -> Source:
        """Get a single source by ID.

        Args:
            source_id: The source ID or full name (e.g., "sources/abc123" or "abc123")

        Returns:
            Source object

        Example:
            >>> source = client.sources.get("abc123")
            >>> if source.github_repo:
            ...     print(f"Repo: {source.github_repo.owner}/{source.github_repo.repo}")
        """
        if not source_id.startswith("sources/"):
            source_id = f"sources/{source_id}"

        response = self.client.get(source_id)
        return Source.from_dict(response)

    def list(
        self,
        filter_str: Optional[str] = None,
        page_size: Optional[int] = None,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List sources.

        Args:
            filter_str: Optional filter string
            page_size: Maximum number of sources to return
            page_token: Token for pagination

        Returns:
            Dictionary with 'sources' list and optional 'nextPageToken'

        Example:
            >>> result = client.sources.list(page_size=10)
            >>> for source in result['sources']:
            ...     print(source.id)
            >>> # Get next page if available
            >>> if result['nextPageToken']:
            ...     next_page = client.sources.list(page_token=result['nextPageToken'])
        """
        params: Dict[str, Any] = {}
        if filter_str:
            params["filter"] = filter_str
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token:
            params["pageToken"] = page_token

        response = self.client.get("sources", params=params)

        sources = []
        if response.get("sources"):
            sources = [Source.from_dict(s) for s in response["sources"]]

        return {
            "sources": sources,
            "nextPageToken": response.get("nextPageToken"),
        }

    def list_all(self, filter_str: Optional[str] = None) -> List[Source]:
        """List all sources (handles pagination automatically).

        Args:
            filter_str: Optional filter string

        Returns:
            List of all Source objects

        Example:
            >>> all_sources = client.sources.list_all()
            >>> github_sources = [s for s in all_sources if s.github_repo]
            >>> print(f"GitHub sources: {len(github_sources)}")
        """
        all_sources: List[Source] = []
        page_token: Optional[str] = None

        while True:
            result = self.list(filter_str=filter_str, page_token=page_token)
            all_sources.extend(result["sources"])

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        return all_sources
