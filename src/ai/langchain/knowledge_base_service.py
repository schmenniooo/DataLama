"""Module to fetch data from configured knowledge base"""

import yaml

class KnowledgeBaseService:

    def __init__(self, config_file_path: str):
        self.providers = self._read_provider_config_file(config_file_path)

    @staticmethod
    def _read_provider_config_file(path: str):
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        return config.get("knowledge_bases", [])

    def knowledge_base_fetch_workflow(self):
        pass

    def _get_knowledge_base_data(self):
        pass

    def _push_data_to_vector_store(self):
        pass
