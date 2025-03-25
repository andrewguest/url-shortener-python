FROM python:3.13-slim-bookworm

# Copy the uv binary from their image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

LABEL authors="Andrew"

COPY . /app
WORKDIR /app

RUN apt update && apt upgrade -y

# Install the project's dependencies
RUN uv python install && \
    uv venv && \
    uv sync --frozen

EXPOSE 8000

# Granian workers
ENV GRANIAN_WORKERS=2
ENV GRANIAN_WORKERS_LIFETIME=86400
ENV GRANIAN_RESPAWN_FAILED_WORKERS=true

# Granian logging
ENV GRANIAN_LOG_ACCESS_ENABLED=true
ENV GRANIAN_LOG_LEVEL=debug

# Granian loop
ENV GRANIAN_LOOP=uvloop


ENTRYPOINT ["uv", "run", "granian", "--interface", "asgi", "main:app", "--host", "0.0.0.0", "--port", "8000"]