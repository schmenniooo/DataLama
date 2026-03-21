"""Model for network traffic"""
import time

from pydantic import BaseModel


class BaseRequest(BaseModel):
    """Request model for analysis endpoints."""

    data_sets: list[str]
    format: str
    daterange: list[str]


class BaseResponse(BaseModel):
    """Response model for analysis endpoints."""

    message: str
    date: str
