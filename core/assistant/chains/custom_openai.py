from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_openai import ChatOpenAI

from core.assistant.chains.base import BaseChain


class CustomOpenAIChain(BaseChain):

    def _init_llm(self):
        callbacks = [StreamingStdOutCallbackHandler()]
        return ChatOpenAI(
            openai_api_base=self.config.custom.api_url,
            openai_api_key=self.config.custom.api_key,
            model_name=self.config.custom.model_name,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            callbacks=callbacks
        )

    def stream(self, input_documents, query):
        stream = self._chain.stream({
            'context': input_documents,
            'query': query
        })
        full = next(stream)
        for chunk in stream:
            full += chunk
