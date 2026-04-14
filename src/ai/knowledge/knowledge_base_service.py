"""Module to fetch data from configured knowledge bases"""
import hashlib
import logging
import os

import yaml
from langchain_chroma import Chroma
from langchain_community.document_loaders import ConfluenceLoader
from langchain_community.document_loaders import GithubFileLoader
from jira import JIRA
from langchain_core.documents import Document
from slack_sdk import WebClient
from typing_extensions import Any

logger = logging.getLogger("logger")

class KnowledgeBaseService:

    _REQUIRED_FIELDS: dict[str, set[str]] = {
        "slack": {"token", "channel_ids"},
        "jira": {"api_token", "username", "server", "project"},
        "confluence": {"url", "username", "api_key"},
        "github": {"repo", "access_token"},
    }

    def __init__(self, config_file_path: str):
        # Initializing chroma db
        self.chroma = Chroma(
            collection_name=os.getenv("CHROMA_COLLECTION_NAME", "datalens"),
            host=os.getenv("CHROMA_HOST", "localhost"),
            port=int(os.getenv("CHROMA_PORT", "8000"))
        )

        # Getting providers from config file
        self.providers = self._read_provider_config_file(config_file_path)
        self.configFileValid = False

        # Validating config
        if not self._validate_config(self.providers):
            logger.error("Invalid knowledge base provider configuration")
        else:
            self.configFileValid = True

    @staticmethod
    def _read_provider_config_file(path: str) -> list:
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        return config.get("knowledge_bases", [])

    @classmethod
    def _validate_config(cls, config: list) -> bool:
        # Type check
        if not isinstance(config, list):
            logger.error("Knowledge base config must be a list")
            return False

        # Checking if appropriate fields are present for each provider and its fields
        for index, provider in enumerate(config):
            if not isinstance(provider, dict):
                logger.error(f"Provider at index {index} must be a mapping")
                return False

            name = provider.get("provider")
            if not name:
                logger.error(f"Provider at index {index} is missing the 'provider' field")
                return False

            if name not in cls._REQUIRED_FIELDS:
                logger.error(f"Unsupported provider '{name}' at index {index}")
                return False

            missing = cls._REQUIRED_FIELDS[name] - provider.keys()
            if missing:
                logger.error(f"Provider '{name}' at index {index} is missing fields: {sorted(missing)}")
                return False

        return True

    def knowledge_base_fetch_workflow(self):
        # Checking for valid config
        if not self.configFileValid:
            logger.error("Knowledge base configuration not valid")
            return

        # Iterating through providers and saving their content in chroma
        for provider in self.providers:
            logger.info(f"Fetching data from {provider.get('provider')}")

            # Get data from provider
            docs = self._get_knowledge_base_data(provider=provider)
            if docs is None:
                logger.error(f"Failed to fetch data from {provider.get('provider')}")
                return

            # Saving data in vector store
            self._push_data_to_vector_store(docs=docs)

    def _get_knowledge_base_data(self, provider: Any) -> list | None:
        name = provider.get("provider")

        # Checking for chosen provider(s)
        match name:
            case "slack":
                # Using slack sdk
                docs = self._load_slack_documents(
                    token=provider.get("token"),
                    channel_ids=provider.get("channel_ids")
                )
            case "jira":
                # Using jira sdk
                docs = self._load_jira_documents(
                    server=provider.get("server"),
                    username=provider.get("username"),
                    api_token=provider.get("api_token"),
                    project=provider.get("project"),
                )
            case "confluence":
                loader = ConfluenceLoader(
                    url=provider.get("url"),
                    username=provider.get("username"),
                    api_key=provider.get("api_key"),
                )
                docs = loader.load()
            case "github":
                loader = GithubFileLoader(
                    repo=provider.get("repo"),
                    access_token=provider.get("access_token"),
                    github_api_url="https://api.github.com",
                    file_filter=lambda path: path.endswith(".md")
                )
                docs = loader.load()
            case _:
                logger.error("Unknown provider")
                return None

        logger.info(f"Found {len(docs)} documents in {name}")
        return docs

    @staticmethod
    def _load_slack_documents(token: Any, channel_ids: Any) -> list[Document]:
        client = WebClient(token=token)
        docs = []

        # Iterating through every given channel
        for channel_id in channel_ids:
            response = client.conversations_history(channel=channel_id)
            # Creating doc for every message in channel
            for message in response["messages"]:
                if message.get("text"):
                    # Creating new doc with message text and id
                    docs.append(Document(
                        page_content=message["text"],
                        metadata={"channel": channel_id, "ts": message["ts"]}
                    ))
        return docs

    @staticmethod
    def _load_jira_documents(server: str, username: str, api_token: str, project: str) -> list[Document]:
        client = JIRA(server=server, basic_auth=(username, api_token))
        docs = []

        issues = client.search_issues(f"project={project}", maxResults=False)
        for issue in issues:
            docs.append(Document(
                page_content=f"{issue.fields.summary}\n{issue.fields.description or ''}",
                metadata={"key": issue.key, "project": project, "status": str(issue.fields.status)},
            ))
        return docs

    def _push_data_to_vector_store(self, docs: list[Document]) -> None:
        logger.info(f"Pushing {len(docs)} documents to vector store")

        self.chroma.add_documents(documents=docs)

        logger.info(f"Finished pushing {len(docs)} documents to vector store")
        return
