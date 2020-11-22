import time
from rpi_ws281x import PixelStrip, Color

LED_COUNT = 300       # number of LED pixels.
LED_PIN = 19          # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 64  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53

def get_hex_value(i):
    return max(0, min(255, int(i)))

def get_color(color_values):
    r = get_hex_value(color_values[0])
    g = get_hex_value(color_values[1])
    b = get_hex_value(color_values[2])
    return Color(r, g, b)

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

if __name__ == '__main__':
    depths_range = [pow(2, i) for i in range(0, 8)]
    depths_range = depths_range + depths_range[::-1][1::][:-1]

    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    print("Press Ctrl-C to quit.")
    try:
        ptr = 0
        while True:
            depth_index = 1
            for depths in depths_range:
                colors = get_colors(depths)
                print(colors)
                sleep = 0.1 / pow(depths, 2)
                for pixel in range(0, round((LED_COUNT / 4) * depth_index)):
                    print([depths, pixel])
                    for i in range(0, LED_COUNT):
                        p = (i + ptr) % len(colors)
                        strip.setPixelColor(i, colors[p])
                    strip.show()
                    ptr += 1
                    ptr %= len(colors)
                    time.sleep(sleep)
                depth_index += 1
    except KeyboardInterrupt:
        for i in range(0, LED_COUNT):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
