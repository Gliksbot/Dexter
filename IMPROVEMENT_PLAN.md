# Improvement Plan for Dexter

## Clarifying questions
- Remove the existing pattern-based intent detection from `autonomy.py`.
- Let the primary LLM ask clarifying questions dynamically and broadcast those questions and answers to all other LLM slots for context.

## UI overhaul
- Break up the large `ResizableGrid.jsx` component into smaller chat panes.
- Use a grid-layout library (like `react-grid-layout`) to allow users to resize and arrange LLM chat panels side-by-side.
- Preserve unsent user input across renders and contain long messages in scrollable containers.
- Add minimization/maximization controls for each panel and ensure the page doesn’t refresh unexpectedly.

## CLI interface
- Add a `backend/cli.py` script that lets the user interact with Dexter from a terminal.
- The script should prompt for user input, call the autonomy and collaboration functions, and display responses.

## Repository structure
- Move core logic into modular packages (`autonomy`, `collaboration`, `skills`, etc.).
- Use environment variables or secrets management for API keys.
