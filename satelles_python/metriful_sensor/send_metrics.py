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
        thread = Thread(target=send_metrics_loop, args=(self,))
        thread.start()

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def on_action(self, action: IImperiumAction) -> None:
        pass


def send_metrics_loop(runner: SensorRunner):
    # How often to read and report the data (every 3, 100 or 300 seconds)
    cycle_period = const.CYCLE_PERIOD_3_S

    # Set up the GPIO and I2C communications bus
    (GPIO, I2C_bus) = sensor.SensorHardwareSetup()

    # Apply the settings to the MS430
    I2C_bus.write_i2c_block_data(sensor.i2c_7bit_address, const.PARTICLE_SENSOR_SELECT_REG, [sensor.PARTICLE_SENSOR])
    I2C_bus.write_i2c_block_data(sensor.i2c_7bit_address, const.CYCLE_TIME_PERIOD_REG, [cycle_period])

    # Enter cycle mode
    I2C_bus.write_byte(sensor.i2c_7bit_address, const.CYCLE_MODE_CMD)

    while True:
        # Wait for the next new data release, indicated by a falling edge on READY
        while not GPIO.event_detected(sensor.READY_pin):
            time.sleep(0.05)

        # Now read all data from the MS430
        air_data = sensor.get_air_data(I2C_bus)
        air_quality_data = sensor.get_air_quality_data(I2C_bus)
        light_data = sensor.get_light_data(I2C_bus)
        sound_data = sensor.get_sound_data(I2C_bus)
        particle_data = sensor.get_particle_data(I2C_bus, sensor.PARTICLE_SENSOR)

        # Send data to Rerum Imperium
        runner.commands = [
            {
                "name": f"Temperature: {air_data['T']:.1f} {air_data['T_unit']}",
                "type": "info",
            },
            {
                "name": f"Humidity: {air_data['H_pc']} %",
                "type": "info",
            },
            {
                "name": f"Pressure: {air_data['P_Pa']} Pa",
                "type": "info",
            },
            {
                "name": f"Illuminance: {light_data['illum_lux']:.2f} lx",
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
            {
                "name": f"Particle concentration: {particle_data['concentration']:.2f} {particle_data['conc_unit']}",
                "type": "info",
            },
        ]
        command_register.on_commands(runner, runner.commands)

        # # Specify information needed by Home Assistant.
        # # Icons are chosen from https://cdn.materialdesignicons.com/5.3.45/
        # temperature = dict(name='Temperature', data=air_data['T'],
        #                    unit=air_data['T_unit'], icon='thermometer', decimals=1)
        # humidity = dict(name='Humidity', data=air_data['H_pc'], unit='%',
        #                 icon='water-percent', decimals=1)
        # pressure = dict(name='Pressure', data=air_data['P_Pa'], unit='Pa',
        #                 icon='weather-cloudy', decimals=0)
        # illuminance = dict(name='Illuminance', data=light_data['illum_lux'],
        #                    unit='lx', icon='white-balance-sunny', decimals=2)
        # sound_level = dict(name='Sound level', data=sound_data['SPL_dBA'],
        #                    unit='dBA', icon='microphone', decimals=1)
        # sound_peak = dict(name='Sound peak', data=sound_data['peak_amp_mPa'],
        #                   unit='mPa', icon='waveform', decimals=2)
        # AQI = dict(name='Air Quality Index', data=air_quality_data['AQI'],
        #            unit=' ', icon='thought-bubble-outline', decimals=1)
        # AQI_interpret = dict(name='Air quality assessment',
        #                      data=sensor.interpret_AQI_value(air_quality_data['AQI']),
        #                      unit='', icon='flower-tulip', decimals=0)
        # particle = dict(name='Particle concentration', data=particle_data['concentration'],
        #                 unit=particle_data['conc_unit'], icon='chart-bubble', decimals=2)
        #
        # # Send data to Home Assistant using HTTP POST requests
        # variables = [pressure, humidity, temperature, illuminance, sound_level, sound_peak, AQI, AQI_interpret]
        # if sensor.PARTICLE_SENSOR != const.PARTICLE_SENSOR_OFF:
        #     variables.append(particle)
        # try:
        #     for v in variables:
        #         try:
        #             valueStr = "{:.{dps}f}".format(v['data'], dps=v['decimals'])
        #         except Exception:
        #             valueStr = v['data']
        #         payload = {"state": valueStr, "attributes": {
        #             "unit_of_measurement": v['unit'], "friendly_name": v['name'],
        #             "icon": "mdi:" + v['icon']}}
        #         requests.post(url, json=payload, headers=head, timeout=2)
        # except Exception as e:
        #     # An error has occurred, likely due to a lost network connection,
        #     # and the post has failed.
        #     # The program will retry with the next data release and will succeed
        #     # if the network reconnects.
        #     print("HTTP POST failed with the following error:")
        #     print(repr(e))
        #     print("The program will continue and retry on the next data output.")
