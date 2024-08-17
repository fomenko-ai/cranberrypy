import sys

from core.configuration.config import Config
from core.logger import Logger

CONFIG = Config('cranberrypy.ini')

LOGGER = Logger(config=CONFIG, name=__name__)
LOGGER.setup_logger(stream=sys.stdout)


SYSTEM_MESSAGE = (
    "You are a helpful assistant. "
    "In your context memory there is data about Python project. "
    "Project data contain information about modules: "
    "code, imports, classes, dependencies, directory. "
    "When answering questions, use information about module code first. "
)


def run_chat():
    from core.assistant.llm_model import qa_chain

    LOGGER.info("Run chat.")
    while True:
        query = input("\n\n> ")
        print('')
        LOGGER.info("Query received.\n")

        result = qa_chain.invoke({"query": query})
        print(f"< {result['result']}\n")
        LOGGER.info("Response returned.")


if __name__ == "__main__":
    run_chat()
