# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\household_utilities\utility_types.py
# Compiled at: 2016-04-20 20:17:06
# Size of source mod 2**32: 526 bytes
from sims4.tuning.dynamic_enum import DynamicEnum

class Utilities(DynamicEnum):
    POWER = 0
    WATER = 1


class UtilityShutoffReasonPriority(DynamicEnum):
    NO_REASON = 0