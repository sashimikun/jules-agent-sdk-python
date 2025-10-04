"""Async usage example for Jules Agent SDK."""

import os
import asyncio
from jules_agent_sdk import AsyncJulesClient
from jules_agent_sdk.models import SessionState

# Your API key - set via environment variable or replace with your actual API key
# Example: export JULES_API_KEY="your-api-key-here"
API_KEY = os.environ.get("JULES_API_KEY", "your-api-key-here")


async def monitor_session(client, session_id):
    """Monitor a session and print progress updates."""
    print(f"\n[{session_id}] Monitoring session...")

    while True:
        session = await client.sessions.get(session_id)
        print(f"[{session_id}] State: {session.state}")

        if session.state in [SessionState.COMPLETED, SessionState.FAILED]:
            return session

        await asyncio.sleep(5)


async def create_and_track_session(client, prompt, source):
    """Create a session and track it to completion."""
    print(f"\nCreating session: {prompt[:50]}...")

    session = await client.sessions.create(
        prompt=prompt, source=source, starting_branch="main"
    )

    print(f"Session created: {session.id}")

    # Wait for completion
    final_session = await client.sessions.wait_for_completion(session.id)

    # Get activities
    activities = await client.activities.list_all(session.id)
    print(f"Session {session.id} completed with {len(activities)} activities")

    return final_session


async def main():
    """Main async function."""
    # Use async context manager for automatic cleanup
    async with AsyncJulesClient(api_key=API_KEY) as client:
        # List sources
        print("=== Fetching Sources ===")
        sources = await client.sources.list_all()
        print(f"Found {len(sources)} sources")

        if not sources:
            print("No sources available. Please connect a source first.")
            return

        source_id = sources[0].name

        # Example 1: Single session
        print("\n=== Example 1: Single Session ===")
        await create_and_track_session(
            client=client,
            prompt="Add comprehensive error handling to the API endpoints",
            source=source_id,
        )

        # Example 2: Multiple concurrent sessions
        print("\n=== Example 2: Concurrent Sessions ===")
        tasks = [
            create_and_track_session(
                client, "Improve database query performance", source_id
            ),
            create_and_track_session(
                client, "Add unit tests for authentication module", source_id
            ),
            create_and_track_session(
                client, "Update documentation with latest API changes", source_id
            ),
        ]

        # Run all sessions concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        print("\n=== Results ===")
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Task {i+1} failed: {result}")
            else:
                print(f"Task {i+1} completed: {result.state}")

        # Example 3: List all sessions
        print("\n=== Example 3: List All Sessions ===")
        all_sessions = await client.sessions.list(page_size=10)
        for session in all_sessions["sessions"]:
            print(f"  {session.id}: {session.state} - {session.title or session.prompt[:50]}")


if __name__ == "__main__":
    asyncio.run(main())
