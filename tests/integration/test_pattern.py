"""Integration tests for the /pattern endpoint."""

import ollama
import pytest

from tests.integration.conftest import HEADERS, SEPARATOR, VALID_PAYLOAD


# --- Authentication ---

def test_pattern_without_api_key_returns_401(client):
    """Request without API key is rejected."""
    test_client, _ = client
    response = test_client.post("/pattern", json=VALID_PAYLOAD)
    assert response.status_code == 401


def test_pattern_with_wrong_api_key_returns_401(client):
    """Request with wrong API key is rejected."""
    test_client, _ = client
    response = test_client.post("/pattern", json=VALID_PAYLOAD, headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


# --- Happy path ---

def test_pattern_returns_200_with_valid_payload(client):
    """Valid request returns 200."""
    test_client, _ = client
    response = test_client.post("/pattern", json=VALID_PAYLOAD, headers=HEADERS)
    assert response.status_code == 200


def test_pattern_response_shape(client):
    """Response contains message and updated_data list echoing input."""
    test_client, _ = client
    response = test_client.post("/pattern", json=VALID_PAYLOAD, headers=HEADERS)
    body = response.json()
    assert isinstance(body["message"], str)
    assert len(body["message"]) > 0
    assert body["updated_data"] == VALID_PAYLOAD["data_sets"]


def test_pattern_llm_response_is_returned_as_message(client):
    """The LLM response text is returned in the message field."""
    test_client, mock_service = client
    mock_service.make_analyse_request.return_value = "Custom pattern output"
    response = test_client.post("/pattern", json=VALID_PAYLOAD, headers=HEADERS)
    assert response.json()["message"] == "Custom pattern output"


def test_pattern_ollama_called_with_correct_analysis_type(client):
    """OllamaService is called with analysis_type='pattern'."""
    test_client, mock_service = client
    test_client.post("/pattern", json=VALID_PAYLOAD, headers=HEADERS)
    mock_service.make_analyse_request.assert_called_once()
    call_kwargs = mock_service.make_analyse_request.call_args
    assert call_kwargs.kwargs["analysis_type"] == "pattern"


def test_pattern_multiple_datasets_are_joined_with_separator(client):
    """Multiple datasets are joined with the separator before sending to Ollama."""
    test_client, mock_service = client
    payload = {
        "data_sets": ["date,value\n2024-01-01,100", "date,value\n2024-01-01,200"],
        "format": "csv",
        "daterange": ["2024-01-01", "2024-12-31"],
    }
    test_client.post("/pattern", json=payload, headers=HEADERS)
    call_kwargs = mock_service.make_analyse_request.call_args
    assert call_kwargs.kwargs["data"] == SEPARATOR.join(payload["data_sets"])


# --- Validation ---

@pytest.mark.parametrize("payload_override,description", [
    ({"data_sets": []}, "empty data_sets"),
    ({"data_sets": [""]}, "empty dataset string"),
    ({"format": "xml"}, "unsupported format"),
    ({"daterange": ["2024-01-01"]}, "single date in range"),
    ({"daterange": ["01-01-2024", "12-31-2024"]}, "invalid date format"),
    ({"daterange": ["2024-12-31", "2024-01-01"]}, "inverted daterange"),
])
def test_pattern_validation_returns_400(client, payload_override, description):
    """Invalid payload ({description}) is rejected with 400."""
    test_client, _ = client
    response = test_client.post("/pattern", json={**VALID_PAYLOAD, **payload_override}, headers=HEADERS)
    assert response.status_code == 400


# --- Ollama errors ---

def test_pattern_returns_502_on_ollama_error(client):
    """OllamaService failure returns 502."""
    test_client, mock_service = client
    mock_service.make_analyse_request.side_effect = ollama.ResponseError("model not found")
    response = test_client.post("/pattern", json=VALID_PAYLOAD, headers=HEADERS)
    assert response.status_code == 502
