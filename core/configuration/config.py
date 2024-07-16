import configparser

from pydeps.target import Target


class Config:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config = configparser.ConfigParser()
        self.config.read(file_path)
        self.project_path = self.config.get('main', 'project_path')
        self.excluded_folders = self.config.get(
            'main', 'excluded_paths'
        ).replace('\n', ' ')

        self.target = Target(self.project_path)
        self.base_filename = self.target.modpath.replace('.', '_')

    @property
    def sections(self):
        return self.config.sections()

    def get(self, section, option):
        try:
            return self.config.get(section, option)
        except configparser.Error:
            return None
