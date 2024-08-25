import os
import pickle

from langchain.chains import RetrievalQA
from langchain.chains import create_retrieval_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores import FAISS
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import SystemMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from chat import LOGGER
from chat import SYSTEM_MESSAGE
from core.utils.hf_model import download_hf_model
from core.assistant.models import CustomLlamaCpp, Mistral


JSON_FILE = "core/assistant/data.json"
VECTORSTORE_FILE = "core/assistant/vectorstore.pkl"


class Chat:
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

    @staticmethod
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def __create_qa_chain(self):
        #self.history = {}
        #template_messages = [
        #    SystemMessage(content=SYSTEM_MESSAGE),
        #    MessagesPlaceholder(variable_name="chat_history"),
        #    HumanMessagePromptTemplate.from_template("{text}"),
        #]
        #prompt_template = ChatPromptTemplate.from_messages(template_messages)

        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Answer any use questions based solely on the context below:< context >{context}</ context > "),
             ("placeholder", "{chat_history}"),
            ("human", "{input}"),
        ])

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

        model = Mistral(llm=llm)
        LOGGER.info("Initialised model.")

        #runnable = prompt_template | model
        #runnable_with_history = RunnableWithMessageHistory(
        #    runnable,
        #    self.__get_session_history,
        #    input_messages_key="text",
        #    history_messages_key="chat_history",
        #)

        self.__load_vectorstore()

        #self.qa_chain = RetrievalQA.from_chain_type(
        #    llm=model,
        #    chain_type="stuff",
        #    retriever=self.vectorstore.as_retriever()
        #)

        #prompt = ChatPromptTemplate.from_messages(
        #    [
        #        ("system", SYSTEM_MESSAGE + "\n\n{context}"),
        #        ("human", "{input}"),
        #    ]
        #)
        #question_answer_chain = create_stuff_documents_chain(model, prompt)
        #self.qa_chain = create_retrieval_chain(
        #    self.vectorstore.as_retriever(), question_answer_chain
        #)

        self.qa_chain = (
                {
                    "context": self.vectorstore.as_retriever() | self.format_docs,
                    "question": RunnablePassthrough(),
                }
                | prompt
                | llm
                | StrOutputParser()
        )

        ### Contextualize question ###
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""
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

        ### Answer question ###
        qa_system_prompt = """You are an assistant for question-answering tasks. \
        Use the following pieces of retrieved context to answer the question. \
        If you don't know the answer, just say that you don't know. \
        Use three sentences maximum and keep the answer concise.\

        {context}"""
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

        rag_chain = create_retrieval_chain(history_aware_retriever,
                                           question_answer_chain)

        ### Statefully manage chat history ###
        self.history = {}

        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            self.__get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        self.qa_chain = conversational_rag_chain

        LOGGER.info("Created QA chain.")

    def run(self):
        LOGGER.info("Run chat.")
        while True:
            query = input("\n\n> ")
            print('')
            LOGGER.info("Query received.\n")

            #self.qa_chain.invoke({"query": query})
            self.qa_chain.invoke(
                {"input": query},
                config={"configurable": {"session_id": self.session_id}}
            )
            print('')
            LOGGER.info("Response returned.")
