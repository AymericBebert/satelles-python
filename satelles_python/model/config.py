from .camel_case_model import CamelCaseModel


class HubConfig(CamelCaseModel):
    server_url: str
    room_token: str
    room_name: str
    device_id: str
    device_name: str


class MiscConfig(CamelCaseModel):
    debug_socket: bool


class Config(CamelCaseModel):
    hub: HubConfig
    commands: list[str]
    misc: MiscConfig
