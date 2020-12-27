# import time
# from rpi_ws281x import PixelStrip, Color

# LED_COUNT = 300       # number of LED pixels.
# LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
# LED_DMA = 10          # DMA channel to use for generating signal (try 10)
# LED_BRIGHTNESS = 64   # Set to 0 for darkest and 255 for brightest
# LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
# LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# colors = [
#     Color(255, 0, 0),
#     Color(255, 153, 0),
#     Color(204, 255, 0),
#     Color(51, 255, 0),
#     Color(0, 255, 102),
#     Color(0, 255, 255),
#     Color(0, 102, 255),
#     Color(51, 0, 255),
#     Color(204, 0, 255),
#     Color(255, 0, 153),
# ]
# ptr = 0

# if __name__ == '__main__':
#     strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
#     strip.begin()

#     print("Press Ctrl-C to quit.")
#     try:
#         while True:
#             for i in range(0, LED_COUNT):
#                 p = (i + ptr) % len(colors)
#                 strip.setPixelColor(i, colors[p])
#             strip.show()
#             ptr -= 1
#             if ptr < 0:
#                 ptr = len(colors)
#             time.sleep(0.025)

#     except KeyboardInterrupt:
#         for i in range(0, LED_COUNT):
#             strip.setPixelColor(i, Color(0, 0, 0))
#         strip.show()

# Simple test for NeoPixels on Raspberry Pi
import time
import board
import neopixel
 
 
# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18
 
# The number of NeoPixels
num_pixels = 11
 
# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.RGB
 
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER
)
 
 
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)
 
 
def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)
 
if __name__ == '__main__':
    try:
        while True:
            rainbow_cycle(0.001)  # rainbow cycle with 1ms delay per step
    except KeyboardInterrupt:
        pixels.deinit()
