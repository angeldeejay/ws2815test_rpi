from time import sleep
from rpi_ws281x import PixelStrip, Color
from traceback import format_exc

def animation_mock(instance):
    colors = [
        Color(255, 0, 0), Color(255, 0, 0), Color(255, 0, 0), Color(255, 0, 0), Color(255, 0, 0), 
        Color(0, 255, 0), Color(0, 255, 0), Color(0, 255, 0), Color(0, 255, 0), Color(0, 255, 0), 
    ]
    ptr = 0
    led_strip = PixelStrip(instance.led_count, instance.gpio_pin, instance.frequency, instance.dma, False, instance.brightness, instance.channel)
    try:
        led_strip.begin()
        while True:
            if not instance.thread_active: break
            print(instance)
            pixels_range = range(instance.led_count - 1, -1, -1) if instance.reverse else range(0, instance.led_count)
            for i in pixels_range:
                p = (i + ptr) % len(colors)
                led_strip.setPixelColor(i, colors[p])
            led_strip.show()
            ptr += 1
            ptr %= len(colors)
            sleep(instance.interval)
    except Exception:
        error_output = "\n\n\t" + format_exc().replace("\n", "\n\t")
        instance.log("Couldn't start strip light:\n\t* strip data: " + str(instance) + "\n\t* reason:" + error_output + "\n", "error")
        while True:
            if not instance.thread_active: break
        pass

    
