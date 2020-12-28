from time import sleep
from random import randrange
from rpi_ws281x import Color
from traceback import format_exc

def animate(instance):
    colors = [
        [ 1, 0, 0 ],
        [ 0, 1, 0 ],
        [ 0, 0, 1 ],
        [ 1, 1, 0 ],
        [ 1, 0, 1 ],
        [ 0, 1, 1 ],
        [ 1, 1, 1 ]
    ]

    pixels = [ [ 0, 0, 0 ] ] * instance.led_count
    steps = [0] * instance.led_count

    try:
        instance.begin()
        while True:
            if not instance.thread_active:
                break

            while True:
                if not instance.thread_active:
                    break
                p = randrange(0, instance.led_count, 1)
                if steps[p] == 0:
                    steps[p] = 1
                    pixels[p] = randrange(0, len(colors))
                    break

            for i in range(0, instance.led_count):
                if steps[i] > 0:
                    c = (51 - abs(51 - steps[i])) * 5
                    instance.set_pixel_color(i, Color(colors[pixels[i]][0] * c, colors[pixels[i]][1] * c, colors[pixels[i]][2] * c))
                    steps[i] += 1
                    if (steps[i] == 102):
                        steps[i] = 0
                else:
                    instance.set_pixel_color(i, Color(0, 0, 0))
            instance.show()
            sleep(0.0005)

    except Exception:
        pass
        error_output = "\n\n\t" + format_exc().replace("\n", "\n\t")
        instance.log("Couldn't start strip light:\n\t* strip data: " + str(instance) + "\n\t* reason:" + error_output + "\n", "error")
        while True:
            if not instance.thread_active:
                break

    
