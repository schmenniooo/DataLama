"""Module to fetch data from configured knowledge base"""

class KnowledgeBaseService:

    def __init__(self, config_file_path: str):
        self.providers = self._read_provider_config_file(config_file_path)

    @staticmethod
    def _read_provider_config_file(path: str):
        return []

    def knowledge_base_fetch_workflow(self):
        pass

    def _get_knowledge_base_data(self):
        pass

    def _push_data_to_vector_store(self):
        pass
