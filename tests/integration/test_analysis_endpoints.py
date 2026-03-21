"""Integration tests for all analysis endpoints."""

from datetime import datetime

import pytest
from langchain_core.exceptions import LangChainException

from tests.integration.conftest import HEADERS, SEPARATOR, VALID_PAYLOAD

ENDPOINTS = ["forecasting", "summary", "anomaly", "pattern", "comparison"]


# --- Authentication ---

@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_without_api_key_returns_401(client, endpoint):
    """Request without API key is rejected."""
    test_client, _ = client
    response = test_client.post(f"/{endpoint}", json=VALID_PAYLOAD)
    assert response.status_code == 401


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_with_wrong_api_key_returns_401(client, endpoint):
    """Request with wrong API key is rejected."""
    test_client, _ = client
    response = test_client.post(f"/{endpoint}", json=VALID_PAYLOAD, headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


# --- Happy path ---

@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_returns_200_with_valid_payload(client, endpoint):
    """Valid request returns 200."""
    test_client, _ = client
    response = test_client.post(f"/{endpoint}", json=VALID_PAYLOAD, headers=HEADERS)
    assert response.status_code == 200


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_response_contains_message_and_date(client, endpoint):
    """Response contains a non-empty message string and a valid ISO date."""
    test_client, _ = client
    response = test_client.post(f"/{endpoint}", json=VALID_PAYLOAD, headers=HEADERS)
    body = response.json()
    assert isinstance(body["message"], str)
    assert len(body["message"]) > 0
    assert datetime.fromisoformat(body["date"])


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_llm_response_is_returned_as_message(client, endpoint):
    """The LLM response text is returned in the message field."""
    test_client, mock_service = client
    mock_service.make_analyse_request.return_value = "Custom output"
    response = test_client.post(f"/{endpoint}", json=VALID_PAYLOAD, headers=HEADERS)
    assert response.json()["message"] == "Custom output"


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_ai_service_called_with_correct_analysis_type(client, endpoint):
    """AiCommunicationService is called with the matching analysis type."""
    test_client, mock_service = client
    test_client.post(f"/{endpoint}", json=VALID_PAYLOAD, headers=HEADERS)
    mock_service.make_analyse_request.assert_called_once()
    call_kwargs = mock_service.make_analyse_request.call_args
    assert call_kwargs.kwargs["analysis_type"] == endpoint


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_multiple_datasets_are_joined_with_separator(client, endpoint):
    """Multiple datasets are joined with the separator before sending to the AI service."""
    test_client, mock_service = client
    payload = {
        "data_sets": ["date,value\n2024-01-01,100", "date,value\n2024-01-01,200"],
        "format": "csv",
        "daterange": ["2024-01-01", "2024-12-31"],
    }
    test_client.post(f"/{endpoint}", json=payload, headers=HEADERS)
    call_kwargs = mock_service.make_analyse_request.call_args
    assert call_kwargs.kwargs["data"] == SEPARATOR.join(payload["data_sets"])


# --- Validation ---

@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize("payload_override,description", [
    ({"data_sets": []}, "empty data_sets"),
    ({"data_sets": [""]}, "empty dataset string"),
    ({"format": "xml"}, "unsupported format"),
    ({"daterange": ["2024-01-01"]}, "single date in range"),
    ({"daterange": ["01-01-2024", "12-31-2024"]}, "invalid date format"),
    ({"daterange": ["2024-12-31", "2024-01-01"]}, "inverted daterange"),
])
def test_validation_returns_400(client, endpoint, payload_override, description):  # pylint: disable=unused-argument
    """Invalid payload is rejected with 400."""
    test_client, _ = client
    response = test_client.post(
        f"/{endpoint}",
        json={**VALID_PAYLOAD, **payload_override},
        headers=HEADERS,
    )
    assert response.status_code == 400


# --- LLM errors ---

@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_returns_502_on_llm_error(client, endpoint):
    """AiCommunicationService failure returns 502."""
    test_client, mock_service = client
    mock_service.make_analyse_request.side_effect = LangChainException("model not found")
    response = test_client.post(f"/{endpoint}", json=VALID_PAYLOAD, headers=HEADERS)
    assert response.status_code == 502
