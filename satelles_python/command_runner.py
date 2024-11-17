from .command_register import CommandRegister
from .model.imperium import IImperiumAction


class CommandRunner:
    name: str

    def __init__(self, command_register: CommandRegister):
        self.command_register = command_register
        command_register.register_runner(self)

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def on_action(self, action: IImperiumAction) -> None:
        pass
