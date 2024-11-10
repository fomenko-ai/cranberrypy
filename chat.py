import sys

from core.configuration.chat import ChatConfig
from core.logger import Logger

CONFIG = ChatConfig('cranberrypy.ini')

LOGGER = Logger(config=CONFIG, name=__name__)
LOGGER.setup_logger(stream=sys.stdout)


SYSTEM_PROMPT = """You are a helpful assistant, you will use the provided context to answer user question.
Read the given context before answering questions and think step by step. If you can`t answer a user question based on
the provided context, inform the user. Do not use any other information for answering user."""

MODULE_PATHS = """
/path_to/root_directory/your_project/module_1
/path_to/root_directory/your_project/module_2
"""

TEST_CONDITIONS = """
For configuration use function 'get_config' in module 'your_project.tests.utils'.
"""


def run_chat():
    from core.assistant.ai import AI

    ai = AI(config=CONFIG)

    # ai.chat()
    # ai.chat_with_persistent_context(module_paths=MODULE_PATHS)
    # ai.chat_with_current_context(module_paths=MODULE_PATHS)
    #
    # ai.generate_code_according_to_diagram(using_project_context=True)

    # ai.generate_documentation_with_current_context()
    ai.generate_documentation(
        description=True,
        code=True,
        dependencies=True,
        contain_code_text=False
    )

    # ai.generate_unit_tests(
    #     conditions=TEST_CONDITIONS,
    #     using_pytest=True
    # )
    # ai.generate_unit_tests_with_persistent_context(
    #     conditions=TEST_CONDITIONS,
    #     using_pytest=True
    # )
    # ai.generate_unit_tests_with_current_context(
    #     conditions=TEST_CONDITIONS,
    #     using_pytest=True
    # )


if __name__ == "__main__":
    run_chat()
