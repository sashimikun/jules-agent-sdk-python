# Quick Start Guide

Get started with the Jules Agent SDK in minutes!

## Installation

```bash
pip install jules-agent-sdk
```

## Get Your API Key

1. Visit the Jules API dashboard
2. Navigate to API settings
3. Generate a new API key
4. Save it securely

## Your First Session

Create a simple script to start your first Jules session:

```python
from jules_agent_sdk import JulesClient

# Initialize client
client = JulesClient(api_key="your-api-key")

# List your sources
sources = client.sources.list_all()
print(f"Available sources: {len(sources)}")

# Use the first source
source = sources[0]
print(f"Using source: {source.id}")

# Create a session
session = client.sessions.create(
    prompt="Add error handling to the API endpoints",
    source=source.name,
    starting_branch="main"
)

print(f"✓ Session created: {session.id}")
print(f"View at: {session.url}")

# Close client
client.close()
```

## Monitor Progress

Track your session until completion:

```python
from jules_agent_sdk import JulesClient
from jules_agent_sdk.models import SessionState

client = JulesClient(api_key="your-api-key")

# Create session
session = client.sessions.create(
    prompt="Fix the login bug",
    source="sources/my-repo-id",
    starting_branch="main"
)

print(f"Session: {session.id}")

# Wait for completion (with timeout)
try:
    completed = client.sessions.wait_for_completion(
        session.id,
        poll_interval=5,
        timeout=600  # 10 minutes
    )
    print(f"✓ Completed! State: {completed.state}")
except TimeoutError:
    print("Session still in progress after 10 minutes")

client.close()
```

## View Activities

See what Jules did during the session:

```python
from jules_agent_sdk import JulesClient

client = JulesClient(api_key="your-api-key")

# Get all activities for a session
activities = client.activities.list_all("your-session-id")

print(f"Total activities: {len(activities)}")

for activity in activities:
    print(f"\n{activity.description}")

    # Show agent messages
    if activity.agent_messaged:
        msg = activity.agent_messaged.get("agentMessage", "")
        print(f"  Agent: {msg[:100]}...")

    # Show plan if generated
    if activity.plan_generated:
        plan = activity.plan_generated["plan"]
        print(f"  Plan with {len(plan['steps'])} steps")

client.close()
```

## Using Context Manager

Automatically handle cleanup:

```python
from jules_agent_sdk import JulesClient

with JulesClient(api_key="your-api-key") as client:
    # Create session
    session = client.sessions.create(
        prompt="Refactor database layer",
        source="sources/repo-id",
        starting_branch="main"
    )

    # Do work...
    print(f"Session: {session.id}")

# Client automatically closes when exiting the block
```

## Async Example

Use async/await for better performance:

```python
import asyncio
from jules_agent_sdk import AsyncJulesClient

async def main():
    async with AsyncJulesClient(api_key="your-api-key") as client:
        # Create session
        session = await client.sessions.create(
            prompt="Add unit tests",
            source="sources/repo-id",
            starting_branch="main"
        )

        # Wait for completion
        completed = await client.sessions.wait_for_completion(session.id)
        print(f"Completed: {completed.state}")

        # Get activities
        activities = await client.activities.list_all(session.id)
        print(f"Activities: {len(activities)}")

asyncio.run(main())
```

## Error Handling

Handle API errors gracefully:

```python
from jules_agent_sdk import JulesClient
from jules_agent_sdk.exceptions import (
    JulesAuthenticationError,
    JulesNotFoundError,
    JulesValidationError,
)

client = JulesClient(api_key="your-api-key")

try:
    session = client.sessions.create(
        prompt="My task",
        source="sources/invalid-id",
        starting_branch="main"
    )
except JulesAuthenticationError:
    print("Invalid API key!")
except JulesNotFoundError:
    print("Source not found!")
except JulesValidationError as e:
    print(f"Validation error: {e.message}")

client.close()
```

## Plan Approval Workflow

Require approval before Jules executes the plan:

```python
from jules_agent_sdk import JulesClient
from jules_agent_sdk.models import SessionState
import time

client = JulesClient(api_key="your-api-key")

# Create session with plan approval required
session = client.sessions.create(
    prompt="Complex refactoring task",
    source="sources/repo-id",
    require_plan_approval=True  # Key parameter
)

# Wait for plan
while True:
    session = client.sessions.get(session.id)

    if session.state == SessionState.AWAITING_PLAN_APPROVAL:
        # Get the plan
        activities = client.activities.list_all(session.id)
        for activity in activities:
            if activity.plan_generated:
                plan = activity.plan_generated["plan"]
                print("Plan generated:")
                for step in plan["steps"]:
                    print(f"  {step['index']}: {step['title']}")

                # Approve the plan
                client.sessions.approve_plan(session.id)
                print("Plan approved!")
                break
        break

    time.sleep(2)

client.close()
```

## Next Steps

- Read the [full documentation](README.md)
- Explore [examples](../examples/)
- Check the [API reference](README.md#api-reference)
- Learn about [async usage](README.md#async-usage)

## Common Use Cases

### 1. Bug Fixing
```python
session = client.sessions.create(
    prompt="Fix the authentication bug where users can't log in with special characters",
    source="sources/backend-repo",
    starting_branch="main"
)
```

### 2. Feature Development
```python
session = client.sessions.create(
    prompt="Add pagination to the /users endpoint with page size and offset parameters",
    source="sources/api-repo",
    starting_branch="develop"
)
```

### 3. Code Refactoring
```python
session = client.sessions.create(
    prompt="Refactor the payment processing module to improve error handling and logging",
    source="sources/payments-repo",
    starting_branch="main"
)
```

### 4. Documentation
```python
session = client.sessions.create(
    prompt="Add JSDoc comments to all public functions in the utils module",
    source="sources/frontend-repo",
    starting_branch="main"
)
```

## Tips & Best Practices

1. **Use descriptive prompts**: Be specific about what you want Jules to do
2. **Set timeouts**: Use the `timeout` parameter in `wait_for_completion()`
3. **Handle errors**: Always wrap API calls in try/except blocks
4. **Use context managers**: Automatically handle cleanup with `with` statements
5. **Check session URLs**: Visit the session URL to see progress in the web UI
6. **Monitor activities**: Check activities regularly to see what Jules is doing
7. **Use plan approval**: For critical tasks, require plan approval first

## Support

Need help?

- Check the [FAQ](README.md#faq) (if available)
- Review [examples](../examples/)
- Open an [issue](https://github.com/jules/jules-agent-sdk/issues)
- Email: support@jules.ai
