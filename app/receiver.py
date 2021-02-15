import os
import sys
import traceback
from time import sleep
from lib.artnet import ArtNet
from lib.devices.neopixel import neopixel, Pin, hardware_available
from lib.threading import Thread
from optparse import OptionParser
from subprocess import Popen as call_process, PIPE


class ReceiverService:
    def __init__(self, quiet=False):
        self.running = False
        self.quiet = quiet
        self.packager = ArtNet(target_ip='0.0.0.0', receiver=True)
        self.__thread = None

        self.running = False
        if not hardware_available:
            self.strips = [
                neopixel.NeoPixel(Pin(18), 170, auto_write=False,
                                  pixel_order='GRB', simulate=not self.quiet),
                neopixel.NeoPixel(Pin(19), 170, auto_write=False,
                                  pixel_order='GRB', simulate=not self.quiet)
            ]
        else:
            self.strips = [
                neopixel.NeoPixel(
                    Pin(18), 170, auto_write=False, pixel_order='GRB'),
                neopixel.NeoPixel(
                    Pin(18), 170, auto_write=False, pixel_order='GRB')
            ]

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)

    def run(self):
        self.running = True
        while True:
            # Manual control
            if self.running == False:
                return

            data = self.packager.receive()
            num_pixels = data['pixels_count']
            for i in range(num_pixels):
                self.strips[data["universe"] -
                            1][i] = data["data"][i]
            self.strips[data["universe"] - 1].show()

    def stop(self):
        print('', flush=True)
        self.__log('Exiting...')
        self.running = False
        for strip in self.strips:
            strip.deinit()


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
            raise Exception()
    except:
        pass
    finally:
        main.stop()
        pass
