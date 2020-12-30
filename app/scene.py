from lib.devices import Sonoff
from lib.pyledshop import *

main_host = "192.168.1.13"
controller_host = "192.168.1.203"

is_alive = False
last_ping = False
start_at = '17:30:00'
end_at = '06:30:00'
date_fmt = '%Y/%m/%d '
time_fmt = '%H:%M:%S'

desktop_lights = Sonoff(broker="192.168.1.20", device="desktop")
controller = None


def shutdown():
    if desktop_lights.connected:
        while desktop_lights.on:
            desktop_lights.turn_off()
            time.sleep(2)


if __name__ == '__main__':
    import time
    import pythonping
    from lib.utils import turn_on_condition
    from sys import argv

    try:
        if len(argv) > 1 and argv[1] == '--off':
            shutdown()
        else:
            while True:
                ping_result = pythonping.ping(
                    main_host, timeout=1.5, count=1).success()
                if ping_result:
                    is_alive = ping_result
                    last_ping = ping_result
                else:
                    if not last_ping:
                        is_alive = ping_result
                    else:
                        is_alive = last_ping
                    last_ping = ping_result

                # is_alive = turn_on_condition(start_at, end_at, date_fmt, time_fmt) and is_alive
                preset = None
                speed = None
                if turn_on_condition(start_at, end_at, date_fmt, time_fmt):
                    # Rainbow
                    preset = 0
                    speed = 128
                else:
                    # Meteor
                    speed = 200
                    preset = MonoEffect.METEOR

                if desktop_lights.connected:
                    if is_alive:
                        if not desktop_lights.on:
                            if controller is not None:
                                try:
                                    controller.close()
                                except:
                                    pass
                            controller = None

                        desktop_lights.turn_on()

                        if controller is None:
                            controller = WifiLedShopLight(controller_host)
                            controller.sync_state()
                        controller.set_preset(preset)
                        controller.set_speed(speed)
                    else:
                        try:
                            controller.close()
                        except:
                            pass
                        controller = None
                        desktop_lights.turn_off()

                time.sleep(4)
    except KeyboardInterrupt:
        print("\nExiting...")
        pass
    finally:
        shutdown()
        pass
