import time
import math
import sys
from lib.threading import Thread
from colors import color as colorize

# Pixel color order constants
RGB = "RGB"
"""Red Green Blue"""
GRB = "GRB"
"""Green Red Blue"""
RGBW = "RGBW"
"""Red Green Blue White"""
GRBW = "GRBW"
"""Green Red Blue White"""


class NeoPixel(list):
    def __init__(self, pin, n, *, bpp=3, brightness=1.0, auto_write=True, pixel_order=None, simulate=True):
        self._pixels = n
        self.pin = pin
        self.auto_write = auto_write
        self.brightness = min(max(int(round(100 * brightness, 0)), 100), 0)
        self._data = []
        self._byteorder_string = pixel_order
        self.__thread = None
        self.__simulate = simulate
        self.on = False
        self.begin()

    def begin(self):
        for i in range(self._pixels):
            self._data.append((0, 0, 0))

        if self.__simulate == True:
            if self.__thread is not None:
                self.deinit()
            self.on = True
            self.__thread = Thread(target=self.simulate, args=[], daemon=True)
            self.__thread.start()

    def deinit(self):
        self.on = False
        if self.__simulate == True:
            time.sleep(1)
            self.__thread = None

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self._data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, ii):
        return self._data[ii]

    def __delitem__(self, ii):
        del self._data[ii]
        self.__handle_write()

    def __setitem__(self, ii, val):
        self._data[ii] = val
        self.__handle_write()

    def __str__(self):
        return str(self._data)

    def __handle_write(self):
        if self.auto_write:
            self.show()

    def insert(self, ii, val):
        self._data.insert(ii, val)
        self.__handle_write()

    def append(self, val):
        self.insert(len(self._data), val)
        self.__handle_write()

    def show(self):
        return

    def simulate(self, end="\r"):
        if self.__simulate == True:
            while True:
                if not self.on:
                    break
                try:
                    output = ''.join([colorize('█', (r, g, b), None)
                                    for r, g, b in self._data])
                    sys.stdout.write(self.__class__.__name__ +
                                    ' => ' + output + end)
                    sys.stdout.flush()
                except:
                    pass
                time.sleep(0.01)

    def fill(self, color):
        for pixel in range(self._pixels):
            self._data[pixel] = color
