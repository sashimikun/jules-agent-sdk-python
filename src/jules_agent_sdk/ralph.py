"""Ralph Wiggum Loop - Iterative, self-referential AI development loops for Jules.

The Ralph Wiggum technique runs AI agents in a continuous loop, where:
1. A prompt is fed to the agent
2. The agent works on the task
3. When the session completes/fails, the same prompt is fed back
4. This continues until a completion promise is detected or max iterations reached

Named after Ralph Wiggum from The Simpsons, embodying the philosophy of
persistent iteration despite setbacks.

Reference: https://ghuntley.com/ralph/
"""

import time
import asyncio
import logging
import re
from dataclasses import dataclass, field
from typing import Optional, List, Callable, Any, Union

from jules_agent_sdk.models import Session, SessionState, Activity

logger = logging.getLogger(__name__)


@dataclass
class RalphLoopResult:
    """Result of a Ralph loop execution.

    Attributes:
        completed: Whether the loop completed successfully (completion promise found)
        completion_reason: Reason for loop termination
        iterations: Number of iterations executed
        sessions: List of sessions created during the loop
        final_session: The last session in the loop
        activities: All activities from all sessions (if collected)
        total_duration_seconds: Total time spent in the loop
    """

    completed: bool = False
    completion_reason: str = ""
    iterations: int = 0
    sessions: List[Session] = field(default_factory=list)
    final_session: Optional[Session] = None
    activities: List[Activity] = field(default_factory=list)
    total_duration_seconds: float = 0.0

    def __str__(self) -> str:
        status = "✅ COMPLETED" if self.completed else "⏹ STOPPED"
        return (
            f"RalphLoopResult({status})\n"
            f"  Reason: {self.completion_reason}\n"
            f"  Iterations: {self.iterations}\n"
            f"  Sessions: {len(self.sessions)}\n"
            f"  Duration: {self.total_duration_seconds:.1f}s"
        )


