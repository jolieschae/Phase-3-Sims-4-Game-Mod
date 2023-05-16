# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\seasons\seasons_enums.py
# Compiled at: 2018-04-16 20:26:15
# Size of source mod 2**32: 1160 bytes
import enum

class SeasonType(enum.Int):
    SUMMER = 0
    FALL = 1
    WINTER = 2
    SPRING = 3


class SeasonLength(enum.Int):
    NORMAL = 0
    LONG = 1
    VERY_LONG = 2


class SeasonSegment(enum.Int):
    EARLY = 0
    MID = 1
    LATE = 2


class SeasonParameters(enum.Int):
    LEAF_ACCUMULATION = 1
    FLOWER_GROWTH = 2
    FOLIAGE_REDUCTION = 3
    FOLIAGE_COLORSHIFT = 4


class SeasonSetSource(enum.Int, export=False):
    PROGRESSION = ...
    CHEAT = ...
    LOOT = ...