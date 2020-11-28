import time, argparse
from rpi_ws281x import PixelStrip, Color

parser = argparse.ArgumentParser()
parser.add_argument('--led-pin', default=19, help='GPIO led pin')
args = parser.parse_args()
print(args.led_pin)

#      19
# ++++++++++++
# +          +
# +          +
# + 18    19 +

RED_LED_PIN     = 19
RED_LED_CHANNEL = 0
if RED_LED_PIN in [13, 19, 41, 45, 53]:
    RED_LED_CHANNEL = 1

YELLOW_LED_PIN     = 19
YELLOW_LED_CHANNEL = 0
if YELLOW_LED_PIN in [13, 19, 41, 45, 53]:
    YELLOW_LED_CHANNEL = 1

BLUE_LED_PIN     = 19
BLUE_LED_CHANNEL = 0
if BLUE_LED_PIN in [13, 19, 41, 45, 53]:
    BLUE_LED_CHANNEL = 1

LED_COUNT = 300                 # number of LED pixels.
# LED_PIN = int(args.led_pin)     # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000            # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10                    # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 64             # Set to 0 for darkest and 255 for brightest
LED_INVERT = False              # True to invert the signal (when using NPN transistor level shift)
# LED_CHANNEL = 0                 # set to '1' for GPIOs 13, 19, 41, 45 or 53
# if LED_PIN in [13, 19, 41, 45, 53]:
#     LED_CHANNEL = 1

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
