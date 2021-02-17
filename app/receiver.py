from config import ANYWHERE
from lib.artnet import ArtNet
from lib.animations import *
from lib.devices.led_strip import LedStrip
# from lib.devices.neopixel import neopixel, Pin, hardware_available
from lib.threading import Thread
from optparse import OptionParser
from subprocess import Popen as call_process, PIPE
from time import sleep
import os
import sys
import traceback


class ReceiverService:
    def __init__(self, quiet=False):
        self.running = False
        self.quiet = quiet
        self.packager = ArtNet(target_ip=ANYWHERE, receiver=True)
        self.strips = [
            LedStrip(gpio_pin=18, led_count=170, quiet=self.quiet),
            LedStrip(gpio_pin=19, led_count=170, quiet=self.quiet)
        ]
        # self.strips = [
        #     neopixel.NeoPixel(
        #         Pin(18), 170, auto_write=False, pixel_order='GRB'),
        #     neopixel.NeoPixel(
        #         Pin(19), 170, auto_write=False, pixel_order='GRB')
        # ]

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)

    def write(self, animation_code, pixels):
        eval(animation_code, {**globals(), **locals()},
             {**globals(), **locals()})

    def render(self, data, led_count, pixels):
        for i in range(led_count):
            pixels[i] = data[i]
        pixels.show()

    def run(self):
        self.running = True
        while self.running:
            data = self.packager.receive()
            animation = ''.join([chr(c) for c in data['data']]).rstrip('\x00')
            self.strips[data['universe'] - 1].set_animation(
                lambda pixels: self.write(animation, pixels))
            sleep(0.1)

    def stop(self):
        print('', flush=True)
        self.__log('Exiting...')
        self.running = False
        for strip in self.strips:
            strip.stop()


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--off", action="store_true",
                      dest="terminate", default=False)
    parser.add_option("-q", "--quiet", action="store_true",
                      dest="quiet", default=False)
    (options, args) = parser.parse_args()

    main = ReceiverService(quiet=options.quiet)
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
