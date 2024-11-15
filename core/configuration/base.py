import configparser


class BaseConfig:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read(file_path)
        self.project_path = self.config.get('main', 'project_path')
        self.relative_source_module = self.config.get(
            'crutches', 'relative_source_module'
        )

    @property
    def sections(self):
        return self.config.sections()

    def get(self, section, option):
        return self.config.get(section, option)
