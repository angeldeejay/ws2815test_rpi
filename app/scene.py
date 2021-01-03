import time
from lib.utils import evaluate_day_night
from lib.pyledshop import WifiLedShopLight
from lib.devices import Sonoff
from lib.network_scanner import NetworkScanner
from sys import argv

scanner = NetworkScanner()

main_host = "192.168.1.13"
controller_host = "192.168.1.203"
sonoff_host = "192.168.1.153"
sonoff_broker = "192.168.1.20"

def log(e):
    print(__name__, e)

is_alive = False
last_ping = False
start_at = '17:30:00'
end_at = '06:30:00'
date_fmt = '%Y/%m/%d '
time_fmt = '%H:%M:%S'

log(f'Detecting Broker in {sonoff_broker}...')
scanner.wait_host(sonoff_broker)
log(f'Broker detected!')
log(f'Detecting Sonoff in {sonoff_host}...')
scanner.wait_host(sonoff_host)
log(f'Sonoff detected!')

sonoff = Sonoff(broker=sonoff_broker, device="desktop")
controller = None


def shutdown():
    global controller
    global scanner
    global sonoff
    print(f'\n{__name__}', 'Exiting...')
    attempts = 0
    while not sonoff.connected:
        if attempts < 10:
            attempts += 1
            time.sleep(1)

    if sonoff.connected:
        if sonoff.on:
            if controller is None:
                print(
                    __name__, f'Detecting controller in {controller_host}...')
                if scanner.wait_host(controller_host):
                    log(f'Controller detected!')
                    controller = WifiLedShopLight(controller_host)
                    controller.sync_state()

            if controller is not None:
                if controller.state.is_on:
                    controller.turn_off()

            attempts = 0
            sonoff.turn_off()

    scanner.stop()
    time.sleep(1)


if len(argv) > 1 and argv[1] == '--off':
    shutdown()
else:
    try:
        while True:
            preset = None
            speed = None

            if sonoff.connected:
                if scanner.is_alive(main_host):
                    if not sonoff.on:
                        if controller is not None:
                            try:
                                controller.close()
                            except:
                                pass
                        controller = None
                        sonoff.turn_on()

                    if controller is None:
                        log(f'Detecting controller in {controller_host}...')
                        scanner.wait_host(controller_host)
                        log('Controller detected!')
                        controller = WifiLedShopLight(controller_host)
                        controller.sync_state()
                        controller.set_segments(1)
                        controller.set_lights_per_segment(144)

                    if evaluate_day_night(start_at, end_at, date_fmt, time_fmt):
                        if controller.state.mode != 0:
                            log('Activating night mode!')
                            controller.set_preset(0)
                    else:
                        if controller.state.mode != 219:
                            log('Activating day mode!')
                            controller.set_custom(1)

                    controller.turn_on()

                else:
                    sonoff.turn_off()
            else:
                if controller is not None:
                    try:
                        controller.close()
                    except:
                        pass
                    controller = None

            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        shutdown()
        pass
