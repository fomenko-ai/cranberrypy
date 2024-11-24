from examples.inheritance.child import *
from examples.composition.composite import *
from examples.wildcard_imports.utils import *


class CompositeChild(Child):
    def __init__(self):
        super().__init__()
        self.composite = Composite()

    @staticmethod
    def use_func():
        func()

    @staticmethod
    async def use_async_func():
        await async_func()
