import json

import socketio

from .model import CommandRunner, ICommand


class CommandRegister:
    def __init__(self):
        self._runners: dict[str, CommandRunner] = {}
        self._commands: dict[str, list[ICommand]] = {}
        self._last_commands: str = '[]'
        self._sio: socketio.Client | None = None

    def register_runner(self, runner: CommandRunner) -> None:
        self._runners[runner.name] = runner
        self._commands[runner.name] = []
        runner.init()

    def connect(self, sio: socketio.Client) -> None:
        for runner in self._runners.values():
            runner.connect()
        self._sio = sio

    def disconnect(self) -> None:
        for runner in self._runners.values():
            runner.disconnect()
        self._sio = None

    def on_action(self, action) -> None:
        for runner in self._runners.values():
            runner.on_action(action)

    def on_commands(self, runner: CommandRunner, commands: list[ICommand]) -> None:
        self._commands[runner.name] = commands
        self._update_commands()

    @property
    def commands(self) -> list[ICommand]:
        return [c for g in self._commands.values() for c in g]

    def _update_commands(self) -> None:
        if self._sio is not None:
            commands_dto = [c.to_dict() for c in self.commands]
            commands_str = json.dumps(commands_dto)
            if commands_str != self._last_commands:
                self._last_commands = commands_str
                self._sio.emit("satelles update", commands_dto)


command_register = CommandRegister()
