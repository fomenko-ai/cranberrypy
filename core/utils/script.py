import subprocess
from typing import Union, Callable

from core.logger import Logger


class Command:
    def __init__(self, command: str):
        self.command = command

    def run(self):
        subprocess.run(self.command, shell=True, check=True)


class Script:
    def __init__(self, logger: Logger):
        self.commands = None
        self.logger = logger

    def add(
        self,
        command: Union[str, Callable],
        description=None,
        exception_break=True
    ):
        if self.commands is None:
            self.commands = []
        if isinstance(command, str):
            func = Command(command).run
            desc = description if description else command
        elif callable(command):
            func = command
            desc = description if description else command.__name__
        else:
            raise ValueError(f"'{command}' is not a valid")
        self.commands.append((func, desc, exception_break))

    def run(self):
        for func, desc, exception_break in self.commands:
            try:
                self.logger.info(f"Run: {desc}")
                func()
                self.logger.info(f"Finish successfully: {desc}")
            except Exception as e:
                self.logger.error(f"Fail: {desc}", e)
                if exception_break is True:
                    break
