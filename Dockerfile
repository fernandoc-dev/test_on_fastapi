FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (maintain app/ package structure)
COPY app/ ./app/

# Copy startup script
COPY app/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose port (default 8000, can be overridden via docker-compose)
EXPOSE 8000

# Default command (uses startup script which handles hot reload)
CMD ["/app/start.sh"]

