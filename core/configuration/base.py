import configparser


class BaseConfig:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read(file_path)
        self.project_path = self.config.get('main', 'project_path')
        self.relative_source_module = self.config.get(
            'main', 'relative_source_module'
        )
        self.excluded_paths = None

        self._get_excluded_paths()

    @property
    def sections(self):
        return self.config.sections()

    def get(self, section, option):
        return self.config.get(section, option)

    def _get_excluded_paths(self):
        paths_or_dirs_list = self.config.get(
            'main', 'excluded_paths'
        ).split('\n')

        paths = []
        for path in paths_or_dirs_list:
            if path and len(path.split('/')) == 1:
                path = self.project_path + path
            paths.append(path)

        self.excluded_paths = ' '.join(paths)
