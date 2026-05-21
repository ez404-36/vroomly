#!/bin/bash
set -e

if [ ! -f /app/.venv/bin/python ]; then
    uv sync --locked --no-editable --no-install-project
fi

exec "$@"
