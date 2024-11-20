import time

import configue
import socketio

from .command_register import CommandRegister
from .model import Config, IAnnounce, IImperiumAction, ISatelles

config = Config(**configue.load("config.yml"))
command_register = CommandRegister(config)

sio = socketio.Client()


@sio.event
def connect():
    announce = IAnnounce(
        token=config.hub.room_token,
        room_name=config.hub.room_name,
        satelles=ISatelles(
            id=config.hub.device_id,
            name=config.hub.device_name,
            commands=command_register.commands,
        ),
    )
    announce_dto = announce.to_dict()
    if config.misc.debug_socket:
        print('satelles join:', announce_dto)
    sio.emit("satelles join", announce_dto)
    command_register.connect(sio)


@sio.event
def connect_error(reason: dict[str, str]):
    print('connect_error', reason)
    command_register.disconnect()


@sio.event
def disconnect():
    print('disconnect')
    command_register.disconnect()


@sio.on('imperium action')
def on_imperium_action(action_dto: dict):
    if config.misc.debug_socket:
        print('imperium action:', action_dto)
    action = IImperiumAction(**action_dto)
    command_register.on_action(action)


if "sensor" in config.commands:
    from .metriful_sensor.sensor_runner import SensorRunner

    sensor_runner = SensorRunner(command_register)

if "debug" in config.commands:
    from .debug_runner.debug_runner import DebugRunner

    debug_runner = DebugRunner(command_register)

wait_for = 1

while True:
    if not sio.connected:
        try:
            print(f"Connecting to {config.hub.server_url}")
            sio.connect(config.hub.server_url)
        except Exception as e:
            print(f'Connection error (retrying in {wait_for}s):', e)
            time.sleep(wait_for)
            if wait_for < 32:
                wait_for *= 2
            continue
    wait_for = 1
    print("Waiting for events...")
    sio.wait()
