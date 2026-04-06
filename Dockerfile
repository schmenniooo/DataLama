
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

# Using build stage for dependencies
COPY --from=build /app .

# LLM Communication
ENV LLM_PROVIDER="anthropic"
ENV LLM_PROVIDER_API_TOKEN="anthropic-api-key"
ENV MODEL="claude-sonnet-4-6"

# Knowledge Base Handling
ENV KNOWLEDGE_BASE_ENABLED="false"
ENV KNOWLEDGE_BASE_CONFIG_PATH="/app/config/knowledge_bases.yml"

# Langsmith Integration
ENV LANGSMITH_TRACING="false"
ENV LANGSMITH_API_KEY="langsmith-api-key"
ENV LANGSMITH_PROJECT="my-project"

# Service Config
ENV DEBUG="false"
ENV HOST="0.0.0.0"
ENV PORT=3000

EXPOSE ${PORT}

# Running the application
ENTRYPOINT ["uv", "run", "python", "-m", "src.main"]
