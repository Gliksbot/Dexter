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
            question_generator or generate_clarifying_questions_llm
        )

    async def ask_clarifications(self, query: str) -> List[str]:
        """
        Ask clarifying questions to the user about their query.

        This implementation stores the original query in short- and long-term
        memory, then uses an LLM-driven ``question_generator`` to produce
        clarifying questions. By default this calls Dexter's primary
        language model so that the questions are created dynamically
        rather than from a hard-coded list.
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


def generate_clarifying_questions_llm(query: str, minimum: int = 3) -> List[str]:
    """Generate clarifying questions for ``query`` using an LLM.

    This function contacts the configured language model (via the OpenAI
    API) and instructs it to produce at least ``minimum`` clarifying
    questions. The questions are returned as a list of strings with any
    empty lines removed. If the model returns fewer than the requested
    number, the list is padded with generic prompts to satisfy the minimum.
    """

    import os

    try:
        import openai
    except ImportError as exc:  # pragma: no cover - import guarded for tests
        raise RuntimeError("openai package is required for question generation") from exc

    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = (
        "Ask at least {n} concise clarifying questions about the following user "
        "request. Respond with each question on a separate line.\nRequest: {q}".format(
            n=minimum, q=query
        )
    )

    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are Dexter, an AI assistant that clarifies user intent.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    text = resp["choices"][0]["message"]["content"]
    questions = [
        line.strip("- ")
        for line in text.splitlines()
        if line.strip()
    ]

    if len(questions) < minimum:
        questions.extend(["Could you provide more detail?"] * (minimum - len(questions)))

    return questions[:minimum]


