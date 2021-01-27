try:
    import neopixel
except:
    import time
    import math
    from colored import fg, bg, attr

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
        def __init__(self, pin, n, *, bpp=3, brightness=1.0, auto_write=True, pixel_order=None):
            self._pixels = n
            self.pin = pin
            self.auto_write = auto_write
            self.brightness = min(max(int(round(100 * brightness, 0)), 100), 0)
            self._data = []
            self._byteorder_string = pixel_order
            self.begin()

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
                self.__draw()

        def insert(self, ii, val):
            self._data.insert(ii, val)
            self.__handle_write()

        def append(self, val):
            self.insert(len(self._data), val)
            self.__handle_write()

        def begin(self):
            for i in range(self._pixels):
                self._data.append((0, 0, 0))
            self.__draw()

        def show(self):
            self.__draw()

        def fill(self, color):
            for pixel in range(self._pixels):
                self._data[pixel] = color

        def clear(self):
            self.fill((0, 0, 0))

        def delay(self, ms):
            time.sleep(ms / 1000)

        def __draw(self):
            reset = attr('reset')
            output = ''
            for r, g, b in self._data:
                color = reset + bg('#%02x%02x%02x' % (r, g, b))
                output = output + color + '  ' + reset
            print(reset + self.__class__.__name__ + 'Simulation', output, sep=' => ', flush=True, end=f"\r")

    pass
