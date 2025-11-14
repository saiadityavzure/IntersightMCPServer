# -------------------------------------------------------------
# Intersight MCP Server - Dockerfile
# -------------------------------------------------------------

FROM python:3.12-slim

# -------------------------------------------------------------
# System dependencies
# -------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------------------
# Create working directory
# -------------------------------------------------------------
WORKDIR /app

# -------------------------------------------------------------
# Copy requirement files first (better cache)
# -------------------------------------------------------------
COPY requirements.txt .

# -------------------------------------------------------------
# Install Python requirements
# -------------------------------------------------------------
RUN pip install --no-cache-dir -r requirements.txt

# Install fastmcp CLI globally
RUN pip install --no-cache-dir fastmcp

# -------------------------------------------------------------
# Copy project files
# -------------------------------------------------------------
COPY . .

# -------------------------------------------------------------
# Environment variables
# -------------------------------------------------------------
ENV PYTHONUNBUFFERED=1
ENV FASTMCP_HOST=0.0.0.0
ENV FASTMCP_PORT=8000

# -------------------------------------------------------------
# Expose port for HTTP transport
# -------------------------------------------------------------
EXPOSE 8000

# -------------------------------------------------------------
# ENTRYPOINT to start the MCP server
# -------------------------------------------------------------
CMD ["fastmcp", "run", "intersight_server.py:mcp", "--host", "0.0.0.0", "--transport", "http", "--port", "8000"]
