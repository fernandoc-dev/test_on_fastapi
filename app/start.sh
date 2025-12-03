#!/bin/sh
# Startup script for FastAPI application
# Enables hot reload in development mode

set -e

# Set PYTHONPATH
export PYTHONPATH=/app

# Determine if we should use reload
if [ "${DEBUG:-false}" = "true" ] || [ "${ENVIRONMENT:-production}" = "development" ]; then
    echo "Starting in DEVELOPMENT mode with hot reload enabled"
    exec uvicorn app.main:app \
        --host "${API_HOST:-0.0.0.0}" \
        --port "${API_PORT:-8000}" \
        --reload \
        --reload-dir /app/app
else
    echo "Starting in PRODUCTION mode"
    exec uvicorn app.main:app \
        --host "${API_HOST:-0.0.0.0}" \
        --port "${API_PORT:-8000}"
fi

