#!/usr/bin/env python3
"""Interactive demo showing all SDK features."""

import os
from jules_agent_sdk import JulesClient
from jules_agent_sdk.exceptions import JulesAPIError

# Your API key - set via environment variable or replace with your actual API key
# Example: export JULES_API_KEY="your-api-key-here"
API_KEY = os.environ.get("JULES_API_KEY", "your-api-key-here")


def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_sources(client):
    """Demonstrate source operations."""
    print_section("📋 SOURCES API")

    # List all sources
    print("Fetching all sources...")
    sources = client.sources.list_all()
    print(f"✅ Total sources: {len(sources)}\n")

    # Show first 5 with details
    for i, source in enumerate(sources[:5], 1):
        print(f"{i}. {source.id}")
        if source.github_repo:
            repo = source.github_repo
            print(f"   Owner: {repo.owner}")
            print(f"   Repo: {repo.repo}")
            print(f"   Private: {repo.is_private}")
            if repo.default_branch:
                print(f"   Default branch: {repo.default_branch.display_name}")
            if repo.branches:
                print(f"   Total branches: {len(repo.branches)}")
        print()

    # Get a specific source
    if sources:
        source_id = sources[0].id
        print(f"Getting source: {source_id}")
        source = client.sources.get(source_id)
        print(f"✅ Retrieved: {source.name}\n")

    return sources


def demo_sessions(client, sources):
    """Demonstrate session operations."""
    print_section("🚀 SESSIONS API")

    if not sources:
        print("⚠️  No sources available. Skipping session creation.\n")
        return None

    # Create a session
    source = sources[0]
    branch = "main"
    if source.github_repo and source.github_repo.default_branch:
        branch = source.github_repo.default_branch.display_name

    print(f"Creating session with:")
    print(f"  Source: {source.id}")
    print(f"  Branch: {branch}")
    print(f"  Prompt: Add unit tests for authentication module\n")

    session = client.sessions.create(
        prompt="Add comprehensive unit tests for the authentication module with edge cases",
        source=source.name,
        starting_branch=branch,
        title="Unit Tests - Authentication Module"
    )

    print(f"✅ Session created!")
    print(f"   ID: {session.id}")
    print(f"   State: {session.state.value}")
    print(f"   URL: {session.url}\n")

    # Get session details
    print(f"Retrieving session: {session.id}")
    session_details = client.sessions.get(session.id)
    print(f"✅ Current state: {session_details.state.value}")
    print(f"   Created: {session_details.create_time}")
    print(f"   Updated: {session_details.update_time}\n")

    # List recent sessions
    print("Listing recent sessions (top 5):")
    recent = client.sessions.list(page_size=5)
    for i, s in enumerate(recent["sessions"], 1):
        print(f"{i}. {s.id} - {s.state.value}")
        print(f"   {s.title or s.prompt[:60]}")
    print()

    # Pagination example
    if recent.get("nextPageToken"):
        print(f"Next page token available: {recent['nextPageToken'][:20]}...\n")

    return session


