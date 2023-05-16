# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\trends\trend_tuning.py
# Compiled at: 2018-10-08 19:22:22
# Size of source mod 2**32: 2675 bytes
from sims4.localization import TunableLocalizedString
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.tunable import TunableTuple, TunableEnumEntry, TunableList, TunableMapping, TunableReference
from tag import TunableTag
from tunable_time import TunableTimeSpan
import services

class TrendType(DynamicEnum):
    INVALID = 0


class TrendTuning:
    TREND_DATA = TunableList(description='\n        A list of data about trends.\n        ',
      tunable=TunableTuple(description='\n            The data about this trend.\n            ',
      trend_tag=TunableTag(description='\n                The tag for this trend.\n                ',
      filter_prefixes=('func_trend', )),
      trend_type=TunableEnumEntry(description='\n                The type of this trend.\n                ',
      tunable_type=TrendType,
      default=(TrendType.INVALID),
      invalid_enums=(
     TrendType.INVALID,)),
      trend_name=TunableLocalizedString(description='\n                The name for this trend. This will show up in a bulleted\n                list when a player researches current trends.\n                ')))
    TREND_REFRESH_COOLDOWN = TunableTimeSpan(description='\n        The amount of time it takes before trends refresh.\n        ',
      default_days=2)
    TREND_TIME_REMAINING_DESCRIPTION = TunableMapping(description='\n        A mapping of thresholds, in Sim Hours, to descriptions used when\n        describing the amount of time remaining in the study trends\n        notification.\n        ',
      key_name='sim_hours',
      key_type=int,
      value_name='description_string',
      value_type=(TunableLocalizedString()))
    TODDLER_CHILD_TREND = TunableTag(description='\n        The tag we use to indicate Toddler or Child trends.\n        ',
      filter_prefixes=('func_trend', ))
    CELEBRITY_TREND = TunableTag(description='\n        The tag we use to indicate Celebrity Trends.\n        ',
      filter_prefixes=('func_trend', ))
    TRENDLESS_VIDEO_DEFINITION = TunableReference(description='\n        The object definition to use if a Sim records a trendless video.\n        ',
      manager=(services.definition_manager()),
      pack_safe=True)