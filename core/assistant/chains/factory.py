from typing import Union

from core.configuration.chat import ChatConfig
from core.assistant.chains.mistral import MistralChain
from core.assistant.chains.gemini import GeminiChain


class ChainFactory:

    def __init__(self, config: ChatConfig):
        self.config = config

    def get_chain(self) -> Union[MistralChain, GeminiChain]:
        if self.config.google_api_key:
            return GeminiChain(self.config)
        else:
            return MistralChain(self.config)
