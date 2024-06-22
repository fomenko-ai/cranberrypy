from typing import Tuple, List

from core.converters.base import AbstractConverter
from core.utils import write_json


class Exports2Diagrams(AbstractConverter):

    @staticmethod
    def __link_to_dict(link: Tuple[str, str, str, str]) -> dict:
        _from, _to, text, link_types = link
        if link_types == 'is_inheritance':
            return {
                "from": _from,
                "to": _to,
                "text": text,
                "toArrow": None,
                "fromArrow": "BackwardTriangle"

            }
        elif link_types == 'is_call':
            return {
                "from": _from,
                "to": _to,
                "text": text,
                "toArrow": "StretchedDiamond",
                "fromArrow": None
            }
        else:
            return {
                "from": _from,
                "to": _to,
                "text": text,
                "toArrow": None,
                "fromArrow": None
            }

    @staticmethod
    def __color(dirname: str):
        if dirname == 'built_in':
            return 'yellow'
        elif dirname == 'third_party':
            return 'CornflowerBlue'
        else:
            return 'LightGreen'

    @staticmethod
    def __visibility(value: str) -> str:
        if value.startswith('__'):
            return '-'
        elif value.startswith('_'):
            return '#'
        else:
            return '+'

    def __attributes(self, values: List[dict]) -> List[str]:
        attributes = []
        for attr in values:
            text = ''
            names = []
            for name in attr['names']:
                names.append(f"{self.__visibility(name)} {name}")
            text += ', '.join(names)
            if attr['annotation']:
                text += f" : ({attr['annotation']})"
            attributes.append(text)
        return attributes

    def __methods(self, values: List[dict]) -> List[str]:
        methods = []
        for method in values:
            text = f"{self.__visibility(method['name'])} {method['name']}"
            arguments = []
            if method['arguments']:
                for arg in method['arguments']:
                    argument = f"{arg['name']}"
                    if arg['annotation']:
                        argument += f" : {arg['annotation']}"
                    arguments.append(argument)
            text += f"({', '.join(arguments)})"
            if method['returns']:
                text += f" : {method['returns']}"
            methods.append(text)
        return methods

    def __full_info(self, module_name: str, classes: dict):
        info = [f'{module_name}']

        letter_quantity = int(0.8*len(module_name))
        line = '-'*letter_quantity
        double_line = '='*letter_quantity

        if module_name in classes:
            info.append(f'\n{double_line}')
            for _class, structure in classes[module_name].items():
                info.append(f'\n{_class}')
                for key, values in structure.items():
                    if values:
                        info.append(f'\n{key}')
                        if key == 'attributes':
                            info.extend(self.__attributes(values))
                        elif key == 'methods':
                            info.extend(self.__methods(values))
                        else:
                            for value in values:
                                info.append(f'. {value}')
                info.append(f'\n{line}')

        return '\n'.join(info)

    def __node_params(self, nodes: set, dirnames: dict, classes: dict):
        node_params = []
        groups = set()
        for key in nodes:
            params = {
                "key": key,
                "color": self.__color(dirnames[key]),
                "text": key,
                "shortInfo": key,
                "fullInfo": self.__full_info(key, classes)
            }
            if key in dirnames:
                params['group'] = dirnames[key]
                groups.add(dirnames[key])
            node_params.append(params)
        for group in groups:
            node_params.append(
                {
                    "key": group,
                    "text": group,
                    "isGroup": True,
                    "shortInfo": group,
                    "fullInfo": group
                }
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
                        for _to, link_types in to_modules:
                            nodes.add(_to)
                            links.add((_from, _to, text, link_types))
        self.data = {
            "nodes": self.__node_params(
                nodes, modules['dirnames'], modules['classes']
            ),
            "links": [
                self.__link_to_dict(link) for link in links
            ]
        }

    def save(self):
        write_json(self.data, f"{self.filename}_DIAGRAM.json")
        write_json(
            self.data,
            "core/diagrams/data.json"
        )
