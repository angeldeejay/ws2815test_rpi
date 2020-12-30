import random
import time
import socket
import binascii
from paho.mqtt import client as mqtt_client


class Sonoff:
    def __init__(self, broker="localhost", port=1883, device=None):
        self.broker = broker
        self.port = port
        self.device = device
        self.connected = False
        self.on = False
        self.client_id = f'rpi-{random.randint(1000000, 9999999)}'
        self.client = None
        self.__connect()

    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f'Connected to {self.broker}:{self.port}', flush=True)
            self.connected = True
            print('Getting initial state...', flush=True)
            self.client.subscribe(f'stat/{self.device}/POWER')
            self.__publish(f'cmnd/{self.device}/Power')
        else:
            self.connected = False

    def __on_message(self, client, userdata, message):
        status = str(message.payload.decode("utf-8"))
        # print(f'Status: {status}', flush=True)
        self.on = status == "ON"

    def __on_disconnect(self, client, userdata, rc):
        print('Disconnected. Reconnecting...', flush=True)

    def __connect(self, on_connect_lambda=None):
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

            print(
                f"Failed to send message `{message}` to topic {topic}: {result}", flush=True)
        return False

    def __repr__(self):
        return f'{self.__class__.__name__}@<broker: {self.broker}, port: {self.port}, device: {self.device}, connected: {self.connected}, on: {self.on}>'

    def turn_on(self):
        if not self.on:
            print(f"Turning on {self}", flush=True)
            self.__publish(f'cmnd/{self.device}/Power', 1)

    def turn_off(self):
        if self.on:
            print(f"Turning off {self}", flush=True)
            self.__publish(f'cmnd/{self.device}/Power', 0)

    def toggle_off_on(self):
        self.__publish(f'cmnd/{self.device}/Power', 'TOGGLE')