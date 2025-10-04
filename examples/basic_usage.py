"""Basic usage example for Jules Agent SDK."""

import os
from jules_agent_sdk import JulesClient

# Your API key - set via environment variable or replace with your actual API key
# Example: export JULES_API_KEY="your-api-key-here"
API_KEY = os.environ.get("JULES_API_KEY", "your-api-key-here")

# Initialize the client with your API key
client = JulesClient(api_key=API_KEY)

try:
    # List available sources
    print("=== Available Sources ===")
    sources_result = client.sources.list(page_size=5)
    for source in sources_result["sources"]:
        print(f"Source ID: {source.id}")
        if source.github_repo:
            print(f"  GitHub: {source.github_repo.owner}/{source.github_repo.repo}")

    # Select a source (replace with your actual source ID)
    source_id = "sources/your-source-id"

    # Create a new session
    print("\n=== Creating Session ===")
    session = client.sessions.create(
        prompt="Fix the authentication bug in the login module",
        source=source_id,
        starting_branch="main",
        title="Authentication Bug Fix",
    )

    print(f"Session created: {session.id}")
    print(f"State: {session.state}")
    print(f"URL: {session.url}")

    # Monitor session progress
    print("\n=== Monitoring Progress ===")
    completed_session = client.sessions.wait_for_completion(
        session_id=session.id, poll_interval=5, timeout=600  # 10 minutes
    )

    print(f"Final state: {completed_session.state}")

    # Get session activities
    print("\n=== Session Activities ===")
    activities = client.activities.list_all(session.id)
    for activity in activities[:10]:  # Show first 10 activities
        print(f"\n{activity.description}")
        print(f"  Originator: {activity.originator}")
        print(f"  Time: {activity.create_time}")

        # Show activity-specific data
        if activity.agent_messaged:
            print(f"  Message: {activity.agent_messaged.get('agentMessage', '')[:100]}")
        elif activity.plan_generated:
            plan = activity.plan_generated.get("plan", {})
            steps = plan.get("steps", [])
            print(f"  Plan with {len(steps)} steps generated")

    # List all sessions
    print("\n=== Recent Sessions ===")
    sessions_result = client.sessions.list(page_size=5)
    for s in sessions_result["sessions"]:
        print(f"Session {s.id}: {s.state} - {s.title or s.prompt[:50]}")

finally:
    # Always close the client
    client.close()
