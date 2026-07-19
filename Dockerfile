FROM python:3.12-slim

ARG INSTALL_FFMPEG=false
WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Install ffmpeg conditionally
RUN if [ "$INSTALL_FFMPEG" = "true" ]; then \
    apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*; \
    fi

# Copy project config and install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy the app directory
COPY app/ /app/app/

# Command to run the server
CMD ["/app/.venv/bin/python", "/app/app/server.py"]
