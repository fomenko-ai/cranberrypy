from core.configuration.main import MainConfig


class AbstractConverter:
    def __init__(self, config: MainConfig):
        self.config = config
        self.save_dir = config.save_dir
        self.data = None

    def add(self, *args, **kwargs):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        raise NotImplementedError
