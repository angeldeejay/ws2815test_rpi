#!/usr/bin/env python3
import signal, time, sys, threading, platform, subprocess, os, pythonping
from magichue import discover_bulbs, Light
from datetime import datetime, timedelta
from lib.utils import turn_on_condition

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

def turn_on(light, colors, interval):
    print("Waking up " + str(light) + "...")
    light.rgb = (0, 0, 0)
    light.on = True
    i = 0;
    while True:
        global STOP_THREADS
        global TERMINATE
        if STOP_THREADS or TERMINATE:
            break
        color = colors[i]
        light.rgb = (color[0], color[1], color[2])
        light.on = True
        i += 1
        if i == len(colors):
            i = 0
        time.sleep(interval)

def turn_off(light):
    while True:
        if light.on and light.rgb != (0, 0, 0):
            print('Setting color to black in ' + str(light) + '...')
            light.rgb = (0, 0, 0)
            light.on = True
        elif light.on:
            print('Shutting down ' + str(light) + '...')
            light.on = False
        else:
            print(str(light) + ' is off...')
            break
        time.sleep(0.1)

def shutdown():
    global STOP_THREADS
    global THREADS
    global TERMINATE
    global IS_ALIVE
    global LAST_PING
    STOP_THREADS = True
    TERMINATE = True
    IS_ALIVE = False
    LAST_PING = False
    for thread_index, light, thread in THREADS:
        turn_off(light)

def change_test_dates():
    global START_AT
    global END_AT
    global TIME_FMT
    global LAST_PING
    LAST_PING = True
    while True:
        global TERMINATE
        if TERMINATE:
            break
        now = datetime.now()
        START_AT = (now + timedelta(0, 5)).strftime(TIME_FMT)
        END_AT = (now + timedelta(0, 10)).strftime(TIME_FMT)
        print("<TEST> Should turn on at: " + START_AT)
        print("<TEST> Should turn off at: " + END_AT)
        time.sleep(10)

def create_thread(thread_index, light):
    global THREADS
    thread = threading.Thread(target=turn_on, daemon=True, args=(light, COLORS, 0.2))
    if len(THREADS) > thread_index:
        THREADS[thread_index] = (thread_index, light, thread)
    else:
        THREADS.append((thread_index, light, thread))

START_AT = '18:00:00'
END_AT = '06:00:00'
DATE_FMT = '%Y/%m/%d '
TIME_FMT = '%H:%M:%S'
THREADS = []
TEST_THREAD = None
STOP_THREADS = False
IPS = discover_bulbs()
LIGHTS = [Light(strip_ip) for strip_ip in IPS]
ARGS = sys.argv
COLORS = get_colors(8)
MAIN_HOST="192.168.1.13"
TERMINATE = False
IS_ALIVE = False
LAST_PING = False

def is_alive():
    global IS_ALIVE
    global LAST_PING
    global MAIN_HOST
    while True:
        global TERMINATE
        if TERMINATE:
            LAST_PING = False
            IS_ALIVE = False
            break
        PING_RESULT = pythonping.ping(MAIN_HOST, timeout=1, count=1).success()
        if PING_RESULT:
            IS_ALIVE = PING_RESULT
        else:
            if not LAST_PING:
                IS_ALIVE = PING_RESULT
            else:
                IS_ALIVE = LAST_PING
                LAST_PING = PING_RESULT

        time.sleep(1)

alive_thread = threading.Thread(target=is_alive)
alive_thread.start()

if len(ARGS) > 1 and ARGS[1] == '--test':
    TEST_THREAD = (threading.Thread(target=change_test_dates)).start()

if len(ARGS) > 1 and ARGS[1] == '--on':
    START_AT = '00:00:00'
    END_AT = '23:59:59'

if len(ARGS) > 1 and ARGS[1] == '--off':
    for light in LIGHTS:
        turn_off(light)
else:
    thread_index = 0
    for light in LIGHTS:
        thread = threading.Thread(target=turn_on, daemon=True, args=(light, COLORS, 0.2))
        create_thread(thread_index, light)
        thread_index = thread_index + 1

    try:
        print("Should turn on at: " + START_AT)
        print("Should turn off at: " + END_AT)
        while True:
            LIGHT_ON = turn_on_condition(START_AT, END_AT, DATE_FMT, TIME_FMT) and IS_ALIVE
            STOP_THREADS = not LIGHT_ON

            for thread_index, light, thread in THREADS:
                if LIGHT_ON:
                    if not thread.is_alive():
                        thread.start()
                else:
                    if thread.is_alive():
                        turn_off(light)
                        create_thread(thread_index, light)
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()

