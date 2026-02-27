"""Authentication module"""

from fastapi import Request

class AuthInterceptor:
    """Handles authentication through api tokens"""

    def __init__(self, api_key_field_name: str, api_key: str):
        self.api_key_field_name = api_key_field_name 
        self.api_key = api_key

    def register_auth_middleware(request: Request, call_next):
        pass
