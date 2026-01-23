# Build stage - use Python image for building dependencies
FROM --platform=$BUILDPLATFORM python:3.13-slim

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Install Python runtime and system dependencies for graphics and SPI
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    procps \
    libfontconfig1 \
    libegl1 \
    libgl1 \
    libegl-mesa0 \
    libgl1-mesa-dri \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project files for dependency installation
COPY pyproject.toml uv.lock* ./

# Install Python dependencies using uv
# Use --system to install into the system Python environment
RUN uv pip install --system --no-cache -r pyproject.toml

# Copy fonts directory
COPY fonts/ /app/fonts/

# Copy src directory
COPY src/ /app/src/

# Health check to ensure stats.py is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD pgrep -f "python3 /app/src/stats.py" || exit 1

# Run the direct SPI stats
CMD ["python3", "/app/src/stats.py"]
