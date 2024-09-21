import os
from typing import List

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers.language.language_parser import LanguageParser
from langchain_community.vectorstores import DeepLake
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import LlamaCpp
from langchain_core.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from core.configuration.chat import ChatConfig
from chat import LOGGER
from chat import SYSTEM_PROMPT
from core.assistant.func import download_hf_model
from core.utils.func import write_file, read_file, read_json


SOURCE_PATH = "./temp/saved/{source_key}/"

ASSISTANT_JSON_PATH = SOURCE_PATH + "assistant.json"
ASSISTANT_KEY_PATH = SOURCE_PATH + "assistant_key"

VECTORSTORE_DIR_PATH = SOURCE_PATH + "vectorstore/"
VECTORSTORE_KEY_PATH = VECTORSTORE_DIR_PATH + "vectorstore_key"

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"

INSTRUCTION = """
Context: {context}
User: {query}"""


class AI:
    def __init__(self, config: ChatConfig):
        self.config = config
        self.source_key = None
        self.module_dict = None
        self.vectorstore = None
        self.qa_chain = None

        self._load_source_key()
        self._load_module_dict()
        self._create_qa_chain()

    def _init_model(self):
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

        if self.config.google_api_key:
            model = "gemini-1.5-pro"
            llm = ChatGoogleGenerativeAI(
                google_api_key=self.config.google_api_key,
                model=model,
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                callbacks=callback_manager
            )
        else:
            model = "MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF"
            model_path = download_hf_model(
                repo_id=model,
                filename="*Q4_K_M.gguf"
            )
            LOGGER.info("HF model downloaded.")

            llm = LlamaCpp(
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
        LOGGER.info(f"Initialised model: {model}")
        return llm

    def _load_source_key(self):
        self.source_key = read_file("./temp/source/source_key")
        LOGGER.info("Source key loaded.")

    def _load_module_dict(self):
        data = read_json(
            ASSISTANT_JSON_PATH.format(source_key=self.source_key)
        )
        self.module_dict = data['module_dict']
        LOGGER.info("Module dictionary loaded.")

    def _check_key(self, key1):
        key2 = read_file(
            VECTORSTORE_KEY_PATH.format(source_key=self.source_key)
        )
        return key1 == key2

    def _python_code(self):
        loader = GenericLoader.from_filesystem(
            self.config.project_path,
            glob="**/*",
            suffixes=[".py"],
            parser=LanguageParser("python")
        )
        documents = loader.load()
        python_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, chunk_size=2000, chunk_overlap=200
        )
        docs = python_splitter.split_documents(documents)
        for doc in docs:
            doc.metadata["content_type"] = 'code'
        return docs

    @staticmethod
    def _dependency_metadata_func(source_dict, doc_dict):
        for key, value in source_dict["metadata"].items():
            doc_dict[key] = value
        return doc_dict

    def _module_dependencies(self):
        jq_schema = ".dependencies[]"
        loader = JSONLoader(
            ASSISTANT_JSON_PATH.format(source_key=self.source_key),
            jq_schema=jq_schema,
            content_key=".content",
            is_content_key_jq_parsable=True,
            metadata_func=self._dependency_metadata_func,
            text_content=False
        )
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=300
        )
        return text_splitter.split_documents(documents)

    def _load_vectorstore(self):
        self.vectorstore = None
        embedding = HuggingFaceEmbeddings()

        assistant_key = read_file(
            ASSISTANT_KEY_PATH.format(source_key=self.source_key)
        )

        if os.path.exists(
            VECTORSTORE_KEY_PATH.format(source_key=self.source_key)
        ):
            if self._check_key(assistant_key):
                self.vectorstore = DeepLake(
                    dataset_path=VECTORSTORE_DIR_PATH.format(
                        source_key=self.source_key
                    ),
                    embedding=embedding,
                    read_only=True,
                    verbose=False
                )
                LOGGER.info("Vectorstore loaded.")
            else:
                LOGGER.info(
                    "Outdated vectorstore data found."
                )
                DeepLake.force_delete_by_path(
                    VECTORSTORE_DIR_PATH.format(source_key=self.source_key)
                )
                LOGGER.info("Vectorstore deleted.")
        else:
            LOGGER.info(
                "No vectorstore data found."
            )

        if self.vectorstore is None:
            LOGGER.info(
                "Creating vectorstore..."
            )

            self.vectorstore = DeepLake(
                dataset_path=VECTORSTORE_DIR_PATH.format(
                    source_key=self.source_key
                ),
                embedding=embedding,
                verbose=True
            )

            docs = []
            docs.extend(self._python_code())
            docs.extend(self._module_dependencies())
            self.vectorstore.add_documents(docs)
            write_file(
                assistant_key,
                VECTORSTORE_KEY_PATH.format(source_key=self.source_key)
            )
            LOGGER.info("Vectorstore saved.")

    @staticmethod
    def _prompt_format():
        system_prompt = B_SYS + SYSTEM_PROMPT + E_SYS
        prompt_template = B_INST + system_prompt + INSTRUCTION + E_INST
        return prompt_template

    def _create_qa_chain(self):
        self._load_vectorstore()
        template = self._prompt_format()
        qa_chain_prompt = PromptTemplate(
            input_variable=["context", "query"],
            template=template
        )
        self.qa_chain = create_stuff_documents_chain(
            llm=self._init_model(),
            prompt=qa_chain_prompt
        )
        LOGGER.info("Created QA-chain.")

    def _get_documents_by_query(self, query: str, k: int = 20) -> list:
        return self.vectorstore.similarity_search(query=query, k=k)

    def _get_documents_by_module_path(
        self,
        module_path: str,
        k: int = 1000
    ) -> list:
        return self.vectorstore.similarity_search(
            query=' ',
            k=k,
            filter={"metadata":  {'source': module_path}}
        )

    def _invoke(self, input_documents, query):
        self.qa_chain.invoke(
            {
                'context': input_documents,
                'query': query
            }
        )

    def chat(self):
        LOGGER.info("Run chat.")
        separator = ''
        while True:
            query = input("\n\nQuery: ")
            module_path = input("\n\nModule Path: ")
            module_path = module_path.strip()
            print(separator)
            LOGGER.info("Query received.\n")
            if module_path:
                docs = self._get_documents_by_module_path(module_path)
            else:
                docs = self._get_documents_by_query(query)
            self._invoke(docs, query)
            print(separator)
            LOGGER.info("Response returned.")

    def _get_module(self, module_path: str) -> dict:
        module = self.module_dict.get(module_path)
        if module is None:
            raise Exception(f"No module named '{module_path}'.")
        else:
            return module

    @staticmethod
    def _get_classes(module: dict) -> List[str]:
        return [c for c in module['classes'].keys()]

    def _classes_str(self, module: dict) -> str:
        classes = self._get_classes(module)
        return ', '.join(classes)

    @staticmethod
    def _get_method_names(classes: dict) -> List[str]:
        return [m['name'] for m in classes['methods']]

    def _methods_str(self, module: dict) -> str:
        result = list()
        for cls, methods in module['classes'].items():
            method_names = self._get_method_names(methods)
            result.append(
                f'{cls} class - ' + ', '.join(method_names)
            )
        return ';\n'.join(result)

    @staticmethod
    def _filter_by_metadata(
        docs: list,
        key: str = "content_type",
        value: str = "code"
    ) -> list:
        return [
            doc for doc in docs if doc.metadata[key] == value
        ]

    def _description(self, module: dict, docs: list):
        query = (
            f"Briefly describe the purpose of '{module['name']}' module. "
            f"The description of the module should not exceed 3 sentences."
        )
        self._invoke(
            input_documents=self._filter_by_metadata(docs, value='code'),
            query=query
        )

    def _code_documentation(self, module: dict, docs: list):
        query = (
            f"Create documentaion for '{module['name']}' module by Markdown format. "
            "In the documentation, describe in one sentence "
            f"the purpose of all methods of {self._classes_str(module)} "
            f"{'class' if len(self._get_classes(module)) else 'classes'}. "
            f"The documentation have to include methods:\n{self._methods_str(module)}."
        )
        self._invoke(
            input_documents=self._filter_by_metadata(docs, value='code'),
            query=query
        )

    def _dependencies_documentation(self, module: dict, docs: list):
        filtered_docs = self._filter_by_metadata(docs, value='dependency')
        for dep_type in ['inheritance', 'call', 'usage']:
            dep_docs = self._filter_by_metadata(
                filtered_docs,
                key='dependency_type',
                value=dep_type
            )
            if len(dep_docs) > 0:
                print(f"## {dep_type.capitalize()}s\n")
                s = 's' if len(dep_docs) > 1 else ''
                are = 'are' if len(dep_docs) > 1 else 'is'
                query = (
                    f"In '{module['name']}' module there {are} {len(dep_docs)} {dep_type}{s} with another module{s}. "
                    f"Create a brief conclusion about {dep_type}{s}. "
                    "The conclusion should not exceed 1 sentence. "
                    f"At the end of the sentence, list all {len(dep_docs)} {dep_type}{s}."
                )
                self._invoke(input_documents=dep_docs, query=query)
                print('\n')

    def generate_documentation(self):
        LOGGER.info("Run chat.")
        separator = ('\n\n===================================================='
                     '====================================================\n\n')
        while True:
            module_path = input("\n\nModule Path: ")
            module_path = module_path.strip()
            print(separator)
            LOGGER.info("Query received.\n")
            module = self._get_module(module_path)
            docs = self.vectorstore.similarity_search(
                query=' ',
                k=1000,
                filter={"metadata":  {'source': module_path}}
            )
            print(separator)
            self._description(module, docs)
            print(separator)
            self._code_documentation(module, docs)
            print(separator)
            self._dependencies_documentation(module, docs)
            print(separator)
            LOGGER.info("Response returned.")
