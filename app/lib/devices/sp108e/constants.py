from enum import IntEnum


class ConstantEnum(IntEnum):
    """
    Constant Enum super class
    """
    @classmethod
    def is_member(cls, value: int):
        return value in cls.__members__.values()

    @classmethod
    def cast(cls, value: int):
        for k, v in cls.__members__.items():
            if v == value:
                return cls[k]

        return None


class Command(ConstantEnum):
    """
    Commands that can be sent to the device.

    Mostly for internal use, prefer to use the functions on SP108E_Controller instead.

    To be used with SP108E_Controller.send_command()
    """
    TOGGLE = 0xAA
    SET_COLOR = 0x22
    SET_BRIGHTNESS = 0x2A
    SET_SPEED = 0x03
    SET_PRESET = 0x2C
    SET_CUSTOM = 0x02
    SET_LIGHTS_PER_SEGMENT = 0x2D
    SET_SEGMENT_COUNT = 0x2E
    SYNC = 0x10


class CommandFlag(ConstantEnum):
    """
    All messages to the device must be wrapped in a start and end flag

    Mostly for internal use, prefer to use the functions on SP108E_Controller instead.
    """
    START = 0x38
    END = 0x83


class Effect(ConstantEnum):
    """
    Effects super class
    """
    @classmethod
    def get_effect(cls, effect: int):
        for derived in Effect.__subclasses__():
            for constant, value in derived.__members__.items():
                if effect == value:
                    return derived[constant]

        raise Exception(f'Invalid effect {effect}')

    @classmethod
    def get_command(cls, effect: int):
        for derived in Effect.__subclasses__():
            if derived.is_member(effect):
                return Command.SET_CUSTOM if derived.__name__ == 'CustomEffect' else Command.SET_PRESET

        raise Exception(f'Invalid effect {effect}')


