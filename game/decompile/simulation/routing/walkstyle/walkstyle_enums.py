# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\walkstyle\walkstyle_enums.py
# Compiled at: 2017-06-23 18:16:01
# Size of source mod 2**32: 943 bytes
import enum
from sims4.tuning.dynamic_enum import DynamicEnum

class WalkStyleRunAllowedFlags(enum.IntFlags):
    RUN_ALLOWED_INDOORS = 1
    RUN_ALLOWED_OUTDOORS = 2


class WalkstyleBehaviorOverridePriority(DynamicEnum):
    DEFAULT = 0


class WalkStylePriority(DynamicEnum):
    INVALID = 0
    COMBO = 1