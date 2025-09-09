"""
Autonomy manager for Dexter.

This module defines the classes responsible for coordinating queries from
users, asking clarifying questions through Dexter's built-in heuristics,
and managing conversations across multiple LLM collaborators. It
integrates Dexter's memory system to retain both recent context and
long-term conversation history. The initial implementation here provides
a simple framework and placeholder logic to illustrate the intended API.
"""

from __future__ import annotations

from typing import Callable, List

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
        question_generator: Callable[[str, int], List[str]] | None = None,
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
        # Function used to produce clarifying questions
        self.question_generator = (
            question_generator or generate_clarifying_questions
        )

    async def ask_clarifications(self, query: str) -> List[str]:
        """
        Ask clarifying questions to the user about their query.

        This implementation stores the original query in short- and
        long-term memory, then uses a lightweight ``question_generator``
        to produce clarifying questions. By default a simple heuristic is
        used so that Dexter can operate without contacting an external
        language model.
        """
        # Store the user's initial query in memory
        self.memory.add_message("user", query)
        if self.collaboration:
            await self.collaboration.broadcast("user_query", {"query": query})

        questions = self.question_generator(query, minimum=3)
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

    async def record_clarification_answers(self, answers: List[str]) -> None:
        """Record user answers to clarifying questions.

        Each answer is stored in memory and broadcast so that background
        collaborators receive updates in real time. After all answers are
        processed a ``clarifications_complete`` event is emitted to signal
        that collaborators may begin drafting final proposals.
        """
        for ans in answers:
            self.memory.add_message("user", ans)
            if self.collaboration:
                await self.collaboration.broadcast(
                    "clarification_answer", {"answer": ans}
                )
        if self.collaboration:
            await self.collaboration.broadcast(
                "clarifications_complete", {"count": len(answers)}
            )


def generate_clarifying_questions(query: str, minimum: int = 3) -> List[str]:
    """Generate clarifying questions for ``query`` using a simple template.

    Dexter relies on a deterministic set of prompts that incorporate the
    user's query. Exactly ``minimum`` questions are returned so that the
    caller can anticipate the number of required responses.
    """

    templates = [
        "What is the main goal of '{q}'?",
        "Are there any constraints or preferences I should consider?",
        "Is there additional context about '{q}' that would help?",
    ]
    questions = [t.format(q=query) for t in templates[:minimum]]

    if len(questions) < minimum:
        questions.extend(["Could you provide more detail?"] * (minimum - len(questions)))

    return questions[:minimum]


