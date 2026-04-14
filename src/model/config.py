"""Stores global microservice configuration."""

from dataclasses import dataclass


@dataclass
class Config:  # pylint: disable=too-many-instance-attributes
    """Holds all configuration values for the microservice."""

    api_key_field_name: str
    api_key: str
    llm_provider: str
    llm_provider_api_token: str
    model: str
    knowledge_base_enabled: bool
    knowledge_base_config_path: str
    langsmith_tracing_enabled: bool
    langsmith_api_key: str
    langsmith_project: str
    debug: bool
    host: str
    port: int
