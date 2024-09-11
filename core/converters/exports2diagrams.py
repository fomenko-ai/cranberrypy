from typing import Tuple, List

from core.converters.base import AbstractConverter
from core.utils.func import write_json


class Exports2Diagrams(AbstractConverter):

    @staticmethod
    def _cls_key(module_name: str, class_name: str) -> str:
        return '.'.join([module_name, class_name])

    @staticmethod
    def _link_to_dict(link: Tuple[str, str, str, str, bool]) -> dict:
        _from, _to, import_item, link_types, is_class = link
        if link_types == 'is_inheritance':
            return {
                "from": _from,
                "to": _to,
                "text": import_item,
                "toArrow": None,
                "fromArrow": "BackwardTriangle",
                "isClass": is_class,
                "type": "inheritance"

            }
        elif link_types == 'is_call':
            return {
                "from": _from,
                "to": _to,
                "text": import_item,
                "toArrow": "StretchedDiamond",
                "fromArrow": None,
                "isClass": is_class,
                "type": "call"
            }
        else:
            return {
                "from": _from,
                "to": _to,
                "text": import_item,
                "toArrow": None,
                "fromArrow": None,
                "isClass": is_class,
                "type": "usage"
            }

    @staticmethod
    def _dividing_lines(module_name: str) -> Tuple[str, str]:
        letter_quantity = int(0.8 * len(module_name))
        line = '-' * letter_quantity
        double_line = '=' * letter_quantity
        return line, double_line

    @staticmethod
    def _color(dirname: str):
        if dirname == 'built_in':
            return 'yellow'
        elif dirname == 'third_party':
            return 'CornflowerBlue'
        else:
            return 'LightGreen'

    @staticmethod
    def _visibility(value: str) -> str:
        if value.startswith('__'):
            return '-'
        elif value.startswith('_'):
            return '#'
        else:
            return '+'

    def _attributes(self, values: List[dict]) -> List[str]:
        attributes = []
        for attr in values:
            text = ''
            names = []
            for name in attr['names']:
                names.append(f"{self._visibility(name)} {name}")
            text += ', '.join(names)
            if attr['annotation']:
                text += f" : ({attr['annotation']})"
            attributes.append(text)
        return attributes

    def _methods(self, values: List[dict]) -> List[str]:
        methods = []
        for method in values:
            text = f"{self._visibility(method['name'])} {method['name']}"
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

    def _cls_structure(self, structure: dict) -> list:
        info = []
        for key, values in structure.items():
            if values:
                info.append(f'\n{key}')
                if key == 'attributes':
                    info.extend(self._attributes(values))
                elif key == 'methods':
                    info.extend(self._methods(values))
                else:
                    for value in values:
                        info.append(f'. {value}')
        return info

    def _full_info(
        self, module_name: str, classes: dict, class_name: str = None
    ) -> str:
        info = [f'{module_name}']

        line, double_line = self._dividing_lines(module_name)

        if module_name in classes:
            info.append(f'\n{double_line}')
            if class_name is None:
                for _class, structure in classes[module_name].items():
                    info.append(f'\n{_class}')
                    info.extend(self._cls_structure(structure))
                    info.append(f'\n{line}')
            else:
                info.append(f'\n{class_name}')
                if class_name in classes[module_name]:
                    info.extend(
                        self._cls_structure(classes[module_name][class_name])
                    )
        return '\n'.join(info)

    def _short_info(
        self, module_name: str, classes: dict, class_name: str = None
    ) -> str:
        info = [f'{module_name}']

        line, double_line = self._dividing_lines(module_name)

        if module_name in classes:
            info.append(f'\n{double_line}')
            if class_name is None:
                for _class, _ in classes[module_name].items():
                    info.append(f'\n{_class}')
                    info.append(f'\n{line}')
            else:
                info.append(f'\n{class_name}')

        return '\n'.join(info)

    def _node_params(self, nodes: set, dirnames: dict, classes: dict):
        node_params = []
        modules = set()
        groups = set()

        for module, cls in nodes:
            if cls is not None:
                params = {
                    "key": self._cls_key(module, cls),
                    "color": self._color(dirnames[module]),
                    "text": cls,
                    "shortInfo": self._short_info(module, classes, cls),
                    "fullInfo": self._full_info(module, classes, cls),
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
                "color": self._color(dirnames[module]),
                "text": module,
                "shortInfo": self._short_info(module, classes),
                "fullInfo": self._full_info(module, classes),
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
                                    self._cls_key(_from, import_item),
                                    self._cls_key(_to, cls),
                                    import_item,
                                    link_types,
                                    True
                                )
                            )
        self.data = {
            "nodes": self._node_params(
                nodes, modules['dirnames'], modules['classes']
            ),
            "links": [
                self._link_to_dict(link) for link in links
            ]
        }

    def save(self):
        write_json(
            self.data, f"./temp/saved/{self.filename}_DIAGRAM.json"
        )
        write_json(
            self.data,
            "./temp/source/diagrams.json"
        )
