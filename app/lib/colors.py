def wheel(position: int, order='RGB'):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    w = 255
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

    result = ()
    for i in order.lower():
        if i == 'r':
            result += (r, )
        elif i == 'g':
            result += (g, )
        elif i == 'b':
            result += (b, )
        elif i == 'w':
            result += (w, )

    return result


def wheelBrightLevel(position: int, bright: int, order='RGB'):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    w = bright
    if position < 0 or position > 255:
        r = g = b = 0
    elif position < 85:
        r = int(position * 3)
        g = int(255 - position*3)
        b = 0
    elif position < 170:
        position -= 85
        r = int(255 - position*3)
        g = 0
        b = int(position*3)
    else:
        position -= 170
        r = 0
        g = int(position*3)
        b = int(255 - position*3)
    # bight level logic
    color = brightnessRGB(r, g, b, bright)
    r = color[0]
    g = color[1]
    b = color[2]

    result = ()
    for i in order.lower():
        if i == 'r':
            result += (r, )
        elif i == 'g':
            result += (g, )
        elif i == 'b':
            result += (b, )
        elif i == 'w':
            result += (w, )

    return result


def brightnessRGB(red: int, green: int, blue: int, bright: int, order='RGB'):
    r = (bright/256.0)*red
    g = (bright/256.0)*green
    b = (bright/256.0)*blue
    return (int(r), int(g), int(b))


def fadeToBlack(oldColor: tuple, fadeValue: int, order='RGB'):
    r = oldColor[0]
    g = oldColor[1]
    b = oldColor[2]
    w = 0
    if (r <= 10):
        r = 0
    else:
        r = r - (r * fadeValue / 256)
    if (g <= 10):
        g = 0
    else:
        g = g - (g * fadeValue / 256)
    if (b <= 10):
        b = 0
    else:
        b = b - (b * fadeValue / 256)

    result = ()
    for i in order.lower():
        if i == 'r':
            result += (r, )
        elif i == 'g':
            result += (g, )
        elif i == 'b':
            result += (b, )
        elif i == 'w':
            result += (w, )

    return result
