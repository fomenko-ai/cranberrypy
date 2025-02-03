from core.configuration.base import BaseConfig


class AssistantConfig:
    section = 'assistant'

    def __init__(self, config):
        self.api_url = config.get(self.section, 'api_url', fallback=None)
        self.api_key = config.get(self.section, 'api_key')
        self.model_name = config.get(self.section, 'model_name')


class GeminiAssistantConfig(AssistantConfig):
    section = 'gemini_assistant'


class CustomAssistantConfig(AssistantConfig):
    section = 'custom_assistant'


class ChatConfig(BaseConfig):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.type = self.config.get('assistant', 'type')
        self.custom = CustomAssistantConfig(self.config)
        self.gemini = GeminiAssistantConfig(self.config)
