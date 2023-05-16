# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\career_story_progression.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 2718 bytes
from _weakrefset import WeakSet
import itertools, random
from event_testing.resolver import SingleSimResolver
from objects import ALL_HIDDEN_REASONS
from sims.sim_info_lod import SimInfoLODLevel
from sims4 import math
from sims4.random import weighted_random_index
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, OptionalTunable, TunableInterval
from story_progression.story_progression_action import _StoryProgressionFilterAction
from tunable_multiplier import TunableMultiplier
import gsi_handlers, services

class CareerStoryProgressionParameters(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'joining':OptionalTunable(description='\n            If enabled, Sims will be able to join this career via Story\n            Progression.\n            ',
       tunable=TunableMultiplier.TunableFactory(description='\n                The weight of a particular Sim joining this career versus all\n                other eligible Sims doing the same. A weight of zero prevents\n                the Sim from joining the career.\n                ')), 
     'retiring':OptionalTunable(description="\n            If enabled, Sims will be able to retire from this career via Story\n            Progression. This does not override the 'can_quit' flag on the\n            career tuning.\n            \n            Story Progression will attempt to have Sims retire before having\n            Sims quit.\n            ",
       tunable=TunableMultiplier.TunableFactory(description='\n                The weight of a particular Sim retiring from this career versus\n                all other eligible Sims doing the same. A weight of zero\n                prevents the Sim from retiring from the career.\n                ')), 
     'quitting':OptionalTunable(description="\n            If enabled, Sims will be able to quit this career via Story\n            Progression. This does not override the 'can_quit' flag on the\n            career tuning.\n            ",
       tunable=TunableMultiplier.TunableFactory(description='\n                The weight of a particular Sim quitting this career versus all\n                other eligible Sims doing the same. A weight of zero prevents\n                the Sim from quitting the career.\n                '))}