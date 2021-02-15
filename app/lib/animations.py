import time
import random
import math
import serial
from .colors import wheel, brightnessRGB, fadeToBlack


def default_write_fn(data):
    pass


def ColorAll2Color(num_pixels, c1, c2, write_fn=default_write_fn):
    # ColorAll2Color allows two alternating colors to be shown
    pixels = [(0, 0, 0)]*num_pixels
    for i in range(num_pixels):
        pixels[i] = c1 if(i % 2 == 0) else c2
    if callable(write_fn):
        write_fn(pixels)


def ColorAllColorGroup(num_pixels, colorObject, write_fn=default_write_fn):
    # ColorAllColorGroup(colorObject) allows colors to be
    # - colorObject: list of color objects. example ((255, 0, 0), (0, 255, 0))
    pixels = [(0, 0, 0)]*num_pixels
    colorCount = len(colorObject)
    for i in range(num_pixels):
        colorIndex = i % colorCount
        pixels[i] = colorObject[colorIndex]
    if callable(write_fn):
        write_fn(pixels)


def CandyCaneCustom(num_pixels, c1, c2, thisbright, size, delay, cycles, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    N3 = int(num_pixels / size)
    N6 = int(num_pixels / (size*2))
    N12 = int(num_pixels / (size*4))
    for loop in range(cycles):
        cSwap = c1
        c1 = c2
        c2 = cSwap
        for i in range(N6):
            j0 = int((i + num_pixels - N12) % num_pixels)
            j1 = int((j0 + N6) % num_pixels)
            j2 = int((j1 + N6) % num_pixels)
            j3 = int((j2 + N6) % num_pixels)
            j4 = int((j3 + N6) % num_pixels)
            j5 = int((j4 + N6) % num_pixels)
            pixels[j0] = brightnessRGB(
                c1[0], c1[1], c1[2], int(thisbright*.75))
            pixels[j1] = brightnessRGB(c2[0], c2[1], c2[2], thisbright)
            pixels[j2] = brightnessRGB(
                c1[0], c1[1], c1[2], int(thisbright*.75))
            pixels[j3] = brightnessRGB(c2[0], c2[1], c2[2], thisbright)
            pixels[j4] = brightnessRGB(
                c1[0], c1[1], c1[2], int(thisbright*.75))
            pixels[j5] = brightnessRGB(c2[0], c2[1], c2[2], thisbright)
            # show pixel values
            if callable(write_fn):
                write_fn(pixels)
            time.sleep(delay)


def RunningLights(num_pixels, WaveDelay, cycles, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    # gather existing colors in strip of pixel
    strip = []
    for i in range(num_pixels):
        strip.append(pixels[i])
    for loop in range(cycles):
        # change the color level on the existing colors
        for i in range(num_pixels):
            # calculate level
            level = math.sin(i + loop) * 127 + 128
            # change color level on for red, green, and blue
            r = (level / 255)*strip[i][0]
            g = (level / 255)*strip[i][1]
            b = (level / 255)*strip[i][2]
            pixels[i] = (int(r), int(g), int(b))
        if callable(write_fn):
            write_fn(pixels)
        time.sleep(WaveDelay)


def SnowSparkle(num_pixels, Count, SparkleDelay, SpeedDelay, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    # gather existing colors in strip of pixel
    strip = pixels
    for i in range(Count):
        index = random.randint(0, num_pixels - 1)
        pixels[index] = (255, 255, 255)
        if callable(write_fn):
            write_fn(pixels)
        time.sleep(SparkleDelay)
        pixels[index] = strip[index]
        if callable(write_fn):
            write_fn(pixels)
        time.sleep(SpeedDelay)


def HalloweenEyes(num_pixels, red, green, blue, EyeWidth, EyeSpace, Fade, Steps, FadeDelay, EndPause, cycles, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    for c in range(cycles):
        # gather existing colors in strip of pixel
        strip = pixels
        # define eye1 and eye2 location
        StartPoint = random.randint(0, num_pixels - (2*EyeWidth) - EyeSpace)
        Start2ndEye = StartPoint + EyeWidth + EyeSpace
        #  set color of eyes for given location
        for i in range(EyeWidth):
            pixels[StartPoint + i] = (red, green, blue)
            pixels[Start2ndEye + i] = (red, green, blue)
        if callable(write_fn):
            write_fn(pixels)
        # if user wants fading, then fadeout pixel color
        if Fade == True:
            for j in range(Steps, - 1, - 1):
                r = (j / Steps)*red
                g = (j / Steps)*green
                b = (j / Steps)*blue
                for i in range(EyeWidth):
                    pixels[StartPoint + i] = ((int(r), int(g), int(b)))
                    pixels[Start2ndEye + i] = ((int(r), int(g), int(b)))
                if callable(write_fn):
                    write_fn(pixels)
                time.sleep(FadeDelay)
        # Set all pixels to back
        # set color of eyes for given location
        for i in range(EyeWidth):
            pixels[StartPoint + i] = strip[StartPoint + i]
            pixels[Start2ndEye + i] = strip[Start2ndEye + i]
        if callable(write_fn):
            write_fn(pixels)
        # pause before changing eye location
        time.sleep(EndPause)


def HeartBeat(num_pixels, beat1Step, beat1FadeInDelay, beat1FadeOutDelay, beat1Delay, beat2Step, beat2FadeInDelay, beat2FadeOutDelay, beat2Delay, cycles, write_fn=default_write_fn):
    # HeartBeat - mimics a heart beat pulse, with 2 beats at different speeds. The existing colors
    # on the pixel strip are preserved, rather than a single color.
    #
    # HeartBeat(beat1Step, beat1FadeInDelay, beat1FadeOutDelay, beat1Delay,
    #                     beat2Step, beat2FadeInDelay, beat2FadeOutDelay, beat1Delay, cycles):
    # HeartBeat(3, .005, .003, 0.001, 6, .002, .003, 0.05, 10)
    #
    #   beat1Step: (1 - 255) first beat color transition step
    #   beat1FadeInDelay: (0 - 2147483647) first beat fade in transition speed, in seconds
    #   beat1FadeOutDelay: (0 - 2147483647) first beat fade out transition speed, in seconds
    #   beat1Delay: (0 - 2147483647)  beat time delay between first and second beat, in seconds
    #   beat2Step: (1 - 255) second beat color transition step
    #   beat2FadeInDelay: (0 - 2147483647) second beat fade in transition speed, in seconds
    #   beat2FadeOutDelay: (0 - 2147483647) second beat fade out transition speed, in seconds
    #   beat1Delay: (0 - 2147483647)  beat time delay between second and first beat, in seconds
    #   cycles: (1 - 2147483647) number of times this effect will run
    pixels = [(0, 0, 0)]*num_pixels
    # gather existing colors in strip of pixel
    strip = pixels
    for loop in range(cycles):
        for ii in range(1, 252, beat1Step):  # for (ii = 1 ; ii <252 ; ii = ii = ii + x)
            for index in range(num_pixels):
                r = strip[index][0]
                g = strip[index][1]
                b = strip[index][2]
                pixels[index] = brightnessRGB(r, g, b, ii)
            if callable(write_fn):
                write_fn(pixels)
            time.sleep(beat1FadeInDelay)
        for ii in range(252, 3, - beat1Step):  # for (int ii = 252 ; ii > 3 ; ii = ii - x){
            for index in range(num_pixels):
                r = strip[index][0]
                g = strip[index][1]
                b = strip[index][2]
                pixels[index] = brightnessRGB(r, g, b, ii)
            if callable(write_fn):
                write_fn(pixels)
            time.sleep(beat1FadeOutDelay)
        time.sleep(beat1Delay)
        for ii in range(1, 252, beat1Step):  # for (int ii = 1 ; ii <255 ; ii = ii = ii + y){
            for index in range(num_pixels):
                r = strip[index][0]
                g = strip[index][1]
                b = strip[index][2]
                pixels[index] = brightnessRGB(r, g, b, ii)
            if callable(write_fn):
                write_fn(pixels)
            time.sleep(beat2FadeInDelay)
        for ii in range(252, 3, - beat1Step):  # for (int ii = 255 ; ii > 1 ; ii = ii - y){
            for index in range(num_pixels):
                r = strip[index][0]
                g = strip[index][1]
                b = strip[index][2]
                pixels[index] = brightnessRGB(r, g, b, ii)
            if callable(write_fn):
                write_fn(pixels)
            time.sleep(beat2FadeOutDelay)
        time.sleep(.050)


def Rotate(num_pixels, delay, cycles, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    # gather existing colors in strip of pixel
    strip = pixels
    for loop in range(cycles):
        pixels[0] = pixels[num_pixels - 1]
        # rotate pixel position
        for i in range(num_pixels - 1, 0, - 1):
            pixels[i] = pixels[i - 1]
        # there is an issue with first 2 pixels are same color
        #pixels[0] = (0, 0, 0)
        if callable(write_fn):
            write_fn(pixels)
        time.sleep(delay)


def CylonBounce(num_pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay, cycles, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    for i in range(cycles):
        pixels = [(0, 0, 0)]*num_pixels
        for i in range(num_pixels - EyeSize - 1):
            pixels = [(0, 0, 0)]*num_pixels
            pixels[i] = (int(red / 10), int(green / 10), int(blue / 10))
            for j in range(1, EyeSize + 1):
                pixels[i + j] = (red, green, blue)
            pixels[i + EyeSize + 1] = (int(red / 10),
                                       int(green / 10), int(blue / 10))
            if callable(write_fn):
                write_fn(pixels)
            time.sleep(SpeedDelay)
        time.sleep(ReturnDelay)

        for i in range(num_pixels - EyeSize - 2, - 1, - 1):
            pixels = [(0, 0, 0)]*num_pixels
            pixels[i] = (int(red / 10), int(green / 10), int(blue / 10))
            for j in range(1, EyeSize + 1):
                pixels[i + j] = (red, green, blue)
            pixels[i + EyeSize + 1] = (int(red / 10),
                                       int(green / 10), int(blue / 10))
            if callable(write_fn):
                write_fn(pixels)
            time.sleep(SpeedDelay)
        time.sleep(ReturnDelay)


def RainbowCycle(num_pixels, SpeedDelay, cycles, write_fn=default_write_fn):
    # RainbowCycle: rotate colors using rainbow scheme.
    #
    #   SpeedDelay: (0 - ...) slow down the effect by injecting a delay in Sec. 0=no delay, .05=50msec, 2=2sec
    pixels = [(0, 0, 0)]*num_pixels
    for i in range(cycles):
        for j in range(255):
            for i in range(num_pixels):
                pixel_index = (i * 256 // num_pixels) + j
                pixels[i] = wheel(pixel_index & 255)
            if callable(write_fn):
                write_fn(pixels)
            time.sleep(SpeedDelay)


def FireCustom(num_pixels, CoolingRangeStart, CoolingRangeEnd, Sparking, SparkingRangeStart, SparkingRangeEnd, SpeedDelay, cycles, write_fn=default_write_fn):
    # FireCustom: makes the strand of pixels show an effect that looks flame. This effect also
    # adds more detail control of "sparks" that inject "heat" to the effect, thus changing color
    # and flame length. The spark position can also be controlled via start and end range.
    # Color options include red, green, and blue.
    #
    #   CoolingRangeStart: (0 - 255) cooling random value, start range
    #   CoolingRangeEnd: (0 - 255) cooling random value, end range
    #   Sparking: (0 - 100)  chance of sparkles are added randomly controld through a % value, 100= 100% and 0 = 0%
    #   SparkingRangeStart: (0 - number of pixels) spark position random value, start range
    #   SparkingRangeEnd: (0 - number of pixels) spark position random value, end range
    #   SpeedDelay: (0 - ...) slow down the effect by injecting a delay in Sec. 0=no delay, .05=50msec, 2=2sec
    #
    # Improvements:
    #  - add choice for 3 diffrent fire effect logic.
    #  - add choice to control heat values "random.randint(160, 255)"
    #  - add choice for flame color options include red, green, and blue.
    # initialize heat array, same size of as the strip of pixels
    pixels = [(0, 0, 0)]*num_pixels
    heat = [0]*num_pixels
    #
    for loop in range(cycles):
        cooldown = 0
        # Step 1.  Cool down every cell a little
        for i in range(num_pixels):
            cooldown = random.randint(CoolingRangeStart, CoolingRangeEnd)
            if cooldown > heat[i]:
                heat[i] = 0
            else:
                heat[i] = heat[i] - cooldown
        # Step 2.  Heat from each cell drifts 'up' and diffuses a little
        for k in range(num_pixels - 1, 2, - 1):
            heat[k] = (heat[k - 1] + heat[k - 2] + heat[k - 2]) / 3
        # Step 3.  Randomly ignite new 'sparks' near the bottom
        if random.randint(0, 100) < Sparking:
            # randomly pick the position of the spark
            y = random.randint(SparkingRangeStart, SparkingRangeEnd)
            # different fire effects
            heat[y] = random.randint(160, 255)
        # Step 4.  Convert heat to LED colors
        for j in range(num_pixels):
            t192 = round((int(heat[j]) / 255.0)*191)
            # calculate ramp up from
            heatramp = t192 & 63  # 0..63  0x3f=63
            heatramp <<= 2  # scale up to 0..252
            # figure out which third of the spectrum we're in:
            if t192 > 0x80:  # hottest 128 = 0x80
                pixels[j] = (255, 255, int(heatramp))
            elif t192 > 0x40:  # middle 64 = 0x40
                pixels[j] = (255, int(heatramp), 0)
            else:  # coolest
                pixels[j] = (int(heatramp), 0, 0)
        if callable(write_fn):
            write_fn(pixels)
        time.sleep(SpeedDelay)


def FireCustomMirror(num_pixels, CoolingRangeStart, CoolingRangeEnd, Sparking, SparkingRangeStart, SparkingRangeEnd, SpeedDelay, cycles, write_fn=default_write_fn):
    # FireCustomMirror: makes the strand of pixels show an effect that looks flame. This is similar to FireCustom,
    # however it mirrors the effect on top and bottom  (rather than using just from bottom). The intent is to
    # have a fire effect that could be used 144 pixel strip for a lanyard id.
    #
    #   CoolingRangeStart: (0 - 255) cooling random value, start range
    #   CoolingRangeEnd: (0 - 255) cooling random value, end range
    #   Sparking: (0 - 100)  chance of sparkles are added randomly controld through a % value, 100= 100% and 0 = 0%
    #   SparkingRangeStart: (0 - number of pixels) spark position random value, start range
    #   SparkingRangeEnd: (0 - number of pixels) spark position random value, end range
    #   SpeedDelay: (0 - ...) slow down the effect by injecting a delay in Sec. 0=no delay, .05=50msec, 2=2sec
    #
    # Improvements:
    #  - add choice for 3 diffrent fire effect logic.
    #  - add choice to control heat values "random.randint(160, 255)"
    #  - add choice for flame color options include red, green, and blue.
    # initialize heat array, same size of as the strip of pixels
    pixels = [(0, 0, 0)]*num_pixels
    halfNumPixel = int(num_pixels / 2)  # note that this will round down
    heat = [0]*halfNumPixel
    #
    for loop in range(cycles):
        cooldown = 0
        # Step 1.  Cool down every cell a little
        for i in range(halfNumPixel):
            cooldown = random.randint(CoolingRangeStart, CoolingRangeEnd)
            if cooldown > heat[i]:
                heat[i] = 0
            else:
                heat[i] = heat[i] - cooldown
        # Step 2.  Heat from each cell drifts 'up' and diffuses a little
        for k in range(halfNumPixel - 1, 2, - 1):
            heat[k] = (heat[k - 1] + heat[k - 2] + heat[k - 2]) / 3
        # Step 3.  Randomly ignite new 'sparks' near the bottom
        if random.randint(0, 100) < Sparking:
            # randomly pick the position of the spark
            y = random.randint(SparkingRangeStart, SparkingRangeEnd)
            # different fire effects
            heat[y] = random.randint(160, 255)
        # Step 4.  Convert heat to LED colors
        for j in range(halfNumPixel):
            t192 = round((int(heat[j]) / 255.0)*191)
            # calculate ramp up from
            heatramp = t192 & 63  # 0..63  0x3f=63
            heatramp <<= 2  # scale up to 0..252
            # figure out which third of the spectrum we're in for color:
            if t192 > 0x80:  # hottest 128 = 0x80
                colortemp = (255, 255, int(heatramp))
            elif t192 > 0x40:  # middle 64 = 0x40
                colortemp = (255, int(heatramp), 0)
            else:  # coolest
                colortemp = (int(heatramp), 0, 0)
            pixels[j] = colortemp
            pixels[num_pixels - 1 - j] = colortemp
        if callable(write_fn):
            write_fn(pixels)
        time.sleep(SpeedDelay)


def TheaterChaseCustom(num_pixels, colorobj, darkspace, cycles, SpeedDelay, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    colorCount = len(colorobj)
    n = colorCount + darkspace
    for j in range(cycles):
        for q in range(n):
            for i in range(0, num_pixels, n):
                for index in range(0, colorCount, 1):
                    if i + q + index < num_pixels:
                        pixels[i + q + index] = colorobj[index]
            if callable(write_fn):
                write_fn(pixels)
            time.sleep(SpeedDelay)
            pixels = [(0, 0, 0)]*num_pixels
            for i in range(0, num_pixels, n):
                for index in range(0, colorCount, 1):
                    if i + q + index < num_pixels:
                        pixels[i + q + index] = (0, 0, 0)


def NewKITT(num_pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay, cycles, write_fn=default_write_fn):
    for i in range(cycles):
        RightToLeft(num_pixels, red, green, blue, EyeSize,
                    SpeedDelay, ReturnDelay, write_fn=write_fn)
        LeftToRight(num_pixels, red, green, blue, EyeSize,
                    SpeedDelay, ReturnDelay, write_fn=write_fn)
        OutsideToCenter(num_pixels, red, green, blue, EyeSize,
                        SpeedDelay, ReturnDelay, write_fn=write_fn)
        CenterToOutside(num_pixels, red, green, blue, EyeSize,
                        SpeedDelay, ReturnDelay, write_fn=write_fn)
        LeftToRight(num_pixels, red, green, blue, EyeSize,
                    SpeedDelay, ReturnDelay, write_fn=write_fn)
        RightToLeft(num_pixels, red, green, blue, EyeSize,
                    SpeedDelay, ReturnDelay, write_fn=write_fn)
        OutsideToCenter(num_pixels, red, green, blue, EyeSize,
                        SpeedDelay, ReturnDelay, write_fn=write_fn)
        CenterToOutside(num_pixels, red, green, blue, EyeSize,
                        SpeedDelay, ReturnDelay, write_fn=write_fn)


def CenterToOutside(num_pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    for i in range(int((num_pixels - EyeSize) / 2), - 1, - 1):
        pixels = [(0, 0, 0)]*num_pixels
        pixels[i] = (int(red / 10), int(green / 10), int(blue / 10))

        for j in range(1, EyeSize + 1):
            pixels[i + j] = (red, green, blue)

        pixels[i + EyeSize + 1] = (int(red / 10),
                                   int(green / 10), int(blue / 10))
        pixels[num_pixels - i - j] = (int(red / 10),
                                      int(green / 10), int(blue / 10))

        for j in range(1, EyeSize + 1):
            pixels[num_pixels - i - j] = (red, green, blue)

        pixels[num_pixels - i - EyeSize -
               1] = (int(red / 10), int(green / 10), int(blue / 10))
        if callable(write_fn):
            write_fn(pixels)
        time.sleep(SpeedDelay)

    time.sleep(ReturnDelay)


def OutsideToCenter(num_pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    for i in range(int(((num_pixels - EyeSize) / 2) + 1)):
        pixels = [(0, 0, 0)]*num_pixels
        pixels[i] = (int(red / 10), int(green / 10), int(blue / 10))

        for j in range(1, EyeSize + 1):
            pixels[i + j] = (red, green, blue)

        pixels[i + EyeSize + 1] = (int(red / 10),
                                   int(green / 10), int(blue / 10))
        pixels[num_pixels - i - 1] = (int(red / 10),
                                      int(green / 10), int(blue / 10))

        for j in range(1, EyeSize + 1):
            pixels[num_pixels - i - j] = (red, green, blue)

        pixels[num_pixels - i - EyeSize -
               1] = (int(red / 10), int(green / 10), int(blue / 10))
        if callable(write_fn):
            write_fn(pixels)
        time.sleep(SpeedDelay)

    time.sleep(ReturnDelay)


def LeftToRight(num_pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    for i in range(num_pixels - EyeSize - 2):
        pixels = [(0, 0, 0)]*num_pixels
        pixels[i] = (int(red / 10), int(green / 10), int(blue / 10))

        for j in range(1, EyeSize + 1):
            pixels[i + j] = (red, green, blue)

        pixels[i + EyeSize + 1] = (int(red / 10),
                                   int(green / 10), int(blue / 10))
        if callable(write_fn):
            write_fn(pixels)
        time.sleep(SpeedDelay)

    time.sleep(ReturnDelay)


def RightToLeft(num_pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    for i in range(num_pixels - EyeSize - 2, 0, - 1):
        pixels = [(0, 0, 0)]*num_pixels
        pixels[i] = (int(red / 10), int(green / 10), int(blue / 10))

        for j in range(1, EyeSize + 1):
            pixels[i + j] = (red, green, blue)

        pixels[i + EyeSize + 1] = (int(red / 10),
                                   int(green / 10), int(blue / 10))
        if callable(write_fn):
            write_fn(pixels)
        time.sleep(SpeedDelay)

    time.sleep(ReturnDelay)


def Twinkle(num_pixels, red, green, blue, Count, SpeedDelay, OnlyOne, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    for i in range(Count):
        pixels[random.randint(0, num_pixels - 1)] = (red, green, blue)
        if callable(write_fn):
            write_fn(pixels)
        time.sleep(SpeedDelay)
        if OnlyOne:
            pixels = [(0, 0, 0)]*num_pixels

    time.sleep(SpeedDelay)


def TwinkleRandom(num_pixels, Count, SpeedDelay, OnlyOne, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    for i in range(Count):
        pixels[random.randint(0, num_pixels - 1)] = (random.randint(0, 255),
                                                     random.randint(0, 255), random.randint(0, 255))
        if callable(write_fn):
            write_fn(pixels)
        time.sleep(SpeedDelay)
        if OnlyOne:
            pixels = [(0, 0, 0)]*num_pixels

    time.sleep(SpeedDelay)


def Sparkle(num_pixels, red, green, blue, Count, SpeedDelay, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    for i in range(Count):
        pixel = random.randint(0, num_pixels - 1)
        pixels[pixel] = (red, green, blue)
        if callable(write_fn):
            write_fn(pixels)
        time.sleep(SpeedDelay)
        pixels[pixel] = (0, 0, 0)


def MeteorRain(num_pixels, red, green, blue, meteorSize, meteorTrailDecay, meteorRandomDecay, SpeedDelay, cycles, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    for loop in range(cycles):
        pixels = [(0, 0, 0)]*num_pixels
        for i in range(num_pixels*2):
            # fade brightness all LEDs one step
            for j in range(num_pixels):
                if (not meteorRandomDecay) or (random.randint(0, 10) > 5):
                    pixels[j] = fadeToBlack(pixels[j], j, meteorTrailDecay)

            # draw meteor
            for k in range(meteorSize):
                if (i - k < num_pixels) and (i - j >= 0):
                    pixels[i - k] = (red, green, blue)

            if callable(write_fn):
                write_fn(pixels)
            time.sleep(SpeedDelay)


def fill(num_pixels, r, g, b, write_fn=None):
    pixels = [(r, g, b)]*num_pixels
    if callable(write_fn):
        write_fn(pixels)


def shutdown(num_pixels, write_fn=default_write_fn):
    pixels = [(0, 0, 0)]*num_pixels
    if callable(write_fn):
        write_fn(pixels)
