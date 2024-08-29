import os
import pickle

from langchain.chains import create_retrieval_chain
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores import FAISS
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings

from chat import LOGGER
from chat import contextualize_q_system_prompt
from chat import qa_system_prompt
from core.assistant.models import CustomLlamaCpp
from core.assistant.func import download_hf_model


JSON_FILE = "./temp/source/assistant.json"
VECTORSTORE_FILE = "./temp/source/vectorstore.pkl"


class AI:
    def __init__(self, session_id: str = '1', history=None, vectorstore=None):
        self.session_id = session_id
        self.history = history
        self.vectorstore = vectorstore
        self.qa_chain = None

        self.__create_qa_chain()

    def __save_vectorstore(self, filename=VECTORSTORE_FILE):
        LOGGER.info("Saving vectorstore.")
        with open(filename, "wb") as f:
            pickle.dump(self.vectorstore, f)
        LOGGER.info("Vectorstore saved.")

    def __load_vectorstore(self, filename=VECTORSTORE_FILE):
        LOGGER.info("Loading vectorstore.")
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                self.vectorstore = pickle.load(f)
                LOGGER.info("Vectorstore loaded.")

        if self.vectorstore is None:
            LOGGER.info(
                "No vectorstore data found, creating vectorstore."
            )

            jq_schema = ".[]"
            loader = JSONLoader(JSON_FILE, jq_schema=jq_schema)
            documents = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500,
                chunk_overlap=300
            )
            docs = text_splitter.split_documents(documents)

            embeddings = HuggingFaceEmbeddings()

            self.vectorstore = FAISS.from_documents(docs, embeddings)
            self.__save_vectorstore()

    def __get_session_history(self, session_id: str) -> ChatMessageHistory:
        if session_id not in self.history:
            self.history[session_id] = ChatMessageHistory()
        return self.history[session_id]

    def __create_qa_chain(self):
        model_path = download_hf_model(
            repo_id="MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF",
            filename="*Q4_K_M.gguf"
        )
        LOGGER.info("HF model downloaded.")

        llm = CustomLlamaCpp(
            temperature=0.1,
            model_path=model_path,
            n_ctx=8192,
            n_gpu_layers=-1,
            n_batch=1024,
            max_tokens=512,
            n_threads=8,
            repeat_penalty=1.1,
            top_p=0.95,
            top_k=40,
            verbose=False
        )
        LOGGER.info("Initialised model.")

        self.__load_vectorstore()

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        history_aware_retriever = create_history_aware_retriever(
            llm, self.vectorstore.as_retriever(), contextualize_q_prompt
        )

        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

        rag_chain = create_retrieval_chain(
            history_aware_retriever, question_answer_chain
        )

        self.history = {}

        self.qa_chain = RunnableWithMessageHistory(
            rag_chain,
            self.__get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        LOGGER.info("Created QA-chain.")

    def chat(self):
        LOGGER.info("Run chat.")
        while True:
            query = input("\n\n> ")
            print('')
            LOGGER.info("Query received.\n")

            self.qa_chain.invoke(
                {"input": query},
                config={"configurable": {"session_id": self.session_id}}
            )
            print('')
            LOGGER.info("Response returned.")
