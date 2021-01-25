from paho.mqtt import client as mqtt_client
from rpi_ws281x import PixelStrip, Color
import asyncore
import binascii
import random
import socket
import threading
import time

class LedStrip:
    def __init__(self, name, gpio_pin=None, led_count=None, reverse=None, interval=None, frequency=None):
        self.animation = None
        self.name = name
        self.gpio_pin = int(gpio_pin)
        self.led_count = int(led_count)
        self.frequency = int(self.__default_value(frequency, 800000))
        self.dma = 10
        self.brightness = 30
        self.interval = float(self.__default_value(interval, 0.05))
        self.reverse = self.__default_value(reverse, False)
        self.channel = 1 if gpio_pin in [13, 19, 41, 45, 53] else 0
        self.thread = None
        self.thread_active = False
        self.led_strip = PixelStrip(
            self.led_count, self.gpio_pin, self.frequency, self.dma, False, self.brightness, self.channel)

    def set_animation(self, animation_fn):
        self.animation = self.__default_value(animation_fn, self.__lambda)

    def set_pixel_color(self, i, color):
        try:
            self.led_strip.setPixelColor(i, color)
        except:
            pass

    def show(self):
        try:
            self.led_strip.show()
            True
        except:
            pass

    def begin(self):
        try:
            self.led_strip.begin()
            True
        except:
            error_output = "\n\n\t" + format_exc().replace("\n", "\n\t")
            self.log("\n\t" + error_output + "\n", "error")
            pass

    def __lambda(self, instance):
        while True:
            if not instance.thread_active:
                break
            sleep(instance.interval)

    def __default_value(self, value, default=None):
        return default if value is None else value

    def start(self):
        if self.animation is not None:
            self.thread_active = True
            self.thread = Thread(target=self.animation,
                                 daemon=True, args=[self])
            self.log("Starting thread")
            self.thread.start()

    def stop(self):
        self.thread_active = False
        if self.thread is not None:
            self.log("Stopping thread")
            while self.thread.is_alive():
                sleep(0.01)

        try:
            for i in range(0, self.led_count):
                self.set_pixel_color(i, Color(0, 0, 0))
            self.show()
        except:
            pass

        self.thread = None
        self.changed = False
        self.log("Shutted down")

    def log(self, message, level="debug"):
        print(str('[{:^7}]'.format(level.upper())) +
              ' {' + str(self.name) + "}: " + str(message))

    def __repr__(self):
        return self.__class__.__name__ + str(vars(self))


class Sonoff:
    def __init__(self, broker="localhost", port=1883, device=None):
        self.broker = broker
        self.port = port
        self.device = device
        self.connected = False
        self.initialized = False
        self.on = False
        self.client_id = f'rpi-{random.randint(1000000, 9999999)}'
        self.client = None
        self.__connect()

    def __log(self, a):
        print(self.__class__.__name__, a, sep=' => ')

    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.__log(f'Connected to {self.broker}:{self.port}')
            self.connected = True
            self.__log('Getting initial state...')
            self.client.subscribe(f'stat/{self.device}/POWER')
            self.__publish(f'cmnd/{self.device}/Power')
        else:
            self.connected = False

    def __on_message(self, client, userdata, message):
        status = str(message.payload.decode("utf-8"))
        if not self.initialized:
            self.__log(f'Initial status: {status}')
            self.initialized = True
        self.on = status == "ON"

    def __on_disconnect(self, client, userdata, rc):
        self.connected = False
        self.__log('Disconnected. Reconnecting...')
        try:
            self.client.loop_stop()
        except:
            pass
        self.__connect()

    def __connect(self):
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
                time.sleep(0.1)

    def turn_off(self):
        if self.on:
            self.__log(f'Turning off {self}')
            while self.on:
                self.__publish(f'cmnd/{self.device}/Power', 0)
                time.sleep(0.1)

    def toggle_off_on(self):
        self.__publish(f'cmnd/{self.device}/Power', 'TOGGLE')
