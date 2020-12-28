import time
import board
import neopixel
import random
import math
import serial
import ctypes
from lib.utils import *

### ColorAll2Color allows two alternating colors to be shown
def ColorAll2Color(pixels, c1, c2):
    num_pixels = pixels._pixels
    for i in range(num_pixels):
        if(i % 2 == 0): # even
            pixels[i] = c1
        else: # odd
            pixels[i] = c2
    pixels.show()

# ColorAllColorGroup(colorObject) allows colors to be
# - colorObject: list of color objects. example ((255, 0, 0), (0, 255, 0))
def ColorAllColorGroup(pixels, colorObject):
    num_pixels = pixels._pixels
    colorCount = len(colorObject)
    for i in range(num_pixels):
            colorIndex = i % colorCount
            pixels[i] = colorObject[colorIndex]
    pixels.show()

def CandyCaneCustom(pixels, c1, c2, thisbright, size, delay, cycles):
    num_pixels = pixels._pixels
    N3  = int(num_pixels / size)
    N6  = int(num_pixels / (size*2))
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
            pixels[j0] = brightnessRGB(c1[0], c1[1], c1[2], int(thisbright*.75))
            pixels[j1] = brightnessRGB(c2[0], c2[1], c2[2], thisbright)
            pixels[j2] = brightnessRGB(c1[0], c1[1], c1[2], int(thisbright*.75))
            pixels[j3] = brightnessRGB(c2[0], c2[1], c2[2], thisbright)
            pixels[j4] = brightnessRGB(c1[0], c1[1], c1[2], int(thisbright*.75))
            pixels[j5] = brightnessRGB(c2[0], c2[1], c2[2], thisbright)
            # show pixel values
            pixels.show()
            time.sleep(delay)

def RunningLights(pixels, WaveDelay, cycles):
    num_pixels = pixels._pixels
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
        pixels.show()
        time.sleep(WaveDelay)

def SnowSparkle(pixels, Count, SparkleDelay, SpeedDelay):
    num_pixels = pixels._pixels
    # gather existing colors in strip of pixel
    strip = []
    for i in range(num_pixels):
        strip.append(pixels[i])
    for i in range(Count):
        index = random.randint(0, num_pixels - 1)
        pixels[index] = (255, 255, 255)
        pixels.show()
        time.sleep(SparkleDelay)
        pixels[index] = strip[index]
        pixels.show()
        time.sleep(SpeedDelay)

def HalloweenEyes(pixels, red, green, blue, EyeWidth, EyeSpace, Fade, Steps, FadeDelay, EndPause, cycles):
    num_pixels = pixels._pixels
    for c in range(cycles):
        # gather existing colors in strip of pixel
        strip = []
        for i in range(num_pixels):
            strip.append(pixels[i])
        # define eye1 and eye2 location
        StartPoint  = random.randint(0, num_pixels - (2*EyeWidth) - EyeSpace)
        Start2ndEye = StartPoint + EyeWidth + EyeSpace
        #  set color of eyes for given location
        for i in range(EyeWidth):
            pixels[StartPoint + i] = (red, green, blue)
            pixels[Start2ndEye + i] = (red, green, blue)
        pixels.show()
        # if user wants fading, then fadeout pixel color
        if Fade == True:
            for j in range(Steps, - 1, - 1):
                r = (j / Steps)*red
                g = (j / Steps)*green
                b = (j / Steps)*blue
                for i in range(EyeWidth):
                    pixels[StartPoint + i] = ((int(r), int(g), int(b)))
                    pixels[Start2ndEye + i] = ((int(r), int(g), int(b)))
                pixels.show()
                time.sleep(FadeDelay)
        # Set all pixels to back
        # set color of eyes for given location
        for i in range(EyeWidth):
            pixels[StartPoint + i] = strip[StartPoint + i]
            pixels[Start2ndEye + i] = strip[Start2ndEye + i]
        pixels.show()
        # pause before changing eye location
        time.sleep(EndPause)

