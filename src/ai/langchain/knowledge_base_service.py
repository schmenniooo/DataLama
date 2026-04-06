"""Module to fetch data from configured knowledge base"""
import logging

import yaml
from langchain_community.document_loaders import SlackDirectoryLoader
from langchain_community.document_loaders.sharepoint import SharePointLoader
from langchain_community.document_loaders import ConfluenceLoader
from langchain_community.document_loaders import JiraLoader
from langchain_community.document_loaders import GithubFileLoader
from typing_extensions import Any
from slack_sdk import WebClient
from langchain_core.documents import Document

logger = logging.getLogger("logger")

class KnowledgeBaseService:

    _REQUIRED_FIELDS: dict[str, set[str]] = {
        "slack": {"token", "channel_ids"},
        "sharepoint": {"client_id", "client_secret", "site_url"},
        "jira": {"api_token", "username", "server", "project"},
        "confluence": {"url", "username", "api_key"},
        "github": {"repo", "access_token"},
    }

    def __init__(self, config_file_path: str):
        self.providers = self._read_provider_config_file(config_file_path)

    @staticmethod
    def _read_provider_config_file(path: str) -> list:
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        return config.get("knowledge_bases", [])

    def knowledge_base_fetch_workflow(self):
        # Validating config file at every call
        if not self._validate_config(self.providers):
            logger.error("Invalid knowledge base provider configuration")
            return

        # Iterating through providers and saving their content in chroma
        for provider in self.providers:
            logger.info(f"Fetching data from {provider.get("name")}")

            # Get data from provider
            docs = self._get_knowledge_base_data(provider=provider)
            if docs is None:
                logger.error(f"Failed to fetch data from {provider.get('name')}")
                return

            # Saving data in vector store
            self._push_data_to_vector_store(docs=docs)

    @classmethod
    def _validate_config(cls, config: list) -> bool:
        if not isinstance(config, list):
            logger.error("Knowledge base config must be a list")
            return False

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

    def _get_knowledge_base_data(self, provider: Any) -> list | None:
        name = provider.get("name")

        if name == "slack":
            docs = self._load_slack_documents(provider=provider)
        elif name == "sharepoint":
            loader = SharePointLoader(
                client_id=provider.client_id,
                client_secret=provider.client_secret,
                site_url=provider.site_url
            )
            docs = loader.load()
        elif name == "jira":
            loader = JiraLoader(
                cloud=True,
                api_token=provider.api_token,
                username=provider.username,
                server=provider.server,
                project=provider.project,
            )
            docs = loader.load()
        elif name == "confluence":
            loader = ConfluenceLoader(
                url=provider.url,
                username=provider.username,
                api_key=provider.api_key,
            )
            docs = loader.load()
        elif name == "github":
            loader = GithubFileLoader(
                repo=provider.repo,
                access_token=provider.access_token,
                github_api_url="https://api.github.com",
                file_filter=lambda path: path.endswith(".md")
            )
            docs = loader.load()
        else:
            logger.error("Unknown provider")
            return None

        logger.info(f"Found {len(docs)} documents in {name}")
        return docs

    @staticmethod
    def _load_slack_documents(provider: Any) -> list[Document]:
        token = provider.token
        channel_ids = provider.channel_ids

        client = WebClient(token=token)
        docs = []

        for channel_id in channel_ids:
            response = client.conversations_history(channel=channel_id)
            for message in response["messages"]:
                if message.get("text"):
                    docs.append(Document(
                        page_content=message["text"],
                        metadata={"channel": channel_id, "ts": message["ts"]}
                    ))
        return docs

    @staticmethod
    def _push_data_to_vector_store(docs: list) -> None:
        logger.info(f"Pushing {len(docs)} documents to vector store")

        # TODO: Save documents in chroma

        logger.info(f"Finished pushing {len(docs)} documents to vector store")
        return
