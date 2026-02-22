
# Build stage
FROM python:3.13-slim as build

# Installing uv
COPY --from=ghcr.io/astral-sh/uv:0.8.21 /uv /uvx /bin/
WORKDIR /app

# Installing dependencies
COPY uv.lock pyproject.toml ./
RUN uv sync --no-install-project --no-dev
COPY . . 
RUN uv sync --frozen --no-dev

# Run stage
FROM python:3.13-slim as runtime
WORKDIR /app
COPY --from=build --chown=appuser:appgroup /app .

ARG PORT=3000
ENV PORT=${PORT}

# Starting uvicorn server
ENTRYPOINT ["uv", "run", "uvicorn", "src.main:app", "--reload", "--port", ${PORT}]