# HeartBeat - mimics a heart beat pulse, with 2 beats at different speeds. The existing colors
# on the pixel strip are preserved, rather than a single color.
#
# HeartBeat(beat1Step, beat1FadeInDelay, beat1FadeOutDelay, beat1Delay,
#                     beat2Step, beat2FadeInDelay, beat2FadeOutDelay, beat1Delay, cycles):
# HeartBeat(3, .005, .003, 0.001, 6, .002, .003, 0.05, 10)
#
#   beat1Step: (1 - 255) first beat color transition step
#   beat1FadeInDelay: (0 - 2147483647) first beat fade in trasition speed, in seconds
#   beat1FadeOutDelay: (0 - 2147483647) first beat fade out trasition speed, in seconds
#   beat1Delay: (0 - 2147483647)  beat time delay bewteen frist and sencond beat, in seconds
#   beat2Step: (1 - 255) second beat color transition step
#   beat2FadeInDelay: (0 - 2147483647) second beat fade in trasition speed, in seconds
#   beat2FadeOutDelay: (0 - 2147483647) second beat fade out trasition speed, in seconds
#   beat1Delay: (0 - 2147483647)  beat time delay bewteen sencond and first beat, in seconds
#   cycles: (1 - 2147483647) number of times this effect will run
def HeartBeat(pixels, beat1Step, beat1FadeInDelay, beat1FadeOutDelay, beat1Delay, beat2Step, beat2FadeInDelay, beat2FadeOutDelay, beat2Delay, cycles):
    num_pixels = pixels._pixels
    # gather existing colors in strip of pixel
    strip = []
    for i in range(num_pixels):
        strip.append(pixels[i])
    for loop in range(cycles):
        for ii in range(1, 252, beat1Step): #for (ii = 1 ; ii <252 ; ii = ii = ii + x)
            for index in range(num_pixels):
                r = strip[index][0]
                g = strip[index][1]
                b = strip[index][2]
                pixels[index] = brightnessRGB(r, g, b, ii)
                #pixels.fill(brightnessRGB(redo, greeno, blueo, ii)) #strip.setBrightness(ii)
            pixels.show()
            time.sleep(beat1FadeInDelay)
        for ii in range(252, 3, - beat1Step): #for (int ii = 252 ; ii > 3 ; ii = ii - x){
            for index in range(num_pixels):
                r = strip[index][0]
                g = strip[index][1]
                b = strip[index][2]
                pixels[index] = brightnessRGB(r, g, b, ii)
                #pixels.fill(brightnessRGB(redo, greeno, blueo, ii)) #strip.setBrightness(ii)
            pixels.show()
            time.sleep(beat1FadeOutDelay)
        time.sleep(beat1Delay)
        for ii in range(1, 252, beat1Step): #for (int ii = 1 ; ii <255 ; ii = ii = ii + y){
            for index in range(num_pixels):
                r = strip[index][0]
                g = strip[index][1]
                b = strip[index][2]
                pixels[index] = brightnessRGB(r, g, b, ii)
                #pixels.fill(brightnessRGB(redo, greeno, blueo, ii)) #strip.setBrightness(ii)
            pixels.show()
            time.sleep(beat2FadeInDelay)
        for ii in range(252, 3, - beat1Step): #for (int ii = 255 ; ii > 1 ; ii = ii - y){
            for index in range(num_pixels):
                r = strip[index][0]
                g = strip[index][1]
                b = strip[index][2]
                pixels[index] = brightnessRGB(r, g, b, ii)
                #pixels.fill(brightnessRGB(redo, greeno, blueo, ii)) #strip.setBrightness(ii)
            pixels.show()
            time.sleep(beat2FadeOutDelay)
        time.sleep(.050)


def Rotate(delay, cycles):
    num_pixels = pixels._pixels
    # gather existing colors in strip of pixel
    strip = []
    for i in range(num_pixels):
        strip.append(pixels[i])
    for loop in range(cycles):
        pixels[0] = pixels[num_pixels - 1]
        # rotate pixel positon
        for i in range(num_pixels - 1, 0, - 1):
            pixels[i] = pixels[i - 1]
        # there is an issue with first 2 pixels are same color
        #pixels[0] = (0, 0, 0)
        pixels.show()
        time.sleep(delay)


