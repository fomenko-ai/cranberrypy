import configparser

from pydeps.target import Target


class Config:
    def __init__(self, file_path, in_docker_image=False):
        self.file_path = file_path
        self.in_docker_image = in_docker_image
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read(file_path)
        self.project_path = self.config.get('main', 'project_path')
        self.python_version = self.config.get('starter', 'python_version')
        self.requirements_path = self.config.get('starter', 'requirements_path')
        self.install_kwargs = self.config.get('starter', 'install_kwargs')
        self.root_directory_path = self.config.get('starter', 'root_directory_path')
        self.root_image_path = self.config.get('starter', 'root_image_path')
        self.excluded_paths = None

        self.__get_excluded_paths()

        if self.in_docker_image:
            self.__convert_paths()

        self.target = Target(self.project_path)
        self.base_filename = self.target.modpath.replace('.', '_')

    @property
    def sections(self):
        return self.config.sections()

    def get(self, section, option):
        return self.config.get(section, option)

    def __get_excluded_paths(self):
        paths_or_dirs_list = self.config.get(
            'main', 'excluded_paths'
        ).split('\n')

        paths = []
        for path in paths_or_dirs_list:
            if path and len(path.split('/')) == 1:
                path = self.project_path + path
            paths.append(path)

        self.excluded_paths = ' '.join(paths)

    def to_image_path(self, path: str):
        return path.replace(
            self.root_directory_path, self.root_image_path
        )

    def __convert_paths(self):
        self.project_path = self.to_image_path(self.project_path)

        self.excluded_paths = self.to_image_path(self.excluded_paths)

        if self.requirements_path:
            self.requirements_path = self.to_image_path(self.requirements_path)
        else:
            self.requirements_path = self.project_path + 'requirements.txt'
