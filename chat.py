from core.configuration.config import Config
from core.logger import Logger

CONFIG = Config('cranberrypy.ini')

LOGGER = Logger(config=CONFIG, name=__name__)
LOGGER.setup_logger()


# Contextualize question
contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""

# Answer question
qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.\

{context}"""


def run_chat():
    from core.assistant.ai import AI

    ai = AI()
    ai.chat()


if __name__ == "__main__":
    run_chat()
