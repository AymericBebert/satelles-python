import inspect
import runpy
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import configue
import socketio

from satelles_python.command_register import CommandRegister
from satelles_python.model import Config, IAnnounce, IArgValue, ICommand, IImperiumAction, ISatelles


class DependencyCompatibilityTests(unittest.TestCase):
    def setUp(self):
        template = Path(__file__).resolve().parents[1] / "config.template.yml"
        self.config = Config(**configue.load(str(template)))

    def test_config_and_model_serialization(self):
        self.assertEqual(self.config.hub.server_url, "http://localhost:4060")
        self.assertEqual(self.config.commands, ["debug", "sensor"])
        announce = IAnnounce(
            token=self.config.hub.room_token,
            room_name=self.config.hub.room_name,
            satelles=ISatelles(
                id=self.config.hub.device_id,
                name=self.config.hub.device_name,
                commands=[ICommand(name="Click", type="action")],
            ),
        )
        self.assertEqual(
            announce.to_dict(),
            {
                "token": self.config.hub.room_token,
                "roomName": self.config.hub.room_name,
                "satelles": {
                    "id": self.config.hub.device_id,
                    "name": self.config.hub.device_name,
                    "commands": [{"name": "Click", "type": "action", "args": None}],
                },
            },
        )
        action = IImperiumAction(
            satellesId="device", commandName="Click", args=[{"name": "value", "type": "boolean", "booleanValue": True}]
        )
        self.assertEqual(action.args, [IArgValue(name="value", type="boolean", boolean_value=True)])

    def test_socketio_handlers_accept_disconnect_reason(self):
        class StopLoop(BaseException):
            pass

        self.config.commands = []
        register = CommandRegister(self.config)
        runner = Mock()
        runner.name = "test"
        register.register_runner(runner)
        client = socketio.Client(reconnection=False)
        action = {"satellesId": "device", "commandName": "Click"}

        def connect(url):
            self.assertEqual(url, self.config.hub.server_url)
            client._trigger_event("connect", "/")
            client._trigger_event("imperium action", "/", action)
            client._trigger_event("disconnect", "/", client.reason.SERVER_DISCONNECT)
            raise StopLoop()

        with (
            patch("configue.load", return_value=self.config.to_dict()),
            patch("socketio.Client", return_value=client),
            patch("satelles_python.command_register.CommandRegister", return_value=register),
            patch.object(client, "connect", side_effect=connect),
            patch.object(client, "emit") as emit,
            self.assertRaises(StopLoop),
        ):
            runpy.run_module("satelles_python.__main__", run_name="__main__")

        emit.assert_called_once_with(
            "satelles join",
            {
                "token": self.config.hub.room_token,
                "roomName": self.config.hub.room_name,
                "satelles": {"id": self.config.hub.device_id, "name": self.config.hub.device_name, "commands": []},
            },
        )
        runner.connect.assert_called_once_with()
        runner.on_action.assert_called_once_with(IImperiumAction(**action))
        runner.disconnect.assert_called_once_with()
        self.assertEqual(list(inspect.signature(client.handlers["/"]["disconnect"]).parameters), ["reason"])


if __name__ == "__main__":
    unittest.main()
