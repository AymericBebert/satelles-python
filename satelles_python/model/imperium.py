from typing import Literal

from .camel_case_model import CamelCaseModel


class IJoinRoom(CamelCaseModel):
    token: str


class IArgValue(CamelCaseModel):
    name: str
    type: Literal["string", "number", "boolean", "color", "select"]
    string_value: str | None = None
    number_value: float | None = None
    boolean_value: bool | None = None
    color_value: str | None = None
    select_value: str | None = None


class IImperiumAction(CamelCaseModel):
    satelles_id: str
    command_name: str
    args: list[IArgValue] | None = None
