import os
import sys
import traceback
from time import sleep
from .lib.animations import NewKITT, RainbowCycle
from .lib.devices import LedStrip
from .lib.network_scanner import NetworkScanner
from .lib.utils import evaluate_day_night
from optparse import OptionParser
from subprocess import Popen as call_process, PIPE


class StripService:
    def __init__(self, quiet=False, gpio_pin=None, led_count=None):
        self.main_host = "192.168.1.13"
        self.gpio_pin = gpio_pin
        self.led_count = led_count
        self.running = False
        self.__log(f'Main Host: {self.main_host}')
        self.__log(f'GPIO: {self.gpio_pin}')
        self.__log(f'LED Count: {self.led_count}')

        self.__start_at = '17:55:00'
        self.__end_at = '23:30:00'
        self.__date_fmt = '%Y/%m/%d '
        self.__time_fmt = '%H:%M:%S'

        self.strip = LedStrip(
            gpio_pin=self.gpio_pin, led_count=self.led_count, quiet=quiet, pixel_order="GRB")

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)

    def __is_night(self):
        return evaluate_day_night(self.__start_at, self.__end_at, self.__date_fmt, self.__time_fmt)

    def animate(self, pixels):
        num_pixels = pixels._pixels
        if self.__is_night():
            # RainbowCycle(pixels, SpeedDelay, cycles)
            RainbowCycle(pixels, 3 / 255, 1)
        else:
            # NewKITT(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay, cycles)
            eye_size = max(1, int(round(num_pixels / 10)))
            steps = (num_pixels - eye_size - 2) * 8
            speed = 6 / steps
            NewKITT(pixels, 128, 0, 0, eye_size, speed, 0, 1)

    def run(self):
        self.running = True
        self.strip.set_animation(lambda pixels: self.animate(pixels))
        while True:
            # Manual control
            if self.running == False:
                return

            sleep(0.1)

    def stop(self):
        print('', flush=True)
        self.__log('Exiting...')
        self.running = False
        self.strip.stop()


ALLOWED_PINS = [18, 21, 19, 13]

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--off", action="store_true",
                      dest="terminate", default=False)
    parser.add_option("-q", "--quiet", action="store_true",
                      dest="quiet", default=False)
    (options, args) = parser.parse_args()

    strip_specs = list(map(lambda x: int(x), args.pop(0).split('-')))
    if strip_specs[0] not in ALLOWED_PINS:
        raise Exception(f'Invalid GPIO. Allowed pins: {ALLOWED_PINS}')

    main = StripService(quiet=options.quiet,
                        gpio_pin=strip_specs[0], led_count=strip_specs[1])
    try:
        if options.terminate == False:
            main.run()
        else:
            raise Exception()
    except:
        pass
    finally:
        main.stop()
        pass
