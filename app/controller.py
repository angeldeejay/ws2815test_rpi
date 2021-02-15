import os
import sys
import traceback
from time import sleep
from lib.artnet import ArtNet
from lib.colors import wheel
from lib.network_scanner import NetworkScanner
from lib.utils import evaluate_day_night
from optparse import OptionParser
from subprocess import Popen as call_process, PIPE

START_AT = '17:55:00'
END_AT = '23:30:00'
DATE_FMT = '%Y/%m/%d '
TIME_FMT = '%H:%M:%S'


class ControllerService:
    def __init__(self, ip='127.0.0.1', universe=None, led_count=None, quiet=False):
        self.target_ip = ip
        self.universe = universe
        self.led_count = led_count
        self.running = False
        self.packager = ArtNet(target_ip=self.target_ip,
                               universe=self.universe, receiver=False)

        self.__log(f'Target IP: {self.target_ip}')
        self.__log(f'Universe:  {self.universe}')
        self.__log(f'LED Count: {self.led_count}')

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)

    def __is_night(self):
        return evaluate_day_night(START_AT, END_AT, DATE_FMT, TIME_FMT)

    def animate(self):
        # Data placeholder
        self.packager.set(511, self.led_count)
        for j in range(255):
            for i in range(self.led_count):
                pixel_index = (i * 256 // self.led_count) + j
                color = wheel(pixel_index & 255, 'GRB')
                self.packager.set_rgb(i, *color)
            self.packager.send()
            sleep(9 / 255)

    def run(self):
        self.running = True
        while True:
            # Manual control
            if self.running == False:
                return

            self.animate()
            sleep(0.1)

    def stop(self):
        print('', flush=True)
        self.__log('Exiting...')
        self.running = False
        attemps = 0
        while attemps < 10:
          self.packager.clear()
          self.packager.set(511, self.led_count)
          self.packager.send()
          attempts += 1
          sleep(0.1)
        self.packager.close()


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--off", action="store_true",
                      dest="terminate", default=False)
    parser.add_option("-q", "--quiet", action="store_true",
                      dest="quiet", default=False)
    (options, args) = parser.parse_args()

    strip_specs = args.pop(0).split('-')
    if int(strip_specs[1]) not in range(1, 3, 1):
        raise Exception(
            f'Invalid universe: {strip_specs[1]}. Allowed universes: 1-2')

    main = ControllerService(quiet=options.quiet, ip=strip_specs[0], universe=int(
        strip_specs[1]), led_count=int(strip_specs[2]))
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
