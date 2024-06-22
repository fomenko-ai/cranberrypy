class Base:

    def __init__(self, definition):
        self.definition = definition
        self.body = definition.body
        self.name = definition.name

    def __parse(self):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError
