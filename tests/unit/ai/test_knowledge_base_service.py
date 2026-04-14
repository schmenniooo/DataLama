"""Tests for the KnowledgeBaseService class."""
# pylint: disable=redefined-outer-name

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import yaml
from langchain_core.documents import Document

from src.ai.knowledge.knowledge_base_service import KnowledgeBaseService


# --- Fixtures ---

VALID_SLACK_PROVIDER = {"provider": "slack", "token": "xoxb-test", "channel_ids": ["C1"]}
VALID_JIRA_PROVIDER = {"provider": "jira", "api_token": "tok", "username": "u", "server": "http://jira", "project": "P"}
VALID_CONFLUENCE_PROVIDER = {"provider": "confluence", "url": "http://wiki", "username": "u", "api_key": "k"}
VALID_GITHUB_PROVIDER = {"provider": "github", "repo": "org/repo", "access_token": "ghp_test"}


def _write_config(providers: list) -> str:
    """Writes a temporary YAML config file and returns its path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False)
    yaml.dump({"knowledge_bases": providers}, f)
    f.close()
    return f.name


@pytest.fixture
def mock_chroma():
    """Patches the Chroma client so no real connection is needed."""
    with patch("src.ai.knowledge.knowledge_base_service.Chroma") as mock:
        yield mock


@pytest.fixture
def service_with_slack(mock_chroma):
    """Returns a KnowledgeBaseService configured with a single valid Slack provider."""
    path = _write_config([VALID_SLACK_PROVIDER])
    service = KnowledgeBaseService(config_file_path=path)
    os.unlink(path)
    return service


@pytest.fixture
def service_with_all_providers(mock_chroma):
    """Returns a KnowledgeBaseService configured with all supported providers."""
    path = _write_config([VALID_SLACK_PROVIDER, VALID_JIRA_PROVIDER, VALID_CONFLUENCE_PROVIDER, VALID_GITHUB_PROVIDER])
    service = KnowledgeBaseService(config_file_path=path)
    os.unlink(path)
    return service


# --- Config reading ---

def test_read_provider_config_file_parses_yaml(mock_chroma):
    """_read_provider_config_file returns the list under 'knowledge_bases'."""
    providers = [VALID_SLACK_PROVIDER, VALID_GITHUB_PROVIDER]
    path = _write_config(providers)

    result = KnowledgeBaseService._read_provider_config_file(path)

    os.unlink(path)
    assert result == providers


def test_read_provider_config_file_returns_empty_on_missing_key(mock_chroma):
    """Returns an empty list when 'knowledge_bases' key is absent."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False)
    yaml.dump({"other_key": "value"}, f)
    f.close()

    result = KnowledgeBaseService._read_provider_config_file(f.name)

    os.unlink(f.name)
    assert result == []


# --- Validation ---

def test_validate_config_accepts_valid_providers():
    """Validation passes for all supported provider types with required fields."""
    config = [VALID_SLACK_PROVIDER, VALID_JIRA_PROVIDER, VALID_CONFLUENCE_PROVIDER, VALID_GITHUB_PROVIDER]
    assert KnowledgeBaseService._validate_config(config) is True


def test_validate_config_rejects_non_list():
    """Validation fails when config is not a list."""
    assert KnowledgeBaseService._validate_config("not a list") is False


def test_validate_config_rejects_non_dict_entry():
    """Validation fails when a provider entry is not a dict."""
    assert KnowledgeBaseService._validate_config(["not a dict"]) is False


def test_validate_config_rejects_missing_provider_field():
    """Validation fails when 'provider' field is missing."""
    assert KnowledgeBaseService._validate_config([{"token": "x"}]) is False


def test_validate_config_rejects_unsupported_provider():
    """Validation fails for an unknown provider name."""
    assert KnowledgeBaseService._validate_config([{"provider": "unknown"}]) is False


def test_validate_config_rejects_missing_required_fields():
    """Validation fails when required fields are missing from a provider."""
    incomplete = {"provider": "slack", "token": "xoxb-test"}  # missing channel_ids
    assert KnowledgeBaseService._validate_config([incomplete]) is False


def test_validate_config_accepts_empty_list():
    """An empty list is valid — no providers means nothing to validate."""
    assert KnowledgeBaseService._validate_config([]) is True


# --- Init sets configFileValid ---

def test_init_marks_config_valid_on_good_config(service_with_slack):
    """configFileValid is True when the config passes validation."""
    assert service_with_slack.configFileValid is True


