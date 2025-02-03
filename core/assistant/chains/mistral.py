from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain_community.llms import LlamaCpp

from core.assistant.chains.base import BaseChain
from core.assistant.func import download_hf_model


class MistralChain(BaseChain):

    def _init_llm(self):
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        model_path = download_hf_model(
            repo_id="MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF",
            filename="*Q4_K_M.gguf"
        )
        return LlamaCpp(
            model_path=model_path,
            n_ctx=8192,
            max_tokens=8000,
            n_gpu_layers=-1,
            n_batch=1024,
            n_threads=8,
            repeat_penalty=1.1,
            top_p=0.95,
            top_k=40,
            f16_kv=True,
            callback_manager=callback_manager,
            verbose=False
        )

    def stream(self, input_documents, query):
        self._chain.invoke(
            {
                'context': input_documents,
                'query': query
            }
        )
