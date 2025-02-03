from langchain_core.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

from core.configuration.chat import ChatConfig
from chat import SYSTEM_PROMPT

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"

INSTRUCTION = """
Context: {context}
User: {query}"""


class BaseChain:

    def __init__(self, config: ChatConfig):
        self.config = config
        self.type = config.type
        self._chain = None

    @staticmethod
    def _prompt_format():
        system_prompt = B_SYS + SYSTEM_PROMPT + E_SYS
        prompt_template = B_INST + system_prompt + INSTRUCTION + E_INST
        return prompt_template

    def _init_llm(self):
        raise NotImplementedError

    def create(self):
        template = self._prompt_format()
        qa_chain_prompt = PromptTemplate(
            input_variable=["context", "query"],
            template=template
        )
        self._chain = create_stuff_documents_chain(
            llm=self._init_llm(),
            prompt=qa_chain_prompt
        )

    def stream(self, input_documents, query):
        raise NotImplementedError
