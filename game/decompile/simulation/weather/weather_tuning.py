# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\weather\weather_tuning.py
# Compiled at: 2020-08-06 15:24:49
# Size of source mod 2**32: 1535 bytes
from sims4.tuning.tunable import TunableTuple, Tunable

class TuningPrescribedWeatherType(TunableTuple):

    def __init__(self, **kwargs):
        (super().__init__)(rain=Tunable(description='\n                If checked this forecast will be unavailable if rain is disabled\n                ',
  tunable_type=bool,
  default=False), 
         storm=Tunable(description='\n                If checked this forecast will be unavailable if storm is disabled\n                ',
  tunable_type=bool,
  default=False), 
         snow=Tunable(description='\n                If checked this forecast will be unavailable if snow is disabled\n                ',
  tunable_type=bool,
  default=False), 
         blizzard=Tunable(description='\n                If checked this forecast will be unavailable if blizzard is disabled\n                ',
  tunable_type=bool,
  default=False), 
         thunder_snow_storms=Tunable(description='\n                If checked this forecast will be unavailable if thunder snow storms are disabled in the options menu.\n                ',
  tunable_type=bool,
  default=False), **kwargs)