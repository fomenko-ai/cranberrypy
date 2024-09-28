SOURCE_PATH = "./temp/saved/{source_key}/"

ASSISTANT_JSON_PATH = SOURCE_PATH + "assistant.json"
ASSISTANT_KEY_PATH = SOURCE_PATH + "assistant_key"

VECTORSTORE_DIR_PATH = SOURCE_PATH + "vectorstore/"
VECTORSTORE_KEY_PATH = VECTORSTORE_DIR_PATH + "vectorstore_key"


class PathSwitcher:
    def __init__(self, source_key: str):
        self.source_key = source_key

    @property
    def assistant_json(self):
        return ASSISTANT_JSON_PATH.format(source_key=self.source_key)

    @property
    def assistant_key(self):
        return ASSISTANT_KEY_PATH.format(source_key=self.source_key)

    @property
    def vectorstore_dir(self):
        return VECTORSTORE_DIR_PATH.format(source_key=self.source_key)

    @property
    def vectorstore_key(self):
        return VECTORSTORE_KEY_PATH.format(source_key=self.source_key)
