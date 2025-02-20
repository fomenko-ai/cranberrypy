from core.configuration.base import BaseConfig


class StarterConfig(BaseConfig):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.python_version = self.config.get('starter', 'python_version')
        self.requirements_path = self.config.get('starter', 'requirements_path')
        self.package_installer = self.config.get('starter', 'package_installer')
        self.install_kwargs = self.config.get('starter', 'install_kwargs')
        self.root_directory_path = self.config.get(
            'starter', 'root_directory_path'
        )
        self.root_image_path = self.config.get('starter', 'root_image_path')

        if not self.requirements_path:
            self.requirements_path = self.project_path + 'requirements.txt'
