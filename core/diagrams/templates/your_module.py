from core.diagrams.templates.parent import Parent
from core.diagrams.templates.component import Component
from core.diagrams.templates.cls import Class
from core.diagrams.templates.func import func


class YourClass(Parent):
    name = "YourClass"

    def __init__(self):
        super().__init__()
        self.component = Component()

    def call_func(self):
        self._call_func()

    @staticmethod
    def _call_func():
        func()

    def use_class_method(self):
        self.__use_class_method()

    @staticmethod
    def __use_class_method():
        return Class.method()
