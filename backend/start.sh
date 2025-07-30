#!/bin/bash
# Emergency start script for Railway deployment
# This script tries multiple startup methods

echo "=== Railway Deployment Start Script ==="
echo "Environment: $ENVIRONMENT"
echo "Port: $PORT"
echo "Working Directory: $(pwd)"
echo "Python Version: $(python --version)"

# Function to test if port is available
test_health() {
    echo "Testing health endpoint..."
    sleep 5
    curl -f "http://localhost:$PORT/health" || echo "Health check failed"
}

# Method 1: Try gunicorn (recommended for production)
echo "Attempting to start with gunicorn..."
if command -v gunicorn &> /dev/null; then
    echo "Gunicorn found, starting..."
    gunicorn main:app \
        --workers 1 \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind "0.0.0.0:$PORT" \
        --timeout 120 \
        --log-level info \
        --access-logfile - \
        --error-logfile - \
        --preload &
    
    GUNICORN_PID=$!
    echo "Gunicorn started with PID: $GUNICORN_PID"
    
    # Test if it's working
    sleep 3
    if kill -0 $GUNICORN_PID 2>/dev/null; then
        echo "Gunicorn is running, testing health..."
        test_health &
        wait $GUNICORN_PID
    else
        echo "Gunicorn failed to start, trying uvicorn..."
    fi
fi

# Method 2: Fallback to uvicorn
echo "Starting with uvicorn as fallback..."
uvicorn main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --log-level info \
    --access-log