import time
from rpi_ws281x import PixelStrip, Color

LED_COUNT = 300       # number of LED pixels.
LED_PIN = 19          # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 64  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53

colors = [
    Color(255, 0, 0), Color(255, 0, 0), Color(255, 0, 0), Color(255, 0, 0), Color(255, 0, 0), 
    Color(0, 255, 0), Color(0, 255, 0), Color(0, 255, 0), Color(0, 255, 0), Color(0, 255, 0), 
]
ptr = 0

if __name__ == '__main__':
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    print("Press Ctrl-C to quit.")
    try:
        while True:
            for i in range(0, LED_COUNT):
                p = (i + ptr) % len(colors)
                strip.setPixelColor(i, colors[p])
            strip.show()
            ptr += 1
            ptr %= len(colors)
            time.sleep(0.1)

    except KeyboardInterrupt:
        for i in range(0, LED_COUNT):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
