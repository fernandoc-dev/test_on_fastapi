FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Expose port (default 8000, can be overridden via docker-compose)
EXPOSE 8000

# Default command (uses environment variables from docker-compose)
CMD ["sh", "-c", "uvicorn main:app --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000}"]

