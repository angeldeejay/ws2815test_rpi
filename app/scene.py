from lib.devices import Sonoff

main_host = "192.168.1.13"
controller_host = "192.168.1.203"

is_alive  = False
last_ping = False
start_at  = '17:30:00'
end_at    = '06:30:00'
date_fmt  = '%Y/%m/%d '
time_fmt  = '%H:%M:%S'

desktop_lights = Sonoff(broker="192.168.1.20", device="desktop")

def shutdown():
    if desktop_lights.connected:
        while desktop_lights.on:
            desktop_lights.turn_off()
            time.sleep(2)

if __name__ == '__main__':
    import time, pythonping
    from lib.utils import turn_on_condition
    from sys import argv

    try:
        if len(argv) > 1 and argv[1] == '--off':
            shutdown()
        else:
            while True:
                ping_result = pythonping.ping(main_host, timeout=1.5, count=1).success()
                if ping_result:
                    is_alive = ping_result
                    last_ping = ping_result
                else:
                    if not last_ping:
                        is_alive = ping_result
                    else:
                        is_alive = last_ping
                    last_ping = ping_result

                is_alive = turn_on_condition(start_at, end_at, date_fmt, time_fmt) and is_alive

                if desktop_lights.connected:
                    if is_alive:
                        desktop_lights.turn_on()
                    else:
                        desktop_lights.turn_off()

                time.sleep(2)
    except KeyboardInterrupt:
        print("\nExiting...")
        pass
    finally:
        shutdown()
        pass
