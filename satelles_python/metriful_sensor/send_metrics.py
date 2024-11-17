import time
from threading import Thread

import satelles_python.metriful_sensor.sensor_package.sensor_constants as const
import satelles_python.metriful_sensor.sensor_package.sensor_functions as sensor
from satelles_python.command_register import command_register
from satelles_python.model import CommandRunner, ICommand, IImperiumAction


class SensorRunner(CommandRunner):
    name: str = "sensor"

    def __init__(self):
        self.commands: list[ICommand] = []

    def init(self) -> None:
        send_metrics(self)

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def on_action(self, action: IImperiumAction) -> None:
        pass


def send_metrics(runner: SensorRunner):
    # How often to read and report the data (every 3, 100 or 300 seconds)
    cycle_period = const.CYCLE_PERIOD_3_S

    # Set up the GPIO and I2C communications bus
    (GPIO, I2C_bus) = sensor.SensorHardwareSetup()

    # Apply the settings to the MS430
    I2C_bus.write_i2c_block_data(sensor.i2c_7bit_address, const.PARTICLE_SENSOR_SELECT_REG, [sensor.PARTICLE_SENSOR])
    I2C_bus.write_i2c_block_data(sensor.i2c_7bit_address, const.CYCLE_TIME_PERIOD_REG, [cycle_period])

    # Enter cycle mode
    I2C_bus.write_byte(sensor.i2c_7bit_address, const.CYCLE_MODE_CMD)

    thread = Thread(target=send_metrics_loop, args=(runner, GPIO, I2C_bus))
    thread.start()


def send_metrics_loop(runner: SensorRunner, GPIO, I2C_bus):
    while True:
        # Wait for the next new data release, indicated by a falling edge on READY
        while not GPIO.event_detected(sensor.READY_pin):
            time.sleep(0.05)

        # Now read all data from the MS430
        air_data = sensor.get_air_data(I2C_bus)
        air_quality_data = sensor.get_air_quality_data(I2C_bus)
        light_data = sensor.get_light_data(I2C_bus)
        sound_data = sensor.get_sound_data(I2C_bus)
        # particle_data = sensor.get_particle_data(I2C_bus, sensor.PARTICLE_SENSOR)

        # Send data to Rerum Imperium
        runner.commands = [
            {
                "name": f"Temperature: {air_data['T']:.1f} {air_data['T_unit']}",
                "type": "info",
            },
            {
                "name": f"Humidity: {air_data['H_pc']}%",
                "type": "info",
            },
            {
                "name": f"Pressure: {air_data['P_Pa'] / 100:.2f} hPa",
                "type": "info",
            },
            {
                "name": f"Illuminance: {light_data['illum_lux']:d} lux",
                "type": "info",
            },
            {
                "name": f"Sound level: {sound_data['SPL_dBA']:.1f} dBA",
                "type": "info",
            },
            {
                "name": f"Sound peak: {sound_data['peak_amp_mPa']:.2f} mPa",
                "type": "info",
            },
            {
                "name": f"Air Quality Index: {air_quality_data['AQI']:.1f}",
                "type": "info",
            },
            {
                "name": f"Air quality assessment: {sensor.interpret_AQI_value(air_quality_data['AQI'])}",
                "type": "info",
            },
            # {
            #     "name": f"Particle concentration: {particle_data['concentration']:.2f} {particle_data['conc_unit']}",
            #     "type": "info",
            # },
        ]
        command_register.on_commands(runner, runner.commands)
