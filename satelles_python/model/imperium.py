from typing import Any

from pydantic import BaseModel

from .satelles import CommandArgType


class IJoinRoom(BaseModel):
    token: str

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "IJoinRoom":
        return IJoinRoom(**data)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class IArgValue(BaseModel):
    name: str
    type: CommandArgType
    string_value: str | None = None
    number_value: float | None = None
    boolean_value: bool | None = None
    color_value: str | None = None
    select_value: str | None = None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "IArgValue":
        return IArgValue(**data)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class IImperiumAction(BaseModel):
    satelles_id: str
    command_name: str
    args: list[IArgValue] | None = None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "IImperiumAction":
        return IImperiumAction(**data)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
