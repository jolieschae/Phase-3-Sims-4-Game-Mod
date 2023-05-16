# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\visibility\visibility_enums.py
# Compiled at: 2016-08-29 20:46:43
# Size of source mod 2**32: 591 bytes
import enum

class VisibilityFlags(enum.IntFlags):
    MIRRORS = 1
    LOT_WATER_REFLECTION = 2
    WORLD_WATER_REFLECTION = 4