class RalphLoop:
    """Synchronous Ralph Wiggum loop for Jules sessions.

    Example:
        >>> from jules_agent_sdk import JulesClient
        >>> from jules_agent_sdk.ralph import RalphLoop
        >>>
        >>> client = JulesClient(api_key="your-api-key")
        >>> ralph = RalphLoop(client)
        >>>
        >>> result = ralph.run(
        ...     prompt="Build a REST API. Output <promise>COMPLETE</promise> when done.",
        ...     source="sources/my-repo",
        ...     starting_branch="main",
        ...     completion_promise="COMPLETE",
        ...     max_iterations=50
        ... )
        >>>
        >>> print(result)
    """

    def __init__(self, client: Any) -> None:
        """Initialize the Ralph loop.

        Args:
            client: JulesClient instance
        """
        self.client = client

    def run(
        self,
        prompt: str,
        source: str,
        starting_branch: Optional[str] = None,
        title: Optional[str] = None,
        completion_promise: Optional[str] = None,
        max_iterations: Optional[int] = None,
        poll_interval: int = 5,
        session_timeout: int = 3600,
        collect_activities: bool = True,
        on_iteration_start: Optional[Callable[[int, str], None]] = None,
        on_iteration_end: Optional[Callable[[int, Session], None]] = None,
    ) -> RalphLoopResult:
        """Run the Ralph loop.

        Args:
            prompt: The prompt to run on each iteration (stays the same)
            source: Source for the session (e.g., "sources/repo-id")
            starting_branch: Optional starting branch for GitHub repos
            title: Optional session title prefix (iteration number appended)
            completion_promise: Text that signals completion when found in output
            max_iterations: Maximum iterations before stopping (safety limit)
            poll_interval: Seconds between session polling
            session_timeout: Timeout for each session in seconds
            collect_activities: Whether to collect activities from each session
            on_iteration_start: Callback(iteration, prompt) at start of each iter
            on_iteration_end: Callback(iteration, session) at end of each iter

        Returns:
            RalphLoopResult with details about the loop execution
        """
        result = RalphLoopResult()
        start_time = time.time()
        iteration = 0

        logger.info(f"🔄 Starting Ralph loop with prompt: {prompt[:100]}...")

        while True:
            iteration += 1
            result.iterations = iteration

            # Check max iterations
            if max_iterations and iteration > max_iterations:
                result.completion_reason = f"Max iterations ({max_iterations}) reached"
                logger.info(f"⏹ {result.completion_reason}")
                break

            logger.info(f"🔄 Ralph iteration {iteration}")

            # Callback for iteration start
            if on_iteration_start:
                on_iteration_start(iteration, prompt)

            # Create session with iteration-specific title
            session_title = f"{title} (Ralph #{iteration})" if title else f"Ralph Loop #{iteration}"

            try:
                session = self.client.sessions.create(
                    prompt=prompt,
                    source=source,
                    starting_branch=starting_branch,
                    title=session_title,
                )
                result.sessions.append(session)
                logger.info(f"  Created session: {session.id}")

                # Wait for session to complete
                final_session = self.client.sessions.wait_for_completion(
                    session.id,
                    poll_interval=poll_interval,
                    timeout=session_timeout,
                )
                result.sessions[-1] = final_session
                result.final_session = final_session

            except Exception as e:
                logger.warning(f"  Session failed: {e}")
                # Continue to next iteration on failure (Ralph philosophy)
                if on_iteration_end and result.sessions:
                    on_iteration_end(iteration, result.sessions[-1])
                continue

            # Collect activities if requested
            if collect_activities:
                try:
                    activities = self.client.activities.list_all(final_session.id)
                    result.activities.extend(activities)
                except Exception as e:
                    logger.warning(f"  Failed to collect activities: {e}")

            # Check for completion promise in activities
            if completion_promise and self._check_completion_promise(
                result.activities, completion_promise
            ):
                result.completed = True
                result.completion_reason = f"Completion promise '{completion_promise}' found"
                logger.info(f"✅ {result.completion_reason}")
                break

            # Callback for iteration end
            if on_iteration_end:
                on_iteration_end(iteration, final_session)

            logger.info(f"  Iteration {iteration} complete, continuing loop...")

        result.total_duration_seconds = time.time() - start_time
        return result

    def _check_completion_promise(
        self, activities: List[Activity], promise: str
    ) -> bool:
        """Check if completion promise is found in activities."""
        # Build patterns for common promise formats
        patterns = [
            promise,  # Exact match
            f"<promise>{promise}</promise>",  # XML-style
            f"PROMISE:{promise}",  # Prefix style
        ]

        for activity in activities:
            # Check in agent messages
            if activity.agent_messaged:
                msg = activity.agent_messaged.get("agentMessage", "")
                for pattern in patterns:
                    if pattern in msg:
                        return True

            # Check in description
            if activity.description:
                for pattern in patterns:
                    if pattern in activity.description:
                        return True

            # Check session completed event
            if activity.session_completed:
                summary = str(activity.session_completed)
                for pattern in patterns:
                    if pattern in summary:
                        return True

        return False