def CylonBounce(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay, cycles):
    for i in range(cycles):
        num_pixels = pixels._pixels
        for i in range(num_pixels - EyeSize - 1):
            pixels.fill((0, 0, 0))
            pixels[i] = (int(red / 10), int(green / 10), int(blue / 10))
            for j in range(1, EyeSize + 1):
                pixels[i + j] = (red, green, blue)
            pixels[i + EyeSize + 1] = (int(red / 10), int(green / 10), int(blue / 10))
            pixels.show()
            time.sleep(SpeedDelay)
        time.sleep(ReturnDelay)

        for i in range(num_pixels - EyeSize - 2, - 1, - 1):
            pixels.fill((0, 0, 0))
            pixels[i] = (int(red / 10), int(green / 10), int(blue / 10))
            for j in range(1, EyeSize + 1):
                pixels[i + j] = (red, green, blue)
            pixels[i + EyeSize + 1] = (int(red / 10), int(green / 10), int(blue / 10))
            pixels.show()
            time.sleep(SpeedDelay)
        time.sleep(ReturnDelay)

# RainbowCycle: rotate colors using rainbow scheme.
#
#   SpeedDelay: (0 - ...) slow down the effect by injecting a delay in Sec. 0=no delay, .05=50msec, 2=2sec
def RainbowCycle(pixels, SpeedDelay, cycles):
    num_pixels = pixels._pixels
    order = pixels._byteorder_string
    for i in range(cycles):
        for j in range(255):
            for i in range(num_pixels):
                pixel_index = (i * 256 // num_pixels) + j
                pixels[i] = wheel(pixel_index & 255, order)
            pixels.show()
            time.sleep(SpeedDelay)

# FireCustom: makes the strand of pixels show an effect that looks flame. This effect also
# adds more detail control of "sparks" that inject "heat" to the effect, thus changing color
# and flame length. The spark position can also be controled via start and end range.
# Color options include red, green, and blue.
#
#   CoolingRangeStart: (0 - 255) cooling random value, start range
#   CoolingRangeEnd: (0 - 255) cooling random value, end range
#   Sparking: (0 - 100)  chance of sparkes are added randomly controld througn a % value, 100= 100% and 0 = 0%
#   SparkingRangeStart: (0 - number of pixels) spark position random value, start range
#   SparkingRangeEnd: (0 - number of pixels) spark position random value, end range
#   SpeedDelay: (0 - ...) slow down the effect by injecting a delay in Sec. 0=no delay, .05=50msec, 2=2sec
#
# Improvements:
#  - add choice for 3 diffrent fire effect logic.
#  - add choice to control heat values "random.randint(160, 255)"
#  - add choice for flame color options include red, green, and blue.
def FireCustom(pixels, CoolingRangeStart, CoolingRangeEnd, Sparking, SparkingRangeStart, SparkingRangeEnd, SpeedDelay, cycles):
    num_pixels = pixels._pixels
    # intialize heat array, same size of as the strip of pixels
    heat = []
    for i in range(num_pixels):
        heat.append(0)
    #
    for loop in range(cycles):
        cooldown = 0
        # Step 1.  Cool down every cell a little
        for i in range(num_pixels):
            cooldown = random.randint(CoolingRangeStart, CoolingRangeEnd)
            if cooldown > heat[i]:
                heat[i]=0
            else:
                heat[i]=heat[i] - cooldown
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
            heatramp = t192 & 63 # 0..63  0x3f=63
            heatramp <<= 2 # scale up to 0..252
            # figure out which third of the spectrum we're in:
            if t192 > 0x80: # hottest 128 = 0x80
                pixels[j] = (255, 255, int(heatramp))
            elif t192 > 0x40: # middle 64 = 0x40
                pixels[j] = (255, int(heatramp), 0)
            else: # coolest
                pixels[j] = (int(heatramp), 0, 0)
        pixels.show()
        time.sleep(SpeedDelay)

# FireCustomMirror: makes the strand of pixels show an effect that looks flame. This is simular to FireCustom,
# however it mirrors the effect on top and bottom  (rather than using just from bottom). The intent is to
# have a fire effect that could be used 144 pixel strip for a lanyard id.
#
#   CoolingRangeStart: (0 - 255) cooling random value, start range
#   CoolingRangeEnd: (0 - 255) cooling random value, end range
#   Sparking: (0 - 100)  chance of sparkes are added randomly controld througn a % value, 100= 100% and 0 = 0%
#   SparkingRangeStart: (0 - number of pixels) spark position random value, start range
#   SparkingRangeEnd: (0 - number of pixels) spark position random value, end range
#   SpeedDelay: (0 - ...) slow down the effect by injecting a delay in Sec. 0=no delay, .05=50msec, 2=2sec
#
# Improvements:
#  - add choice for 3 diffrent fire effect logic.
#  - add choice to control heat values "random.randint(160, 255)"
#  - add choice for flame color options include red, green, and blue.
def FireCustomMirror(pixels, CoolingRangeStart, CoolingRangeEnd, Sparking, SparkingRangeStart, SparkingRangeEnd, SpeedDelay, cycles):
    num_pixels = pixels._pixels
    # intialize heat array, same size of as the strip of pixels
    heat = []
    halfNumPixel = int(num_pixels / 2) # note that this will round down
    for i in range(halfNumPixel):
        heat.append(0)
    #
    for loop in range(cycles):
        cooldown = 0
        # Step 1.  Cool down every cell a little
        for i in range(halfNumPixel):
            cooldown = random.randint(CoolingRangeStart, CoolingRangeEnd)
            if cooldown > heat[i]:
                heat[i]=0
            else:
                heat[i]=heat[i] - cooldown
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
            heatramp = t192 & 63 # 0..63  0x3f=63
            heatramp <<= 2 # scale up to 0..252
            # figure out which third of the spectrum we're in for color:
            if t192 > 0x80: # hottest 128 = 0x80
                colortemp = (255, 255, int(heatramp))
            elif t192 > 0x40: # middle 64 = 0x40
                colortemp = (255, int(heatramp), 0)
            else: # coolest
                colortemp = (int(heatramp), 0, 0)
            pixels[j] = colortemp
            pixels[num_pixels - 1 - j] = colortemp
        pixels.show()
        time.sleep(SpeedDelay)

def TheaterChaseCustom(pixels, colorobj, darkspace, cycles, SpeedDelay):
    num_pixels = pixels._pixels
    colorCount = len(colorobj)
    n = colorCount + darkspace
    for j in range(cycles):
        for q in range(n):
            for i in range(0, num_pixels, n):
                for index in range(0, colorCount, 1):
                    if i + q + index < num_pixels:
                        #print("pixel=", i + q + index, "index", index, "i", i, "q", q, "colorobj[index]", colorobj[index])
                        pixels[i + q + index] = colorobj[index]
            pixels.show()
            time.sleep(SpeedDelay)
            pixels.fill((0, 0, 0))
            for i in range(0, num_pixels, n):
                for index in range(0, colorCount, 1):
                    if i + q + index < num_pixels:
                        pixels[i + q + index] = (0, 0, 0)

def NewKITT(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay, cycles):
    for i in range(cycles):
        RightToLeft(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay)
        LeftToRight(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay)
        OutsideToCenter(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay)
        CenterToOutside(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay)
        LeftToRight(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay)
        RightToLeft(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay)
        OutsideToCenter(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay)
        CenterToOutside(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay)

def CenterToOutside(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay):
    num_pixels = pixels._pixels
    for i in range(int((num_pixels - EyeSize) / 2), - 1, - 1):
        pixels.fill((0, 0, 0))
        pixels[i] = (int(red / 10), int(green / 10), int(blue / 10))

        for j in range(1, EyeSize + 1):
            pixels[i + j] = (red, green, blue)
        
        pixels[i + EyeSize + 1] = (int(red / 10), int(green / 10), int(blue / 10))
        pixels[num_pixels - i - j] = (int(red / 10), int(green / 10), int(blue / 10))

        for j in range(1, EyeSize + 1):
            pixels[num_pixels - i - j] = (red, green, blue)

        pixels[num_pixels - i - EyeSize - 1] = (int(red / 10), int(green / 10), int(blue / 10))
        pixels.show()
        time.sleep(SpeedDelay)

    time.sleep(ReturnDelay)

def OutsideToCenter(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay):
    num_pixels = pixels._pixels

    for i in range(int(((num_pixels - EyeSize) / 2) + 1)):
        pixels.fill((0, 0, 0))
        pixels[i] = (int(red / 10), int(green / 10), int(blue / 10))

        for j in range(1, EyeSize + 1):
            pixels[i + j] = (red, green, blue) 
        
        pixels[i + EyeSize + 1] = (int(red / 10), int(green / 10), int(blue / 10))
        pixels[num_pixels - i - 1] = (int(red / 10), int(green / 10), int(blue / 10))

        for j in range(1, EyeSize + 1):
            pixels[num_pixels - i - j] = (red, green, blue)
        
        pixels[num_pixels - i - EyeSize - 1] = (int(red / 10), int(green / 10), int(blue / 10))
        pixels.show()
        time.sleep(SpeedDelay)
  
    time.sleep(ReturnDelay)


def LeftToRight(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay):
    num_pixels = pixels._pixels
    for i in range(num_pixels - EyeSize - 2):
        pixels.fill((0, 0, 0))
        pixels[i] = (int(red / 10), int(green / 10), int(blue / 10))

        for j in range(1, EyeSize + 1):
            pixels[i + j] = (red, green, blue)

        pixels[i + EyeSize + 1] = (int(red / 10), int(green / 10), int(blue / 10))
        pixels.show()
        time.sleep(SpeedDelay)
    
    time.sleep(ReturnDelay)


def RightToLeft(pixels, red, green, blue, EyeSize, SpeedDelay, ReturnDelay):
    num_pixels = pixels._pixels
    for i in range(num_pixels - EyeSize - 2, 0, - 1):
        pixels.fill((0, 0, 0))
        pixels[i] = (int(red / 10), int(green / 10), int(blue / 10))

        for j in range(1, EyeSize + 1):
            pixels[i + j] = (red, green, blue)

        pixels[i + EyeSize + 1] = (int(red / 10), int(green / 10), int(blue / 10))
        pixels.show()
        time.sleep(SpeedDelay)
  
    time.sleep(ReturnDelay)

def Twinkle(pixels, red, green, blue, Count, SpeedDelay, OnlyOne):
    num_pixels = pixels._pixels
    pixels.fill((0, 0, 0))
  
    for i in range(Count):
        pixels[random.randint(0, num_pixels - 1)] = (red, green, blue)
        pixels.show()
        time.sleep(SpeedDelay)
        if OnlyOne:
            pixels.fill((0, 0, 0))

    time.sleep(SpeedDelay)


def TwinkleRandom(pixels, Count, SpeedDelay, OnlyOne):
    num_pixels = pixels._pixels
    pixels.fill((0, 0, 0))

    for i in range(Count):
        pixels[random.randint(0, num_pixels - 1)] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        pixels.show()
        time.sleep(SpeedDelay)
        if OnlyOne:
            pixels.fill((0, 0, 0))

    time.sleep(SpeedDelay)


def Sparkle(pixels, red, green, blue, Count, SpeedDelay):
    num_pixels = pixels._pixels

    for i in range(Count):    
        Pixel = random.randint(0, num_pixels - 1)
        pixels[Pixel] = (red, green, blue)
        pixels.show()
        time.sleep(SpeedDelay)
        pixels[Pixel] = (0, 0, 0)

def SnowSparkle(pixels, red, green, blue, Count, SparkleDelay, SpeedDelay):
    num_pixels = pixels._pixels
    pixels.fill((red, green, blue))

    for i in range(Count):
        Pixel = random.randint(0, num_pixels - 1)
        pixels[Pixel] = (255, 255, 255)
        pixels.show()
        time.sleep(SparkleDelay)
        pixels[Pixel] = (red, green, blue)
        pixels.show()
        time.sleep(SpeedDelay)

def MeteorRain(pixels, red, green, blue, meteorSize, meteorTrailDecay, meteorRandomDecay, SpeedDelay, cycles): 
    num_pixels = pixels._pixels
    for loop in range(cycles):
        pixels.fill((0, 0, 0))
        
        for i in range(num_pixels*2):
            # fade brightness all LEDs one step
            for j in range(num_pixels):
                if (not meteorRandomDecay) or (random.randint(0, 10) > 5):
                    pixels[ledNo] = fadeToBlack(pixels[ledNo], j, meteorTrailDecay)      
            
            # draw meteor
            for j in range(meteorSize):
                if (i - j < num_pixels) and (i - j >= 0): 
                    pixels[i - j] = (red, green, blue)

            pixels.show()
            time.sleep(SpeedDelay)

def shutdown(pixels):
    for i in range(pixels._pixels):
        pixels[i] = (0, 0, 0)
    pixels.show()

