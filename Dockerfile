
# Build stage
FROM python:3.13-slim AS build

# Installing uv
COPY --from=ghcr.io/astral-sh/uv:0.8.21 /uv /uvx /bin/
WORKDIR /app

# Installing dependencies
COPY uv.lock pyproject.toml ./
RUN uv sync --no-install-project --no-dev
COPY . . 
RUN uv sync --frozen --no-dev

# Run stage
FROM python:3.13-slim AS runtime

# Installing uv
COPY --from=ghcr.io/astral-sh/uv:0.8.21 /uv /uvx /bin/
WORKDIR /app

# Using build stage
COPY --from=build /app .

# Setting environment variables
ENV MODEL="claude-sonnet-4-6"
ENV LLM_PROVIDER_API_TOKEN="anthropic-api-key"
ENV DEBUG="false"
ENV HOST="0.0.0.0"
ENV PORT=3000

EXPOSE ${PORT}

# Running the application
ENTRYPOINT ["uv", "run", "python", "-m", "src.main"]
