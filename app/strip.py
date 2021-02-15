from config import START_AT, END_AT, DATE_FMT, TIME_FMT
from lib.animations import NewKITT, RainbowCycle
from lib.devices.led_strip import LedStrip
from lib.network_scanner import NetworkScanner
from lib.utils import evaluate_day_night
from optparse import OptionParser
from subprocess import Popen as call_process, PIPE
from time import sleep
import os
import sys
import traceback


class StripService:
    def __init__(self, quiet=False, gpio_pin=None, led_count=None):
        self.gpio_pin = gpio_pin
        self.led_count = led_count
        self.running = False
        self.__log(f'GPIO: {self.gpio_pin}')
        self.__log(f'LED Count: {self.led_count}')

        self.strip = LedStrip(
            gpio_pin=self.gpio_pin, brightness=1.0, led_count=self.led_count, quiet=quiet, pixel_order="GRB")

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)

    def __is_night(self):
        return evaluate_day_night(START_AT, END_AT, DATE_FMT, TIME_FMT)

    def __write(self, data, pixels):
        for i in range(self.led_count):
            pixels[i] = data[i]
        pixels.show()

    def animate(self, pixels):
        num_pixels = pixels._pixels
        if self.__is_night():
            # RainbowCycle(pixels, SpeedDelay, cycles)
            RainbowCycle(num_pixels, 3 / 255, 1, write_fn=lambda x: self.__write(x, pixels))
        else:
            # NewKITT(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay, cycles)
            eye_size = max(1, int(round(num_pixels / 10)))
            steps = (num_pixels - eye_size - 2) * 8
            speed = 6 / steps
            NewKITT(num_pixels, 128, 0, 0, eye_size, speed, 0, 1, write_fn=lambda x: self.__write(x, pixels))

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
            main.stop()
    except KeyboardInterrupt:
        main.stop()
        pass
    except:
        traceback.print_exc()
        pass
