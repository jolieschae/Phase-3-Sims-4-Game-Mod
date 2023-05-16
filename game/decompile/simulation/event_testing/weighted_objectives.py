# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\weighted_objectives.py
# Compiled at: 2020-03-16 22:18:00
# Size of source mod 2**32: 1578 bytes
import services
from event_testing.tests import TunableTestSet
from sims4.resources import Types
from sims4.tuning.tunable import TunableList, TunableTuple, TunableReference, TunableRange

class WeightedObjectives(TunableList):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, tunable=TunableTuple(description='\n                A set of tests that are run against the Sim. If the tests pass,\n                this objective and the weight are added to a list for randomization.\n                ',
                    objective=TunableReference(description='\n                    The objective that will be provided if the tests pass.\n                    ',
                    manager=(services.get_instance_manager(Types.OBJECTIVE))),
                    tests=TunableTestSet(description='\n                    The tests that must pass for this objective to be valid.\n                    '),
                    weight=TunableRange(description='\n                    The weight of this objective against the other passing objectives.\n                    ',
                    tunable_type=float,
                    minimum=0,
                    default=1)), **kwargs)