# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\path_planner\path_plan_enums.py
# Compiled at: 2021-03-09 19:20:42
# Size of source mod 2**32: 1292 bytes
import enum, routing

class AllowedHeightsFootprintKeyMaskBits(enum.IntFlags):
    SMALL_HEIGHT = routing.FOOTPRINT_KEY_REQUIRE_SMALL_HEIGHT
    TINY_HEIGHT = routing.FOOTPRINT_KEY_REQUIRE_TINY_HEIGHT
    LOW_HEIGHT = routing.FOOTPRINT_KEY_REQUIRE_LOW_HEIGHT
    MEDIUM_HEIGHT = routing.FOOTPRINT_KEY_REQUIRE_MEDIUM_HEIGHT
    FLOATING = routing.FOOTPRINT_KEY_REQUIRE_FLOATING
    LARGE_HEIGHT = routing.FOOTPRINT_KEY_REQUIRE_LARGE_HEIGHT


class WadingFootprintKeyMaskBits(enum.IntFlags):
    WADING_DEEP = routing.FOOTPRINT_KEY_REQUIRE_WADING_DEEP
    WADING_MEDIUM = routing.FOOTPRINT_KEY_REQUIRE_WADING_MEDIUM
    WADING_SHALLOW = routing.FOOTPRINT_KEY_REQUIRE_WADING_SHALLOW
    WADING_VERY_SHALLOW = routing.FOOTPRINT_KEY_REQUIRE_WADING_VERY_SHALLOW