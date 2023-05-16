# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\statistic_categories.py
# Compiled at: 2013-05-16 22:23:47
# Size of source mod 2**32: 498 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
import sims4.log
logger = sims4.log.Logger('SimStatistics')

class StatisticCategory(DynamicEnum):
    INVALID = 0