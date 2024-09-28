from core.configuration.base import BaseConfig


class ChatConfig(BaseConfig):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.google_api_key = self.config.get('assistant', 'google_api_key')
