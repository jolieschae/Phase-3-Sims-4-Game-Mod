# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\food_restrictions_tests.py
# Compiled at: 2021-02-23 19:12:00
# Size of source mod 2**32: 3328 bytes
from crafting.food_restrictions_utils import FoodRestrictionUtils
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from caches import cached_test
from interactions import ParticipantTypeSingleSim, ParticipantTypeSingle
from objects.components.types import CRAFTING_COMPONENT
from sims4.tuning.tunable import TunableVariant, HasTunableSingletonFactory, TunableEnumEntry, AutoFactoryInit

class FoodRestrictionTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    NO_RESTRICTIONS = 1
    HAS_RESTRICTIONS = 2
    FACTORY_TUNABLES = {'sim':TunableEnumEntry(description='\n            The sim to check food restrictions for.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'object':TunableEnumEntry(description='\n            The food object to check food restrictions against.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Object), 
     'test':TunableVariant(description='\n            The test to perform. \n            ',
       locked_args={'no_restrictions':NO_RESTRICTIONS, 
      'has_restrictions':HAS_RESTRICTIONS},
       default='no_restrictions')}

    def get_expected_args(self):
        return {'sim':self.sim, 
         'object':self.object}

    @cached_test
    def __call__(self, sim=None, object=None):
        sim = next(iter(sim), None)
        object = next(iter(object), None)
        if sim is None or object is None:
            return TestResult(False, 'The sim or the object is none', self.tooltip)
        else:
            tracker = sim.food_restriction_tracker
            if not (tracker and object.has_component(CRAFTING_COMPONENT)):
                if self.test == self.NO_RESTRICTIONS:
                    return TestResult.TRUE
                if self.test == self.HAS_RESTRICTIONS:
                    return TestResult(False, 'Sim {} does not have a food restriction against {}', sim, object, self.tooltip)
        crafting_process = object.get_crafting_process()
        recipe = crafting_process.get_order_or_recipe()
        has_restriction = tracker.recipe_has_restriction(recipe)
        if self.test == self.NO_RESTRICTIONS:
            if has_restriction:
                return TestResult(False, 'Sim {} has a food restriction against {}', sim, object, self.tooltip)
        if self.test == self.HAS_RESTRICTIONS:
            if not has_restriction:
                return TestResult(False, 'Sim {} does not have a food restriction against {}', sim, object, self.tooltip)
        return TestResult.TRUE