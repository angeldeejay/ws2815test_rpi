import time
import board
import neopixel
from sys import argv
from lib.utils import evaluate_day_night
from lib.animations import NewKITT, RainbowCycle, shutdown

start_at = '17:30:00'
end_at = '06:30:00'
date_fmt = '%Y/%m/%d '
time_fmt = '%H:%M:%S'

pixels = neopixel.NeoPixel(
    board.D18, 11, brightness=1.0, auto_write=False, pixel_order=neopixel.GRB)
if __name__ == '__main__':
    try:
        if len(argv) > 1 and argv[1] == '--off':
            shutdown(pixels)
            pixels.deinit()
        else:
            while True:
                if evaluate_day_night(start_at, end_at, date_fmt, time_fmt):
                    RainbowCycle(pixels, 0.001, 1)
                else:
                    NewKITT(pixels, 255, 0, 0, 1, 0.075, 0, 1)
    except KeyboardInterrupt:
        pass
    finally:
        shutdown(pixels)
        pixels.deinit()
