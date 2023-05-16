# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\developmental_milestones\developmental_milestone_enums.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 593 bytes
import enum

class DevelopmentalMilestoneStates(enum.Int):
    LOCKED = -1
    ACTIVE = 0
    UNLOCKED = 1


class MilestoneDataClass(enum.Int):
    DEFAULT = 0
    HAD_CHILD = 1