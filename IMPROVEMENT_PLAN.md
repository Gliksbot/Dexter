# Improvement Plan for Dexter

## Clarifying questions
- Remove the existing pattern-based intent detection from `autonomy.py`.
- Let the primary LLM ask clarifying questions dynamically and broadcast those questions and answers to all other LLM slots for context.

## UI overhaul
- Break up the large `ResizableGrid.jsx` component into smaller chat panes.
- Use a grid-layout library (like `react-grid-layout`) to allow users to resize and arrange LLM chat panels side-by-side.
- Preserve unsent user input across renders and contain long messages in scrollable containers.
- Add minimization/maximization controls for each panel and ensure the page doesn’t refresh unexpectedly.

## Additional UI features
- Dashboard/Home tab summarizing active slots, recent activity, and system health.
- Dedicated agent/model management tab for creating, renaming, grouping, and configuring slots, with preset support.
- Conversation enhancements including search, filtering by slot or date, transcript export, and threaded topics.
- Memory explorer to browse and curate short-term and long-term memory entries.
- Skill marketplace to install, update, or remove skills with version info and documentation links.
- Task/workflow runner for building reusable automation chains and schedules.
- Global notifications panel for errors, downloads, and workflow status.
- Analytics and metrics tracking response times and token usage per slot.
- Layout customization: drag, resize, minimize, theme selection, and font scaling.
- In-app help center with quick tips, searchable documentation, and community links.
- Collaboration features such as shared sessions and role-based permissions.
- Plugin/extension support to allow third-party UI panels and integrations.
- Expanded voice and accessibility options, including transcription, language selection, keyboard shortcuts, and ARIA labels.
- Testing/sandbox mode to prototype prompts or run isolated conversations.
- Improved error handling with structured logs, filtering, downloading, and clearing options.
- Include version info and changelog in Settings.
- Allow importing/exporting of configuration for backup or sharing.
- Provide in-app feedback mechanism for bug reports or feature requests.

## CLI interface
- Add a `backend/cli.py` script that lets the user interact with Dexter from a terminal.
- The script should prompt for user input, call the autonomy and collaboration functions, and display responses.

## Repository structure
- Move core logic into modular packages (`autonomy`, `collaboration`, `skills`, etc.).
- Use environment variables or secrets management for API keys.
