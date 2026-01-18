import os
import requests
from jules_agent_sdk import JulesClient

# Configuration
GITHUB_REPO_OWNER = "vercel-labs"
GITHUB_REPO_NAME = "agent-browser"
# The API requires the full source resource name
JULES_SOURCE = "sources/github/sashimikun/agent-browser"
JULES_STARTING_BRANCH = "main"
API_KEY = os.environ.get("JULES_API_KEY")

def get_open_issues(owner, repo):
    """Fetches all open issues from the GitHub repository."""
    issues = []
    page = 1
    per_page = 30
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"

    print(f"Fetching issues from {owner}/{repo}...")

    while True:
        try:
            response = requests.get(
                url,
                params={"state": "open", "page": page, "per_page": per_page},
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            response.raise_for_status()

            page_issues = response.json()
            if not page_issues:
                break

            for issue in page_issues:
                # Filter out pull requests, as they are also returned by the issues endpoint
                if "pull_request" not in issue:
                    issues.append(issue)

            print(f"Fetched page {page} ({len(page_issues)} items)...")
            page += 1

        except requests.exceptions.RequestException as e:
            print(f"Error fetching issues: {e}")
            break

    return issues

def create_jules_session(client, issue):
    """Creates a Jules session for a given issue."""
    issue_number = issue["number"]
    issue_title = issue["title"]
    issue_body = issue.get("body", "") or "No description provided."

    print(f"Creating session for Issue #{issue_number}: {issue_title}")

    # Construct an intuitive prompt
    prompt = (
        f"Address issue #{issue_number}: {issue_title}\n\n"
        f"Issue Description:\n{issue_body}\n\n"
        f"Please analyze this issue, create a plan to resolve it, and implement the necessary changes."
    )

    try:
        session = client.sessions.create(
            prompt=prompt,
            source=JULES_SOURCE,
            starting_branch=JULES_STARTING_BRANCH,
            title=f"Fix Issue #{issue_number}: {issue_title}"
        )

        print(f"  -> Session created successfully!")
        print(f"  -> Session ID: {session.id}")
        print(f"  -> URL: {session.url}")
        print("-" * 50)
        return session

    except Exception as e:
        print(f"  -> Error creating session: {e}")
        return None

def main():
    if not API_KEY:
        print("Error: JULES_API_KEY environment variable not set.")
        return

    # Initialize Jules Client
    client = JulesClient(api_key=API_KEY)

    try:
        # Fetch issues
        issues = get_open_issues(GITHUB_REPO_OWNER, GITHUB_REPO_NAME)
        print(f"Found {len(issues)} open issues.")
        print("-" * 50)

        # Create a session for each issue
        for issue in issues:
            create_jules_session(client, issue)

    finally:
        client.close()

if __name__ == "__main__":
    main()
