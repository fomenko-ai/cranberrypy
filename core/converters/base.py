class AbstractConverter:
    def __init__(self, config):
        self.filename = config.base_filename
        self.data = None

    def add(self, *args, **kwargs):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        raise NotImplementedError
