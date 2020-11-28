from time import sleep
from rpi_ws281x import Color
from traceback import format_exc

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

def animate(instance):
    colors = get_colors(8)
    colors.reverse() if instance.reverse else True
    try:
        instance.begin()
        while True:
            if not instance.thread_active:
                break
            for i in range(0, instance.led_count):
                p = i % len(colors)
                instance.set_pixel_color(i, colors[p])
            instance.show()
            if instance.reverse:
                colors = colors[1:] + [colors[0]]
            else:
                colors.insert(0, colors.pop())
            sleep(instance.interval)
    except:
        error_output = "\n\n\t" + format_exc().replace("\n", "\n\t")
        instance.log("\n\t" + error_output + "\n", "error")
        while True:
            if not instance.thread_active:
                break
        pass

    
