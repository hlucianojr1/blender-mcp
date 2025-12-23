# Use Python 3.10 slim image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ src/
COPY addon.py ./
COPY main.py ./
COPY README.md ./
COPY LICENSE ./

# Note: .env files are excluded via .dockerignore for security
# Configure via environment variables in docker-compose.yml instead

# Install dependencies using UV
RUN uv sync

# Set environment variables with defaults
ENV BLENDER_HOST=host.docker.internal
ENV BLENDER_PORT=9876

# Expose the default port (though this server connects to Blender, not serves HTTP)
EXPOSE 9876

# Create a non-root user for security
RUN useradd -m -u 1000 blenderuser && chown -R blenderuser:blenderuser /app
USER blenderuser

# Run the application
CMD ["uv", "run", "python", "-m", "blender_mcp.server"]