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
import re

# Import the unified MemoryManager from our memory module
from .memory import MemoryManager
from .collaboration import CollaborationHub


class AutonomyManager:
    """Manage user queries, clarifications, and memory interactions."""

    def __init__(
        self,
        model_name: str = "default-model",
        memory: MemoryManager | None = None,
        collaboration: CollaborationHub | None = None,
    ) -> None:
        """Create a new autonomy manager.

        Parameters
        ----------
        model_name:
            Identifier for the primary model used to generate clarifying
            questions.  This is purely informational for now.
        memory:
            Optional memory manager instance. If not provided a new one is
            created which stores short and long term context.
        collaboration:
            Optional :class:`CollaborationHub` used to broadcast user input,
            clarifying questions and Dexter's responses so that other
            collaborators can work in parallel.
        """

        # The name of the primary model used to ask clarifying questions
        self.model_name = model_name
        # Initialize a memory manager if one is not provided
        self.memory: MemoryManager = memory or MemoryManager()
        # Event hub for advanced collaboration features
        self.collaboration: CollaborationHub | None = collaboration

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
        if self.collaboration:
            await self.collaboration.broadcast("user_query", {"query": query})

        questions = generate_clarifying_questions(query, minimum=3)
        for q in questions:
            if self.collaboration:
                await self.collaboration.broadcast(
                    "clarifying_question", {"question": q}
                )
        return questions

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
        if self.collaboration:
            await self.collaboration.broadcast(
                "assistant_response", {"response": response}
            )
        return response


STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "about",
    "for",
    "with",
    "on",
    "in",
    "of",
    "to",
    "your",
}


def _extract_keywords(query: str, max_keywords: int = 1) -> List[str]:
    """Extract simple keywords from a query string."""
    words = re.findall(r"\w+", query.lower())
    keywords = [w for w in words if w not in STOPWORDS]
    return keywords[:max_keywords]


def generate_clarifying_questions(query: str, minimum: int = 3) -> List[str]:
    """Generate at least ``minimum`` clarifying questions for a query.

    The questions are phrased to draw out the user's intent, constraints,
    and success criteria. The implementation is deterministic so that tests
    can reliably assert the output, while still customising each question to
    the user's request.
    """

    subject = _extract_keywords(query, 1)
    topic = subject[0] if subject else "your request"

    base_questions = [
        f"What is your primary goal regarding {topic}?",
        f"Are there any specific constraints or preferences for {topic}?",
        "What would a successful outcome look like?",
        "Is there any existing context or code we should consider?",
    ]

    num_needed = max(minimum, 3)
    return base_questions[:num_needed]
