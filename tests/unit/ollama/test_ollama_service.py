"""Tests for the OllamaService class."""
# pylint: disable=redefined-outer-name

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import ai

from src.ai.communication_service import AiCommunicationService


@pytest.fixture
def service():
    """OllamaService with a mocked async ai client."""
    with patch("src.ai.ollama_service.ai.AsyncClient"):
        instance = AiCommunicationService(ollama_base_url="http://localhost:11434", ollama_model="llama3.2")
        instance.ollama_client = MagicMock()
        instance.ollama_client.chat = AsyncMock()
        instance.ollama_client.list = AsyncMock()
        yield instance


@pytest.mark.asyncio
async def test_health_check_returns_true_when_ollama_is_up(service):
    """health_check returns True when list() succeeds."""
    result = await service.health_check()
    assert result is True


@pytest.mark.asyncio
async def test_health_check_returns_false_on_response_error(service):
    """health_check returns False when ai raises ResponseError."""
    service.ollama_client.list.side_effect = ai.ResponseError("connection refused")
    result = await service.health_check()
    assert result is False


@pytest.mark.asyncio
async def test_unknown_analysis_type_raises_value_error(service):
    """An unregistered analysis type raises a ValueError."""
    with pytest.raises(ValueError, match="Unknown analysis type"):
        await service.make_analyse_request(
            analysis_type="unknown",
            data="some data",
            data_format="csv",
            daterange=["2024-01-01", "2024-12-31"],
        )


@pytest.mark.asyncio
async def test_make_analyse_request_returns_llm_content(service):
    """make_analyse_request returns the content string from the LLM response."""
    mock_response = MagicMock()
    mock_response.message.content = "forecasted,data\n2024-02-01,42"
    service.ollama_client.chat.return_value = mock_response

    result = await service.make_analyse_request(
        analysis_type="forecasting",
        data="date,value\n2024-01-01,40",
        data_format="csv",
        daterange=["2024-01-01", "2024-12-31"],
    )

    assert result == "forecasted,data\n2024-02-01,42"


@pytest.mark.asyncio
async def test_chat_called_with_correct_messages(service):
    """The chat call receives the system prompt and user data as separate messages."""
    mock_response = MagicMock()
    mock_response.message.content = "result"
    service.ollama_client.chat.return_value = mock_response

    await service.make_analyse_request(
        analysis_type="forecasting",
        data="col1,col2\n1,2",
        data_format="csv",
        daterange=["2024-01-01", "2024-12-31"],
    )

    call_args = service.ollama_client.chat.call_args
    messages = call_args.kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "col1,col2\n1,2"


@pytest.mark.asyncio
async def test_response_error_is_reraised(service):
    """A ResponseError from ai is caught, logged, and re-raised."""
    service.ollama_client.chat.side_effect = ai.ResponseError("model not found")

    with pytest.raises(ai.ResponseError):
        await service.make_analyse_request(
            analysis_type="summary",
            data="some data",
            data_format="json",
            daterange=["2024-01-01", "2024-12-31"],
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("analysis_type", [
    "forecasting", "summary", "anomaly", "pattern", "comparison"
])
async def test_all_registered_types_are_accepted(service, analysis_type):
    """All entries in analyses_types are valid and do not raise."""
    mock_response = MagicMock()
    mock_response.message.content = "result"
    service.ollama_client.chat.return_value = mock_response

    result = await service.make_analyse_request(
        analysis_type=analysis_type,
        data="data",
        data_format="csv",
        daterange=["2024-01-01", "2024-12-31"],
    )

    assert isinstance(result, str)
