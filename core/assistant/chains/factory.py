from typing import Union

from core.configuration.chat import ChatConfig
from core.assistant.chains.custom_openai import CustomOpenAIChain
from core.assistant.chains.gemini import GeminiChain
from core.assistant.chains.mistral import MistralChain


class ChainFactory:

    def __init__(self, config: ChatConfig):
        self.config = config

    def get_chain(self) -> Union[CustomOpenAIChain, GeminiChain, MistralChain]:
        if self.config.type == 'custom_openai':
            return CustomOpenAIChain(self.config)
        elif self.config.type == 'gemini':
            return GeminiChain(self.config)
        elif self.config.type == 'mistral':
            return MistralChain(self.config)
        else:
            raise ValueError(f'Unknown assistant type: {self.config.type}')
