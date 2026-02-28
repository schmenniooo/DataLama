"""Tests for the OllamaService class."""
# pylint: disable=redefined-outer-name

from unittest.mock import MagicMock, patch

import pytest
import ollama

from src.ollama.ollama import OllamaService


@pytest.fixture
def service():
    """OllamaService with a mocked ollama client."""
    with patch("src.ollama.ollama.ollama.Client") as mock_client_class:
        instance = OllamaService(ollama_base_url="http://localhost:11434", ollama_model="llama3.2")
        instance.ollama_client = mock_client_class.return_value
        yield instance


def test_valid_analysis_type_returns_true(service):
    """A known analysis type with a successful chat call returns True."""
    service.ollama_client.chat.return_value = MagicMock()
    result = service.make_analyse_request(analysis_type="summary", data="some data")
    assert result is True


def test_unknown_analysis_type_raises(service):
    """An unregistered analysis type raises a ValueError."""
    with pytest.raises(ValueError, match="Unknown analysis type"):
        service.make_analyse_request(analysis_type="unknown", data="some data")


def test_chat_called_with_correct_messages(service):
    """The chat call receives the system prompt and user data as separate messages."""
    service.ollama_client.chat.return_value = MagicMock()
    service.make_analyse_request(analysis_type="summary", data="col1,col2\n1,2")

    service.ollama_client.chat.assert_called_once_with(
        model="llama3.2",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": "col1,col2\n1,2"},
        ],
    )


def test_ollama_response_error_returns_false(service):
    """A ResponseError from ollama is caught and returns False."""
    service.ollama_client.chat.side_effect = ollama.ResponseError("model not found")
    result = service.make_analyse_request(analysis_type="summary", data="some data")
    assert result is False


@pytest.mark.parametrize("analysis_type", [
    "forecasting", "summary", "anomaly", "pattern", "comparison"
])
def test_all_registered_types_are_accepted(service, analysis_type):
    """All entries in analyses_types are valid and do not raise."""
    service.ollama_client.chat.return_value = MagicMock()
    result = service.make_analyse_request(analysis_type=analysis_type, data="data")
    assert result is True
