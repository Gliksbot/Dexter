#!/usr/bin/env bash

# setup_and_run.sh - bootstrap script for Dexter development environment.

set -e

# Check for required tools
command -v python3 >/dev/null 2>&1 || { echo >&2 "Python 3 is required but not installed."; exit 1; }
command -v pip >/dev/null 2>&1 || { echo >&2 "pip is required but not installed."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo >&2 "Node.js/npm is required but not installed."; exit 1; }

# Optional: check for docker
if ! command -v docker >/dev/null 2>&1; then
  echo "Warning: Docker is not installed. Skills requiring sandboxing will be unavailable."
  echo "Please install Docker from https://docs.docker.com/get-docker/ if you wish to use the sandbox."
fi

# Create and activate virtual environment
python3 -m venv .venv
. .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
if [ -d "frontend" ]; then
  (cd frontend && npm install)
fi

echo "Setup complete."
echo "To run the backend: source .venv/bin/activate && uvicorn backend.main:app --reload"
echo "To run the frontend: (cd frontend && npm run dev)"