class PresetEffect(Effect):
    """
    Preset effects that are for a single, user customizable color
    """
    RAINBOW = 0,
    COLORS_CHANGING_METEORS = 1,
    FLOWING_COLORS = 2,
    OVERLAYING_FLOWING = 3,
    RED_STACKING = 4,
    GREEN_STACKING = 5,
    BLUE_STACKING = 6,
    COLORS_CHANGING_STACKING = 7,
    FADING_FLOWING = 8,
    COLOR_CHANGING_CROSS_FLOWING = 9,
    CROSS_FLOWING = 10,
    CHASING_COLOR_DOTS = 11,
    COLORFUL_WAVE = 12,
    BURNING_FIRE = 13,
    RED_METEOR = 14,
    GREEN_METEOR = 15,
    BLUE_METEOR = 16,
    YELLOW_METEOR = 17,
    CYAN_METEOR = 18,
    PURPLE_METEOR = 19,
    WHITE_METEOR = 20,
    RED_WAVE = 21,
    GREEN_WAVE = 22,
    BLUE_WAVE = 23,
    YELLOW_WAVE = 24,
    CYAN_WAVE = 25,
    PURPLE_WAVE = 26,
    WHITE_WAVE = 27,
    RED_CHASING_DOTS = 28,
    GREEN_CHASING_DOTS = 29,
    BLUE_CHASING_DOTS = 30,
    YELLOW_CHASING_DOTS = 31,
    CYAN_CHASING_DOTS = 32,
    WHITE_CHASING_DOTS = 33,
    PURPLE_CHASING_DOTS = 34,
    CYAN_DOTS_BLINK_ON_SILVER = 35,
    PURPLE_DOTS_BLINK_ON_SILVER = 36,
    YELLOW_DOTS_BLINK_ON_SILVER = 37,
    BLUE_DOTS_BLINK_ON_SILVER = 38,
    GREEN_DOTS_BLINK_ON_SILVER = 39,
    RED_DOTS_BLINK_ON_SILVER = 40,
    RED_AND_GREEN_FLOWING = 41,
    RED_AND_BLUE_FLOWING = 42,
    RED_AND_YELLOW_FLOWING = 43,
    RED_AND_CYAN_FLOWING = 44,
    RED_AND_PURPLE_FLOWING = 45,
    RED_AND_WHITE_FLOWING = 46,
    GREEN_AND_BLUE_FLOWING = 47,
    GREEN_AND_YELLOW_FLOWING = 48,
    GREEN_AND_CYAN_FLOWING = 49,
    GREEN_AND_PURPLE_FLOWING = 50,
    GREEN_AND_WHITE_FLOWING = 51,
    BLUE_AND_YELLOW_FLOWING = 52,
    BLUE_AND_CYAN_FLOWING = 53,
    BLUE_AND_PURPLE_FLOWING = 54,
    BLUE_AND_WHITE_FLOWING = 55,
    YELLOW_AND_CYAN_FLOWING = 56,
    YELLOW_AND_PURPLE_FLOWING = 57,
    YELLOW_AND_WHITE_FLOWING = 58,
    CYAN_AND_PURPLE_FLOWING = 59,
    CYAN_AND_WHITE_FLOWING = 60,
    RED_CROSSING_FLOWING = 61,
    GREEN_CROSSING_FLOWING = 62,
    BLUE_CROSSING_FLOWING = 63,
    YELLOW_CROSSING_FLOWING = 64,
    CYAN_CROSSING_FLOWING = 65,
    PURPLE_CROSSING_FLOWING = 66,
    WHITE_CROSSING_FLOWING = 67,
    RED_ARROWS = 68,
    GREEN_ARROWS = 69,
    BLUE_ARROWS = 70,
    YELLOW_ARROWS = 71,
    CYAN_ARROWS = 72,
    PURPLE_ARROWS = 73,
    RED_CUDGEL = 74,
    GREEN_CUDGEL = 75,
    BLUE_CUDGEL = 76,
    YELLOW_CUDGEL = 77,
    CYAN_CUDGEL = 78,
    PURPLE_CUDGEL = 79,
    GAPS_IN_CYAN = 80,
    GAPS_IN_PURPLE = 81,
    GAPS_IN_YELLOW = 82,
    GAPS_IN_BLUE = 83,
    GAPS_IN_GREEN = 84,
    GAPS_IN_RED = 85,
    RED_BREATHE = 86,
    GREEN_BREATHE = 87,
    BLUE_BREATHE = 88,
    YELLOW_BREATHE = 89,
    CYAN_BREATHE = 90,
    PURPLE_BREATHE = 91,
    WHITE_BREATHE = 92,
    RED_ARROWS_REVERSE = 93,
    GREEN_ARROWS_REVERSE = 94,
    BLUE_ARROWS_REVERSE = 95,
    YELLOW_ARROWS_REVERSE = 96,
    CYAN_ARROWS_REVERSE = 97,
    PURPLE_ARROWS_REVERSE = 98,
    RED_DOTS_RUNNING_IN_CYAN = 99,
    GREEN_DOTS_RUNNING_IN_PURPLE = 100,
    BLUE_DOTS_RUNNING_IN_YELLOW = 101,
    YELLOW_DOTS_RUNNING_IN_BLUE = 102,
    CYAN_DOTS_RUNNING_IN_GREEN = 103,
    PURPLE_DOTS_RUNNING_IN_RED = 104,
    WHITE_DOTS_RUNNING_IN_CYAN = 105,
    RED_FADING_IN_AND_OUT = 106,
    GREEN_FADING_IN_AND_OUT = 107,
    BLUE_FADING_IN_AND_OUT = 108,
    YELLOW_FADING_IN_AND_OUT = 109,
    CYAN_FADING_IN_AND_OUT = 110,
    PURPLE_FADING_IN_AND_OUT = 111,
    WHITE_FADING_IN_AND_OUT = 112,
    RED_METEOR_REVERSE = 113,
    GREEN_METEOR_REVERSE = 114,
    BLUE_METEOR_REVERSE = 115,
    YELLOW_METEOR_REVERSE = 116,
    CYAN_METEOR_REVERSE = 117,
    PURPLE_METEOR_REVERSE = 118,
    WHITE_METEOR_REVERSE = 119,
    RED_WAVE_2 = 120,
    GREEN_WAVE_2 = 121,
    BLUE_WAVE_2 = 122,
    YELLOW_WAVE_2 = 123,
    CYAN_WAVE_2 = 124,
    PURPLE_WAVE_2 = 125,
    WHITE_WAVE_2 = 126,
    RED_WING_DOTS = 127,
    GREEN_SWING_DOTS = 128,
    BLUE_SWING_DOTS = 129,
    YELLOW_SWING_DOTS = 130,
    CYAN_SWING_DOTS = 131,
    PURPLE_SWING_DOTS = 132,
    WHITE_SWING_DOTS = 133,
    RED_AND_GREEN_CUDGEL = 134,
    GREEN_AND_BLUE_CUDGEL = 135,
    BLUE_AND_YELLOW_CUDGEL = 136,
    YELLOW_AND_CYAN_CUDGEL = 137,
    CYAN_AND_PURPLE_CUDGEL = 138,
    PURPLE_AND_WHITE_CUDGEL = 139,
    WHITE_AND_RED_CUDGEL = 140,
    RED_OVERLAPS_GREEN = 141,
    GREEN_OVERLAPS_RED = 142,
    BLUE_OVERLAPS_GREEN = 143,
    YELLOW_OVERLAPS_GREEN = 144,
    CYAN_OVERLAPS_GREEN = 145,
    PURPLE_OVERLAPS_GREEN = 146,
    WHITE_OVERLAPS_GREEN = 147,
    RED_OVERLAPS_BLUE = 148,
    GREEN_OVERLAPS_BLUE = 149,
    BLUE_OVERLAPS_GREEN_2 = 150,
    YELLOW_OVERLAPS_BLUE = 151,
    CYAN_OVERLAPS_BLUE = 152,
    PURPLE_OVERLAPS_BLUE = 153,
    WHITE_OVERLAPS_BLUE = 154,
    PINK_MIX_BLUE = 155,
    GREEN_MIX_YELLOW = 156,
    BLUE_MIX_PINK = 157,
    BLUE_MIX_WHITE = 158,
    GREEN_MIX_ORANGE = 159,
    BLUE_MIX_PURPLE = 160,
    CYAN_MIX_WHITE = 161,
    RED_BLINKING = 162,
    GREEN_BLINKING = 163,
    BLUE_BLINKING = 164,
    YELLOW_BLINKING = 165,
    CYAN_BLINKING = 166,
    PURPLE_BLINKING = 167,
    WHITE_BLINKING = 168,
    RED_STACKING_INTO_GREEN = 169,
    GREEN_STACKING_INTO_BLUE = 170,
    BLUE_STACKING_INTO_YELLOW = 171,
    YELLOW_STACKING_INTO_CYAN = 172,
    CYAN_STACKING_INTO_PURPLE = 173,
    PURPLE_STACKING_INTO_WHITE = 174,
    WHITE_STACKING_INTO_RED = 175,
    COLOR_CHANGING_BREATHING = 176,
    MULTICOLORED_GRADIENTS = 177,
    COLOR_FLASHING = 178,
    RAINBOW_REVERSE = 179


