"""Tests for the CommunicationService class."""
# pylint: disable=redefined-outer-name,protected-access

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.documents import Document
from langchain_core.exceptions import LangChainException
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from src.ai.communication.llm_communication_service import CommunicationService, CONTEXT_INFO


# --- Fixtures ---

@pytest.fixture
def service():
    """CommunicationService with a mocked LangChain chat model and no retriever."""
    with patch("src.ai.communication.llm_communication_service.init_chat_model") as mock_init:
        mock_model = MagicMock()
        mock_model.ainvoke = AsyncMock()
        mock_init.return_value = mock_model
        instance = CommunicationService(
            provider="anthropic", model="test-model", api_key="test-key",
            chroma_retriever=None,
        )
        yield instance, mock_model


@pytest.fixture
def service_with_retriever():
    """CommunicationService with a mocked LangChain chat model and a mocked retriever."""
    with patch("src.ai.communication.llm_communication_service.init_chat_model") as mock_init:
        mock_model = MagicMock()
        mock_model.ainvoke = AsyncMock()
        mock_init.return_value = mock_model

        mock_retriever = MagicMock()
        mock_retriever.ainvoke = AsyncMock(return_value=[
            Document(page_content="context doc 1"),
            Document(page_content="context doc 2"),
        ])

        instance = CommunicationService(
            provider="anthropic", model="test-model", api_key="test-key",
            chroma_retriever=mock_retriever,
        )
        yield instance, mock_model, mock_retriever


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
    assert isinstance(messages[-1], HumanMessage)
    assert messages[-1].content == "col1,col2\n1,2"


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


# --- Prompt building ---

@pytest.mark.parametrize("analysis_type", [
    "forecasting", "summary", "anomaly", "pattern", "comparison"
])
def test_build_prompt_returns_system_and_human_messages(analysis_type):
    """Returns SystemMessage + HumanMessage for every valid analysis type (no context)."""
    messages = CommunicationService._build_prompt_for_analyse_call(
        context=[],
        analysis_type=analysis_type,
        data="col1,col2\n1,2",
        data_format="csv",
        daterange=["2024-01-01", "2024-12-31"],
    )

    assert len(messages) == 2
    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)


def test_build_prompt_human_message_contains_data():
    """HumanMessage content is the raw data passed in."""
    messages = CommunicationService._build_prompt_for_analyse_call(
        context=[],
        analysis_type="forecasting",
        data="raw,data\nrow1,row2",
        data_format="csv",
        daterange=["2024-01-01", "2024-12-31"],
    )

    assert messages[-1].content == "raw,data\nrow1,row2"


def test_build_prompt_system_message_includes_format_and_daterange():
    """SystemMessage content embeds the data format and the formatted date range."""
    messages = CommunicationService._build_prompt_for_analyse_call(
        context=[],
        analysis_type="summary",
        data="data",
        data_format="json",
        daterange=["2024-06-01", "2024-12-31"],
    )

    system_content = messages[0].content
    assert "json" in system_content
    assert "2024-06-01 to 2024-12-31" in system_content


def test_build_prompt_unknown_analysis_type_raises_value_error():
    """An unregistered analysis type raises ValueError with a descriptive message."""
    with pytest.raises(ValueError, match="Unknown analysis type"):
        CommunicationService._build_prompt_for_analyse_call(
            context=[],
            analysis_type="unknown",
            data="data",
            data_format="csv",
            daterange=["2024-01-01", "2024-12-31"],
        )


def test_build_prompt_system_message_differs_by_analysis_type():
    """Different analysis types produce different system prompts."""
    summary_msgs = CommunicationService._build_prompt_for_analyse_call(
        context=[], analysis_type="summary", data="d", data_format="csv",
        daterange=["2024-01-01", "2024-12-31"],
    )
    forecasting_msgs = CommunicationService._build_prompt_for_analyse_call(
        context=[], analysis_type="forecasting", data="d", data_format="csv",
        daterange=["2024-01-01", "2024-12-31"],
    )

    assert summary_msgs[0].content != forecasting_msgs[0].content


def test_build_prompt_with_context_adds_context_message():
    """Context docs produce a context SystemMessage between system prompt and data."""
    context = [Document(page_content="relevant info"), Document(page_content="more info")]
    messages = CommunicationService._build_prompt_for_analyse_call(
        context=context,
        analysis_type="summary",
        data="data",
        data_format="csv",
        daterange=["2024-01-01", "2024-12-31"],
    )

    assert len(messages) == 3
    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], SystemMessage)
    assert isinstance(messages[2], HumanMessage)
    assert CONTEXT_INFO in messages[1].content
    assert "relevant info" in messages[1].content
    assert "more info" in messages[1].content


def test_build_prompt_empty_context_has_no_context_message():
    """Empty context list produces no context SystemMessage."""
    messages = CommunicationService._build_prompt_for_analyse_call(
        context=[],
        analysis_type="summary",
        data="data",
        data_format="csv",
        daterange=["2024-01-01", "2024-12-31"],
    )

    assert len(messages) == 2
    assert all(not (isinstance(m, SystemMessage) and CONTEXT_INFO in m.content) for m in messages)


# --- Retrieval ---

@pytest.mark.asyncio
async def test_retrieve_returns_empty_when_no_retriever(service):
    """_retrieve_context_from_vector_store returns empty list when retriever is None."""
    instance, _ = service
    result = await instance._retrieve_context_from_vector_store(query="test query")
    assert result == []


@pytest.mark.asyncio
async def test_retrieve_calls_retriever_ainvoke(service_with_retriever):
    """_retrieve_context_from_vector_store calls ainvoke on the retriever."""
    instance, _, mock_retriever = service_with_retriever
    result = await instance._retrieve_context_from_vector_store(query="test query")

    mock_retriever.ainvoke.assert_called_once_with(input="test query")
    assert len(result) == 2
    assert result[0].page_content == "context doc 1"


@pytest.mark.asyncio
async def test_make_analyse_request_with_retriever_includes_context(service_with_retriever):
    """When a retriever is present, the LLM receives context in the messages."""
    instance, mock_model, _ = service_with_retriever
    mock_model.ainvoke.return_value = AIMessage(content="result")

    await instance.make_analyse_request(
        analysis_type="summary",
        data="data",
        data_format="csv",
        daterange=["2024-01-01", "2024-12-31"],
    )

    messages = mock_model.ainvoke.call_args.kwargs["input"]
    assert len(messages) == 3
    assert CONTEXT_INFO in messages[1].content
    assert "context doc 1" in messages[1].content


@pytest.mark.asyncio
async def test_make_analyse_request_without_retriever_has_no_context(service):
    """When retriever is None, LLM receives no context SystemMessage."""
    instance, mock_model = service
    mock_model.ainvoke.return_value = AIMessage(content="result")

    await instance.make_analyse_request(
        analysis_type="summary",
        data="data",
        data_format="csv",
        daterange=["2024-01-01", "2024-12-31"],
    )

    messages = mock_model.ainvoke.call_args.kwargs["input"]
    assert len(messages) == 2