class AsyncRalphLoop:
    """Asynchronous Ralph Wiggum loop for Jules sessions.

    Example:
        >>> import asyncio
        >>> from jules_agent_sdk import AsyncJulesClient
        >>> from jules_agent_sdk.ralph import AsyncRalphLoop
        >>>
        >>> async def main():
        ...     async with AsyncJulesClient(api_key="your-api-key") as client:
        ...         ralph = AsyncRalphLoop(client)
        ...         result = await ralph.run(
        ...             prompt="Build a REST API. Output <promise>DONE</promise> when done.",
        ...             source="sources/my-repo",
        ...             starting_branch="main",
        ...             completion_promise="DONE",
        ...             max_iterations=50
        ...         )
        ...         print(result)
        >>>
        >>> asyncio.run(main())
    """

    def __init__(self, client: Any) -> None:
        """Initialize the async Ralph loop.

        Args:
            client: AsyncJulesClient instance
        """
        self.client = client

    async def run(
        self,
        prompt: str,
        source: str,
        starting_branch: Optional[str] = None,
        title: Optional[str] = None,
        completion_promise: Optional[str] = None,
        max_iterations: Optional[int] = None,
        poll_interval: int = 5,
        session_timeout: int = 3600,
        collect_activities: bool = True,
        on_iteration_start: Optional[Callable[[int, str], Any]] = None,
        on_iteration_end: Optional[Callable[[int, Session], Any]] = None,
    ) -> RalphLoopResult:
        """Run the async Ralph loop.

        Args:
            prompt: The prompt to run on each iteration (stays the same)
            source: Source for the session (e.g., "sources/repo-id")
            starting_branch: Optional starting branch for GitHub repos
            title: Optional session title prefix (iteration number appended)
            completion_promise: Text that signals completion when found in output
            max_iterations: Maximum iterations before stopping (safety limit)
            poll_interval: Seconds between session polling
            session_timeout: Timeout for each session in seconds
            collect_activities: Whether to collect activities from each session
            on_iteration_start: Async callback(iteration, prompt) at start
            on_iteration_end: Async callback(iteration, session) at end

        Returns:
            RalphLoopResult with details about the loop execution
        """
        result = RalphLoopResult()
        start_time = asyncio.get_event_loop().time()
        iteration = 0

        logger.info(f"🔄 Starting async Ralph loop with prompt: {prompt[:100]}...")

        while True:
            iteration += 1
            result.iterations = iteration

            # Check max iterations
            if max_iterations and iteration > max_iterations:
                result.completion_reason = f"Max iterations ({max_iterations}) reached"
                logger.info(f"⏹ {result.completion_reason}")
                break

            logger.info(f"🔄 Ralph iteration {iteration}")

            # Callback for iteration start
            if on_iteration_start:
                callback_result = on_iteration_start(iteration, prompt)
                if asyncio.iscoroutine(callback_result):
                    await callback_result

            # Create session with iteration-specific title
            session_title = f"{title} (Ralph #{iteration})" if title else f"Ralph Loop #{iteration}"

            try:
                session = await self.client.sessions.create(
                    prompt=prompt,
                    source=source,
                    starting_branch=starting_branch,
                    title=session_title,
                )
                result.sessions.append(session)
                logger.info(f"  Created session: {session.id}")

                # Wait for session to complete
                final_session = await self.client.sessions.wait_for_completion(
                    session.id,
                    poll_interval=poll_interval,
                    timeout=session_timeout,
                )
                result.sessions[-1] = final_session
                result.final_session = final_session

            except Exception as e:
                logger.warning(f"  Session failed: {e}")
                # Continue to next iteration on failure (Ralph philosophy)
                if on_iteration_end and result.sessions:
                    callback_result = on_iteration_end(iteration, result.sessions[-1])
                    if asyncio.iscoroutine(callback_result):
                        await callback_result
                continue

            # Collect activities if requested
            if collect_activities:
                try:
                    activities = await self.client.activities.list_all(final_session.id)
                    result.activities.extend(activities)
                except Exception as e:
                    logger.warning(f"  Failed to collect activities: {e}")

            # Check for completion promise in activities
            if completion_promise and self._check_completion_promise(
                result.activities, completion_promise
            ):
                result.completed = True
                result.completion_reason = f"Completion promise '{completion_promise}' found"
                logger.info(f"✅ {result.completion_reason}")
                break

            # Callback for iteration end
            if on_iteration_end:
                callback_result = on_iteration_end(iteration, final_session)
                if asyncio.iscoroutine(callback_result):
                    await callback_result

            logger.info(f"  Iteration {iteration} complete, continuing loop...")

        result.total_duration_seconds = asyncio.get_event_loop().time() - start_time
        return result

    def _check_completion_promise(
        self, activities: List[Activity], promise: str
    ) -> bool:
        """Check if completion promise is found in activities."""
        # Build patterns for common promise formats
        patterns = [
            promise,  # Exact match
            f"<promise>{promise}</promise>",  # XML-style
            f"PROMISE:{promise}",  # Prefix style
        ]

        for activity in activities:
            # Check in agent messages
            if activity.agent_messaged:
                msg = activity.agent_messaged.get("agentMessage", "")
                for pattern in patterns:
                    if pattern in msg:
                        return True

            # Check in description
            if activity.description:
                for pattern in patterns:
                    if pattern in activity.description:
                        return True

            # Check session completed event
            if activity.session_completed:
                summary = str(activity.session_completed)
                for pattern in patterns:
                    if pattern in summary:
                        return True

        return False

