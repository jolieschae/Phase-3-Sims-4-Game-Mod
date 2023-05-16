# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\statistic_enums.py
# Compiled at: 2019-06-11 20:31:41
# Size of source mod 2**32: 1689 bytes
import enum

class PeriodicStatisticBehavior(enum.Int):
    APPLY_AT_START_ONLY = ...
    RETEST_ON_INTERVAL = ...
    APPLY_AT_INTERVAL_ONLY = ...


class CommodityTrackerSimulationLevel(enum.Int, export=False):
    REGULAR_SIMULATION = ...
    LOW_LEVEL_SIMULATION = ...


class StatisticLockAction(enum.Int):
    DO_NOT_CHANGE_VALUE = 0
    USE_MIN_VALUE_TUNING = 1
    USE_MAX_VALUE_TUNING = 2
    USE_BEST_VALUE_TUNING = 3