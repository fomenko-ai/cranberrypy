from typing import Tuple, List

from core.converters.base import AbstractConverter
from core.utils import write_json


class Exports2Diagrams(AbstractConverter):

    @staticmethod
    def __cls_key(module_name: str, class_name: str) -> str:
        return '.'.join([module_name, class_name])

    @staticmethod
    def __link_to_dict(link: Tuple[str, str, str, str, bool]) -> dict:
        _from, _to, import_item, link_types, is_class = link
        if link_types == 'is_inheritance':
            return {
                "from": _from,
                "to": _to,
                "text": import_item,
                "toArrow": None,
                "fromArrow": "BackwardTriangle",
                "isClass": is_class

            }
        elif link_types == 'is_call':
            return {
                "from": _from,
                "to": _to,
                "text": import_item,
                "toArrow": "StretchedDiamond",
                "fromArrow": None,
                "isClass": is_class
            }
        else:
            return {
                "from": _from,
                "to": _to,
                "text": import_item,
                "toArrow": None,
                "fromArrow": None,
                "isClass": is_class
            }

    @staticmethod
    def __dividing_lines(module_name: str) -> Tuple[str, str]:
        letter_quantity = int(0.8 * len(module_name))
        line = '-' * letter_quantity
        double_line = '=' * letter_quantity
        return line, double_line

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

    def __cls_structure(self, structure: dict) -> list:
        info = []
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
        return info

    def __full_info(
        self, module_name: str, classes: dict, class_name: str = None
    ) -> str:
        info = [f'{module_name}']

        line, double_line = self.__dividing_lines(module_name)

        if module_name in classes:
            info.append(f'\n{double_line}')
            if class_name is None:
                for _class, structure in classes[module_name].items():
                    info.append(f'\n{_class}')
                    info.extend(self.__cls_structure(structure))
                    info.append(f'\n{line}')
            else:
                info.append(f'\n{class_name}')
                if class_name in classes[module_name]:
                    info.extend(
                        self.__cls_structure(classes[module_name][class_name])
                    )
        return '\n'.join(info)

    def __short_info(
        self, module_name: str, classes: dict, class_name: str = None
    ) -> str:
        info = [f'{module_name}']

        line, double_line = self.__dividing_lines(module_name)

        if module_name in classes:
            info.append(f'\n{double_line}')
            if class_name is None:
                for _class, _ in classes[module_name].items():
                    info.append(f'\n{_class}')
                    info.append(f'\n{line}')
            else:
                info.append(f'\n{class_name}')

        return '\n'.join(info)

    def __node_params(self, nodes: set, dirnames: dict, classes: dict):
        node_params = []
        modules = set()
        groups = set()

        for module, cls in nodes:
            if cls is not None:
                params = {
                    "key": self.__cls_key(module, cls),
                    "color": self.__color(dirnames[module]),
                    "text": cls,
                    "shortInfo": self.__short_info(module, classes, cls),
                    "fullInfo": self.__full_info(module, classes, cls),
                    "isClass": True,
                    "module": module
                }
                if module in dirnames:
                    params['group'] = dirnames[module]
                node_params.append(params)
            modules.add(module)

        for module in modules:
            params = {
                "key": module,
                "color": self.__color(dirnames[module]),
                "text": module,
                "shortInfo": self.__short_info(module, classes),
                "fullInfo": self.__full_info(module, classes),
                "isModule": True
            }
            if module in dirnames:
                params['group'] = dirnames[module]
                groups.add(dirnames[module])
            node_params.append(params)

        for group in groups:
            node_params.append(
                {
                    "key": group,
                    "text": group,
                    "shortInfo": group,
                    "fullInfo": group,
                    "isGroup": True
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
                if 'exports' in exports:
                    for import_item, to_modules in exports['exports'].items():
                        nodes.add((_from, import_item))
                        for _to, cls, link_types in to_modules:
                            nodes.add((_to, cls))
                            links.add(
                                (
                                    _from,
                                    _to,
                                    import_item,
                                    link_types,
                                    False
                                )
                            )
                            links.add(
                                (
                                    self.__cls_key(_from, import_item),
                                    self.__cls_key(_to, cls),
                                    import_item,
                                    link_types,
                                    True
                                )
                            )
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
