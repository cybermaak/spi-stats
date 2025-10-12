# Build stage - use Python image for building dependencies
FROM --platform=linux/arm64 python:3.13-slim

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Install Python runtime and system dependencies for graphics
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    procps \
    libfontconfig1 \
    libegl1 \
    libgl1 \
    libegl-mesa0 \
    libgl1-mesa-dri \
    && rm -rf /var/lib/apt/lists/*

#ENV LD_LIBRARY_PATH=/usr/lib/:/usr/lib/aarch64-linux-gnu/
#RUN echo $LD_LIBRARY_PATH
#ENV PYTHONPATH=$LD_LIBRARY_PATH:$PYTHONPATH

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy fonts directory
COPY fonts/ /app/fonts/
# Removing this font conf file because it cause a noise warning in pictex
RUN rm /usr/share/fontconfig/conf.avail/05-reset-dirs-sample.conf

# Copy src directory
COPY src/ /app/src/

# Health check to ensure stats.py is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD pgrep -f "python3 /app/src/stats.py" || exit 1

# Run the startup script
CMD ["python3", "/app/src/stats.py"]