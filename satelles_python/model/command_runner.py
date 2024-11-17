from .imperium import IImperiumAction


class CommandRunner:
    name: str

    def init(self) -> None:
        pass

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def on_action(self, action: IImperiumAction) -> None:
        pass
