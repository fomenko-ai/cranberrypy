from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_google_genai import ChatGoogleGenerativeAI

from core.assistant.chains.base import BaseChain


class GeminiChain(BaseChain):
    model_name = 'gemini'

    def _init_llm(self):
        callbacks = [StreamingStdOutCallbackHandler()]
        return ChatGoogleGenerativeAI(
            google_api_key=self.config.google_api_key,
            model='gemini-1.5-pro',
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
