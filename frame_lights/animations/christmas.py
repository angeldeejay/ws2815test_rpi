from time import sleep
from rpi_ws281x import Color

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
            print(instance)
            pixels_range = range(instance.led_count - 1, -1, -1) if instance.reverse else range(0, instance.led_count)
            for i in pixels_range:
                p = (i + ptr) % len(colors)
                instance.led_strip.setPixelColor(i, colors[p])
            instance.led_strip.show()
            ptr += 1
            ptr %= len(colors)
            sleep(instance.interval)
    except Exception as e:
        pass
        instance.log("Couldn't start strip light:\n\t* strip data: " + str(instance) + "\n\t* reason: " + str(e) + "\n", "error")
        while True:
            if not instance.thread_active: break

    
