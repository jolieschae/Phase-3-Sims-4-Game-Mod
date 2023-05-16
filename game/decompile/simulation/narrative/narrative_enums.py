# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\narrative\narrative_enums.py
# Compiled at: 2020-05-20 13:18:13
# Size of source mod 2**32: 2115 bytes
from sims4.tuning.dynamic_enum import DynamicEnum, DynamicEnumLocked
from weather.weather_enums import WeatherEffectType, CloudType
import enum

class NarrativeGroup(DynamicEnum, partitioned=True):
    INVALID = 0


class NarrativeEvent(DynamicEnum, partitioned=True):
    INVALID = 0


class NarrativeProgressionEvent(DynamicEnumLocked, partitioned=True):
    INVALID = 0


class NarrativeSituationShiftType(DynamicEnum, partitioned=True):
    INVALID = 0


class NarrativeEnvironmentParams(enum.Int):
    StrangerVille_Act = WeatherEffectType.STRANGERVILLE_ACT
    BatuuFactionState_RES = WeatherEffectType.STARWARS_RESISTANCE
    BatuuFactionState_FO = WeatherEffectType.STARWARS_FIRST_ORDER
    StrangerVille_Strange_Skybox = CloudType.STRANGE
    StrangerVille_VeryStrange_Skybox = CloudType.VERY_STRANGE