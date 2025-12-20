ARG BUILD_FROM=python:3.11-alpine
FROM ${BUILD_FROM}

# Install system dependencies
RUN apk add --no-cache \
    bash \
    curl \
    jq \
    ca-certificates \
    gcc \
    musl-dev \
    linux-headers

# Copy requirements
COPY requirements.txt /tmp/

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application
COPY app /app

# Create data directory
RUN mkdir -p /data

# Set working directory
WORKDIR /app

# Run the application
CMD ["/app/run.sh"]