import os

from core.configuration.base import BaseConfig
from pydeps.target import Target


class MainConfig(BaseConfig):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.root_directory_path = self.config.get(
            'starter', 'root_directory_path'
        )
        self.root_image_path = self.config.get('starter', 'root_image_path')
        self.in_docker_image = False

        if '/app' in os.getcwd():
            self.in_docker_image = True
            self._convert_paths()

        self.target = Target(self.project_path)
        self.save_dir = self.target.modpath.replace('.', '_')

    def _to_image_path(self, path: str):
        return path.replace(
            self.root_directory_path, self.root_image_path
        )

    def _convert_paths(self):
        self.project_path = self._to_image_path(self.project_path)
        self.excluded_paths = self._to_image_path(self.excluded_paths)
