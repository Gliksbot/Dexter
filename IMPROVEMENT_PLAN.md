# Improvement Plan for Dexter

This document outlines the current state of Dexter and the work required to
realise its vision of a multi‑agent assistant that can clarify user intent,
coordinate collaborators, and provide both terminal and web interfaces.

## Current Status

- FastAPI backend exposes a `/query` endpoint with a simple health check.
- `AutonomyManager` generates clarifying questions deterministically via keyword
  extraction; it is not yet connected to a live language model.
- Memory management combines short‑term and long‑term SQLite storage with an
  in‑memory knowledge graph, which is not persisted or queried elsewhere.
- `CollaborationHub` broadcasts events to in‑process listeners but lacks a
  network transport such as websockets.
- A React frontend scaffold and a minimal CLI exist, but most UI features remain
  placeholders.
- Tests cover memory, collaboration, and the `/query` endpoint.

## Planned Improvements

### Clarifying questions and autonomy

- Replace keyword‑based clarifications with LLM‑driven question generation.
- Support iterative clarification loops and broadcast both questions and user
  answers to collaborators.
- Expose model configuration via environment variables or a settings file.

### Collaboration and real‑time features

- Add websocket or message‑queue transport so dashboards and remote
  collaborators can receive events live.
- Implement listener management (unsubscribe, error reporting) and a structured
  event schema.

### Memory subsystem

- Store timestamps using timezone‑aware datetimes to address the
  `datetime.utcnow` deprecation warning.
- Provide retrieval functions that combine short‑term context with semantic
  search over long‑term memory.
- Persist the knowledge graph and expose query helpers to other modules.

### UI and CLI

- Break the large `ResizableGrid.jsx` component into dedicated chat panels using
  a grid layout library so panels can be rearranged and resized.
- Preserve unsent user input, contain long messages within scrollable views, and
  add panel minimisation/maximisation controls.
- Expand the CLI to display clarifying questions, show streamed responses, and
  allow switching between conversation sessions.

### Additional UI features

- Dashboard summarising active slots and recent activity.
- Agent management tab for creating, renaming, grouping, and configuring slots
  with preset support.
- Conversation tools: search, filter by slot or date, transcript export, and
  threaded topics.
- Memory explorer to browse and curate short‑ and long‑term memories.
- Skill marketplace to install, update, or remove skills with version info and
  documentation links.
- Workflow runner for building reusable automation chains and schedules.
- Global notifications panel for errors, downloads, and workflow status.
- Analytics tracking response times and token usage per slot.
- Layout customisation: drag, resize, minimise, theme selection, and font
  scaling.
- In‑app help centre with quick tips, searchable documentation, and community
  links.
- Collaboration features such as shared sessions and role‑based permissions.
- Plugin/extension API to allow third‑party panels and integrations.
- Expanded voice and accessibility options including transcription, language
  selection, keyboard shortcuts, and ARIA labels.
- Testing/sandbox mode to prototype prompts or run isolated conversations.
- Improved error handling with structured logs, filtering, download, and clear
  controls.
- Include version info and changelog in Settings.
- Allow importing/exporting of configuration for backup or sharing.
- Provide in‑app feedback mechanism for bug reports or feature requests.

### Repository structure and tooling

- Move core logic into modular packages (`autonomy`, `collaboration`, `skills`,
  etc.) and add type hints throughout.
- Set up continuous integration to run linting and tests.
- Use environment variables or a secrets manager for API keys.

