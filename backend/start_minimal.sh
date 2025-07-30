#!/bin/bash
# Minimal start script for Railway deployment testing
# Use this if nixpacks.toml and Procfile both fail

echo "Starting FastAPI with minimal uvicorn configuration..."
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "PORT environment variable: $PORT"
echo "Available files:"
ls -la

# Start with the most basic uvicorn command possible
exec uvicorn main:app --host 0.0.0.0 --port $PORT --log-level info