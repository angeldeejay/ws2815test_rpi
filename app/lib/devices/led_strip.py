from .neopixel import neopixel, Pin, hardware_available
from ..threading import Thread
from ..animations import shutdown
import time
import traceback


class LedStrip:
    def __init__(self, gpio_pin=None, brightness=1.0, led_count=None, pixel_order=None, quiet=False, animation=None):
        self.on = False
        self.gpio_pin = Pin(gpio_pin)
        self.led_count = int(led_count)
        self.pixel_order = pixel_order
        self.simulate = not hardware_available
        self.brightness = brightness
        self.quiet = quiet
        self.pixels = None
        self.animation = None
        # Start thread
        self.on = True
        self.__thread = Thread(target=self.__animate, args=[], daemon=True)
        self.__thread.start()
        self.start()

    def __repr__(self):
        attributes = {
            'simulate': self.simulate,
            'quiet': self.quiet,
            'animation': self.animation,
            'pixels': self.pixels,
        }
        return f'@{self.__class__.__name__}{attributes}'

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)

    def __write(self, data):
        for i in range(len(data)):
            self.pixels[i] = data[i]
        self.pixels.show()

    def __animate(self):
        while True:
            if not self.on:
                break

            if callable(self.animation):
                self.animation(self.pixels)
            else:
                time.sleep(1)

    def set_animation(self, animation):
        if callable(animation):
            self.animation = animation
        else:
            self.animation = None

    def set_pixel_color(self, pos, r, g, b):
        self.pixels[pos] = (r, g, b)

    def init_pixels(self):
        while self.pixels is None:
            try:
                placeholder = None
                if self.simulate == True:
                    placeholder = neopixel.NeoPixel(self.gpio_pin, self.led_count, brightness=self.brightness,
                                                    auto_write=False, pixel_order=self.pixel_order, simulate=not self.quiet)
                else:
                    placeholder = neopixel.NeoPixel(self.gpio_pin, self.led_count, brightness=self.brightness,
                                                    auto_write=False, pixel_order=self.pixel_order)
                self.pixels = placeholder
                self.pixels
                self.__log(f'Initialized LED Strip: {self}')
            except:
                traceback.print_exc()
                self.pixels = None
                pass
            time.sleep(0.1)

    def start(self):
        # Init led strip
        self.init_pixels()
        shutdown(self.led_count, write_fn=self.__write)

    def stop(self):
        # Stop thread
        self.on = False
        if self.__thread is not None:
            self.__thread.kill()
            self.__thread = None

        # Stop led strip
        self.init_pixels()
        while self.pixels is not None:
            try:
                shutdown(self.led_count, write_fn=self.__write)
                self.pixels.deinit()
                self.pixels = None
            except Exception as e:
                self.__log(e)
                pass
            time.sleep(0.1)
