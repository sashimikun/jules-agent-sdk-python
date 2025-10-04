#!/usr/bin/env python3
"""Simple test script for Jules Agent SDK."""

import os
from jules_agent_sdk import JulesClient
from jules_agent_sdk.exceptions import JulesAPIError

# Your API key - set via environment variable or replace with your actual API key
# Example: export JULES_API_KEY="your-api-key-here"
API_KEY = os.environ.get("JULES_API_KEY", "your-api-key-here")


def main():
    print("🚀 Jules Agent SDK - Simple Test\n")

    with JulesClient(api_key=API_KEY) as client:
        try:
            # 1. List sources
            print("📋 Listing sources...")
            sources = client.sources.list(page_size=10)

            if not sources["sources"]:
                print("❌ No sources found")
                return

            print(f"✅ Found {len(sources['sources'])} source(s):\n")
            for i, source in enumerate(sources["sources"][:5], 1):
                if source.github_repo:
                    print(f"   {i}. {source.github_repo.owner}/{source.github_repo.repo}")
                    print(f"      Source ID: {source.id}")
                    print(f"      Default branch: {source.github_repo.default_branch.display_name if source.github_repo.default_branch else 'N/A'}")
                    print()

            # 2. Create a session
            source = sources["sources"][0]
            branch = "main"
            if source.github_repo and source.github_repo.default_branch:
                branch = source.github_repo.default_branch.display_name

            print(f"🚀 Creating session with source: {source.id}")
            print(f"   Branch: {branch}\n")

            session = client.sessions.create(
                prompt="Add comprehensive error handling and logging to all API endpoints",
                source=source.name,
                starting_branch=branch,
                title="API Enhancement - Error Handling & Logging"
            )

            print("✅ Session created successfully!")
            print(f"   Session ID: {session.id}")
            print(f"   State: {session.state.value}")
            print(f"   Title: {session.title}")
            print(f"   View at: {session.url}\n")

            # 3. Get session details
            print("📊 Session details:")
            session_details = client.sessions.get(session.id)
            print(f"   Prompt: {session_details.prompt}")
            print(f"   State: {session_details.state.value}")
            print(f"   Created: {session_details.create_time}")
            print()

            # 4. List recent sessions
            print("📋 Recent sessions:")
            recent = client.sessions.list(page_size=5)
            for i, s in enumerate(recent["sessions"], 1):
                print(f"   {i}. {s.id}")
                print(f"      State: {s.state.value}")
                print(f"      {s.title or s.prompt[:60]}")
                print()

            # 5. Note about activities
            print("💡 Note: Activities are created as the session progresses.")
            print("   To see activities, wait for the session to start processing,")
            print("   then run:")
            print(f"   >>> activities = client.activities.list_all('{session.id}')")

        except JulesAPIError as e:
            print(f"❌ API Error: {e.message}")
            if e.status_code:
                print(f"   Status: {e.status_code}")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
