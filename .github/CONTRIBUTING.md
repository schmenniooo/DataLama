# Contributing to DataLama

Thank you for your interest in contributing to DataLama! This document outlines the process for contributing to this project.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) for dependency management
- A running [Ollama](https://ollama.com/) instance (for local testing)
- Docker (optional, for container testing)

## Getting Started

1. Fork the repository and clone your fork:
   ```bash
   git clone https://github.com/<your-username>/DataLama.git
   cd DataLama
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Copy and configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Ollama URL, API key, etc.
   ```

4. Run the service locally:
   ```bash
   uv run python -m src.main
   ```

## Development Workflow

1. Create a branch from `main` with a descriptive name:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   # or
   git checkout -b refactoring/issue-description
   ```

2. Make your changes, then lint and test before pushing:
   ```bash
   uv run pylint ./src
   uv run pylint ./tests
   uv run pytest ./tests
   ```

3. Open a pull request against `main`. The CI pipeline will automatically run lint, build, and tests.

## Code Standards

- Follow the existing code style — pylint is enforced in CI and must pass
- Keep new functionality covered by tests in `./tests`
- Do not commit secrets, API keys, or credentials
- Keep `DEBUG=false` behavior in mind — authentication is required by default

## Pull Request Guidelines

- Keep PRs focused on a single concern
- Write a clear title and description explaining what and why
- Reference any related issues
- Ensure all CI checks pass before requesting a review
- Assign project owner (@schmenniooo) as reviewer

## Reporting Issues

Please open a GitHub issue with a clear description of the problem, steps to reproduce, and the expected vs. actual behavior. Assign project owner (@schmenniooo).
