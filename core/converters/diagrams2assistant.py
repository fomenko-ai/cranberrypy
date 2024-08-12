from typing import Dict

from core.converters.base import AbstractConverter
from core.utils.func import write_json


class Diagrams2Assistant(AbstractConverter):

    @staticmethod
    def __sort_links(links: list) -> dict:
        result = dict()
        for link in links:
            key = f"{link['from']}_{link['to']}_{link['text']}"
            value = {
                'source': link['from'],
                'target': link['to'],
                'identifier': link['text'],
                'type': link['type']
            }
            result.update({key: value})
        return result

    @staticmethod
    def __get_modules(import_data: dict, links: dict) -> Dict[str, str]:
        for module_name, module_values in import_data['modules'].items():
            dependencies = []
            for key, link in links.items():
                if module_name in key:
                    dependencies.append(link)
            module_values['dependencies'] = dependencies
            module_values['directory'] = import_data['dirnames'][module_name]
        return {"modules": str(import_data['modules'])}

    def add(self, import_data: dict, diagram_data: dict):
        links = self.__sort_links(diagram_data['links'])
        self.data = self.__get_modules(import_data, links)

    def save(self):
        write_json(self.data, f"{self.filename}_ASSISTANT.json")
        write_json(
            self.data,
            "core/assistant/data.json"
        )
