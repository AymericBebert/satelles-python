from enum import Enum
from typing import Any

from pydantic import BaseModel


class CommandType(str, Enum):
    info = "info"
    action = "action"
    complex = "complex"
    UNKNOWN = "UNKNOWN"


class CommandArgType(str, Enum):
    string = "string"
    number = "number"
    boolean = "boolean"
    color = "color"
    select = "select"
    UNKNOWN = "UNKNOWN"


class IArg(BaseModel):
    name: str
    type: CommandArgType
    string_value: str | None = None
    number_value: float | None = None
    number_min: float | None = None
    number_max: float | None = None
    number_step: float | None = None
    boolean_value: bool | None = None
    color_value: str | None = None
    select_value: str | None = None
    select_options: list[str] | None = None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "IArg":
        return IArg(**data)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class ICommand(BaseModel):
    name: str
    type: CommandType
    args: list[IArg] | None = None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ICommand":
        return ICommand(**data)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class ISatelles(BaseModel):
    id: str
    name: str
    commands: list[ICommand]

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ISatelles":
        return ISatelles(**data)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class IAnnounce(BaseModel):
    token: str
    roomName: str
    satelles: ISatelles

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "IAnnounce":
        return IAnnounce(**data)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
