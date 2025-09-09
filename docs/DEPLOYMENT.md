# Deployment (Docker-first)

## Prereqs
- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- Optional: Git (to clone) and Make

## Quick start (dev)
```bash
# macOS/Linux
docker compose -f infra/docker-compose.yml up --build

# Windows
./setup_and_run.ps1 -Rebuild
```
- API docs: http://localhost:${API_PORT:-8000}/docs
- Web UI:   http://localhost:${WEB_PORT:-5173}

Data (SQLite) persists in named volume `dexter_data`.

## Production tips
- Switch api command to non-reload uvicorn
- Add reverse proxy (Caddy/Nginx) with TLS
- Move from SQLite -> Postgres/pgvector for retrieval
- Optional Graph: enable `neo4j` profile in compose
