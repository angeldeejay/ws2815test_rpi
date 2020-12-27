import neopixel;

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
