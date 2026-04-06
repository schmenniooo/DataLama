"""Module to fetch data from configured knowledge base"""
import logging

import yaml
from langchain_community.document_loaders import SlackDirectoryLoader
from langchain_community.document_loaders.sharepoint import SharePointLoader
from langchain_community.document_loaders import ConfluenceLoader
from langchain_community.document_loaders import JiraLoader
from langchain_community.document_loaders import GithubFileLoader
from typing_extensions import Any

logger = logging.getLogger("logger")

class KnowledgeBaseService:

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

            # Saving data in vector store
            self._push_data_to_vector_store(docs=docs)

    @staticmethod
    def _validate_config(config: list) -> bool:
        if config is None:
            return False
        return False

    def _get_knowledge_base_data(self, provider: Any) -> list or None:
        name = provider.get("name")

        # TODO: Use fields from provider object

        if name == "slack":
            loader = ConfluenceLoader(
                url="https://yourcompany.atlassian.net/wiki",
                username="your@email.com",
                api_key="..."
            )
            docs = loader.load(space_key="ENG")
        elif name == "sharepoint":
            loader = SharePointLoader(
                client_id="...",
                client_secret="...",
                site_url="https://yourcompany.sharepoint.com/sites/yoursite"
            )
            docs = loader.load()
        elif name == "jira":
            loader = JiraLoader(
                cloud=True,
                api_token="...",
                username="your@email.com",
                server="https://yourcompany.atlassian.net",
                project="ENG"
            )
            docs = loader.load()
        elif name == "confluence":
            loader = ConfluenceLoader(
                url="https://yourcompany.atlassian.net/wiki",
                username="your@email.com",
                api_key="..."
            )
            docs = loader.load(space_key="ENG")
        elif name == "github":
            loader = GithubFileLoader(
                repo="org/repo",
                access_token="ghp_...",
                github_api_url="https://api.github.com",
                file_filter=lambda path: path.endswith(".md")  # e.g. only docs
            )
            docs = loader.load()
        else:
            logger.error("Unknown provider")
            return None

        logger.info(f"Found {len(docs)} documents in {name}")
        return docs

    def _push_data_to_vector_store(self, docs: list) -> None:
        if docs is None:
            logger.error("documents empty")
            return

        logger.info(f"Pushing {len(docs)} documents to vector store")

        # TODO: Save documents in chroma

        logger.info(f"Finished pushing {len(docs)} documents to vector store")
        return
