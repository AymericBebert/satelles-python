import time
from threading import Thread

from satelles_python.command_register import CommandRegister
from satelles_python.command_runner import CommandRunner
from satelles_python.model import ICommand, IImperiumAction


class DebugRunner(CommandRunner):
    name: str = "debug"

    def __init__(self, command_register: CommandRegister):
        super().__init__(command_register)
        self.nb_clicks = 0
        self.nb_reconnections = 0
        self.nb_auto_increment = 0
        self.commands: list[ICommand] = []
        self._refresh_commands()
        send_metrics(self)

    def connect(self) -> None:
        self.nb_reconnections += 1
        self._refresh_commands()

    def disconnect(self) -> None:
        pass

    def on_action(self, action: IImperiumAction) -> None:
        if action.command_name == "Click":
            self.nb_clicks += 1
            self._refresh_commands()

    def increment(self) -> None:
        self.nb_auto_increment += 1
        self._refresh_commands()

    def _refresh_commands(self) -> None:
        self.commands = [
            ICommand(
                name=f"Alive for {self.nb_auto_increment} polls",
                type="info",
            ),
            ICommand(
                name=f"Connected {self.nb_reconnections} times",
                type="info",
            ),
            ICommand(
                name=f"Clicked {self.nb_clicks} times",
                type="info",
            ),
            ICommand(
                name="Click",
                type="action",
            ),
        ]
        self.command_register.on_commands(self, self.commands)


def send_metrics(runner: DebugRunner):
    thread = Thread(target=send_metrics_loop, args=(runner,))
    thread.start()


def send_metrics_loop(runner: DebugRunner):
    while True:
        runner.increment()
        time.sleep(3)
