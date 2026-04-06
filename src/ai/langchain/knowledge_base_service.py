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
        if not self._validate_config(self.providers):
            logger.error("Invalid knowledge base provider configuration")
            return

        for provider in self.providers:
            self._get_knowledge_base_data(provider=provider)

    @staticmethod
    def _validate_config(config: list) -> bool:
        if config is None:
            return False
        return False

    def _get_knowledge_base_data(self, provider: Any) -> list:
        docs = []
        name = provider.get("name")

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
            return []

        logger.info(f"Found {len(docs)} documents in {name}")
        return docs

    def _push_data_to_vector_store(self):
        pass
