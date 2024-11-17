import logging

logger = logging.getLogger("Mock GPIO")
logger.warning("Using fake GPIO, could not import real library.")

# Constants defined in GPIO
BCM = 11
BOARD = 10
BOTH = 33
FALLING = 32
HARD_PWM = 43
HIGH = 1
I2C = 42
IN = 1
LOW = 0
OUT = 0
PUD_DOWN = 21
PUD_OFF = 20
PUD_UP = 22
RISING = 31
SERIAL = 40
SPI = 41
UNKNOWN = -1
VERSION = "0.7.1"


def setmode(mode: int) -> None:
    logger.info(f"Mock GPIO setmode {mode}")


def setwarnings(mode: bool) -> None:
    logger.info(f"Mock GPIO setwarnings {mode}")


def setup(pin: int, mode: int, initial: int = None) -> None:
    logger.info(f"Mock GPIO setup {pin} as {mode} (starts {initial})")


def add_event_detect(pin: int, mode: int) -> None:
    logger.info(f"Mock GPIO add_event_detect {pin} as {mode}")


# noinspection PyShadowingBuiltins
def input(pin: int) -> int:
    logger.info(f"Mock GPIO input {pin}")
    return LOW


def output(pin: int, state: str) -> None:
    logger.info(f"Mock GPIO output pin {pin} as {state}")
