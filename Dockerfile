# FALLBACK: Alternative Docker deployment for Railway
# Use this ONLY if nixpacks.toml fails to force uvicorn
# To use: Set Railway build to "Docker" in project settings

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip list | grep -E "(fastapi|uvicorn)" && \
    echo "uvicorn installed and ready for Railway deployment"

# Copy application code
COPY backend/ .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 app && \
    chown -R app:app /app
USER app

# Health check using internal health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Start command - use uvicorn directly for consistency with nixpacks.toml
# Using exec for proper signal handling
CMD exec uvicorn src.main:app \
    --host 0.0.0.0 \
    --port ${PORT} \
    --workers 2 \
    --log-level info \
    --access-log \
    --no-use-colors