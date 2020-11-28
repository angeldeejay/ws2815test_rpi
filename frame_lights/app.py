from threading import Thread
from time import sleep
from animations.christmas import animation_mock
from rpi_ws281x import PixelStrip, Color

class LedStrip:
    def __init__(self, name, gpio_pin=None, led_count=None, reverse=None, animation=None, interval=None, frequency=None):
        self.name = name
        self.gpio_pin = int(gpio_pin)
        self.led_count = int(led_count)
        self.frequency = int(self.__default_value(frequency, 800000))
        self.dma = 10
        self.brightness = 64
        self.interval = float(self.__default_value(interval, 0.1))
        self.reverse = self.__default_value(reverse, False)
        self.animation = self.__default_value(animation, self.__lambda)
        self.channel = 1 if gpio_pin in [13, 19, 41, 45, 53] else 0
        self.thread = None
        self.thread_active = False
        self.led_strip = PixelStrip(self.led_count, self.gpio_pin, self.frequency, self.dma, False, self.brightness, self.channel)

    def __lambda(self, instance):
        while True:
            if not instance.thread_active: break
            instance.log("Dummy lambda waiting...")
            sleep(instance.interval)

    def __default_value(self, value, default=None):
        return default if value in [None, ''] else value

    def start(self):
        self.thread_active = True
        self.thread = Thread(target=self.animation, daemon=True, args=[self])
        self.log("Starting thread")
        self.thread.start()

    def stop(self):
        self.thread_active = False
        self.log("Stopping thread")
        while self.thread.is_alive():
            self.thread.join()
            sleep(self.interval)

        for i in range(0, self.led_count):
            self.led_strip.setPixelColor(i, Color(0, 0, 0))
        self.led_strip.show()

        self.thread = None
        self.log("Thread stopped")

    def log(self, message, level="debug"):
        print(str('[{:^7}]'.format(level.upper())) + ' {' + str(self.name) + "}: " + str(message))

    def __repr__(self):
        return self.__class__.__name__ + str(vars(self))

if __name__ == '__main__':
    print("Press Ctrl-C to quit.")
    test_strip_top = LedStrip(name='WS2815 - TOP', gpio_pin=19, led_count=300, animation=animation_mock)
    # test_strip_right = LedStrip(name='5050 - RIGHT', gpio_pin=19, led_count=60, animation=animation_mock)
    test_strip_left = LedStrip(name='5050 - LEFT', gpio_pin=18, led_count=60, reverse=True, animation=animation_mock)

    test_strip_top.start()
    # test_strip_right.start()
    test_strip_left.start()
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        test_strip_top.stop()
        # test_strip_right.stop()
        test_strip_left.stop()
