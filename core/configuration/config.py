import configparser


class Config:
    def __init__(self, filename):
        self.config = configparser.ConfigParser()
        self.config.read(filename)
        self.project_path = self.config.get('main', 'project_path')
        self.excluded_folders = self.config.get(
            'main', 'excluded_paths'
        ).replace('\n', ' ')

    @property
    def sections(self):
        return self.config.sections()

    def get(self, section, option):
        try:
            return self.config.get(section, option)
        except configparser.Error:
            return None

    def getint(self, section, option):
        try:
            return self.config.getint(section, option)
        except configparser.Error:
            return None

    def getfloat(self, section, option):
        try:
            return self.config.getfloat(section, option)
        except configparser.Error:
            return None

    def getboolean(self, section, option):
        try:
            return self.config.getboolean(section, option)
        except configparser.Error:
            return None


CONFIG = Config('/path_to_your_folder/cranberrypy.ini')