def test_init_marks_config_invalid_on_bad_config(mock_chroma):
    """configFileValid is False when the config fails validation."""
    path = _write_config([{"provider": "slack"}])  # missing required fields
    service = KnowledgeBaseService(config_file_path=path)
    os.unlink(path)
    assert service.configFileValid is False


# --- Fetch workflow ---

def test_workflow_skips_on_invalid_config(mock_chroma):
    """Workflow returns early without fetching when config is invalid."""
    path = _write_config([{"provider": "slack"}])
    service = KnowledgeBaseService(config_file_path=path)
    os.unlink(path)

    with patch.object(service, "_get_knowledge_base_data") as mock_get:
        service.knowledge_base_fetch_workflow()
        mock_get.assert_not_called()


def test_workflow_calls_get_data_and_push_for_each_provider(service_with_all_providers):
    """Workflow fetches and pushes data for every configured provider."""
    mock_docs = [Document(page_content="test")]
    with (
        patch.object(service_with_all_providers, "_get_knowledge_base_data", return_value=mock_docs) as mock_get,
        patch.object(service_with_all_providers, "_push_data_to_vector_store") as mock_push,
    ):
        service_with_all_providers.knowledge_base_fetch_workflow()
        assert mock_get.call_count == 4
        assert mock_push.call_count == 4


def test_workflow_stops_on_fetch_failure(service_with_all_providers):
    """Workflow stops processing further providers when one fails."""
    with (
        patch.object(service_with_all_providers, "_get_knowledge_base_data", return_value=None) as mock_get,
        patch.object(service_with_all_providers, "_push_data_to_vector_store") as mock_push,
    ):
        service_with_all_providers.knowledge_base_fetch_workflow()
        assert mock_get.call_count == 1
        mock_push.assert_not_called()


# --- Slack loader ---

def test_load_slack_documents_creates_documents():
    """_load_slack_documents returns a Document per message with text."""
    mock_response = {
        "messages": [
            {"text": "hello", "ts": "1234.5"},
            {"text": "", "ts": "1234.6"},
            {"ts": "1234.7"},
            {"text": "world", "ts": "1234.8"},
        ]
    }
    with patch("src.ai.knowledge.knowledge_base_service.WebClient") as mock_client_cls:
        mock_client_cls.return_value.conversations_history.return_value = mock_response
        docs = KnowledgeBaseService._load_slack_documents(token="tok", channel_ids=["C1"])

    assert len(docs) == 2
    assert docs[0].page_content == "hello"
    assert docs[0].metadata == {"channel": "C1", "ts": "1234.5"}
    assert docs[1].page_content == "world"


# --- Jira loader ---

def test_load_jira_documents_creates_documents():
    """_load_jira_documents returns a Document per issue."""
    mock_issue = MagicMock()
    mock_issue.fields.summary = "Bug title"
    mock_issue.fields.description = "Bug description"
    mock_issue.fields.status = "Open"
    mock_issue.key = "PROJ-1"

    with patch("src.ai.knowledge.knowledge_base_service.JIRA") as mock_jira_cls:
        mock_jira_cls.return_value.search_issues.return_value = [mock_issue]
        docs = KnowledgeBaseService._load_jira_documents(
            server="http://jira", username="u", api_token="t", project="PROJ"
        )

    assert len(docs) == 1
    assert "Bug title" in docs[0].page_content
    assert "Bug description" in docs[0].page_content
    assert docs[0].metadata == {"key": "PROJ-1", "project": "PROJ", "status": "Open"}


def test_load_jira_documents_handles_none_description():
    """Jira issues with no description don't break the loader."""
    mock_issue = MagicMock()
    mock_issue.fields.summary = "No desc"
    mock_issue.fields.description = None
    mock_issue.fields.status = "Done"
    mock_issue.key = "PROJ-2"

    with patch("src.ai.knowledge.knowledge_base_service.JIRA") as mock_jira_cls:
        mock_jira_cls.return_value.search_issues.return_value = [mock_issue]
        docs = KnowledgeBaseService._load_jira_documents(
            server="http://jira", username="u", api_token="t", project="PROJ"
        )

    assert len(docs) == 1
    assert "No desc" in docs[0].page_content


# --- Push to vector store ---

def test_push_data_calls_chroma_add_documents(service_with_slack):
    """_push_data_to_vector_store passes documents to chroma.add_documents."""
    docs = [Document(page_content="test")]
    service_with_slack._push_data_to_vector_store(docs)
    service_with_slack.chroma.add_documents.assert_called_once_with(documents=docs)
