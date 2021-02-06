import os
import traceback
from time import sleep
from lib.animations import NewKITT, RainbowCycle, shutdown as shutdownPixels
from lib.devices import Sonoff as Switch
from lib.network_scanner import NetworkScanner
from lib.pyledshop import WifiLedShopLight as LedController
from lib.utils import evaluate_day_night
from optparse import OptionParser
from subprocess import Popen as call_process, PIPE
from sys import argv


class RootService:
    def __init__(self, quiet=False):
        self.main_host = "192.168.1.13"
        self.controller_host = "192.168.1.203"
        self.switch_host = "192.168.1.153"
        self.mqtt_broker = "192.168.1.20"

        self.__log(f'Main Host:       {self.main_host}')
        self.__log(f'Controller Host: {self.controller_host}')
        self.__log(f'Switch Host:     {self.switch_host}')
        self.__log(f'Switch Broker:   {self.mqtt_broker}')

        self.__scanner = NetworkScanner(ips=[
            self.main_host,
            self.controller_host,
            self.switch_host,
            self.mqtt_broker
        ])

        self.__start_at = '17:30:00'
        self.__end_at = '06:30:00'
        self.__date_fmt = '%Y/%m/%d '
        self.__time_fmt = '%H:%M:%S'
        self.running = False

        self.switch = None
        self.controller = None

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)

    def __is_night(self):
        return evaluate_day_night(self.__start_at, self.__end_at, self.__date_fmt, self.__time_fmt)

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
                        self.controller.set_segments(1)
                        self.controller.set_lights_per_segment(144)

                        if night_mode:
                            if self.controller.state.mode != 0:
                                self.__log('Activating night mode!')
                                self.controller.set_preset(0)
                        else:
                            if self.controller.state.mode != 219:
                                self.__log('Activating day mode!')
                                self.controller.set_custom(1)

                        if not self.controller.state.is_on:
                            self.__log("Turning on controller")
                        self.controller.turn_on()
                else:
                    if self.switch.on:
                        self.__log("Turning off switch")
                    self.switch.turn_off()
            sleep(1)

    def __wait_host(self, ip, timeout=10):
        return self.__scanner.wait_host(ip, timeout)

    def wait_broker(self):
        if not self.__wait_host(self.mqtt_broker):
            self.__log(
                'MQTT broker could not be found in {self.mqtt_broker}...')
            self.controller = None
            self.switch = None
            self.broker = None
            return False
        return True

    def wait_switch(self):
        # MQTT broker available
        if self.wait_broker():
            # Detecting switch
            if self.switch is None:
                self.__log(f'Detecting switch in {self.switch_host}...')
                if self.__wait_host(self.switch_host):
                    self.switch = Switch(
                        broker=self.mqtt_broker, device="desktop")

            # Connecting switch
            attempts = 0
            while attempts < 5:
                if self.switch.connected:
                    return True
                attempts += 1
                sleep(1)

        self.__log('Switch could not be found in {self.switch_host}')
        self.switch = None
        self.broker = None
        return False

    def wait_controller(self):
        # Switch available
        if self.wait_switch():
            if self.controller is not None:
                # Switch and controller available
                return True

            # Detecting controller
            self.__log(f'Detecting controller in {self.controller_host}...')
            if self.__wait_host(self.controller_host):
                self.__log(f'Controller detected!')
                self.controller = LedController(self.controller_host)
                self.controller.sync_state()
                return True

        # Switch not available supposes controller is also unavailable
        self.controller = None
        self.__log('Controller could not be found!')
        return False

    def stop(self):
        print('', flush=True)
        self.__log('Exiting...')
        self.running = False

        self.__log("Turning off controller")
        try:
            if self.wait_controller() and self.controller.state.is_on:
                self.controller.turn_off()
        except:
            pass

        self.__log("Turning off switch")
        try:
            if self.wait_switch() and self.switch.on:
                self.switch.turn_off()
        except:
            pass

        self.__scanner.stop()


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--off", action="store_true",
                      dest="terminate", default=False)
    parser.add_option("-q", "--quiet", action="store_true",
                      dest="quiet", default=False)
    (options, _) = parser.parse_args()

    main = RootService(quiet=options.quiet)
    try:
        if options.terminate == False:
            main.run()
        else:
            raise Exception()
    except:
        pass
    finally:
        main.stop()
        pass
