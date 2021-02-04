from lib.animations import NewKITT, RainbowCycle, shutdown as shutdownPixels
from lib.devices import Sonoff
from lib.network_scanner import NetworkScanner
from lib.pyledshop import WifiLedShopLight
from lib.threading import Thread
from lib.utils import evaluate_day_night
from optparse import OptionParser
from subprocess import Popen as call_process, PIPE
from sys import argv

simulate_allowed=False
try:
    import neopixel
except:
    import lib.neopixel.neopixel as neopixel
    simulate_allowed=True
    pass

try:
    import board
except:
    import lib.neopixel.board as board
    pass

import time
import traceback
import os

parser = OptionParser()
parser.add_option("--off", action="store_true", dest="terminate", default=False)
parser.add_option("-q", "--quiet", action="store_false", dest="simulate", default=True)
(options, _) = parser.parse_args()


def log(a, sep=' => ', flush=True, end="\n"):
    print(__name__, a, sep=sep, flush=flush, end=end)


ips = {
    'main_host': "192.168.1.13",
    'controller_host': "192.168.1.203",
    'sonoff_host': "192.168.1.153",
    'sonoff_broker': "localhost",
    # 'sonoff_broker': "192.168.1.20",
}

log(ips)
scanner = NetworkScanner(ips=list(ips.values()))
is_alive = False
last_ping = False
start_at = '17:30:00'
end_at = '06:30:00'
date_fmt = '%Y/%m/%d '
time_fmt = '%H:%M:%S'

log(f'Detecting Broker in {ips["sonoff_broker"]}...')
scanner.wait_host(ips["sonoff_broker"])
log(f'Broker detected!')
log(f'Detecting Sonoff in {ips["sonoff_host"]}...')
scanner.wait_host(ips["sonoff_host"])
log(f'Sonoff detected!')

sonoff = Sonoff(broker=ips["sonoff_broker"], device="desktop")
controller = None
pixels = None
fan_thread = None
night_mode = False


def turn_on_screen(on):
    path = '/sys/class/backlight/rpi_backlight/brightness'
    if os.path.exists(path):
        try:
            brightness = 64 if on == True else 1
            call_process(
                f'echo {brightness} > {path}', shell=True, stdout=PIPE).wait()
        except:
            traceback.print_exc()
            pass


def pixels_animation():
    global scanner
    global night_mode
    global ips
    global pixels
    while True:
        if scanner.is_alive(ips["main_host"]):
            turn_on_screen(True)
            if pixels is not None:
                if night_mode:
                    RainbowCycle(pixels, 0.001, 1)
                else:
                    NewKITT(pixels, 255, 0, 0, 1, 0.075, 0, 1)
        else:
            turn_on_screen(False)
            if pixels is not None:
                pixels.fill((0, 0, 0))
                pixels.show()
        time.sleep(0.01)


def start_fan_threads():
    global fan_thread
    if fan_thread is None:
        fan_thread = Thread(target=pixels_animation, args=[], daemon=True)
        fan_thread.start()


def stop_fan_threads():
    global fan_thread
    while fan_thread is not None:
        try:
            if fan_thread.is_alive():
                fan_thread.kill()
            fan_thread = None
        except Exception as e:
            log(e)
            pass
        time.sleep(0.1)


def load_pixels():
    global pixels
    global fan_thread
    global simulate_allowed
    global options
    while pixels is None:
        try:
            placeholder = None
            if simulate_allowed == True:
                placeholder = neopixel.NeoPixel(
                    board.D18, 11, brightness=1.0, auto_write=False, pixel_order=neopixel.GRB, simulate=options.simulate)
            else:
                placeholder = neopixel.NeoPixel(
                    board.D18, 11, brightness=1.0, auto_write=False, pixel_order=neopixel.GRB)
            pixels = placeholder
        except:
            traceback.print_exc()
            pixels = None
            pass
        time.sleep(0.1)

    start_fan_threads()


def unload_pixels():
    stop_fan_threads()
    global pixels
    while pixels is not None:
        try:
            shutdownPixels(pixels)
            pixels.deinit()
            pixels = None
        except Exception as e:
            log(e)
            pass
        time.sleep(0.1)
    pixels = None


def shutdown():
    global controller
    global scanner
    global sonoff
    print(f'\n{__name__}', 'Exiting...', sep=' => ')
    unload_pixels()
    attempts = 0
    while not sonoff.connected:
        if attempts < 10:
            attempts += 1
            time.sleep(1)

    if sonoff.connected:
        print(".")
        if sonoff.on:
            if controller is None:
                log(f'Detecting controller in {ips["controller_host"]}...')
                if scanner.wait_host(ips["controller_host"]):
                    log(f'Controller detected!')
                    controller = WifiLedShopLight(ips["controller_host"])
                    controller.sync_state()

            if controller is not None:
                if controller.state.is_on:
                    log("Turning off controller")
                    controller.turn_off()

            attempts = 0
            log("Turning off Sonoff device")
            sonoff.turn_off()

    scanner.stop()


if __name__ == '__main__':
    try:
        if options.terminate == True:
            shutdown()
        else:
            load_pixels()
            while True:
                preset = None
                speed = None
                night_mode = evaluate_day_night(
                    start_at, end_at, date_fmt, time_fmt)

                if sonoff.connected:
                    if scanner.is_alive(ips["main_host"]):
                        if not sonoff.on:
                            if controller is not None:
                                try:
                                    controller.close()
                                except:
                                    traceback.print_exc()
                                    pass
                            controller = None
                            log("Turning on Sonoff device")
                            sonoff.turn_on()

                        if controller is None:
                            log(
                                f'Detecting controller in {ips["controller_host"]}...')
                            scanner.wait_host(ips["controller_host"])
                            log('Controller detected!')
                            controller = WifiLedShopLight(
                                ips["controller_host"])
                            controller.sync_state()
                            controller.set_segments(1)
                            controller.set_lights_per_segment(144)

                        if night_mode:
                            if controller.state.mode != 0:
                                log('Activating night mode!')
                                controller.set_preset(0)
                        else:
                            if controller.state.mode != 219:
                                log('Activating day mode!')
                                controller.set_custom(1)

                        if not controller.state.is_on:
                            log("Turning on controller")
                        controller.turn_on()

                    else:
                        if sonoff.on:
                            log("Turning off Sonoff device")
                        sonoff.turn_off()
                else:
                    if controller is not None:
                        try:
                            controller.close()
                        except:
                            traceback.print_exc()
                            pass
                        controller = None

                time.sleep(1)
    except:
        pass
    finally:
        shutdown()
        pass
