import os
import sys
import traceback
from time import sleep
from config import MAIN_HOST, SWITCH_HOST, MQTT_BROKER_HOST, START_AT, END_AT, DATE_FMT, TIME_FMT
from lib.devices.sonoff import Sonoff as Switch
from lib.network_scanner import NetworkScanner
from lib.devices.sp108e import SP108E_Controller as LedController, MonoEffect, PresetEffect, CustomEffect
from lib.utils import evaluate_day_night
from optparse import OptionParser


class SceneControlService:
    def __init__(self, quiet=False):
        self.main_host = MAIN_HOST
        self.switch_host = SWITCH_HOST
        self.mqtt_broker_host = MQTT_BROKER_HOST

        self.__log(f'Main Host:        {self.main_host}')
        self.__log(f'Switch Host:      {self.switch_host}')
        self.__log(f'MQTT Broker Host: {self.mqtt_broker_host}')

        self.__scanner = NetworkScanner(ips=[
            self.main_host,
            self.switch_host,
            self.mqtt_broker_host,
        ])

        self.running = False
        self.switch = None

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)

    def __is_night(self):
        return evaluate_day_night(START_AT, END_AT, DATE_FMT, TIME_FMT)

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
                while attempts < 10:
                    print(self.switch, flush=True)
                    if self.switch.connected:
                        return True
                    attempts += 1
                    sleep(1)

        self.__log(f'Switch could not be found in {self.switch_host}')
        self.switch = None
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
            main.stop()
    except KeyboardInterrupt:
        main.stop()
        pass
    except:
        traceback.print_exc()
        pass
