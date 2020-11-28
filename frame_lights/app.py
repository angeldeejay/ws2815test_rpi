from sys import argv
from signal import signal, SIGSEGV
from threading import Thread
from time import sleep
from animations.christmas import animate as christmas_animation
from animations.rainbow import animate as rainbow_animation
from animations.snow import animate as snow_animation
from rpi_ws281x import PixelStrip, Color
from traceback import format_exc

class LedStrip:
    def __init__(self, name, gpio_pin=None, led_count=None, reverse=None, interval=None, frequency=None):
        self.animation = None
        self.name = name
        self.gpio_pin = int(gpio_pin)
        self.led_count = int(led_count)
        self.frequency = int(self.__default_value(frequency, 800000))
        self.dma = 10
        self.brightness = 64
        self.interval = float(self.__default_value(interval, 0.05))
        self.reverse = self.__default_value(reverse, False)
        self.channel = 1 if gpio_pin in [13, 19, 41, 45, 53] else 0
        self.thread = None
        self.thread_active = False
        self.led_strip = PixelStrip(self.led_count, self.gpio_pin, self.frequency, self.dma, False, self.brightness, self.channel)
        self.changed = False

    def set_animation(self, animation_fn):
        self.animation = self.__default_value(animation_fn, self.__lambda)

    def set_color(self, i, color):
        try:
            self.led_strip.setPixelColor(i, color)
            self.changed = True
        except:
            pass

    def repaint(self):
        try:
            self.led_strip.show()
            True
        except:
            pass

    def begin(self):
        try:
            self.led_strip.begin()
            True
        except:
            error_output = "\n\n\t" + format_exc().replace("\n", "\n\t")
            self.log("\n\t" + error_output + "\n", "error")
            pass

    def __lambda(self, instance):
        while True:
            if not instance.thread_active: break
            sleep(instance.interval)

    def __default_value(self, value, default=None):
        return default if value is None else value

    def start(self):
        if self.animation is not None:
            self.thread_active = True
            self.thread = Thread(target=self.animation, daemon=True, args=[self])
            self.log("Starting thread")
            self.thread.start()

    def stop(self):
        self.thread_active = False
        if self.thread is not None:
            self.log("Stopping thread")
            while self.thread.is_alive():
                sleep(0.01)

        if self.changed:
            try:
                for i in range(0, self.led_count):
                    self.set_color(i, 0, 0, 0)
                self.repaint()
            except:
                pass

        self.thread = None
        self.changed = False
        self.log("Shutted down")

    def log(self, message, level="debug"):
        print(str('[{:^7}]'.format(level.upper())) + ' {' + str(self.name) + "}: " + str(message))

    def __repr__(self):
        return self.__class__.__name__ + str(vars(self))

def stop_animations(strips):
    for strip in strips:
        strip.stop()

def start_animations(strips, animation_name, animation_fn):
    print("Starting animation: " + animation_name)
    for strip in strips:
        strip.set_animation(animation_fn)
        strip.start()

if __name__ == '__main__':
    strips = [
        LedStrip(name='WS2815 - Yellow', gpio_pin=21, interval=0.05, led_count=300),
        LedStrip(name='5050 - Red', gpio_pin=18, interval=0.05, led_count=60),
        LedStrip(name='5050 - Blue', gpio_pin=13, interval=0.05, led_count=60, reverse=True),
    ]

    try:
        print("Press Ctrl-C to quit.")
        if len(argv) > 1 and argv[1] == '--off':
            stop_animations(strips)
        else:
            animations = [
                ("Christmas", christmas_animation),
                ("Snow", snow_animation),
                ("Rainbow", rainbow_animation),
            ]

            animation_index = 0
            while True:
                animation_name, animation_fn = animations[animation_index]
                start_animations(strips, animation_name, animation_fn)
                sleep(30)
                stop_animations(strips)
                animation_index = 0 if animation_index == len(animations) - 1 else (animation_index + 1)

    except KeyboardInterrupt:
        pass
    except:
        pass
    finally:
        stop_animations(strips)