from typing import Dict, List

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
    def __convert_to_text_chunks(module_name, module_values) -> List[str]:
        text = str(module_values)
        items = len(text)
        N = items // 1000
        size = int(items / (N+1))
        overlap = int(size/5)
        chunks = []
        for n in range(N+2):
            start = n*size - overlap if n > 1 else n*size
            end = (n+1)*size + overlap
            chunks.append(
                f"MODULE_NAME: {module_name}\n\nMODULE_INFO: {text[start:end]}"
            )
        return chunks

    def __compose_for_assistant(self, import_data: dict, links: dict):
        self.data = []
        for module_name, module_values in import_data['modules'].items():
            dependencies = []
            for key, link in links.items():
                if module_name in key:
                    dependencies.append(link)
            module_values['dependencies'] = dependencies
            module_values['directory'] = import_data['dirnames'][module_name]
            chunks = self.__convert_to_text_chunks(module_name, module_values)
            self.data.extend(chunks)

    def add(self, import_data: dict, diagram_data: dict):
        links = self.__sort_links(diagram_data['links'])
        self.__compose_for_assistant(import_data, links)

    def save(self):
        write_json(self.data, f"{self.filename}_ASSISTANT.json")
        write_json(
            self.data,
            "core/assistant/data.json"
        )
