
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

EXPOSE 3000

ENTRYPOINT ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3000"]
