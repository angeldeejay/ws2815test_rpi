from config import LOCALHOST, START_AT, END_AT, DATE_FMT, TIME_FMT
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

    def animate(self):
        # Data placeholder
        self.packager.clear()
        self.packager.set_led_count(self.led_count)
        [self.packager.set_value(i, 0) for i in range(170)]
        if evaluate_day_night(START_AT, END_AT, DATE_FMT, TIME_FMT):
            # RainbowCycle(pixels, SpeedDelay, cycles)
            speed = 2 / 255
            animation = f'RainbowCycle({self.led_count},{speed},1,write_fn=lambda x: self.render(x,{self.led_count},pixels))'
            print(animation, flush=True)
            address = 0
            for c in animation:
                self.packager.set_value(address, ord(c))
                address += 1
        else:
            # NewKITT(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay, cycles)
            eye_size = max(1, int(round(self.led_count / 5)))
            steps = (self.led_count - eye_size - 2) * 8
            speed = 4 / steps
            animation = f'NewKITT({self.led_count},128,0,0,{eye_size},{speed},0,1,write_fn=lambda x: self.render(x,{self.led_count},pixels))'
            print(animation, flush=True)
            address = 0
            for c in animation:
                self.packager.set_value(address, ord(c))
                address += 1
        self.packager.send()

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
            animation = f'shutdown({self.led_count},write_fn=lambda x: self.render(x,{self.led_count},pixels))'
            address = 0
            for c in animation:
                self.packager.set_value(address, ord(c))
                address += 1
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
