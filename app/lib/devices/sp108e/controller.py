from .constants import Effect, PresetEffect, ColorOrder, Command, CommandFlag, StatePosition, ChipType, CUSTOM_EFFECTS_OFFSET
from lib.threading import Thread
from lib.utils import clamp
import asyncore
import socket
import time
import traceback


class State:
    def __init__(self):
        self.is_on = None
        self.chip_type = None
        self.leds_per_segment = None
        self.segments = None
        self.color = None
        self.color_order = None
        self.brightness = None
        self.preset = None
        self.speed = None
        self.recorded_presets = None
        self.white_channel_brightness = None
        self.last_sync = None

    def __repr__(self):
        return f'{vars(self)}'

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)

    def update_from_sync(self, sync_data):
        # [  0,   1,   2,   3,   4,      5,     6,     7,     8,     9,    10,    11,    12,    13,    14,    15,    16]
        # [0:2, 2:4, 4:6, 6:8, 8:10, 10:12, 12:14, 14:16, 16:18, 18:20, 20:22, 22:24, 24:26, 26:28, 28:30, 30:32, 32:34]
        # [ 56,   1, 219, 211,  255,     2,     0,   142,     0,     1,   255,   255,   255,     3,     1,   254,   131]
        self.is_on = sync_data[StatePosition.IS_ON] == 1
        self.chip_type = ChipType.cast(sync_data[StatePosition.CHIP_TYPE])
        self.leds_per_segment = (sync_data[StatePosition.LEDS_PER_SEGMENT_A] * 256) + \
            sync_data[StatePosition.LEDS_PER_SEGMENT_B]
        self.segments = (sync_data[StatePosition.SEGMENTS_A] * 256) + \
            sync_data[StatePosition.SEGMENTS_B]
        self.color_order = ColorOrder.cast(
            sync_data[StatePosition.COLOR_ORDER])
        self.color = (
            sync_data[StatePosition.COLOR_R],
            sync_data[StatePosition.COLOR_G],
            sync_data[StatePosition.COLOR_B]
        )
        self.preset = Effect.get_effect(sync_data[StatePosition.MODE])
        self.speed = sync_data[StatePosition.SPEED]
        self.brightness = sync_data[StatePosition.BRIGHTNESS]
        self.recorded_presets = sync_data[StatePosition.RECORDED_PRESETS]
        self.white_channel_brightness = sync_data[StatePosition.WHITE_CHANNEL_BRIGHTNESS]
        self.last_sync = round(time.time() * 100000)


