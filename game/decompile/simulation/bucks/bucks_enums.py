# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\bucks\bucks_enums.py
# Compiled at: 2016-08-01 21:02:05
# Size of source mod 2**32: 567 bytes
from sims4.tuning.dynamic_enum import DynamicEnumLocked
import enum

class BucksType(DynamicEnumLocked, partitioned=True):
    INVALID = 0


class BucksTrackerType(enum.Int):
    HOUSEHOLD = 0
    CLUB = 1
    SIM = 2