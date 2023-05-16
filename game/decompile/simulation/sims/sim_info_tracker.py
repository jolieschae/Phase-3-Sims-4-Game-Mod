# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\sim_info_tracker.py
# Compiled at: 2019-11-01 20:06:14
# Size of source mod 2**32: 3150 bytes
from sims.sim_info_lod import SimInfoLODLevel
from sims4.common import Pack
from sims4.utils import classproperty

class BaseLODTracker:
    __slots__ = ()

    @classproperty
    def _tracker_lod_threshold(cls):
        return SimInfoLODLevel.BACKGROUND

    @classmethod
    def is_valid_for_lod(cls, lod):
        if lod >= cls._tracker_lod_threshold:
            return True
        return False


class SimInfoTracker(BaseLODTracker):
    __slots__ = ()

    @classproperty
    def required_packs(cls):
        return (
         Pack.BASE_GAME,)

    def on_lod_update(self, old_lod, new_lod):
        pass