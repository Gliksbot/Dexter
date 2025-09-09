"""
Memory management for Dexter.

This module defines classes for managing short-term and long-term memory as
well as a simple knowledge graph. Short-term memory keeps a sliding window
of recent messages during an active conversation. Long-term memory stores
all messages persistently in a SQLite database so that conversation
history can be retrieved across sessions. The KnowledgeGraph class
maintains a directed graph of entities and relations extracted from
Dexter's interactions.
"""

from __future__ import annotations

from typing import List, Dict, Any, Tuple
import sqlite3
import os
import json

class ShortTermMemory:
    """A simple FIFO buffer for recent messages."""

    def __init__(self, max_messages: int = 50) -> None:
        self.max_messages = max_messages
        self.messages: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str) -> None:
        """Append a message to short-term memory and enforce the size limit."""
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def get_context(self) -> List[Dict[str, str]]:
        """Return a copy of the current short-term context."""
        return list(self.messages)

class LongTermMemory:
    """Persistent storage for all conversation messages using SQLite."""

    def __init__(self, db_path: str = "memory.db") -> None:
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._setup()

    def _setup(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def add_message(self, role: str, content: str) -> None:
        """Insert a message into the long-term memory table."""
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO messages (role, content) VALUES (?, ?)", (role, content)
        )
        self.conn.commit()

    def get_recent(self, limit: int = 100) -> List[Dict[str, str]]:
        """Retrieve the most recent messages in chronological order."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT role, content FROM messages ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = cur.fetchall()
        return [
            {"role": role, "content": content}
            for role, content in reversed(rows)
        ]

class KnowledgeGraph:
    """A very simple in-memory knowledge graph."""

    def __init__(self) -> None:
        self.nodes: set[str] = set()
        self.edges: Dict[str, List[Tuple[str, str]]] = {}

    def add_relationship(self, src: str, relation: str, dst: str) -> None:
        """Add a directed relationship to the graph."""
        self.nodes.update([src, dst])
        self.edges.setdefault(src, []).append((relation, dst))

    def query(self, entity: str) -> List[Tuple[str, str]]:
        """Get all outbound edges (relation, target) from an entity."""
        return self.edges.get(entity, [])


class NeuralNetworkMemory:
    """A tiny single-layer neural network trained online.

    The network maintains a weight vector and performs a simple
    delta rule update for each new message. It is intentionally
    lightweight so that it can operate incrementally without
    external dependencies.
    """

    def __init__(
        self, weight_path: str = "neural.json", input_size: int = 26, learning_rate: float = 0.01
    ) -> None:
        self.weight_path = weight_path
        self.input_size = input_size
        self.learning_rate = learning_rate
        self.weights: List[float] = [0.0] * self.input_size
        if os.path.exists(self.weight_path):
            try:
                with open(self.weight_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) == self.input_size:
                        self.weights = [float(x) for x in data]
            except (OSError, json.JSONDecodeError):
                pass

    def _vectorize(self, text: str) -> List[float]:
        vec = [0.0] * self.input_size
        for ch in text.lower():
            if "a" <= ch <= "z":
                idx = ord(ch) - ord("a")
                if idx < self.input_size:
                    vec[idx] += 1.0
        return vec

    def predict(self, text: str) -> float:
        x = self._vectorize(text)
        return sum(w * xi for w, xi in zip(self.weights, x))

    def update(self, text: str, target: float) -> None:
        x = self._vectorize(text)
        prediction = sum(w * xi for w, xi in zip(self.weights, x))
        error = target - prediction
        self.weights = [w + self.learning_rate * error * xi for w, xi in zip(self.weights, x)]
        try:
            with open(self.weight_path, "w", encoding="utf-8") as f:
                json.dump(self.weights, f)
        except OSError:
            pass

class MemoryManager:
    """
    Provides a unified interface over short-term memory, long-term memory,
    and a knowledge graph. Dexter can use this to store and retrieve
    contextual information from different sources.
    """

    def __init__(
        self,
        db_path: str = "memory.db",
        short_term_limit: int = 50,
        neural_path: str | None = None,
    ) -> None:
        self.short_term = ShortTermMemory(max_messages=short_term_limit)
        self.long_term = LongTermMemory(db_path)
        self.knowledge_graph = KnowledgeGraph()
        self.neural_memory = NeuralNetworkMemory(weight_path=neural_path or "neural.json")

    def add_message(self, role: str, content: str) -> None:
        """Store a message in both short-term and long-term memory."""
        self.short_term.add_message(role, content)
        self.long_term.add_message(role, content)
        self.learn(role, content)

    def get_recent_context(self, limit: int = 50) -> List[Dict[str, str]]:
        """Get recent context from short-term memory or fallback to long-term."""
        context = self.short_term.get_context()
        if not context:
            context = self.long_term.get_recent(limit)
        return context

    def add_knowledge(self, src: str, relation: str, dst: str) -> None:
        """Add a fact to the knowledge graph."""
        self.knowledge_graph.add_relationship(src, relation, dst)

    def query_knowledge(self, entity: str) -> List[Tuple[str, str]]:
        """Query relationships for an entity."""
        return self.knowledge_graph.query(entity)

    def learn(self, role: str, content: str) -> None:
        """Update the neural network with the new message."""
        target = 1.0 if role == "user" else -1.0
        self.neural_memory.update(content, target)

    def predict(self, content: str) -> float:
        """Predict a numeric value for a message using neural memory."""
        return self.neural_memory.predict(content)
