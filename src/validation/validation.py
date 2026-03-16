"""Client input validation module"""

from datetime import datetime

from src.model.api.api_model import BaseRequest

SUPPORTED_FORMATS = {"csv", "json", "yaml", "yml"}
DATE_FORMAT = "%Y-%m-%d"


def validate_request(request: BaseRequest) -> str:
    """Validates the incoming analysis request."""
    message = _validate_data_to_analyse(data_sets=request.data_sets)
    if message != "":
        return message

    message = _validate_data_format(data_format=request.format)
    if message != "":
        return message

    message = _validate_daterange(daterange=request.daterange)
    if message != "":
        return message

    return ""


def _validate_data_to_analyse(data_sets: list[str]) -> str:
    if len(data_sets) == 0:
        return "Data cannot be empty"

    for data_set in data_sets:
        if len(data_set) == 0:
            return "Single data sets cannot be empty"

    return ""


def _validate_data_format(data_format: str) -> str:
    if data_format.lower() not in SUPPORTED_FORMATS:
        return (
            f"Unsupported format '{data_format}'. "
            f"Must be one of: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    return ""


def _validate_daterange(daterange: list[str]) -> str:
    if len(daterange) != 2:
        return "daterange must contain exactly 2 dates"

    dates = []
    for date_str in daterange:
        try:
            dates.append(datetime.strptime(date_str, DATE_FORMAT))
        except ValueError:
            return f"Invalid date '{date_str}'. Expected format: YYYY-MM-DD"

    if dates[0] >= dates[1]:
        return "daterange start date must be before end date"

    return ""
