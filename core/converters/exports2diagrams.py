from core.converters.base import AbstractConverter
from core.utils import write_json


class Exports2Diagrams(AbstractConverter):

    @staticmethod
    def __color(key: str):
        if key == 'built_in':
            return 'yellow'
        elif key == 'third_party':
            return 'CornflowerBlue'
        else:
            return 'LightGreen'

    def add(self, modules: dict):
        nodes = set()
        links = set()
        if not self.data:
            self.data = {}
        for _from, exports in modules.items():
            nodes.add((_from, self.__color(_from)))
            if 'exports' in exports:
                for text, to_modules in exports['exports'].items():
                    for _to in to_modules:
                        nodes.add((_to, self.__color(_to)))
                        links.add((_from, _to, text))
        self.data = {
            "nodes": [{"key": key, "color": color} for key, color in nodes],
            "links": [
                {"from": f, "to": to, "text": text} for f, to, text in links
            ]
        }

    def save(self):
        write_json(self.data, f"{self.filename}_DIAGRAM.json")
        write_json(
            self.data,
            "core/diagrams/data.json"
        )
