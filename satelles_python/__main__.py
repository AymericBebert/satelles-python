import configue
import socketio

from .command_register import command_register
from .model import Config, IImperiumAction

config = Config.from_dict(configue.load("config.yml"))

sio = socketio.Client()


@sio.event
def connect():
    sio.emit("satelles join", {
        "token": config.hub.room_token,
        "roomName": config.hub.room_name,
        "satelles": {
            "id": config.hub.device_id,
            "name": config.hub.device_name,
            "commands": [c.to_dict() for c in command_register.commands],
        },
    })
    command_register.connect(sio)


@sio.event
def connect_error():
    command_register.disconnect()


@sio.event
def disconnect():
    command_register.disconnect()


@sio.on('imperium action')
def on_imperium_action(action: IImperiumAction):
    command_register.on_action(action)


if "sensor" in config.commands:
    from .metriful_sensor.send_metrics import SensorRunner

    sensor_runner = SensorRunner()
    command_register.register_runner(sensor_runner)

sio.connect(config.hub.server_url)
