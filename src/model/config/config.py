"""Stores global microservice configuration."""

from dataclasses import dataclass


@dataclass
class Config:
    """Holds all configuration values for the microservice."""

    api_key_field_name: str
    api_key: str
    llm_provider: str
    llm_provider_api_token: str
    model: str
    langsmith_tracing_enabled: bool
    langsmith_api_key: str
    langsmith_project: str
    debug: bool
    host: str
    port: int
