"""Tests for the AiCommunicationService class."""
# pylint: disable=redefined-outer-name

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.exceptions import LangChainException
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from src.ai.langchain.communication_service import AiCommunicationService


@pytest.fixture
def service():
    """AiCommunicationService with a mocked LangChain chat model."""
    with patch("src.ai.langchain.communication_service.init_chat_model") as mock_init:
        mock_model = MagicMock()
        mock_model.ainvoke = AsyncMock()
        mock_init.return_value = mock_model
        instance = AiCommunicationService(provider="anthropic", model="test-model", api_key="test-key")
        yield instance, mock_model


# --- Health check ---

@pytest.mark.asyncio
@pytest.mark.parametrize("side_effect,expected", [
    (None, True),
    (LangChainException("connection refused"), False),
], ids=["healthy", "unhealthy"])
async def test_health_check(service, side_effect, expected):
    """health_check returns True when invoke succeeds, False on LangChainException."""
    instance, mock_model = service
    mock_model.invoke.side_effect = side_effect
    result = await instance.health_check()
    assert result is expected


# --- Analysis types ---

@pytest.mark.asyncio
@pytest.mark.parametrize("analysis_type", [
    "forecasting", "summary", "anomaly", "pattern", "comparison"
])
async def test_all_registered_types_are_accepted(service, analysis_type):
    """All entries in analyses_types are valid and return a string."""
    instance, mock_model = service
    mock_model.ainvoke.return_value = AIMessage(content="result")

    result = await instance.make_analyse_request(
        analysis_type=analysis_type,
        data="data",
        data_format="csv",
        daterange=["2024-01-01", "2024-12-31"],
    )

    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_unknown_analysis_type_raises_value_error(service):
    """An unregistered analysis type raises a ValueError."""
    instance, _ = service
    with pytest.raises(ValueError, match="Unknown analysis type"):
        await instance.make_analyse_request(
            analysis_type="unknown",
            data="some data",
            data_format="csv",
            daterange=["2024-01-01", "2024-12-31"],
        )


# --- LLM invocation ---

@pytest.mark.asyncio
async def test_make_analyse_request_returns_llm_content(service):
    """make_analyse_request returns the content string from the LLM response."""
    instance, mock_model = service
    mock_model.ainvoke.return_value = AIMessage(content="forecasted,data\n2024-02-01,42")

    result = await instance.make_analyse_request(
        analysis_type="forecasting",
        data="date,value\n2024-01-01,40",
        data_format="csv",
        daterange=["2024-01-01", "2024-12-31"],
    )

    assert result == "forecasted,data\n2024-02-01,42"


@pytest.mark.asyncio
async def test_ainvoke_called_with_correct_messages(service):
    """The model.ainvoke call receives SystemMessage and HumanMessage."""
    instance, mock_model = service
    mock_model.ainvoke.return_value = AIMessage(content="result")

    await instance.make_analyse_request(
        analysis_type="forecasting",
        data="col1,col2\n1,2",
        data_format="csv",
        daterange=["2024-01-01", "2024-12-31"],
    )

    call_args = mock_model.ainvoke.call_args
    messages = call_args.kwargs["input"]
    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)
    assert messages[1].content == "col1,col2\n1,2"


@pytest.mark.asyncio
async def test_system_prompt_contains_format_and_daterange(service):
    """The system prompt includes the data format and daterange."""
    instance, mock_model = service
    mock_model.ainvoke.return_value = AIMessage(content="result")

    await instance.make_analyse_request(
        analysis_type="summary",
        data="data",
        data_format="json",
        daterange=["2024-06-01", "2024-12-31"],
    )

    messages = mock_model.ainvoke.call_args.kwargs["input"]
    system_content = messages[0].content
    assert "json" in system_content
    assert "2024-06-01 to 2024-12-31" in system_content


@pytest.mark.asyncio
async def test_langchain_exception_is_reraised(service):
    """A LangChainException from the model is caught and re-raised."""
    instance, mock_model = service
    mock_model.ainvoke.side_effect = LangChainException("model not found")

    with pytest.raises(LangChainException):
        await instance.make_analyse_request(
            analysis_type="summary",
            data="some data",
            data_format="json",
            daterange=["2024-01-01", "2024-12-31"],
        )
