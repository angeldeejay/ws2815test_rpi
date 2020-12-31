import time
from lib.devices import Sonoff
from lib.network_scanner import NetworkScanner

scanner = NetworkScanner()


def wait_host(ip):
    global scanner
    while True:
        if scanner.is_alive(ip):
            break
        time.sleep(1)


main_host = "192.168.1.13"
controller_host = "192.168.1.203"
sonoff_host = "192.168.1.151"
sonoff_broker = "192.168.1.20"

is_alive = False
last_ping = False
start_at = '17:30:00'
end_at = '06:30:00'
date_fmt = '%Y/%m/%d '
time_fmt = '%H:%M:%S'

print(
    __name__, f'Detecting Broker in {sonoff_broker}...', sep=' => ')
wait_host(sonoff_broker)
print(__name__, f'Broker detected!', sep=' => ')
print(
    __name__, f'Detecting Sonoff in {sonoff_host}...', sep=' => ')
wait_host(sonoff_host)
print(__name__, f'Sonoff detected!', sep=' => ')

sonoff = Sonoff(broker=sonoff_broker, device="desktop")
controller = None


def shutdown():
    global controller
    global scanner
    global sonoff
    print(__name__, '\nExiting...', sep=' => ')
    scanner.stop()
    if sonoff is not None and sonoff.connected:
        if controller is None:
            wait_host(controller_host)
            controller = WifiLedShopLight(controller_host)
            controller.sync_status()

        controller.turn_off()
        controller.close()

        if sonoff.on:
            while sonoff.on:
                sonoff.turn_off()
                time.sleep(1)


if __name__ == '__main__':
    import time
    from lib.utils import evaluate_day_night
    from lib.pyledshop import WifiLedShopLight
    from sys import argv

    try:
        if len(argv) > 1 and argv[1] == '--off':
            shutdown()
        else:
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
                            print(__name__, f'Detecting controller in {controller_host}...',
                                  sep=' => ')
                            wait_host(controller_host)
                            print(__name__, 'Controller detected!',
                                  sep=' => ')
                            controller = WifiLedShopLight(controller_host)
                            controller.sync_state()
                            controller.set_segments(1)
                            controller.set_lights_per_segment(144)

                        if evaluate_day_night(start_at, end_at, date_fmt, time_fmt):
                            if controller.state.mode != 0:
                                print(__name__, 'Activating night mode!',
                                      sep=' => ')
                                controller.set_preset(0)
                        else:
                            if controller.state.mode != 219:
                                print(__name__, 'Activating day mode!',
                                      sep=' => ')
                                controller.set_custom(1)

                        controller.turn_on()

                    else:
                        while sonoff.on:
                            sonoff.turn_off()
                            time.sleep(1)
                else:
                    if controller is not None:
                        try:
                            controller.close()
                        except:
                            pass
                        controller = None

                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        shutdown()
        pass
