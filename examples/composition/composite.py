from examples.composition.component_one import ComponentOne
from examples.composition.component_two import ComponentTwo


class Composite:
    name = "Composite class"

    def __init__(self):
        self.component1 = ComponentOne()
        self.component2 = ComponentTwo()

    def __str__(self):
        return f"{self.name} composes from {self.component1} and {self.component2}."
