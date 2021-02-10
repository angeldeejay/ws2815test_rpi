import os
import sys
import traceback
from time import sleep
from lib.devices.sonoff import Sonoff as Switch
from lib.network_scanner import NetworkScanner
from lib.devices.sp108e import SP108E_Controller as LedController, MonoEffect, PresetEffect, CustomEffect
from lib.utils import evaluate_day_night
from optparse import OptionParser


class SceneControlService:
    def __init__(self, quiet=False):
        self.main_host = "192.168.1.13"
        self.switch_host = "192.168.1.153"
        self.controller_host = "192.168.1.203"
        self.mqtt_broker_host = "127.0.0.1"

        self.__log(f'Main Host:        {self.main_host}')
        self.__log(f'Switch Host:      {self.switch_host}')
        self.__log(f'MQTT Broker Host: {self.mqtt_broker_host}')
        self.__log(f'Controller Host:  {self.controller_host}')

        self.__scanner = NetworkScanner(ips=[
            self.main_host,
            self.switch_host,
            self.mqtt_broker_host,
            self.controller_host,
        ])

        self.__start_at = '17:55:00'
        self.__end_at = '23:30:00'
        self.__date_fmt = '%Y/%m/%d '
        self.__time_fmt = '%H:%M:%S'
        self.running = False

        self.switch = None
        self.controller = None

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)

    def __is_night(self):
        return evaluate_day_night(self.__start_at, self.__end_at, self.__date_fmt, self.__time_fmt)

    def stop(self):
        print('', flush=True)
        self.__log('Exiting...')
        self.running = False

        self.__log("Turning off switch")
        try:
            if self.wait_switch() and self.switch.on:
                self.switch.turn_off()
        except:
            pass

        self.__scanner.stop()

    def wait_broker(self):
        if not self.__scanner.wait_host(self.mqtt_broker_host):
            self.__log(
                'MQTT broker could not be found in {self.mqtt_broker_host}...')
            self.switch = None
            return False
        return True

    def wait_switch(self):
        # MQTT broker available
        if self.wait_broker():
            # Detecting switch
            if self.switch is None:
                self.__log(f'Detecting switch in {self.switch_host}...')
                if self.__scanner.wait_host(self.switch_host):
                    self.switch = Switch(
                        broker=self.mqtt_broker_host, device="desktop")

            # Connecting switch
            if self.switch is not None:
                attempts = 0
                while attempts < 5:
                    if self.switch.connected:
                        return True
                    attempts += 1
                    sleep(1)

        self.__log(f'Switch could not be found in {self.switch_host}')
        self.switch = None
        return False

    def wait_controller(self):
        # Controller available
        if self.wait_switch():
            # Detecting controller
            if self.controller is None:
                self.__log(
                    f'Detecting Led controller in {self.controller_host}...')
                if self.__scanner.wait_host(self.controller_host):
                    self.controller = LedController(self.controller_host)
                    self.controller.set_calculated_segments(142, 1)
            
            if self.controller is not None:
                if self.controller.sync_state():
                    # Connecting controller
                    attempts = 0
                    while attempts < self.controller.timeout:
                        if self.controller.connected:
                            return True
                        attempts += 1
                        sleep(1)

        self.controller = None
        self.__log(
            f'Led controller could not be found in {self.controller_host}')
        return False

    def run(self):
        self.running = True
        while True:
            # Manual control
            if self.running == False:
                return

            night_mode = self.__is_night()
            alive = self.__scanner.is_alive(self.main_host)

            if self.wait_switch():
                if alive:
                    if not self.switch.on:
                        self.__log("Turning on switch")
                    self.switch.turn_on()
                    if self.wait_controller():
                        # Setting animation
                        if night_mode:
                            preset = PresetEffect.RAINBOW
                        else:
                            preset = CustomEffect.CUSTOM_1

                        if self.controller.state.preset != preset:
                            self.controller.set_preset(preset)

                        if not self.controller.state.is_on:
                            self.controller.turn_on()
                        
                        self.controller.set_brightness(255)
                else:
                    if self.switch.on:
                        self.__log("Turning off switch")
                    self.switch.turn_off()
            sleep(1)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--off", action="store_true",
                      dest="terminate", default=False)
    parser.add_option("-q", "--quiet", action="store_true",
                      dest="quiet", default=False)
    (options, _) = parser.parse_args()

    main = SceneControlService(quiet=options.quiet)
    try:
        if options.terminate == False:
            main.run()
        else:
            raise Exception()
    except:
        traceback.print_exc()
        pass
    finally:
        main.stop()
        pass
