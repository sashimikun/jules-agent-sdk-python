#!/usr/bin/env python3
"""Ralph Wiggum Loop Example - Iterative AI Development Loops for Jules.

The Ralph Wiggum technique runs AI agents in a continuous loop until
either a completion promise is detected or max iterations are reached.

Named after Ralph Wiggum from The Simpsons, embodying the philosophy
of persistent iteration despite setbacks.

Reference: https://ghuntley.com/ralph/

Usage:
    python ralph_loop_example.py

Set JULES_API_KEY environment variable before running.
"""

import os
import logging
from jules_agent_sdk import JulesClient, RalphLoop

# Enable logging to see Ralph loop progress
logging.basicConfig(level=logging.INFO, format="%(message)s")


def on_iteration_start(iteration: int, prompt: str) -> None:
    """Called at the start of each Ralph iteration."""
    print(f"\n{'='*60}")
    print(f"🔄 Starting iteration {iteration}")
    print(f"{'='*60}")


def on_iteration_end(iteration: int, session) -> None:
    """Called at the end of each Ralph iteration."""
    print(f"\n📊 Iteration {iteration} finished")
    print(f"   Session: {session.id}")
    print(f"   State: {session.state.value}")


def main():
    api_key = os.environ.get("JULES_API_KEY")
    if not api_key:
        print("Error: Set JULES_API_KEY environment variable")
        return

    # The prompt stays the same across all iterations
    # Include clear completion criteria and a completion promise
    prompt = """
Build a simple REST API for a todo list application.

Requirements:
1. CRUD endpoints for todos (GET, POST, PUT, DELETE)
2. Input validation for all endpoints
3. Unit tests with >80% coverage
4. README with API documentation

When all requirements are complete and tests pass:
- Output: <promise>COMPLETE</promise>

If stuck after multiple attempts, document blockers in STUCK.md.
"""

    with JulesClient(api_key=api_key) as client:
        # Method 1: Using the RalphLoop class directly
        print("\n🚀 Starting Ralph Wiggum Loop")
        print("=" * 60)
        
        ralph = RalphLoop(client)
        result = ralph.run(
            prompt=prompt,
            source="sources/my-repo-id",  # Replace with your source
            starting_branch="main",
            title="Todo API Development",
            completion_promise="COMPLETE",
            max_iterations=10,  # Safety limit
            poll_interval=10,
            session_timeout=1800,  # 30 minutes per session
            on_iteration_start=on_iteration_start,
            on_iteration_end=on_iteration_end,
        )
        
        # Print results
        print("\n" + "=" * 60)
        print(result)
        print("=" * 60)
        
        if result.completed:
            print("\n✅ Ralph loop completed successfully!")
            print(f"   Total iterations: {result.iterations}")
            print(f"   Total duration: {result.total_duration_seconds:.1f}s")
            
            # Show the final PR if created
            if result.final_session and result.final_session.outputs:
                for output in result.final_session.outputs:
                    if output.pull_request:
                        print(f"\n📝 Pull Request: {output.pull_request.url}")
        else:
            print(f"\n⏹ Ralph loop stopped: {result.completion_reason}")
            print("   Review session history for details.")


def main_convenience():
    """Alternative using the convenience method on sessions API."""
    api_key = os.environ.get("JULES_API_KEY")
    if not api_key:
        print("Error: Set JULES_API_KEY environment variable")
        return

    prompt = "Fix all linting errors. Output <promise>DONE</promise> when complete."

    with JulesClient(api_key=api_key) as client:
        # Method 2: Using the convenience method
        result = client.sessions.ralph_loop(
            prompt=prompt,
            source="sources/my-repo-id",
            completion_promise="DONE",
            max_iterations=20,
        )
        
        print(result)


if __name__ == "__main__":
    main()

