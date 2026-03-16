"""Integration tests for the /forecasting endpoint."""

import ollama

from tests.integration.conftest import HEADERS, SEPARATOR, VALID_PAYLOAD


# --- Authentication ---

def test_forecasting_without_api_key_returns_401(client):
    """Request without API key is rejected."""
    test_client, _ = client
    response = test_client.post("/forecasting", json=VALID_PAYLOAD)
    assert response.status_code == 401


def test_forecasting_with_wrong_api_key_returns_401(client):
    """Request with wrong API key is rejected."""
    test_client, _ = client
    response = test_client.post("/forecasting", json=VALID_PAYLOAD, headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


# --- Happy path ---

def test_forecasting_returns_200_with_valid_payload(client):
    """Valid request returns 200."""
    test_client, _ = client
    response = test_client.post("/forecasting", json=VALID_PAYLOAD, headers=HEADERS)
    assert response.status_code == 200


def test_forecasting_response_shape(client):
    """Response contains message and updated_data list."""
    test_client, _ = client
    response = test_client.post("/forecasting", json=VALID_PAYLOAD, headers=HEADERS)
    body = response.json()
    assert body["message"] == "Forecasted Data"
    assert isinstance(body["updated_data"], list)
    assert len(body["updated_data"]) > 0


def test_forecasting_with_multiple_datasets_splits_response(client):
    """Multiple datasets are joined, sent, and split back correctly."""
    test_client, mock_service = client
    mock_service.make_analyse_request.return_value = (
        f"date,value\n2024-01-01,100{SEPARATOR}date,value\n2024-01-01,200"
    )
    payload = {
        "data_sets": [
            "date,value\n2024-01-01,100",
            "date,value\n2024-01-01,200",
        ],
        "format": "csv",
        "daterange": ["2024-01-01", "2024-12-31"],
    }
    response = test_client.post("/forecasting", json=payload, headers=HEADERS)
    assert response.status_code == 200
    assert len(response.json()["updated_data"]) == 2


# --- Validation ---

def test_forecasting_with_empty_data_sets_returns_400(client):
    """Empty data_sets list is rejected."""
    test_client, _ = client
    response = test_client.post("/forecasting", json={**VALID_PAYLOAD, "data_sets": []}, headers=HEADERS)
    assert response.status_code == 400


def test_forecasting_with_empty_dataset_string_returns_400(client):
    """A data_set entry that is an empty string is rejected."""
    test_client, _ = client
    response = test_client.post("/forecasting", json={**VALID_PAYLOAD, "data_sets": [""]}, headers=HEADERS)
    assert response.status_code == 400


def test_forecasting_with_unsupported_format_returns_400(client):
    """Unsupported format is rejected."""
    test_client, _ = client
    response = test_client.post("/forecasting", json={**VALID_PAYLOAD, "format": "xml"}, headers=HEADERS)
    assert response.status_code == 400


def test_forecasting_with_single_date_in_range_returns_400(client):
    """daterange with only one date is rejected."""
    test_client, _ = client
    response = test_client.post("/forecasting", json={**VALID_PAYLOAD, "daterange": ["2024-01-01"]}, headers=HEADERS)
    assert response.status_code == 400


def test_forecasting_with_invalid_date_format_returns_400(client):
    """daterange with wrong date format is rejected."""
    test_client, _ = client
    response = test_client.post("/forecasting", json={**VALID_PAYLOAD, "daterange": ["01-01-2024", "12-31-2024"]}, headers=HEADERS)
    assert response.status_code == 400


def test_forecasting_with_inverted_daterange_returns_400(client):
    """daterange where start is after end is rejected."""
    test_client, _ = client
    response = test_client.post("/forecasting", json={**VALID_PAYLOAD, "daterange": ["2024-12-31", "2024-01-01"]}, headers=HEADERS)
    assert response.status_code == 400


# --- Ollama errors ---

def test_forecasting_returns_502_on_ollama_error(client):
    """OllamaService failure returns 502."""
    test_client, mock_service = client
    mock_service.make_analyse_request.side_effect = ollama.ResponseError("model not found")
    response = test_client.post("/forecasting", json=VALID_PAYLOAD, headers=HEADERS)
    assert response.status_code == 502
