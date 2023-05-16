# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\sim_info_lod.py
# Compiled at: 2019-07-08 12:13:46
# Size of source mod 2**32: 1264 bytes
import enum

class SimInfoLODLevel(enum.Int):
    MINIMUM = 1
    BACKGROUND = 10
    BASE = 25
    INTERACTED = 50
    FULL = 100
    ACTIVE = 125
    _prev_lod = {BACKGROUND: MINIMUM, BASE: BACKGROUND, INTERACTED: BASE, FULL: INTERACTED, ACTIVE: FULL}
    _next_lod = {MINIMUM: BACKGROUND, BACKGROUND: BASE, BASE: INTERACTED, INTERACTED: FULL}

    @staticmethod
    def get_previous_lod(from_lod):
        if from_lod in SimInfoLODLevel._prev_lod:
            return SimInfoLODLevel._prev_lod[from_lod]

    @staticmethod
    def get_next_lod(from_lod):
        if from_lod in SimInfoLODLevel._next_lod:
            return SimInfoLODLevel._next_lod[from_lod]