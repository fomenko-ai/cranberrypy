from core.configuration.config import Config
from core.logger import Logger

CONFIG = Config('cranberrypy.ini')

LOGGER = Logger(config=CONFIG, name=__name__)
LOGGER.setup_logger()


SYSTEM_MESSAGE = (
    "You are a helpful assistant. "
    "In your context memory there is data about Python project. "
    "Project data contain information about modules - MODULE_NAME and MODULE_INFO. "
    "MODULE_INFO includes code, imports, classes, dependencies, directory."
    "When answering questions, use information about module code. "
)


def run_chat():
    from core.assistant.llm_model import Chat

    chat = Chat()
    chat.run()


if __name__ == "__main__":
    run_chat()
