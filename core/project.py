import os

from pydeps.target import Target


class Project(Target):
    def __init__(self, config):
        super().__init__(config.project_path)
        self.path = config.project_path
        self.excluded_paths = config.excluded_paths
        self.file_paths = None

        self.__file_scan()

    @staticmethod
    def __check_cache_folder(path):
        if '__pycache__' in path or '.pytest_cache' in path:
            return True
        else:
            return False

    def __file_scan(self):
        file_paths = []
        stop_root = 'stop_root'
        for root, dirs, files in os.walk(self.path):
            if stop_root in root or self.__check_cache_folder(root):
                continue
            if root != self.path and root in self.excluded_paths:
                stop_root = root
                continue
            for file in files:
                if file.endswith('.py'):
                    file_paths.append(os.path.join(root, file))
        self.file_paths = file_paths
