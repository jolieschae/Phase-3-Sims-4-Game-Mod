# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\weather\weather_tuning_mixin.py
# Compiled at: 2020-09-03 14:56:49
# Size of source mod 2**32: 2367 bytes
import enum
from seasons.seasons_enums import SeasonType
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry
from weather.weather_enums import SnowBehavior
from weather.weather_forecast import TunableWeatherSeasonalForecastsReference, TunableWeatherForecastListReference

class WeatherTuningMixin:
    INSTANCE_TUNABLES = {'weather':TunableMapping(description='\n            Forecasts for this location for the various seasons\n            ',
       key_type=TunableEnumEntry(description='\n                The Season.\n                ',
       tunable_type=SeasonType,
       default=(SeasonType.SPRING)),
       value_type=TunableWeatherSeasonalForecastsReference(description='\n                The forecasts for the season by part of season\n                ',
       pack_safe=True)), 
     'weather_no_seasons':TunableWeatherForecastListReference(description='\n            Forecast(s) for this location for players without EP05 installed\n            ',
       pack_safe=True,
       allow_none=True), 
     'snow_behavior':TunableMapping(description='\n            Snow behavior for this location for the various seasons\n            Defaults to NO_SNOW if not tuned for the current season\n            If set to PERMANENT, it will also set initial water to frozen\n            and windows to frosted\n            ',
       key_type=TunableEnumEntry(description='\n                The Season.\n                ',
       tunable_type=SeasonType,
       default=(SeasonType.SPRING)),
       value_type=TunableEnumEntry(description='\n                How snow behaves during this season at this location\n                ',
       tunable_type=SnowBehavior,
       default=(SnowBehavior.NO_SNOW))), 
     'snow_behavior_no_seasons':TunableEnumEntry(description='\n            How snow behaves during this season at this location\n            ',
       tunable_type=SnowBehavior,
       default=SnowBehavior.NO_SNOW)}