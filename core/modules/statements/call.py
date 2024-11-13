import ast

from core.modules.statements.base import Base
from main import LOGGER


class Call(Base):
    def __init__(self, value: ast.Call):
        super().__init__(value)
        self.name = None
        self._parse()

    def _parse(self):
        try:
            self.name = self.recursion_class_call_scan(self.statement)
        except Exception as e:
            LOGGER.error(e)
