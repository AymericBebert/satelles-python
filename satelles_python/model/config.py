from typing import Any

from pydantic import BaseModel, ConfigDict, alias_generators


class HubConfig(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel)

    server_url: str
    room_token: str
    room_name: str
    device_id: str
    device_name: str

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "HubConfig":
        return HubConfig(**data)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class MiscConfig(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel)

    debug_socket: bool

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "MiscConfig":
        return MiscConfig(**data)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class Config(BaseModel):
    hub: HubConfig
    commands: list[str]
    misc: MiscConfig

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Config":
        return Config(**data)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
