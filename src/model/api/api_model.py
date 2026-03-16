"""Model for network traffic"""

from pydantic import BaseModel

class BaseRequest(BaseModel):
    data_sets: list[str] # List of data sets
    format: str # CSV, JSON or YAML
    daterange: list[str] # Max 2 dates as range

class BaseResponse(BaseModel):
    message: str
