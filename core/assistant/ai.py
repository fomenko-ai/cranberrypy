import os
from typing import List, Union

from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers.language.language_parser import LanguageParser
from langchain_community.vectorstores import DeepLake
from langchain_huggingface import HuggingFaceEmbeddings

from core.configuration.chat import ChatConfig
from chat import LOGGER
from core.utils.func import write_file, read_file, read_json
from core.utils.path_switcher import PathSwitcher
from core.assistant.chains.factory import ChainFactory
from core.modules.source_module import SourceModule
from core.converters.diagrams2assistant import Diagrams2Assistant


class AI:
    def __init__(self, config: ChatConfig):
        self.config = config
        self._path_switcher = None
        self._module_dict = None
        self._vectorstore = None
        self._qa_chain = None

        self._load_source_key()
        self._load_module_dict()
        self._load_vectorstore()
        self._create_qa_chain()

    def _load_source_key(self):
        source_key = read_file("./temp/source/source_key")
        self._path_switcher = PathSwitcher(source_key)
        LOGGER.info("Source key loaded.")

    def _load_module_dict(self):
        data = read_json(self._path_switcher.assistant_json)
        self._module_dict = data['module_dict']
        LOGGER.info("Module dictionary loaded.")

    def _check_key(self, key1):
        key2 = read_file(self._path_switcher.vectorstore_key)
        return key1 == key2

    def _python_code(self, path=None):
        if path is None:
            path = self.config.project_path
        loader = GenericLoader.from_filesystem(
            path=path,
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
            self._path_switcher.assistant_json,
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
        self._vectorstore = None
        embedding = HuggingFaceEmbeddings()
        assistant_key = read_file(self._path_switcher.assistant_key)
        if os.path.exists(self._path_switcher.vectorstore_key):
            if self._check_key(assistant_key):
                self._vectorstore = DeepLake(
                    dataset_path=self._path_switcher.vectorstore_dir,
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
                    self._path_switcher.vectorstore_dir
                )
                LOGGER.info("Vectorstore deleted.")
        else:
            LOGGER.info(
                "No vectorstore data found."
            )

        if self._vectorstore is None:
            LOGGER.info(
                "Creating vectorstore..."
            )

            self._vectorstore = DeepLake(
                dataset_path=self._path_switcher.vectorstore_dir,
                embedding=embedding,
                verbose=True
            )

            docs = []
            docs.extend(self._python_code())
            docs.extend(self._module_dependencies())
            self._vectorstore.add_documents(docs)
            write_file(
                assistant_key,
                self._path_switcher.vectorstore_key
            )
            LOGGER.info("Vectorstore saved.")

    def _create_qa_chain(self):
        self._qa_chain = ChainFactory(self.config).get_chain()
        if self._qa_chain is not None:
            self._qa_chain.create()
            LOGGER.info(f"Created QA-chain, model: {self._qa_chain.model_name}.")
        else:
            raise Exception("No QA-chain.")

    @staticmethod
    def _input_file_path(
        is_multiple=True,
        is_necessary=True,
        file_name='Module'
    ) -> Union[str, List[str]]:
        condition = '' if is_necessary else '(not necessary)'
        path = input(f"\n\n{file_name} Path {condition}: ")
        if is_necessary and not path:
            while not path:
                print(f"\n{file_name} Path is required.")
                path = input(f"\nn{file_name} Path: ")
        if is_multiple:
            paths = []
            while path:
                paths.append(path.strip())
                path = input(
                    f"\n{file_name} Path (enter a blank line to complete): "
                )
            return paths
        else:
            return path.strip()

    def _get_documents_by_query(self, query: str, k: int = 20) -> list:
        return self._vectorstore.similarity_search(query=query, k=k)

    def _get_documents_by_module_path(
        self,
        module_path: str,
        k: int = 1000
    ) -> list:
        return self._vectorstore.similarity_search(
            query=' ',
            k=k,
            filter={"metadata":  {'source': module_path}}
        )

    def _invoke(self, input_documents, query):
        self._qa_chain.stream(input_documents, query)

    def chat(self):
        LOGGER.info("Run chat.")
        separator = ''
        while True:
            query = input("\n\nQuery : ")
            module_paths = self._input_file_path(is_necessary=False)
            print(separator)
            LOGGER.info("Query received.\n")
            if module_paths:
                docs = []
                for path in module_paths:
                    docs.extend(self._get_documents_by_module_path(path))
            else:
                docs = self._get_documents_by_query(query)
            self._invoke(docs, query)
            print(separator)
            LOGGER.info("Response returned.")

    def chat_with_persistent_context(
        self,
        module_paths: Union[str, List[str]] = None
    ):
        LOGGER.info("Run chat with persistent context.")
        separator = ''
        if not module_paths:
            module_paths = self._input_file_path()
        elif isinstance(module_paths, str):
            if '\n' in module_paths:
                module_paths = module_paths.splitlines()
            elif ' ' in module_paths:
                module_paths = module_paths.split()
        module_paths = [path.strip() for path in module_paths if path]
        docs = []
        for path in module_paths:
            docs.extend(self._get_documents_by_module_path(path))
        while True:
            query = input("\n\nQuery : ")
            print(separator)
            LOGGER.info("Query received.\n")
            self._invoke(docs, query)
            print(separator)
            LOGGER.info("Response returned.")

    def chat_with_current_context(
        self,
        module_paths: Union[str, List[str]] = None
    ):
        separator = ''
        if not module_paths:
            module_paths = self._input_file_path()
        elif isinstance(module_paths, str):
            if '\n' in module_paths:
                module_paths = module_paths.splitlines()
            elif ' ' in module_paths:
                module_paths = module_paths.split()
        module_paths = [path.strip() for path in module_paths if path]
        docs = []
        for path in module_paths:
            docs.extend(self._python_code(path))
        while True:
            query = input("\n\nQuery : ")
            print(separator)
            LOGGER.info("Query received.\n")
            self._invoke(docs, query)
            print(separator)
            LOGGER.info("Response returned.")

    def _get_module(self, module_path: str) -> dict:
        module = self._module_dict.get(module_path)
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

    def _code_documentation(
        self,
        module: dict,
        docs: list,
        contain_code_text=False
    ):
        query = (
            f"Create documentaion for '{module['name']}' module by Markdown format. "
            "In the documentation, describe in one sentence "
            f"the purpose of all methods of {self._classes_str(module)} "
            f"{'class' if len(self._get_classes(module)) else 'classes'}. "
            f"The documentation have to include methods:\n{self._methods_str(module)}."
        )
        if not contain_code_text:
            query += " The documentation should not contain the module code, only the names of the objects."
        else:
            query += " The documentation should contain the module code."
        self._invoke(
            input_documents=self._filter_by_metadata(docs, value='code'),
            query=query
        )

    def _dependencies_documentation(self, module: dict, docs: list):
        filtered_docs = self._filter_by_metadata(docs, value='dependency')
        for dep_type in ['inheritance', 'composition', 'call', 'usage']:
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

    def generate_documentation(
        self,
        description=True,
        code=True,
        dependencies=True,
        contain_code_text=False
    ):
        LOGGER.info("Run generating documentation.")
        separator = ('\n\n===================================================='
                     '====================================================\n\n')
        while True:
            module_path = self._input_file_path(is_multiple=False)
            print(separator)
            LOGGER.info("Query received.\n")
            module = self._get_module(module_path)
            docs = self._vectorstore.similarity_search(
                query=' ',
                k=1000,
                filter={"metadata":  {'source': module_path}}
            )
            print(separator)
            if description:
                self._description(module, docs)
                print(separator)
            if code:
                self._code_documentation(module, docs, contain_code_text)
                print(separator)
            if dependencies:
                self._dependencies_documentation(module, docs)
                print(separator)
            LOGGER.info("Response returned.")

    def generate_documentation_with_current_context(
        self,
        description=True,
        code=True,
        contain_code_text=False
    ):
        LOGGER.info("Run generating documentation with current context.")
        separator = ('\n\n===================================================='
                     '====================================================\n\n')
        while True:
            module_path = self._input_file_path(is_multiple=False)
            print(separator)
            LOGGER.info("Query received.\n")
            module = SourceModule(module_path)
            module.parse()
            module = {
                'name': module.name,
                'classes': module.classes
            }
            docs = self._python_code(module_path)
            print(separator)
            if description:
                self._description(module, docs)
                print(separator)
            if code:
                self._code_documentation(module, docs, contain_code_text)
                print(separator)
            LOGGER.info("Response returned.")

    @staticmethod
    def _diagram_module(data) -> str:
        text = f"KEY: {data['key']}\n\n"
        text += f"DIRECTORY: '{data.get('directory')}'\n\n" if data.get('directory') else ""
        text += f"'{data['text']}'"
        return text

    @staticmethod
    def _diagram_dependency(data) -> str:
        return data['text']

    def _query_from_diagram(self, data):
        description = list()
        dependencies = set()

        for module in data:
            description.append(self._diagram_module(module))
            for dependency in module['dependencies']:
                dependencies.add(self._diagram_dependency(dependency))

        description = '\n\n'.join(description)
        dependencies = '\n'.join(dependencies)

        return (
            "Create a code based on the text in 'Module Description'. "
            "Each module has a 'KEY' value and can has 'DIRECTORY'. "
            "Dependencies between classes are specified in 'Dependencies'. "
            "If there are dependencies between modules, "
            "create the corresponding imports.\n\n"
            f"Module Description:\n\n{description}\n\n"
            f"Dependencies:\n\n{dependencies}\n\n"
        )

    def generate_code_according_to_diagram(self, using_project_context=False):
        LOGGER.info("Run generating code according to diagram.")
        separator = ('\n\n===================================================='
                     '====================================================\n\n')
        while True:
            file_path = self._input_file_path(
                is_multiple=False,
                file_name='Diagram JSON'
            )
            print(separator)
            LOGGER.info("Query received.\n")
            data = Diagrams2Assistant.from_download_file(file_path)
            query = self._query_from_diagram(data)
            LOGGER.info("Diagram data prepared.\n")
            docs = []
            if using_project_context:
                docs.extend(self._get_documents_by_query(query))
            print(separator)
            self._invoke(docs, query)
            print(separator)
            LOGGER.info("Response returned.")
