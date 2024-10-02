from examples.usage.cls import Class
from examples.usage.func import func


class User:
    name = "User class"

    def __init__(self):
        pass

    @staticmethod
    def use_class():
        return Class()

    @staticmethod
    def use_func():
        return func()
