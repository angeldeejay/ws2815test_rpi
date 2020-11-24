#!/usr/bin/env python3
import signal, time, sys, threading
from magichue import discover_bulbs, Light
from datetime import datetime, timedelta

IPS = discover_bulbs()
LIGHTS = [Light(strip_ip) for strip_ip in IPS]

def get_hex_value(i):
    return max(0, min(255, int(i)))

def get_color(color_values):
    r = get_hex_value(color_values[0])
    g = get_hex_value(color_values[1])
    b = get_hex_value(color_values[2])
    return [r, g, b]

def get_next_index(i):
    if i == 2:
        return 0
    return i + 1

def get_prev_index(i):
    if i == 0:
        return 2
    return i - 1


def turn_off_prev(stay_index, turn_off_index, intensities, depth):
    result = []
    for value in range(intensities - 1, -1, -1):
        color_values = [0, 0, 0]
        color_values[stay_index] = intensities * depth
        color_values[turn_off_index] = value * depth
        if color_values not in result:
            result.append(color_values)

    return result

def get_colors(intensities):
    result = []
    depth = 256 / intensities
    for stay_index in range(0, 3):
        prev_index = get_prev_index(stay_index)
        next_index = get_next_index(stay_index)
        for value in range(0, intensities + 1):
            color_values = [0, 0, 0]
            color_values[stay_index] = intensities * depth
            color_values[next_index] = value * depth
            if color_values not in result:
                result.append(color_values)

        for color_values in turn_off_prev(next_index, stay_index, intensities, depth):
            if color_values not in result:
                result.append(color_values)

    return [get_color(color) for color in result]

STOP_THREADS = False
def colorize(light, colors, interval):
    i = 0;
    while True:
        global STOP_THREADS
        if STOP_THREADS:
            break
        color = colors[i]
        light.rgb = (color[0], color[1], color[2])
        light.on = True
        i += 1
        if i == len(colors):
            i = 0
        time.sleep(interval)

ARGS = sys.argv
COLORS = get_colors(16)
START_AT = '17:45:00'
END_AT = '02:45:00'
DATE_FMT = '%Y/%m/%d '
TIME_FMT = '%H:%M:%S'

def signal_term_handler(signal, frame):
    STOP_THREADS = True
    for light, thread in THREADS:
        print('shutting down ' + str(light) + '...')
        thread.join()
        light.rgb = (0, 0, 0)
        light.on = False
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_term_handler)

if len(ARGS) > 1 and ARGS[1] == '--off':
    for light in LIGHTS:
        print("Shutting down " + str(light) + "...")
        if light.on:
            light.rgb = (0, 0, 0)
            light.on = False
else:
    THREADS = []
    for light in LIGHTS:
        thread = threading.Thread(target=colorize, daemon=True, args=(light, COLORS, 0.1))
        THREADS.append((light, thread))

    while True:
        # datetime object containing current date and time
        now = datetime.now()

        current_start = datetime.strptime(now.strftime(DATE_FMT) + START_AT, DATE_FMT + TIME_FMT)
        delta_interval = datetime.strptime(now.strftime(DATE_FMT) + END_AT, DATE_FMT + TIME_FMT) - current_start

        if delta_interval.days < 0:
            delta_interval = timedelta(days=0, seconds=delta_interval.seconds, microseconds=delta_interval.microseconds)

        current_end = current_start + delta_interval
        last_start = current_start + timedelta(days=-1)
        last_end = current_end + timedelta(days=-1)

        LIGHT_ON = (current_start <= now <= current_end or last_start <= now <= last_end)
        if LIGHT_ON != True:
            STOP_THREADS = True
        for light, thread in THREADS:
            if LIGHT_ON:
                if thread.is_alive() != True:
                    print("Waking up " + str(light) + "...")
                    light.rgb = (0, 0, 0)
                    thread.start()
            else:
                if thread.is_alive() == True:
                    print("Sleeping " + str(light) + "...")
                    thread.join()
                    light.rgb = (0, 0, 0)
        time.sleep(0.1)

