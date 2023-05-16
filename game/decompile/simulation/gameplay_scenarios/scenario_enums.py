# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gameplay_scenarios\scenario_enums.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 974 bytes
import enum
from sims4.tuning.dynamic_enum import DynamicEnum

class ScenarioEntryMethod(enum.IntFlags):
    NEW_HOUSEHOLD = 1
    EXISTING_HOUSEHOLD = 2


class ScenarioProperties(enum.IntFlags):
    ONBOARDING = 1


class ScenarioCategory(DynamicEnum):
    INVALID = 0


class ScenarioDifficultyCategory(DynamicEnum):
    INVALID = 0


class ScenarioTheme(DynamicEnum):
    INVALID = 0