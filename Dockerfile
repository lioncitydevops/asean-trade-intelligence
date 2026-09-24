# Multi-stage optimized container for Maritime Intelligence Terminal & Publisher
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8000

# Install required system dependencies for fonts, image processing, and PDF rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    fonts-dejavu-core \
    fonts-liberation \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code, assets, and configs
COPY src/ ./src/
COPY main.py .
COPY pytest.ini .

# Create output directory
RUN mkdir -p output

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start FastAPI server
CMD ["python", "main.py", "--serve", "--host", "0.0.0.0", "--port", "8000"]
