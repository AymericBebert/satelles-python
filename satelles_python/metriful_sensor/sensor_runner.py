import time
from threading import Thread

import satelles_python.metriful_sensor.sensor_package.sensor_constants as const
import satelles_python.metriful_sensor.sensor_package.sensor_functions as sensor
from satelles_python.command_register import CommandRegister
from satelles_python.command_runner import CommandRunner
from satelles_python.model import ICommand, IImperiumAction


class SensorRunner(CommandRunner):
    name: str = "sensor"

    def __init__(self, command_register: CommandRegister):
        super().__init__(command_register)
        self.commands: list[ICommand] = []
        send_metrics(self)

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def on_action(self, action: IImperiumAction) -> None:
        pass


# How often to read and report the data (every 3, 100 or 300 seconds)
CYCLE_PERIOD = const.CYCLE_PERIOD_3_S
# If no new data is announced within this delay, the sensor is considered stuck
READY_TIMEOUT_S = 30
RETRY_DELAY_S = 5


def setup_sensor():
    # Set up the GPIO and I2C communications bus
    (GPIO, I2C_bus) = sensor.SensorHardwareSetup()

    # Apply the settings to the MS430
    I2C_bus.write_i2c_block_data(sensor.i2c_7bit_address, const.PARTICLE_SENSOR_SELECT_REG, [sensor.PARTICLE_SENSOR])
    I2C_bus.write_i2c_block_data(sensor.i2c_7bit_address, const.CYCLE_TIME_PERIOD_REG, [CYCLE_PERIOD])

    # Enter cycle mode
    I2C_bus.write_byte(sensor.i2c_7bit_address, const.CYCLE_MODE_CMD)
    return GPIO, I2C_bus


def teardown_sensor(GPIO, I2C_bus) -> None:
    try:
        GPIO.remove_event_detect(sensor.READY_pin)
    except Exception:
        pass
    try:
        I2C_bus.close()
    except Exception:
        pass


def send_metrics(runner: SensorRunner):
    (GPIO, I2C_bus) = setup_sensor()
    thread = Thread(target=send_metrics_loop, args=(runner, GPIO, I2C_bus), daemon=True)
    thread.start()


def send_metrics_loop(runner: SensorRunner, GPIO, I2C_bus):
    # Never let a sensor error kill the thread: values would silently stop updating
    while True:
        try:
            if GPIO is None:
                (GPIO, I2C_bus) = setup_sensor()
                print("Sensor re-initialized", flush=True)
            read_and_send_metrics(runner, GPIO, I2C_bus)
        except Exception as e:
            print(f"Sensor error (re-initializing in {RETRY_DELAY_S}s): {e!r}", flush=True)
            if GPIO is not None:
                teardown_sensor(GPIO, I2C_bus)
            GPIO, I2C_bus = None, None
            time.sleep(RETRY_DELAY_S)


def read_and_send_metrics(runner: SensorRunner, GPIO, I2C_bus):
    while True:
        # Wait for the next new data release, indicated by a falling edge on READY
        deadline = time.monotonic() + READY_TIMEOUT_S
        while not GPIO.event_detected(sensor.READY_pin):
            if time.monotonic() > deadline:
                raise TimeoutError(f"no data ready signal for {READY_TIMEOUT_S}s")
            time.sleep(0.05)

        # Now read all data from the MS430
        air_data = sensor.get_air_data(I2C_bus)
        air_quality_data = sensor.get_air_quality_data(I2C_bus)
        light_data = sensor.get_light_data(I2C_bus)
        sound_data = sensor.get_sound_data(I2C_bus)
        particle_data = sensor.get_particle_data(I2C_bus, sensor.PARTICLE_SENSOR) \
            if sensor.PARTICLE_SENSOR != const.PARTICLE_SENSOR_OFF \
            else None

        # Compute commands
        commands: list[ICommand] = []
        commands.extend([
            ICommand(
                name=f"Temperature: {air_data['T']:.1f} {air_data['T_unit']}",
                type="info",
            ),
            ICommand(
                name=f"Humidity: {air_data['H_pc']} %",
                type="info",
            ),
            ICommand(
                name=f"Pressure: {air_data['P_Pa'] / 100:.2f} hPa",
                type="info",
            ),
        ])
        if air_quality_data['AQI_accuracy'] > 0:
            commands.extend([
                ICommand(
                    name=f"Air Quality Index: {air_quality_data['AQI']:.1f} ({sensor.interpret_AQI_value(air_quality_data['AQI'])})",
                    type="info",
                ),
                ICommand(
                    name=f"Estimated CO2: {air_quality_data['CO2e']:.1f} ppm",
                    type="info",
                ),
                ICommand(
                    name=f"Equivalent Breath VOC: {air_quality_data['bVOC']:.2f} ppm",
                    type="info",
                ),
            ])
        commands.extend([
            ICommand(
                name=f"Air Quality Accuracy: {sensor.interpret_AQI_accuracy(air_quality_data['AQI_accuracy'])}",
                type="info",
            ),
        ])
        if particle_data:
            commands.extend([
                ICommand(
                    name=f"Particle concentration: {particle_data['concentration']:.2f} {particle_data['conc_unit']}",
                    type="info",
                ),
            ])
        commands.extend([
            ICommand(
                name=f"Illuminance: {int(light_data['illum_lux'])} lux",
                type="info",
            ),
            ICommand(
                name=f"Sound level: {sound_data['SPL_dBA']:.1f} dBA",
                type="info",
            ),
            # ICommand(
            #     name=f"Sound peak: {sound_data['peak_amp_mPa']:.2f} mPa",
            #     type="info",
            # ),
        ])

        # Send data to Rerum Imperium
        runner.commands = commands
        runner.command_register.on_commands(runner, runner.commands)
