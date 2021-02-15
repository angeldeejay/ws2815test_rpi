from config import LOCALHOST, START_AT, END_AT, DATE_FMT, TIME_FMT
from lib.animations import RainbowCycle, NewKITT
from lib.artnet import ArtNet
from lib.colors import wheel
from lib.network_scanner import NetworkScanner
from lib.utils import evaluate_day_night
from optparse import OptionParser
from subprocess import Popen as call_process, PIPE
from time import sleep
import os
import sys
import traceback


class ControllerService:
    def __init__(self, ip=LOCALHOST, universe=None, led_count=None, quiet=False):
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

    def __write(self, data):
        self.packager.set_led_count(self.led_count)
        for i in range(self.led_count):
            self.packager.set_rgb(i, *data[i])
        self.packager.send()

    def animate(self):
        # Data placeholder
        self.packager.set_led_count(self.led_count)
        if evaluate_day_night(START_AT, END_AT, DATE_FMT, TIME_FMT):
            # RainbowCycle(pixels, SpeedDelay, cycles)
            RainbowCycle(self.led_count, 3 / 255, 1, write_fn=self.__write)
        else:
            # NewKITT(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay, cycles)
            eye_size = max(1, int(round(self.led_count / 10)))
            steps = (self.led_count - eye_size - 2) * 8
            speed = 6 / steps
            NewKITT(self.led_count, 128, 0, 0, eye_size,
                    speed, 0, 1, write_fn=self.__write)

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
        attempts = 0
        while attempts < 5:
            self.packager.clear()
            self.packager.set_led_count(self.led_count)
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
            main.stop()
    except KeyboardInterrupt:
        main.stop()
        pass
    except:
        traceback.print_exc()
        pass
