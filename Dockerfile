# =====================================================================
# Stage 1: Base Image
# =====================================================================
FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and running in buffered mode
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# =====================================================================
# Stage 2: Install Python Dependencies
# =====================================================================
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# =====================================================================
# Stage 3: Copy Application Code
# =====================================================================
COPY . /app

# DO NOT COPY SECRET FILES
# .env and SecretKey files must be mounted at runtime, not built into the image.

# Expose MCP server port
EXPOSE 8000

# =====================================================================
# Stage 4: Run FastMCP Server
# =====================================================================
CMD ["fastmcp", "run", "intersight_server.py:mcp", "--transport", "http", "--host", "0.0.0.0", "--port", "8000"]
