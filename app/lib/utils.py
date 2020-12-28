import neopixel, time, threading;
from datetime import datetime, timedelta

def wheel(position, order):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if position < 0 or position > 255:
        r = g = b = 0
    elif position < 85:
        r = int(position * 3)
        g = int(255 - position * 3)
        b = 0
    elif position < 170:
        position -= 85
        r = int(255 - position * 3)
        g = 0
        b = int(position * 3)
    else:
        position -= 170
        r = 0
        g = int(position * 3)
        b = int(255 - position * 3)
    return (r, g, b) if order in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

def wheelBrightLevel(pixels, pos, bright):
    num_pixels = pixels._pixels
    order = pixels._byteorder_string
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos*3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos*3)
        g = 0
        b = int(pos*3)
    else:
        pos -= 170
        r = 0
        g = int(pos*3)
        b = int(255 - pos*3)
    # bight level logic
    color = brightnessRGB(r, g, b, bright)
    r = color[0]
    g = color[1]
    b = color[2]
    return color if order == neopixel.RGB or order == neopixel.GRB else (r, g, b, 0)

def brightnessRGB(red, green, blue, bright):
    r = (bright/256.0)*red
    g = (bright/256.0)*green
    b = (bright/256.0)*blue
    return (int(r), int(g), int(b))
        
def fadeToBlack(oldColor, ledNo, fadeValue):
    r = oldColor[0]
    g = oldColor[1]
    b = oldColor[2]
    if (r<=10):
        r = 0
    else:
        r = r - ( r * fadeValue / 256 )
    if (g<=10):
        g = 0
    else:
        g = g - ( g * fadeValue / 256 )
    if (b<=10):
        b = 0
    else:
        b = b - ( b * fadeValue / 256 )
    return (int(r), int(g), int(b))

def turn_on_condition(start_at, end_at, date_fmt, time_fmt):
    now = datetime.now()
    current_start = datetime.strptime(now.strftime(date_fmt) + start_at, date_fmt + time_fmt)
    delta_interval = datetime.strptime(now.strftime(date_fmt) + end_at, date_fmt + time_fmt) - current_start

    if delta_interval.days < 0:
        delta_interval = timedelta(days=0, seconds=delta_interval.seconds, microseconds=delta_interval.microseconds)

    current_end = current_start + delta_interval
    last_start = current_start + timedelta(days=-1)
    last_end = current_end + timedelta(days=-1)

    return current_start <= now <= current_end or last_start <= now <= last_end
