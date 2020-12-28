#!/usr/bin/env python3
import socket, binascii, pythonping, threading, time
from datetime import datetime, timedelta
from sys import argv
from lib.utils import turn_on_condition

class SP108E:
    MONO_ANIMATIONS = {
        "meteor" : "cd",
        "breathing" : "ce",
        "wave" : "d1",
        "catch up" : "d4",
        "static" : "d3",
        "stack" : "cf",
        "flash" : "d2",
        "flow" : "d0"
    }
    CHIP_TYPES = {
        "SM16703": "00",
        "TM1804": "01",
        "UCS1903": "02",
        "WS2811": "03",
        "WS2801": "04",
        "SK6812": "05",
        "LPD6803": "06",
        "LPD8806": "07",
        "APA102": "08",
        "APA105": "09",
        "DMX512": "0a",
        "TM1914": "0b",
        "TM1913": "0c",
        "P9813": "0d",
        "INK1003": "0e",
        "P943S": "0f",
        "P9411": "10",
        "P9413": "11",
        "TX1812": "12",
        "TX1813": "13",
        "GS8206": "14",
        "GS8208": "15",
        "SK9822": "16",
        "TM1814": "17",
        "SK6812_RGBW": "18",
        "P9414": "19",
        "P9412": "1a"
    }
    COLOR_ORDERS = {
        "RGB": "00",
        "RBG": "01",
        "GRB": "02",
        "GBR": "03",
        "BRG": "04",
        "BGR": "05"
    }
    def __init__(self, ip=None, port=8189):
        self.ip = ip
        self.port = port

    def get_chip_type(self, x):
        return [k for k, v in self.CHIP_TYPES.items() if v == x][0]

    def get_color_order(self, x):
        return [k for k, v in self.COLOR_ORDERS.items() if v == x][0]

    def get_animation(self, x):
        try:
            animation = [k for k, v in self.MONO_ANIMATIONS.items() if v == x][0]
            return animation
        except IndexError:
            return x

    def __dec_to_even_hex(decimal: int, output_bytes: int=None):
        hex_length = len(hex(decimal)) - 2
        out_length = hex_length + (hex_length % 2)
        if output_bytes:
            out_length = output_bytes * 2
        return f"{decimal:0{out_length}x}"

    def transmit_data(
        self,
        data: str, # the command and it's value(if it has a value)
        expect_response: bool, # set to true if you expect a response
        response_length: int # how long the response is
    ):
        s = socket.create_connection((self.ip, self.port))
        cleaned_data = data.replace(" ", "")
        s.send(binascii.unhexlify(cleaned_data))
        if expect_response:
            return s.recv(response_length)

    def is_device_ready(self):
        return self.transmit_data("38 000000 2f 83", True, 1)

    def send_data(self, data: str, expect_response: bool=False, response_length: int=0):
        response = self.transmit_data(data, expect_response, response_length)
        return response

    def change_color(self, color: str):
        # color in hex format
        color = color.replace("#", "")
        self.send_data(f"38 {color} 22 83")

    def change_speed(self, speed: int):
        if not 0 <= speed <= 255:
            raise ValueError("speed must be between 0 and 255")
        self.send_data(f"38 {speed} ")

    def change_brightness(self, brightness: int):
        if not 0 <= brightness <= 255:
            raise ValueError("brightness must be between 0 and 255")
        self.send_data(f"38 {self.__dec_to_even_hex(brightness)} 0000 2a 83")

    def get_name(self):
        result = self.send_data("38 000000 77 83", True, 18);
        return result

    def get_device_raw_settings(self):
        result = self.send_data("38 000000 10 83", True, 17);
        return binascii.hexlify(result).decode("ascii")

    def get_device_settings(self):
        raw_settings = self.get_device_raw_settings()
        current_animation = self.get_animation(raw_settings[4:6])
        chip_type = self.get_chip_type(raw_settings[26:28])
        color_order = self.get_color_order(raw_settings[10:12])
        turned_on = int(raw_settings[2:4], 16)
        current_color = raw_settings[20:26].upper()
        settings = {
            "turned_on": turned_on == 1,
            "current_animation": current_animation,
            "animation_speed": int(raw_settings[6:8], 16),
            "current_brightness": int(raw_settings[8:10], 16),
            "color_order": color_order,
            "leds_per_segment": int(raw_settings[12:16], 16),
            "segments": int(raw_settings[16:20], 16),
            "current_color": current_color,
            "chip_type": chip_type,
            "recorded_patterns": int(raw_settings[28:30], 16),
            "white_channel_brightness": int(raw_settings[30:32], 16)
        }
        return settings

    def change_mono_color_animation(self, index):
        # 	 Mono animations
        # 		0xcd => Meteor
        # 		0xce => Breathing
        # 		0xd1 => Wave
        # 		0xd4 => Catch up
        # 		0xd3 => Static
        # 		0xcf => Stack
        # 		0xd2 => Flash
        # 		0xd0 => Flow

        self.send_data(f"38 {index} 0000 2c 83")

    def change_mixed_colors_animation(self, index):
        # 0x00 (first animation 1) -> 0xb3 (last animation 180)
        self.send_data(f"38 {self.__dec_to_even_hex(index - 1)} 0000 2c 83") # specific animation

    def enable_multicolor_animation_auto_mode(self):
        self.send_data("38 000000 06 83") #auto mode

    def toggle_off_on(self):
        self.send_data("38 000000 aa 83")

    def change_white_channel_brightness(self, brightness=255):
        if not 0 <= brightness <= 255:
            raise ValueError("brightness must be between 0 and 255")
        self.send_data(f"38  {self.__dec_to_even_hex(brightness)}0000 08 83")

    def set_number_of_segments(self, segments: int=1):
        self.send_data(f"38 {self.__dec_to_even_hex(segments, 2)} 00 2e 83")

    def set_number_of_leds_per_segment(self, leds: int=50):
        self.send_data(f"38 {self.__dec_to_even_hex(leds, 2)} 00 2d 83")

