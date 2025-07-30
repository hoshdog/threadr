#!/bin/bash
# Start script for Railway deployment with src/ structure

echo "Starting Threadr backend..."
echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Port: $PORT"

# Ensure we're in the backend directory
cd /app/backend || cd backend || true

# Set PYTHONPATH if not already set
export PYTHONPATH="${PYTHONPATH:-/app/backend:/app/backend/src}"

# Start uvicorn with the correct module path
exec python -m uvicorn src.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers 1 \
    --log-level info \
    --access-log \
    --timeout-keep-alive 30