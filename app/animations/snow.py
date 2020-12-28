from time import sleep
from rpi_ws281x import Color
from traceback import format_exc

def animate(instance):
    colors = [
        Color(32, 32, 32), Color(64, 64, 64), Color(128, 128, 128), Color(191, 191, 191), Color(255, 255, 255), Color(255, 255, 255),
        Color(0, 0, 0), Color(0, 0, 0), Color(0, 0, 0), Color(0, 0, 0), Color(0, 0, 0), Color(0, 0, 0),
    ]
    colors.reverse() if instance.reverse else True
    try:
        instance.begin()
        while True:
            if not instance.thread_active:
                break
            for i in range(0, instance.led_count):
                p = i % len(colors)
                instance.set_pixel_color(i, colors[p])
            instance.show()
            if instance.reverse:
                colors = colors[1:] + [colors[0]]
            else:
                colors.insert(0, colors.pop())
            sleep(instance.interval)
    except Exception:
        pass
        error_output = "\n\n\t" + format_exc().replace("\n", "\n\t")
        instance.log("Couldn't start strip light:\n\t* strip data: " + str(instance) + "\n\t* reason:" + error_output + "\n", "error")
        while True:
            if not instance.thread_active:
                break

    
