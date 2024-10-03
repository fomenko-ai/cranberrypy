from examples.call.cls import Class
from examples.call.func import func


class Caller:
    name = "Caller class"

    def __init__(self):
        pass

    @staticmethod
    def call_class_method():
        Class.method()

    @staticmethod
    def call_func():
        func()
