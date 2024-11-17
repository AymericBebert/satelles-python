try:
    import RPi.GPIO as GPIO
except ImportError:
    import satelles_python.raspberry_pi.gpio_mock as GPIO

try:
    import smbus
except ImportError:
    import satelles_python.raspberry_pi.smbus_mock as smbus
