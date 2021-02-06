from lib.animations import NewKITT, RainbowCycle, shutdown as shutdownPixels
from lib.network_scanner import NetworkScanner
from lib.threading import Thread
from lib.utils import evaluate_day_night
from paho.mqtt import client as mqtt_client
from rpi_ws281x import PixelStrip, Color
from subprocess import Popen as call_process, DEVNULL
import asyncore
import binascii
import random
import socket
import time
import traceback

hardware_available = False
try:
    import board
    import neopixel
    hardware_available = True
except:
    import lib.neopixel.board as board
    import lib.neopixel.neopixel as neopixel
    pass


class Fan:
    def __init__(self, led_count=None, pixel_order=None, ips=None, start_at=None, end_at=None, date_fmt=None, time_fmt=None, quiet=False):
        global hardware_available
        self.on = False
        self.gpio_pin = board.D18
        self.led_count = int(led_count)
        self.__start_at = start_at
        self.__end_at = end_at
        self.__date_fmt = date_fmt
        self.__time_fmt = time_fmt
        self.__simulate = not hardware_available
        self.__quiet = quiet
        self.__ips = ips
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
                        self.gpio_pin, self.led_count, brightness=1.0, auto_write=False, pixel_order=self.__pixel_order, simulate=not self.__quiet)
                else:
                    placeholder = neopixel.NeoPixel(
                        self.gpio_pin, self.led_count, brightness=1.0, auto_write=False, pixel_order=self.__pixel_order)
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
                shutdownPixels(self.__pixels)
                self.__pixels.deinit()
                self.__pixels = None
            except Exception as e:
                self.__log(e)
                pass
            time.sleep(0.1)

        if self.__scanner is not None:
            self.__scanner.stop()
            self.__scanner = None

    def turn_screen(self, on):
        try:
            call_process(['/usr/bin/vcgencmd', 'display_power',
                          str(1 if on else 0)], shell=False, stdout=DEVNULL)
        except:
            pass

    def __animate(self):
        while True:
            if not self.on:
                break

            alive = any(
                map(lambda ip: self.__scanner.is_alive(ip), self.__ips))
            self.turn_screen(alive)

            if alive:
                if self.__pixels is not None:
                    if evaluate_day_night(self.__start_at, self.__end_at, self.__date_fmt, self.__time_fmt):
                        RainbowCycle(self.__pixels, 0.001, 1)
                    else:
                        NewKITT(self.__pixels, 255, 0, 0, 1, 0.075, 0, 1)
            else:
                if self.__pixels is not None:
                    self.__pixels.fill((0, 0, 0))
                    self.__pixels.show()
                time.sleep(0.5)


class Sonoff:
    def __init__(self, broker="localhost", port=1883, device=None):
        self.broker = broker
        self.port = port
        self.device = device
        self.connected = False
        self.log_initial_status = True
        self.on = False
        self.client_id = f'rpi_{random.randint(1000000, 9999999)}'
        self.client = None
        self.__connect()

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)

    def __on_connect(self, client, userdata, flags, rc):
        self.__log((client, userdata, flags, rc))
        if rc == 0:
            self.connected = True
            self.__log(f'Connected to {self.broker}:{self.port}')
            self.client.subscribe(f'stat/{self.device}/POWER')
            self.__publish(f'cmnd/{self.device}/Power')
        else:
            self.connected = False

    def __on_message(self, client, userdata, message):
        status = str(message.payload.decode("utf-8"))
        if self.log_initial_status:
            self.__log(f'Initial status: {status}')
            self.log_initial_status = False
        self.on = status == "ON"

    def __on_disconnect(self, client, userdata, rc):
        self.__log('Disconnected. Reconnecting...')
        self.connected = False
        try:
            self.client.loop_stop()
        except:
            pass
        self.client = None
        self.__connect()

    def __connect(self):
        self.log_initial_status = True
        self.client = mqtt_client.Client(self.client_id)
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        self.client.on_disconnect = self.__on_disconnect
        self.client.connect_async(self.broker, self.port)
        self.client.loop_start()

    def __publish(self, topic, message=None):
        if self.connected:
            result = self.client.publish(topic, message)
            if result[0] == 0:
                return True

        self.__log(
            f"Failed to send message `{message}` to topic {topic}: {result}")
        return False

    def __repr__(self):
        return f'{self.__class__.__name__}@<broker: {self.broker}, port: {self.port}, device: {self.device}, connected: {self.connected}, on: {self.on}>'

    def turn_on(self):
        if not self.on:
            self.__log(f'Turning on {self}')
            while not self.on:
                self.__publish(f'cmnd/{self.device}/Power', 1)
                time.sleep(1)

    def turn_off(self):
        if self.on:
            self.__log(f'Turning off {self}')
            while self.on:
                self.__publish(f'cmnd/{self.device}/Power', 0)
                time.sleep(1)

    def toggle_off_on(self):
        # self.__publish(f'cmnd/{self.device}/Power', 'TOGGLE')
        if self.on:
            self.turn_off()
        else:
            self.turn_on()
