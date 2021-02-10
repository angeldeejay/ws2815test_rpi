"""BCM283x NeoPixel Driver Class"""
import time
import atexit
import _rpi_ws281x as ws
import sys
import digitalio

if sys.implementation.version[0] < 5:
    import adafruit_pypixelbuf as _pixelbuf
else:
    try:
        import _pixelbuf
    except ImportError:
        import adafruit_pypixelbuf as _pixelbuf

# LED configuration.
# pylint: disable=redefined-outer-name,too-many-branches,too-many-statements
# pylint: disable=global-statement,protected-access
LED_CHANNEL = 0
LED_FREQ_HZ = 800000  # Frequency of the LED signal.  We only support 800KHz
LED_DMA_NUM = 10  # DMA channel to use, can be 0-14.
LED_BRIGHTNESS = 255  # We manage the brightness in the neopixel library
LED_INVERT = 0  # We don't support inverted logic
LED_STRIP = None  # We manage the color order within the neopixel library

# a 'static' object that we will use to manage our PWM DMA channel
# we only support one LED strip per raspi
_led_strip = None
_buf = None


def neopixel_write(gpio, buf):
    """NeoPixel Writing Function"""
    global _led_strip  # we'll have one strip we init if its not at first
    # we save a reference to the buf, and if it changes we will cleanup and re-init.
    global _buf
    LED_CHANNEL = 1 if gpio._pin.id in [13, 19] else 0

    if _led_strip is None or buf is not _buf:
        # This is safe to call since it doesn't do anything if _led_strip is None
        neopixel_cleanup()

        # Create a ws2811_t structure from the LED configuration.
        # Note that this structure will be created on the heap so you
        # need to be careful that you delete its memory by calling
        # delete_ws2811_t when it's not needed.
        _led_strip = ws.new_ws2811_t()
        _buf = buf

        # Initialize all channels to off
        for channum in range(2):
            channel = ws.ws2811_channel_get(_led_strip, channum)
            ws.ws2811_channel_t_count_set(channel, 0)
            ws.ws2811_channel_t_gpionum_set(channel, 0)
            ws.ws2811_channel_t_invert_set(channel, 0)
            ws.ws2811_channel_t_brightness_set(channel, 0)

        channel = ws.ws2811_channel_get(_led_strip, LED_CHANNEL)

        # Initialize the channel in use
        count = 0
        if len(buf) % 3 == 0:
            # most common, divisible by 3 is likely RGB
            LED_STRIP = ws.WS2811_STRIP_RGB
            count = len(buf) // 3
        elif len(buf) % 4 == 0:
            LED_STRIP = ws.SK6812_STRIP_RGBW
            count = len(buf) // 4
        else:
            raise RuntimeError("We only support 3 or 4 bytes-per-pixel")

        ws.ws2811_channel_t_count_set(
            channel, count
        )  # we manage 4 vs 3 bytes in the library
        ws.ws2811_channel_t_gpionum_set(channel, gpio._pin.id)
        ws.ws2811_channel_t_invert_set(channel, LED_INVERT)
        ws.ws2811_channel_t_brightness_set(channel, LED_BRIGHTNESS)
        ws.ws2811_channel_t_strip_type_set(channel, LED_STRIP)

        # Initialize the controller
        ws.ws2811_t_freq_set(_led_strip, LED_FREQ_HZ)
        ws.ws2811_t_dmanum_set(_led_strip, LED_DMA_NUM)

        resp = ws.ws2811_init(_led_strip)
        if resp != ws.WS2811_SUCCESS:
            if resp == -5:
                raise RuntimeError(
                    "NeoPixel support requires running with sudo, please try again!"
                )
            message = ws.ws2811_get_return_t_str(resp)
            raise RuntimeError(
                "ws2811_init failed with code {0} ({1})".format(
                    resp, message)
            )
        atexit.register(neopixel_cleanup)

    channel = ws.ws2811_channel_get(_led_strip, LED_CHANNEL)
    if gpio._pin.id != ws.ws2811_channel_t_gpionum_get(channel):
        raise RuntimeError(
            "Raspberry Pi neopixel support is for one strip only!")

    if ws.ws2811_channel_t_strip_type_get(channel) == ws.WS2811_STRIP_RGB:
        bpp = 3
    else:
        bpp = 4
    # assign all colors!
    for i in range(len(buf) // bpp):
        r = buf[bpp * i]
        g = buf[bpp * i + 1]
        b = buf[bpp * i + 2]
        if bpp == 3:
            pixel = (r << 16) | (g << 8) | b
        else:
            w = buf[bpp * i + 3]
            pixel = (w << 24) | (r << 16) | (g << 8) | b
        ws.ws2811_led_set(channel, i, pixel)

    resp = ws.ws2811_render(_led_strip)
    if resp != ws.WS2811_SUCCESS:
        message = ws.ws2811_get_return_t_str(resp)
        raise RuntimeError(
            "ws2811_render failed with code {0} ({1})".format(
                resp, message)
        )
    time.sleep(0.001 * ((len(buf) // 100) + 1))  # about 1ms per 100 bytes


def neopixel_cleanup():
    """Cleanup when we're done"""
    global _led_strip

    if _led_strip is not None:
        # Ensure ws2811_fini is called before the program quits.
        ws.ws2811_fini(_led_strip)
        # Example of calling delete function to clean up structure memory.  Isn't
        # strictly necessary at the end of the program execution here, but is good practice.
        ws.delete_ws2811_t(_led_strip)
        _led_strip = None    # The MIT License (MIT)
#
# Copyright (c) 2016 Damien P. George
# Copyright (c) 2017 Scott Shawcroft for Adafruit Industries
# Copyright (c) 2019 Carter Nelson
# Copyright (c) 2019 Roy Hooper
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


"""
`neopixel` - NeoPixel strip driver
====================================================
* Author(s): Damien P. George, Scott Shawcroft, Carter Nelson, Roy Hooper
"""

# pylint: disable=ungrouped-imports
# Pixel color order constants
RGB = "RGB"
"""Red Green Blue"""
GRB = "GRB"
"""Green Red Blue"""
RGBW = "RGBW"
"""Red Green Blue White"""
GRBW = "GRBW"
"""Green Red Blue White"""


class NeoPixel(_pixelbuf.PixelBuf):
    """
    A sequence of neopixels.
    :param ~microcontroller.Pin pin: The pin to output neopixel data on.
    :param int n: The number of neopixels in the chain
    :param int bpp: Bytes per pixel. 3 for RGB and 4 for RGBW pixels.
    :param float brightness: Brightness of the pixels between 0.0 and 1.0 where 1.0 is full
    brightness
    :param bool auto_write: True if the neopixels should immediately change when set. If False,
    `show` must be called explicitly.
    :param str pixel_order: Set the pixel color channel order. GRBW is set by default.
    Example for Circuit Playground Express:
    .. code-block:: python
        import neopixel
        from board import *
        RED = 0x100000 # (0x10, 0, 0) also works
        pixels = neopixel.NeoPixel(NEOPIXEL, 10)
        for i in range(len(pixels)):
            pixels[i] = RED
    Example for Circuit Playground Express setting every other pixel red using a slice:
    .. code-block:: python
        import neopixel
        from board import *
        import time
        RED = 0x100000 # (0x10, 0, 0) also works
        # Using ``with`` ensures pixels are cleared after we're done.
        with neopixel.NeoPixel(NEOPIXEL, 10) as pixels:
            pixels[::2] = [RED] * (len(pixels) // 2)
            time.sleep(2)
    .. py:method:: NeoPixel.show()
        Shows the new colors on the pixels themselves if they haven't already
        been autowritten.
        The colors may or may not be showing after this function returns because
        it may be done asynchronously.
    .. py:method:: NeoPixel.fill(color)
        Colors all pixels the given ***color***.
    .. py:attribute:: brightness
        Overall brightness of the pixel (0 to 1.0)
    """

    def __init__(
        self, pin, n, *, bpp=3, brightness=1.0, auto_write=True, pixel_order=None
    ):
        if not pixel_order:
            pixel_order = GRB if bpp == 3 else GRBW
        else:
            if isinstance(pixel_order, tuple):
                order_list = [RGBW[order] for order in pixel_order]
                pixel_order = "".join(order_list)

        super().__init__(
            n, brightness=brightness, byteorder=pixel_order, auto_write=auto_write
        )

        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.OUTPUT

    def deinit(self):
        """Blank out the NeoPixels and release the pin."""
        self.fill(0)
        self.show()
        self.pin.deinit()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.deinit()

    def __repr__(self):
        return "[" + ", ".join([str(x) for x in self]) + "]"

    @property
    def n(self):
        """
        The number of neopixels in the chain (read-only)
        """
        return len(self)

    def write(self):
        """.. deprecated: 1.0.0
            Use ``show`` instead. It matches Micro:Bit and Arduino APIs."""
        self.show()

    def _transmit(self, buffer):
        neopixel_write(self.pin, buffer)
