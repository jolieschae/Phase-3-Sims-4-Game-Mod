# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\eco_footprint\eco_footprint_enums.py
# Compiled at: 2020-01-13 18:00:24
# Size of source mod 2**32: 460 bytes
import enum

class EcoFootprintStateType(enum.Int):
    GREEN = 0
    NEUTRAL = 1
    INDUSTRIAL = 2


class EcoFootprintDirection(enum.Int):
    TOWARD_GREEN = 0
    AT_CONVERGENCE = 1
    TOWARD_INDUSTRIAL = 2