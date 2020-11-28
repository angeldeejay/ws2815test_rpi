from time import sleep
from rpi_ws281x import Color
from traceback import format_exc

def animation_mock(instance):
    colors = [
        Color(255, 0, 0), Color(255, 0, 0), Color(255, 0, 0), Color(255, 0, 0), Color(255, 0, 0), 
        Color(0, 255, 0), Color(0, 255, 0), Color(0, 255, 0), Color(0, 255, 0), Color(0, 255, 0), 
    ]
    ptr = 0
    try:
        instance.led_strip.begin()
        while True:
            if not instance.thread_active: break
            instance.log(str(ptr))
            pixels_range = range(instance.led_count - 1, -1, -1) if instance.reverse else range(0, instance.led_count)
            for i in pixels_range:
                p = (i + ptr) % len(colors)
                instance.led_strip.setPixelColor(i, colors[p])
            instance.led_strip.show()
            if instance.reverse:
                ptr = ptr + 1
            else:
                ptr = ptr - 1
            ptr %= len(colors)
            sleep(instance.interval)
    except Exception:
        error_output = "\n\n\t" + format_exc().replace("\n", "\n\t")
        instance.log("Couldn't start strip light:\n\t* strip data: " + str(instance) + "\n\t* reason:" + error_output + "\n", "error")
        while True:
            if not instance.thread_active: break
        pass

    
