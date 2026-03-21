# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DataLama is a Python microservice that accepts data (CSV, JSON, YAML) and returns LLM-powered analysis (forecasting, summary, anomaly detection, pattern recognition, dataset comparison). Built with FastAPI, LangChain, and uv for package management.

## Common Commands

```bash
# Install dependencies
uv sync

# Run the application locally
uv run python -m src.main

# Run all tests
uv run pytest ./tests

# Run a single test file
uv run pytest ./tests/unit/ai/test_communication_service.py

# Run a single test by name
uv run pytest ./tests -k "test_name"

# Lint source and tests
uv run pylint ./src
uv run pylint ./tests

# Build package
uv build
```

## Architecture

**Entry point**: `src/main.py` — loads `.env`, builds a `Config` dataclass, creates and runs the `Server`.

**Request flow**: FastAPI app → `AuthInterceptor` middleware (API key check, skipped in debug mode) → `AnalysisRouter` → `AiCommunicationService` → LangChain `init_chat_model` → LLM provider.

Key modules:
- `src/server/server.py` — `Server` class wires up middleware, AI service, and routes, then starts uvicorn
- `src/api/analysis_router.py` — `AnalysisRouter` registers all endpoints; each analysis type delegates to a shared `_do_analyze_request` method that validates input, joins datasets with a separator, and calls the AI service
- `src/ai/communication_service.py` — `AiCommunicationService` uses LangChain's `init_chat_model` with configurable model string (e.g. `anthropic/claude-sonnet-4-5-20250514`); prompt templates are built from a `BASE_PROMPT` + analysis-type-specific instructions stored in the `analyses_types` dict
- `src/middleware/authentication.py` — `AuthInterceptor` returns a dynamic `BaseHTTPMiddleware` subclass for API key validation
- `src/validation/validation.py` — validates request data_sets, format (csv/json/yaml/yml), and daterange
- `src/model/api/api_model.py` — Pydantic `BaseRequest` and `BaseResponse` models
- `src/model/config/config.py` — `Config` dataclass holding all env-based configuration

## Testing

Tests are split into `tests/unit/` and `tests/integration/`. Shared fixtures live in `tests/conftest.py` (provides `test_config` and `test_config_with_key` fixtures). pytest is configured with `pythonpath = ["."]` and `asyncio_mode = "auto"` in `pyproject.toml`.

## CI/CD

GitHub Actions workflow (`python-package.yml`) runs on PRs and pushes to `main`: installs via uv, lints src and tests with pylint, builds, then runs pytest. Additional workflows handle Docker image publishing (`docker.yml`), Helm chart publishing (`helm.yml`), and CodeQL analysis (`codeql.yml`).

## Configuration

The app reads environment variables (see README for full list). Key ones: `MODEL` (LangChain model identifier), `LLM_PROVIDER_API_TOKEN`, `API_KEY`, `DEBUG` (disables auth when `true`). A `.env` file is loaded if present.

## Deployment

- **Docker**: Multi-stage build with `python:3.13-slim` and uv. Entrypoint: `uv run python -m src.main`.
- **Helm**: Chart at `helm/datalama-chart/` includes Traefik reverse proxy, Redis for rate limiting, and HPA autoscaling. Published to GHCR.

## Pylint

Disabled messages: `fixme`, `logging-fstring-interpolation`, `raise-missing-from` (configured in `pyproject.toml`).
