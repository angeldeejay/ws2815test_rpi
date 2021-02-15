from ..animations import shutdown, RainbowCycle, NewKITT
from ..network_scanner import NetworkScanner
from ..threading import Thread
from ..utils import evaluate_day_night
from .neopixel import neopixel, Pin, hardware_available
from config import FAN_STRIP_PIXELS, START_AT, END_AT, DATE_FMT, TIME_FMT, LAPTOP_ETH0, LAPTOP_WLAN1
import time
import traceback


class Fan:
    def __init__(self, gpio_pin=None, quiet=False):
        self.on = False
        self.gpio_pin = Pin(int(gpio_pin))
        self.led_count = int(FAN_STRIP_PIXELS)
        self.__simulate = not hardware_available
        self.__quiet = quiet
        self.__ips = [
            LAPTOP_ETH0,
            LAPTOP_WLAN1
        ]
        self.__pixel_order = neopixel.GRB
        self.__thread = None
        self.__pixels = None
        self.__scanner = None

    def __repr__(self):
        return f'@{self.__class__.__name__}<gpio_pin={self.gpio_pin}, led_count={self.led_count}>'

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)

    def init_pixels(self):
        while self.__pixels is None:
            try:
                placeholder = None
                if self.__simulate == True:
                    placeholder = neopixel.NeoPixel(
                        self.gpio_pin, self.led_count, auto_write=False, pixel_order=self.__pixel_order, simulate=not self.__quiet)
                else:
                    placeholder = neopixel.NeoPixel(
                        self.gpio_pin, self.led_count, auto_write=False, pixel_order=self.__pixel_order)
                self.__pixels = placeholder
            except:
                traceback.print_exc()
                self.__pixels = None
                pass
            time.sleep(0.1)

    def start(self):
        # Init led strip
        self.init_pixels()

        self.__scanner = NetworkScanner(ips=self.__ips)

        # Stop thread if is running
        if self.__thread is not None:
            self.stop()

        # Start thread
        self.on = True
        self.__thread = Thread(target=self.__animate, args=[], daemon=True)
        self.__thread.start()

    def stop(self):
        # Stop thread
        self.on = False
        if self.__thread is not None:
            self.__thread.kill()
            self.__thread = None

        # Stop led strip
        self.init_pixels()
        while self.__pixels is not None:
            try:
                shutdown(self.led_count, write_fn=self.__write)
                self.__pixels.deinit()
                self.__pixels = None
            except Exception as e:
                self.__log(e)
                pass
            time.sleep(0.1)

        if self.__scanner is not None:
            self.__scanner.stop()
            self.__scanner = None

    def __write(self, data):
        for i in range(self.led_count):
            self.__pixels[i] = data[i]
        self.__pixels.show()

    def __animate(self):
        while True:
            if not self.on:
                break

            alive = any(
                map(lambda ip: self.__scanner.is_alive(ip), self.__ips))

            if alive:
                if self.__pixels is not None:
                    if evaluate_day_night(START_AT, END_AT, DATE_FMT, TIME_FMT):
                        # RainbowCycle(pixels, SpeedDelay, cycles)
                        RainbowCycle(self.led_count, 3 / 255, 1, write_fn=self.__write)
                    else:
                        # NewKITT(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay, cycles)
                        eye_size = max(1, int(round(self.led_count / 10)))
                        steps = (self.led_count - eye_size - 2) * 8
                        speed = 6 / steps
                        NewKITT(self.led_count, 128, 0, 0, eye_size, speed, 0, 1, write_fn=self.__write)
            else:
                if self.__pixels is not None:
                    self.__pixels.fill((0, 0, 0))
                    self.__pixels.show()
                time.sleep(0.5)
