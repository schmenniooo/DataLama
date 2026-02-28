# Stores global microservice configuration

from dataclasses import dataclass                                       
                  
@dataclass 
class Config: 
    api_key_field_name: str
    api_key: str
    ollama_base_url: str
    ollama_model: str
    debug: bool
    host: str
    port: int
