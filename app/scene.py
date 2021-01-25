from lib.animations import NewKITT, RainbowCycle, shutdown as shutdownPixels
from lib.devices import Sonoff
from lib.network_scanner import NetworkScanner
from lib.pyledshop import WifiLedShopLight
from lib.utils import evaluate_day_night
from subprocess import Popen as call_process, PIPE
from sys import argv
from threading import Thread
import board
import neopixel
import time

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
pixels = None
fan_thread = None
night_mode = False

def turn_on_screen(on):
    try:
        brightness = 64 if on == True else 0
        call_process(f'echo {brightness} > /sys/class/backlight/rpi_backlight/brightness', shell=True, stdout=PIPE).wait()
    except:
        pass

def pixels_animation():
    global scanner
    global night_mode
    global main_host
    while True:
        try:
            if scanner.is_alive(main_host):
                turn_on_screen(True)
                load_pixels()
                if night_mode:
                    RainbowCycle(pixels, 0.001, 1)
                else:
                    NewKITT(pixels, 255, 0, 0, 1, 0.075, 0, 1)
            else:
                turn_on_screen(False)
                unload_pixels()
        except:
            pass

def load_pixels():
    global pixels
    global fan_thread
    if pixels is None:
        while pixels is None:
            try:
                placeholder = neopixel.NeoPixel(board.D18, 11, brightness=1.0, auto_write=False, pixel_order=neopixel.GRB)
                pixels = placeholder
            except:
                pixels = None
                pass
            time.sleep(0.5)

    if fan_thread is None:
        fan_thread = Thread(target=pixels_animation, args=[])
        fan_thread.setDaemon(True)
        fan_thread.start()

def unload_pixels():
    global fan_thread
    if fan_thread is not None:
        try:
            fan_thread.join(0)
        except:
            pass
        fan_thread = None

    global pixels
    load_pixels()
    try:
        shutdownPixels(pixels)
        pixels.deinit()
        pixels = None
    except:
        pass

def shutdown():
    global controller
    global scanner
    global sonoff
    print(f'\n{__name__}', 'Exiting...')
    unload_pixels()
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
            load_pixels()
            preset = None
            speed = None
            night_mode = evaluate_day_night(start_at, end_at, date_fmt, time_fmt)
            # Scene lights
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

                    if night_mode:
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

            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        shutdown()
        pass
