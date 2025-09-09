"""Simple collaboration hub for Dexter.

This module defines an event-based system that allows Dexter's autonomy
manager to broadcast user queries, clarifying questions, and responses to
interested listeners.  Listeners might include background collaborators,
logging utilities, or real-time dashboards.

The hub supports both synchronous and asynchronous listeners and is
intended as a lightweight stand-in for more sophisticated messaging
solutions such as websockets or message queues.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, List
import asyncio

Listener = Callable[[str, Dict[str, Any]], Awaitable[None] | None]


class CollaborationHub:
    """Broadcast events to registered listeners."""

    def __init__(self) -> None:
        self._listeners: List[Listener] = []

    def subscribe(self, listener: Listener) -> None:
        """Register a callback to receive broadcast events."""
        self._listeners.append(listener)

    async def broadcast(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Send an event to all listeners.

        Each listener is invoked safely; exceptions from one listener will not
        prevent delivery to others.
        """
        for listener in list(self._listeners):
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(event_type, payload)
                else:
                    listener(event_type, payload)
            except Exception:
                # Ignore listener failures but continue notifying others.
                continue