CONTROLLER_IP = "192.168.1.203"
CONTROLLER_PORT = 8189
TERMINATE = False
IS_ALIVE = False
LAST_PING = False
START_AT = '18:00:00'
END_AT = '06:00:00'
DATE_FMT = '%Y/%m/%d '
TIME_FMT = '%H:%M:%S'
MAIN_HOST="192.168.1.13"

def is_alive():
    global IS_ALIVE
    global LAST_PING
    global MAIN_HOST
    while True:
        global TERMINATE
        if TERMINATE:
            LAST_PING = False
            IS_ALIVE = False
            break
        PING_RESULT = pythonping.ping(MAIN_HOST, timeout=1, count=1).success()
        if PING_RESULT:
            IS_ALIVE = PING_RESULT
        else:
            if not LAST_PING:
                IS_ALIVE = PING_RESULT
            else:
                IS_ALIVE = LAST_PING
                LAST_PING = PING_RESULT

        time.sleep(5)

def shutdown():
    global TERMINATE
    global IS_ALIVE
    global LAST_PING
    TERMINATE = True
    IS_ALIVE = False
    LAST_PING = False

alive_thread = threading.Thread(target=is_alive)
alive_thread.start()

if __name__ == '__main__':

    controller = SP108E(ip=CONTROLLER_IP, port=CONTROLLER_PORT)
    try:
        while True:
            if controller.is_device_ready():
                break
            time.sleep(0.5)
        if len(argv) > 1 and argv[1] == '--off':
            shutdown()
            while True:
                STATE = controller.get_device_settings()
                if STATE["turned_on"]:
                    controller.toggle_off_on()
                else:
                    break
                time.sleep(1)
        else:
            print("Should turn on at: " + START_AT)
            print("Should turn off at: " + END_AT)
            while True:
                STATE = controller.get_device_settings()
                LIGHT_ON = turn_on_condition(START_AT, END_AT, DATE_FMT, TIME_FMT) and IS_ALIVE
                if LIGHT_ON:
                    if not STATE["turned_on"]:
                        controller.toggle_off_on()
                else:
                    if STATE["turned_on"]:
                        controller.toggle_off_on()
                time.sleep(1)
    except Exception:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        shutdown()
        while True:
            STATE = controller.get_device_settings()
            if STATE["turned_on"]:
                controller.toggle_off_on()
            else:
                break
            time.sleep(1)
