from typing import Optional, List, Any

from langchain_community.llms.llamacpp import LlamaCpp
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_experimental.chat_models.llm_wrapper import ChatWrapper


class CustomLlamaCpp(LlamaCpp):

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the Llama model and return the output.

        Args:
            prompt: The prompt to use for generation.
            stop: A list of strings to stop generation when encountered.

        Returns:
            The generated text.

        Example:
            .. code-block:: python

                from langchain_community.llms import LlamaCpp
                llm = LlamaCpp(model_path="/path/to/local/llama/model.bin")
                llm.invoke("This is a prompt.")
        """
        if self.streaming:
            # If streaming is enabled, we use the stream
            # method that yields as they are generated
            # and return the combined strings from the first choices's text:
            combined_text_output = ""
            for chunk in self._stream(
                prompt=prompt,
                stop=stop,
                run_manager=run_manager,
                **kwargs,
            ):
                print(chunk.text, end='', flush=True)
                combined_text_output += chunk.text
            return combined_text_output
        else:
            params = self._get_parameters(stop)
            params = {**params, **kwargs}
            result = self.client(prompt=prompt, **params)
            return result["choices"][0]["text"]


class Mistral(ChatWrapper):
    @property
    def _llm_type(self) -> str:
        return "mistral"

    sys_beg: str = "[INST] "
    sys_end: str = "\n"
    ai_n_beg: str = " "
    ai_n_end: str = " </s>"
    usr_n_beg: str = " [INST] "
    usr_n_end: str = " [/INST]"
    usr_0_beg: str = ""
    usr_0_end: str = " [/INST]"
