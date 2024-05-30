from core.modules.base import AbstractModule


class ImportModule(AbstractModule):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.type = None

        self.__get_type(file_path)

    def __get_type(self, file_path):
        if 'usr' in file_path and 'lib' in file_path and 'python' in file_path:
            self.type = 'built_in'
        elif 'site-packages' in file_path:
            self.type = 'third_party'
        else:
            self.type = None
