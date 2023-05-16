# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\plex\plex_enums.py
# Compiled at: 2019-01-30 15:48:32
# Size of source mod 2**32: 606 bytes
import enum
INVALID_PLEX_ID = 0

class PlexBuildingType(enum.Int):
    DEFAULT = 0
    FULLY_CONTAINED_PLEX = 1
    PENTHOUSE_PLEX = 2
    INVALID = 3
    EXPLORABLE = 4
    COASTAL = 5