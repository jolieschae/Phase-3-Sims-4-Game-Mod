# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\party.py
# Compiled at: 2014-06-07 17:16:44
# Size of source mod 2**32: 779 bytes
from interactions import ParticipantType
from sims4.tuning.tunable import TunableList
from statistics.statistic_ops import TunableStatisticChange

class Party:
    RALLY_FALSE_ADS = TunableList(description=' \n        A list of false advertisement for rallyable interactions. Use this\n        tunable to entice Sims to autonomously choose rallyable over non-\n        rallyable interactions.\n        ',
      tunable=TunableStatisticChange(locked_args={'subject':ParticipantType.Actor,  'advertise':True}))