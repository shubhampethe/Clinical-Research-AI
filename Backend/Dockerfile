# Use a modern Python base image
FROM python:3.11-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
# --frozen ensures we use the exact versions from uv.lock
RUN /bin/uv sync --frozen

# Copy the rest of the application code
COPY . .

# Expose the ports for both FastAPI (8080) and MCP (8000)
EXPOSE 8080
EXPOSE 8000

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Use entrypoint script to run both processes
CMD ["./entrypoint.sh"]
