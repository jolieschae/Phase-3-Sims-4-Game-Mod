# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\spawn_point_enums.py
# Compiled at: 2016-08-31 18:09:28
# Size of source mod 2**32: 627 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
import enum

class SpawnPointPriority(DynamicEnum):
    DEFAULT = 0


class SpawnPointRequestReason(enum.Int):
    DEFAULT = 0
    SPAWN = 1
    LEAVE = 2