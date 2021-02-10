hardware_available = False
try:
    from board import *
    from microcontroller.pin import Pin
    from . import hw_neopixel as neopixel
    hardware_available = True
except:
    from . import sw_board as board
    from .microcontroller import Pin
    from . import sw_neopixel as neopixel
    pass

__all__ = [
    'neopixel',
    'board',
    'Pin',
    'hardware_available'
]