# Dexter Frontend

This directory will contain the React-based frontend for Dexter. The goal is to provide a streamlined and customizable interface where each language model slot can be resized, moved, minimized, or maximized.

Key planned features:

- **Multiple LLM panes**: Each slot (Dexter, Analyst, Engineer, etc.) will have its own chat panel. Panels can be rearranged and resized via a grid layout, making it easy to view conversations side by side.
- **Clarifying dialogue**: Dexter will ask clarifying questions directly through conversation, rather than using hard‑coded patterns. The UI will display these questions and the user’s answers in real time to all collaborating models.
- **Persistent state**: Input drafts and chat history will persist across refreshes to prevent losing work while typing.
- **Speech support**: Optional text‑to‑speech and speech‑to‑text capabilities for hands‑free interaction.

This is a placeholder file outlining the intended direction for the Dexter frontend. Implementation details will be added as development progresses.

## Getting Started

Install dependencies and start the development server:

```bash
npm install
npm run dev
```

The frontend expects a backend URL defined in the `VITE_API_BASE_URL` environment variable (default: `http://localhost:8000`).
