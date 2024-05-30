from core.converters.base import AbstractConverter
from core.utils import write_json


class Exports2Diagrams(AbstractConverter):

    @staticmethod
    def __color(dirname: str):
        if dirname == 'built_in':
            return 'yellow'
        elif dirname == 'third_party':
            return 'CornflowerBlue'
        else:
            return 'LightGreen'

    @staticmethod
    def __location(key: str):
        if key == 'built_in':
            return '1000 0'
        elif key == 'third_party':
            return '1000 0'
        else:
            return None

    def __node_params(self, nodes: set, dirnames: dict):
        node_params = []
        groups = set()
        for key in nodes:
            params = {
                "key": key,
                "color": self.__color(dirnames[key])
            }
            if key in dirnames:
                params['group'] = dirnames[key]
                groups.add(dirnames[key])
            node_params.append(params)
        for group in groups:
            node_params.append(
                {"key": group, "text": group, "isGroup": True}
            )
        return node_params

    def add(self, modules: dict):
        nodes = set()
        links = set()
        if not self.data:
            self.data = {}
        if modules['modules']:
            for _from, exports in modules['modules'].items():
                nodes.add(_from)
                if 'exports' in exports:
                    for text, to_modules in exports['exports'].items():
                        for _to in to_modules:
                            nodes.add(_to)
                            links.add((_from, _to, text))
        self.data = {
            "nodes": self.__node_params(nodes, modules['dirnames']),
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
