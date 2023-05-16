# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\outcome_enums.py
# Compiled at: 2013-10-22 13:19:24
# Size of source mod 2**32: 262 bytes
from sims4.tuning.dynamic_enum import DynamicEnum

class OutcomeResult(DynamicEnum):
    NONE = 0
    SUCCESS = 1
    FAILURE = 2