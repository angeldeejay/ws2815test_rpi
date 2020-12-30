import time
import board
import neopixel
from sys import argv
from lib.animations import *

pixels = neopixel.NeoPixel(
    board.D18, 11, brightness=1.0, auto_write=False, pixel_order=neopixel.GRB)
if __name__ == '__main__':
    try:
        if len(argv) > 1 and argv[1] == '--off':
            shutdown(pixels)
            pixels.deinit()
        else:
            while True:
                RainbowCycle(pixels, 0.001, 1)
    except KeyboardInterrupt:
        pass
    finally:
        shutdown(pixels)
        pixels.deinit()
