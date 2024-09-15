import datetime
from typing import Dict

from core.converters.base import AbstractConverter
from core.utils.func import write_json, write_file


class Diagrams2Assistant(AbstractConverter):

    @staticmethod
    def _get_link_text(link: dict) -> str:
        if link['type'] == 'inheritance':
            return f"'{link['text']}' from '{link['from']}' is inherited in '{link['to']}'."
        elif link['type'] == 'call':
            return f"'{link['text']}' from '{link['from']}' is called in '{link['to']}'."
        elif link['type'] == 'usage':
            return f"'{link['text']}' from '{link['from']}' is used in '{link['to']}'."

    def _sort_links(self, links: list) -> dict:
        result = dict()
        for link in links:
            if link['isClass'] is True:
                continue
            key = (link['from'], link['to'], link['text'], link['type'])
            value = {
                'type': link['type'],
                'text': self._get_link_text(link)
            }
            result.update({key: value})
        return result

    def _real_path(self, file_path: str) -> str:
        return file_path.replace(
            self.config.root_image_path, self.config.root_directory_path
        )

    def _add_to_dict(
        self,
        file_path: str,
        module_name: str,
        module_values: dict
    ):
        self.data['module_dict'][file_path] = {
            'name': module_name,
            'classes': module_values['classes']
        }

    @staticmethod
    def _document(file_path: str, link: dict) -> Dict[str, dict]:
        return {
            "metadata":  {
                "source": file_path,
                "content_type": "dependency",
                "dependency_type": link['type']
            },
            "content": link['text']
        }

    def _compose_for_assistant(self, import_data: dict, links: dict):
        self.data = {
            'module_dict': {},
            'dependencies': []
        }
        for module_name, module_values in import_data['modules'].items():
            if self.config.in_docker_image:
                file_path = self._real_path(module_values['file_path'])
            else:
                file_path = module_values['file_path']
            self._add_to_dict(file_path, module_name, module_values)
            for key, link in links.items():
                if module_name in key:
                    self.data['dependencies'].append(
                        self._document(file_path, link)
                    )

    def add(self, import_data: dict, diagram_data: dict):
        links = self._sort_links(diagram_data['links'])
        self._compose_for_assistant(import_data, links)

    def _get_source_key(self):
        return (
            f"{self.filename}"
            f"_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        )

    def save(self):
        write_json(
            self.data,
            f"./temp/saved/{self.filename}_ASSISTANT.json"
        )
        write_json(
            self.data,
            "./temp/source/assistant.json"
        )
        write_file(
            self._get_source_key(),
            "./temp/source/source_key"
        )
