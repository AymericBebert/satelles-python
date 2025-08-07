import json
from typing import TYPE_CHECKING

import socketio

if TYPE_CHECKING:
    from .command_runner import CommandRunner
from .model import Config, ICommand, IImperiumAction


class CommandRegister:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._runners: dict[str, "CommandRunner"] = {}
        self._commands: dict[str, list[ICommand]] = {}
        self._last_commands: str = '[]'
        self._sio: socketio.Client | None = None

    def register_runner(self, runner: "CommandRunner") -> None:
        self._runners[runner.name] = runner
        self._commands[runner.name] = []

    def connect(self, sio: socketio.Client) -> None:
        for runner in self._runners.values():
            runner.connect()
        self._sio = sio

    def disconnect(self) -> None:
        for runner in self._runners.values():
            runner.disconnect()
        self._sio = None

    def on_action(self, action: IImperiumAction) -> None:
        for runner in self._runners.values():
            runner.on_action(action)

    def on_commands(self, runner: "CommandRunner", commands: list[ICommand]) -> None:
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
                if self.config.misc.debug_socket:
                    print("satelles update:", commands_dto)
                try:
                    self._sio.emit("satelles update", commands_dto)
                except Exception as e:
                    print("Error sending satelles update:", e)