class MonoEffect(Effect):
    """
    Preset effects that are for a single, user customizable color
    """
    METEOR = 205,
    BREATHING = 206,
    STACK = 207,
    FLOW = 208,
    WAVE = 209,
    FLASH = 210,
    SOLID = 211,
    CATCHUP = 212,


CUSTOM_EFFECTS_OFFSET = 218


class CustomEffect(Effect):
    """
    Sets the brightness of the light (0 to 255)
    """
    CUSTOM_1 = CUSTOM_EFFECTS_OFFSET + 1,
    CUSTOM_2 = CUSTOM_EFFECTS_OFFSET + 2,
    CUSTOM_3 = CUSTOM_EFFECTS_OFFSET + 3,
    CUSTOM_4 = CUSTOM_EFFECTS_OFFSET + 4,
    CUSTOM_5 = CUSTOM_EFFECTS_OFFSET + 5,
    CUSTOM_6 = CUSTOM_EFFECTS_OFFSET + 6,
    CUSTOM_7 = CUSTOM_EFFECTS_OFFSET + 7,
    CUSTOM_8 = CUSTOM_EFFECTS_OFFSET + 8,
    CUSTOM_9 = CUSTOM_EFFECTS_OFFSET + 9,
    CUSTOM_10 = CUSTOM_EFFECTS_OFFSET + 10,
    CUSTOM_11 = CUSTOM_EFFECTS_OFFSET + 11,
    CUSTOM_12 = CUSTOM_EFFECTS_OFFSET + 12,


class ColorOrder(ConstantEnum):
    """
    Sets the color order
    """
    RGB = 0
    RBG = 1
    GRB = 2
    GBR = 3
    BRG = 4
    BGR = 5


class ChipType(ConstantEnum):
    """
    Sets the chip type of the lights
    """
    SM16703 = 0
    TM1804 = 1
    UCS1903 = 2
    WS2811 = 3
    WS2801 = 4
    SK6812 = 5
    LPD6803 = 6
    LPD8806 = 7
    APA102 = 8
    APA105 = 9
    DMX512 = 10
    TM1914 = 11
    TM1913 = 12
    P9813 = 13
    INK1003 = 14
    P943S = 15
    P9411 = 10
    P9413 = 11
    TX1812 = 12
    TX1813 = 13
    GS8206 = 14
    GS8208 = 15
    SK9822 = 16
    TM1814 = 17
    SK6812_RGBW = 18
    P9414 = 19
    P9412 = 20


class StatePosition(ConstantEnum):
    """
    State is returned from the device as a byte array.

    This provides the position of each piece of useful data within the state bytearray.
    """
    IS_ON = 1
    MODE = 2
    SPEED = 3
    BRIGHTNESS = 4
    COLOR_ORDER = 5
    LEDS_PER_SEGMENT_A = 6
    LEDS_PER_SEGMENT_B = 7
    SEGMENTS_A = 8
    SEGMENTS_B = 9
    COLOR_R = 10
    COLOR_G = 11
    COLOR_B = 12
    CHIP_TYPE = 13
    RECORDED_PRESETS = 14
    WHITE_CHANNEL_BRIGHTNESS = 15
