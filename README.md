# Dexter

Dexter is a multi-agent AI assistant orchestrator designed to help automate tasks through clarifying dialogues, collaborative large language models, and sandboxed skill creation. This repository is a fresh start inspired by the gliksbot project, incorporating improvements outlined in `IMPROVEMENT_PLAN.md`.

## Structure

- `backend/` – Python server code for autonomy, collaboration, skill management, and CLI interaction.
- `frontend/` – React-based web interface (work in progress) for interacting with Dexter.

## Getting Started

This repository is under active development. See `IMPROVEMENT_PLAN.md` for high-level goals and planned features.

### Advanced collaboration

The backend now includes a lightweight ``CollaborationHub`` which broadcasts
user queries, Dexter's clarifying questions, and responses to any number of
listeners. This enables real-time cooperation between Dexter and supporting
teammates or tools. Clarifying questions are generated dynamically to surface
intent, constraints, and success criteria, giving collaborators the context and
time they need to craft high-quality solutions.
