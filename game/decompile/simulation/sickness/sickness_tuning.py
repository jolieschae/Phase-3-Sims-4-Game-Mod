# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sickness\sickness_tuning.py
# Compiled at: 2017-04-11 21:44:50
# Size of source mod 2**32: 1826 bytes
from event_testing.tests import TunableTestSet
from sims4.tuning.tunable import TunableRange
from tag import TunableTags
from tunable_multiplier import TestedSum
from tunable_time import TunableTimeOfDay

class SicknessTuning:
    SICKNESS_TIME_OF_DAY = TunableTimeOfDay(description='\n        Hour of day in which sicknesses will be distributed to Sims.\n        ',
      default_hour=3)
    SICKNESS_TESTS = TunableTestSet(description='\n        Test sets determining whether or not a given Sim may become sick at all.\n        These tests run before we attempt to roll on whether or not \n        the Sim can avoid becoming sick. \n        (ORs of ANDs)\n        ')
    SICKNESS_CHANCE = TestedSum.TunableFactory(description='\n        Chance of any given Sim to become sick.  \n        \n        Chance is out of 100.\n        \n        When the sum of the base value and values from passed tests are\n        greater than 100, the Sim is guaranteed to become sick during a \n        sickness distribution pass.\n        \n        When 0 or below, the Sim will not get sick.\n        ')
    PREVIOUS_SICKNESSES_TO_TRACK = TunableRange(description='\n        Number of previous sicknesses to track.  Can use this to help promote\n        variation of sicknesses a Sim receives over time.',
      tunable_type=int,
      minimum=0,
      default=1)
    EXAM_TYPES_TAGS = TunableTags(description='\n        Tags that represent the different types of objects that are used\n        to run exams.\n        ',
      filter_prefixes=('interaction', ))