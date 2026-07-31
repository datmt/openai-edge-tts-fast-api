FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy project config and install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy the app directory
COPY app/ /app/app/

# Command to run the server
CMD ["/app/.venv/bin/python", "/app/app/server.py"]