class SP108E_Controller:
    """
    A Wifi LED Shop Light
    """

    def __init__(self, host, port=8189, timeout=5):
        """
        Creates a new Wifi LED Shop light

        :param host: The IP of the controller on the network (STA Mode, not AP mode).
        :param port: The port the controller should listen on. It should almost always be left as the default.
        :param timeout: The timeout in seconds to wait listening to the socket.
        :param retries: The number of times to retry sending a command if it fails or times out before giving up.
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.state = State()
        self.connected = False
        self.__socket = None
        self.sync_state()
        self.__log(f'Detected {self}')

    def reconnect(self):
        """
        Try to (re-)connect to the controller via a socket
        """
        self.connected = False

        attempts = 0
        while not self.connected:
            try:
                if self.__socket:
                    self.close()
            except:
                pass

            try:
                self.__socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                self.__socket.settimeout(self.timeout)
                self.__socket.connect((self.host, self.port))
                self.connected = True
                return
            except:
                self.__err()
                self.connected = False
                attempts += 1
                pass

            time.sleep(0.5)

    def close(self):
        """
        Closes the socket connection to the light
        """
        try:
            self.__socket.close()
        except:
            pass
        self.__socket = None

    def set_color(self, r=0, g=0, b=0):
        """
        Sets the color of the light (rgb each 0 to 255)
        """
        color = (clamp(r), clamp(g), clamp(b))
        if self.state.color != color:
            self.send_command(Command.SET_COLOR, [int(r), int(g), int(b)])
            self.__log('Color setted to %s' % str((r, g, b)))
            self.state.color = (r, g, b)

    def set_brightness(self, brightness=0):
        """
        Sets the brightness of the light

        :param brightness: An int describing the brightness (0 to 255, where 255 is the brightest)
        """
        brightness = clamp(brightness)
        if self.state.brightness != brightness:
            self.send_command(Command.SET_BRIGHTNESS, [int(brightness)])
            self.__log('Brightness setted to %d' % brightness)
            self.state.brightness = brightness

    def set_speed(self, speed=0):
        """
        Sets the speed of the preset. Not all effects use the speed, but it can be safely set regardless

        :param speed: An int describing the speed an preset will play at. (0 to 255, where 255 is the fastest)
        """
        speed = clamp(speed)
        if self.state.speed != speed:
            self.send_command(Command.SET_SPEED, [int(speed)])
            self.__log('Speed setted to %d' % speed)
            self.state.speed = speed

    def set_preset(self, preset: int = PresetEffect.RAINBOW):
        """
        Sets the light preset to the provided built-in preset number

        :param preset: The preset to use. Valid values are 0 to 255. See the MonoEffect enum, or MONO_EFFECTS and PRESET_EFFECTS for mapping.
        """
        if self.state.preset != preset:
            try:
                preset_value = preset
                preset_cmd = Effect.get_command(preset)
                if preset_cmd is Command.SET_CUSTOM:
                    preset_value -= CUSTOM_EFFECTS_OFFSET
                self.send_command(preset_cmd, [preset_value])
                self.__log('Preset setted to %s' % Effect.get_effect(preset))
                self.state.mode == int(preset)
                self.state.preset == preset
            except:
                self.__err()
                pass

    def toggle(self):
        """
        Toggles the state of the light without checking the current state
        """
        self.send_command(Command.TOGGLE)
        self.state.is_on = not self.state.is_on

    def turn_on(self):
        """
        Toggles the light on only if it is not already on
        """
        if not self.state.is_on:
            self.toggle()
            self.__log('Turned on')

    def turn_off(self):
        """
        Toggles the light off only if it is not already off
        """
        if self.state.is_on:
            self.toggle()
            self.__log('Turned off')

    def set_segments(self, segments: int):
        """
        Sets the total number of segments. Total lights is segments * leds_per_segment.

        :param segments: The number of segments
        """
        if self.state.segments != segments:
            self.send_command(Command.SET_SEGMENT_COUNT, [segments])
            self.__log(f'Segments setted to {segments}')
            self.state.segments = segments

    def set_leds_per_segment(self, leds_per_segment: int):
        """
        Sets the number of lights per segment. Total lights is segments * leds_per_segment.

        :param leds_per_segment: The number of lights per segment
        """
        if self.state.leds_per_segment != leds_per_segment:
            leds_per_segment_data = list(
                leds_per_segment.to_bytes(2, byteorder='little'))
            self.send_command(Command.SET_LIGHTS_PER_SEGMENT,
                            leds_per_segment_data)
            self.__log(f'Leds per segment setted to {leds_per_segment}')
            self.state.leds_per_segment = leds_per_segment

    def set_calculated_segments(self, total_lights, segments):
        """
        Helper function to automatically set the number of segments and lights per segment
        to reach the target total lights (rounded down to never exceed total_lights)

        Usually you know the total number of lights you have available on a light strip
        and want to split it into segments that take up the whole strip

        :param total_lights: The target total number of lights to use
        :param segments: The number of segments to split the total into
        """
        self.set_segments(segments)
        self.set_leds_per_segment(int(total_lights / segments))

    def send_command(self, command, data=[], expect_response: bool = False):
        """
        Helper method to send a command to the controller.
        Mostly for internal use, prefer the specific functions where possible.

        Formats the low level message details like Start/End flag, binary data, and command
        :param command: The command to send to the controller. See the Command enum for valid commands.
        """
        min_data_len = 3
        padded_data = data + [0] * (min_data_len - len(data))
        raw_data = [CommandFlag.START, *padded_data, command, CommandFlag.END]
        return self.__send_bytes(raw_data, expect_response=expect_response)

    def __send_bytes(self, data, expect_response: bool = False):
        """
        Helper method to send raw bytes directly to the controller
        Mostly for internal use, prefer the specific functions where possible
        """
        raw_data = bytes(data)

        attempts = 0
        while attempts < self.timeout:
            try:
                if self.__socket is None:
                    self.reconnect()

                self.__socket.sendall(raw_data)
                time.sleep(0.1)
                if expect_response:
                    return self.__socket.recv(17)
                else:
                    return
            except (socket.timeout, BrokenPipeError):
                attempts += 1
                self.__log('Connection lost. Reconnecting...')
                self.reconnect()
                pass
            except:
                self.__err()
                attempts += 1
                pass

    def sync_state(self):
        """
        Syncs the state of the controller with the state of this object
        """
        try:
            self.state.last_sync = None

            attempts = 0
            while self.state.last_sync is None and attempts <= self.timeout:
                try:
                    # Send the request for sync data
                    response = self.send_command(
                        Command.SYNC, expect_response=True)

                    # Extract the state data
                    state = bytearray(response)
                    self.state.update_from_sync(state)
                    return True
                except (socket.timeout, BrokenPipeError):
                    attempts += 1
                    self.reconnect()
                    pass
                except IndexError:
                    attempts += 1
                    pass
                except:
                    self.__err()
                    attempts += 1
                    pass

                self.state.last_sync = None
                time.sleep(0.1)

            raise Exception('State sync failed')
        except:
            self.__err()
            return False

    def __repr__(self):
        return f'{self.__class__.__name__}<{self.host}:{self.port}>' + '{' + \
            f'timeout: {self.timeout}, ' + \
            f'state: {self.state}, ' + \
            f'connected: {self.connected}' + \
            '}'

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)

    def __err(self):
        self.__log(f'\n{traceback.format_exc()}')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
