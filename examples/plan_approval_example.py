"""Example showing how to handle plan approval workflows."""

import os
import time
from jules_agent_sdk import JulesClient
from jules_agent_sdk.models import SessionState

# Your API key - set via environment variable or replace with your actual API key
# Example: export JULES_API_KEY="your-api-key-here"
API_KEY = os.environ.get("JULES_API_KEY", "your-api-key-here")


def main():
    """Demonstrate plan approval workflow."""
    client = JulesClient(api_key=API_KEY)

    try:
        # Create a session that requires plan approval
        print("=== Creating Session with Plan Approval ===")
        session = client.sessions.create(
            prompt="Refactor the authentication system to use OAuth2",
            source="sources/your-source-id",
            starting_branch="main",
            require_plan_approval=True,  # This is the key setting
        )

        print(f"Session created: {session.id}")
        print(f"Session URL: {session.url}")

        # Poll until we get to the plan approval stage
        print("\n=== Waiting for Plan Generation ===")
        while True:
            session = client.sessions.get(session.id)
            print(f"Current state: {session.state}")

            if session.state == SessionState.AWAITING_PLAN_APPROVAL:
                print("\n✓ Plan has been generated and is awaiting approval!")
                break
            elif session.state in [SessionState.FAILED, SessionState.COMPLETED]:
                print(f"Session ended unexpectedly with state: {session.state}")
                return

            time.sleep(3)

        # Retrieve and display the plan
        print("\n=== Generated Plan ===")
        activities = client.activities.list_all(session.id)

        plan_found = False
        for activity in activities:
            if activity.plan_generated:
                plan_data = activity.plan_generated.get("plan", {})
                plan_id = plan_data.get("id")
                steps = plan_data.get("steps", [])

                print(f"\nPlan ID: {plan_id}")
                print(f"Total Steps: {len(steps)}\n")

                for step in steps:
                    print(f"Step {step['index'] + 1}: {step['title']}")
                    print(f"  Description: {step['description']}")
                    print()

                plan_found = True
                break

        if not plan_found:
            print("No plan found in activities")
            return

        # Ask user for approval (in a real app, you might show this in a UI)
        print("=== Plan Approval ===")
        user_input = input("Approve this plan? (yes/no): ").strip().lower()

        if user_input == "yes":
            print("\nApproving plan...")
            client.sessions.approve_plan(session.id)
            print("✓ Plan approved! Session will now proceed.")

            # Optionally wait for completion
            print("\n=== Waiting for Session Completion ===")
            final_session = client.sessions.wait_for_completion(
                session.id, poll_interval=5, timeout=1800  # 30 minutes
            )
            print(f"\nSession completed with state: {final_session.state}")

            # Show final activities
            final_activities = client.activities.list_all(session.id)
            print(f"Total activities: {len(final_activities)}")

        else:
            print("\nPlan rejected. Session will remain in awaiting approval state.")
            print("You can approve it later or send feedback with:")
            print(f"  client.sessions.send_message('{session.id}', 'Please revise the plan...')")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
