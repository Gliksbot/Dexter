"""
Autonomy manager for Dexter.

This module defines the classes responsible for coordinating queries from
users, asking clarifying questions via a primary language model, and
managing conversations across multiple LLM collaborators. It integrates
Dexter's memory system to retain both recent context and long-term
conversation history. The initial implementation here provides a simple
framework and placeholder logic to illustrate the intended API.
"""

from __future__ import annotations

from typing import List

# Import the unified MemoryManager from our memory module
from .memory import MemoryManager


class AutonomyManager:
    """Manage user queries, clarifications, and memory interactions."""

    def __init__(self, model_name: str = "default-model", memory: MemoryManager | None = None) -> None:
        # The name of the primary model used to ask clarifying questions
        self.model_name = model_name
        # Initialize a memory manager if one is not provided
        self.memory: MemoryManager = memory or MemoryManager()

    async def ask_clarifications(self, query: str) -> List[str]:
        """
        Ask clarifying questions to the user about their query.

        This implementation stores the original query in short- and long-term
        memory, then returns a fixed set of example clarifying questions.
        In a full implementation this would call the primary language
        model with a prompt instructing it to ask clarifying questions
        until the request is fully understood.
        """
        # Store the user's initial query in memory
        self.memory.add_message("user", query)
        # Placeholder clarifying questions
        return [
            "Could you please provide more details about your request?",
            "What specific format or length do you expect?",
        ]

    async def process_request(self, query: str) -> str:
        """
        Process a user query and return a response.

        This method adds the query to memory and, in a full
        implementation, would call the collaborative LLM system to
        generate a skill or answer. For now it simply echoes the
        request back to the user.
        """
        # Record the user query
        self.memory.add_message("user", query)

        # Retrieve recent context (not used yet but available)
        _context = self.memory.get_recent_context()

        # Placeholder response: echo the query
        response = f"Received your request: {query}"
        # Store the response from Dexter
        self.memory.add_message("assistant", response)
        return response
