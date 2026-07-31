#!/usr/bin/env bash
set -euo pipefail

# Create virtual environment with uv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# Install dependencies (non-interactive, skip if already up to date)
uv sync --frozen 2>/dev/null || uv sync

# Copy .env.example to .env if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

# Start the server
export APP_DIR="$(dirname "$0")/app"
exec "${APP_DIR}/../.venv/bin/python" "${APP_DIR}/server.py"
