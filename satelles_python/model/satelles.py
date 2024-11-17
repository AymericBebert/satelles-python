from typing import Literal

from .camel_case_model import CamelCaseModel


class IArg(CamelCaseModel):
    name: str
    type: Literal["string", "number", "boolean", "color", "select"]
    string_value: str | None = None
    number_value: float | None = None
    number_min: float | None = None
    number_max: float | None = None
    number_step: float | None = None
    boolean_value: bool | None = None
    color_value: str | None = None
    select_value: str | None = None
    select_options: list[str] | None = None


class ICommand(CamelCaseModel):
    name: str
    type: Literal["info", "action", "complex"]
    args: list[IArg] | None = None


class ISatelles(CamelCaseModel):
    id: str
    name: str
    commands: list[ICommand]


class IAnnounce(CamelCaseModel):
    token: str
    room_name: str
    satelles: ISatelles