def demo_activities(client, session):
    """Demonstrate activity operations."""
    print_section("📊 ACTIVITIES API")

    if not session:
        print("⚠️  No session available. Skipping activities demo.\n")
        return

    session_id = session.id
    print(f"Fetching activities for session: {session_id}\n")

    try:
        # List activities with pagination
        activities_result = client.activities.list(session_id, page_size=10)
        activities = activities_result["activities"]
    except JulesAPIError as e:
        if e.status_code == 404:
            print("ℹ️  No activities yet. The session was just created.\n")
            print("   Activities will appear as Jules starts working.")
            print("   Try checking a completed session instead:\n")

            # Find a completed session with activities
            recent = client.sessions.list(page_size=20)
            for s in recent["sessions"]:
                if s.state.value in ["COMPLETED", "FAILED", "IN_PROGRESS"]:
                    try:
                        print(f"   Checking session {s.id}...")
                        test_activities = client.activities.list(s.id, page_size=5)
                        if test_activities["activities"]:
                            print(f"   ✅ Found session with activities!\n")
                            session_id = s.id
                            activities_result = test_activities
                            activities = activities_result["activities"]
                            break
                    except:
                        continue
            else:
                print("   No sessions with activities found.\n")
                return
        else:
            raise

    if not activities:
        print("ℹ️  No activities yet. The session may still be starting.\n")
        return

    print(f"✅ Found {len(activities)} activities\n")

    # Show activity details
    for i, activity in enumerate(activities[:5], 1):
        print(f"{i}. Activity {activity.id}")
        print(f"   Description: {activity.description}")
        print(f"   Originator: {activity.originator}")
        print(f"   Created: {activity.create_time}")

        # Show activity type
        if activity.agent_messaged:
            msg = activity.agent_messaged.get("agentMessage", "")
            print(f"   Type: Agent Message")
            print(f"   Content: {msg[:100]}{'...' if len(msg) > 100 else ''}")

        elif activity.plan_generated:
            plan = activity.plan_generated.get("plan", {})
            steps = plan.get("steps", [])
            print(f"   Type: Plan Generated")
            print(f"   Steps: {len(steps)}")
            for step in steps[:2]:
                print(f"      - {step.get('title', 'N/A')}")

        elif activity.progress_updated:
            update = activity.progress_updated
            print(f"   Type: Progress Update")
            print(f"   Title: {update.get('title', 'N/A')}")

        # Show artifacts
        if activity.artifacts:
            print(f"   Artifacts: {len(activity.artifacts)}")
            for artifact in activity.artifacts[:2]:
                if artifact.change_set:
                    print(f"      - Code changes")
                if artifact.bash_output:
                    print(f"      - Bash output: {artifact.bash_output.command}")

        print()

    # Get a specific activity
    if activities:
        activity = activities[0]
        print(f"Retrieving specific activity: {activity.id}")
        activity_details = client.activities.get(session_id, activity.id)
        print(f"✅ Retrieved: {activity_details.name}\n")

    # List all activities (auto-pagination)
    print("Fetching ALL activities (with auto-pagination)...")
    all_activities = client.activities.list_all(session_id)
    print(f"✅ Total activities (all pages): {len(all_activities)}\n")


def demo_advanced_features(client):
    """Demonstrate advanced features."""
    print_section("🔧 ADVANCED FEATURES")

    # Using with statement
    print("1. Context Manager Usage:")
    print("   ✅ Already using 'with' statement - auto cleanup!\n")

    # Error handling
    print("2. Error Handling:")
    print("   Testing invalid source...")
    try:
        client.sources.get("invalid-source-id")
    except JulesAPIError as e:
        print(f"   ✅ Caught error: {e.message}")
        print(f"      Status code: {e.status_code}\n")

    # Pagination
    print("3. Pagination:")
    print("   Using list() - manual pagination")
    print("   Using list_all() - automatic pagination\n")

    # Type hints
    print("4. Type Safety:")
    print("   ✅ Full type hints for IDE autocomplete")
    print("   ✅ Enums for session states")
    print("   ✅ Dataclasses for all models\n")


def main():
    """Run the interactive demo."""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║          JULES AGENT SDK - INTERACTIVE DEMO              ║
║                                                          ║
║  This demo showcases all SDK features with your          ║
║  actual API credentials.                                 ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)

    with JulesClient(api_key=API_KEY) as client:
        try:
            # Demo each API
            sources = demo_sources(client)
            session = demo_sessions(client, sources)
            demo_activities(client, session)
            demo_advanced_features(client)

            # Summary
            print_section("✅ DEMO COMPLETE")
            print("All SDK features demonstrated successfully!")
            print("\nKey takeaways:")
            print("  • Sources API - ✅ List, get, pagination")
            print("  • Sessions API - ✅ Create, get, list")
            print("  • Activities API - ✅ List, get, auto-pagination")
            print("  • Error handling - ✅ Custom exceptions")
            print("  • Type safety - ✅ Full type hints")
            print("  • Context manager - ✅ Auto cleanup")
            print("\nNext steps:")
            print("  • Check examples/ for more code samples")
            print("  • Read docs/README.md for full API reference")
            print("  • Visit session URLs to see progress")
            print("\n🚀 Happy coding with Jules Agent SDK!")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
