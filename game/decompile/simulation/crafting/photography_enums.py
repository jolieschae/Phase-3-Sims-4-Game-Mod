# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\photography_enums.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 2891 bytes
import enum

class CameraMode(enum.Int, export=False):
    FREE_FORM_PHOTO = 0
    SIM_PHOTO = 1
    SELFIE_PHOTO = 2
    TWO_SIM_SELFIE_PHOTO = 3
    PHOTO_STUDIO_PHOTO = 4
    PAINT_BY_REFERENCE = 5
    TRIPOD = 6
    DECORATOR_MODE = 7
    CROSSSTITCH_BY_REFERENCE = 8
    PUZZLE_BY_REFERENCE = 9

    @classmethod
    def is_for_reference(cls, camera_mode):
        return camera_mode in [CameraMode.PAINT_BY_REFERENCE,
         CameraMode.CROSSSTITCH_BY_REFERENCE,
         CameraMode.PUZZLE_BY_REFERENCE]


class ZoomCapability(enum.Int):
    NO_ZOOM = 0
    SHORT = 1
    LONG = 2
    VERY_LONG = 3


class CameraQuality(enum.Int):
    CHEAP = 0
    STANDARD = 1
    EXPENSIVE = 2
    SUPER_EXPENSIVE = 3


class PhotoStyleType(enum.Int):
    NORMAL = 0
    PHOTO_PLAIN = 1
    PHOTO_GRAY = 2
    PHOTO_SEPIA = 3
    PAINT_PLAIN = 4
    EFFECT_OVERSATURATED = 5
    EFFECT_UNDERSATURATED = 6
    PHOTO_VIGNETTE = 7
    PHOTO_WHITE_VIGNETTE = 8
    PHOTO_INVERT = 9
    PHOTO_WARM = 10
    PHOTO_COOL = 11
    PHOTO_BRIGHT = 12
    PHOTO_DARK = 13
    PHOTO_CROSS_STITCH = 14
    PHOTO_FAIL_GNOME = 256
    PHOTO_FAIL_FINGER = 257
    PHOTO_FAIL_BLURRY = 258
    PHOTO_FAIL_NOISE = 259
    EFFECT_GRAINY = 260


class PhotoSize(enum.Int):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2
    EXTRA_LARGE = 3


class PhotoOrientation(enum.Int, export=False):
    LANDSCAPE = 0
    PORTRAIT = 1


class RevealPhotoStates(enum.Int):
    BEFORE_PHOTO = 0
    AFTER_PHOTO = 1