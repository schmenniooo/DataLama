"""Model for network traffic"""
from typing import Any

from pydantic import BaseModel


class BaseRequest(BaseModel):
    """Request model for analysis endpoints."""

    data_sets: list[Any]
    format: str
    daterange: list[str]


class BaseResponse(BaseModel):
    """Response model for analysis endpoints."""

    message: str
    date: str
