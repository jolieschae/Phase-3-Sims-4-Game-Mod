# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\gameplay_object_preference_tests.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 3498 bytes
import services, sims4.log, sims4.resources
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from caches import cached_test
from interactions import ParticipantType, ParticipantTypeObject
from objects.definition import Definition
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableEnumEntry, TunableReference, TunableList, Tunable
from traits.preference_enums import GameplayObjectPreferenceTypes
logger = sims4.log.Logger('GameplayObjectPreferenceTests', default_owner='micfisher')

class GameplayObjectPreferenceTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'sims':TunableEnumEntry(description='\n            The Sim(s) to test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.TargetSim), 
     'targets':TunableEnumEntry(description='\n            The object(s) to test.\n            ',
       tunable_type=ParticipantTypeObject,
       default=ParticipantType.PickedObject), 
     'gameplay_object_preference':TunableReference(description='\n            The Gameplay Object Preferences to be tested.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.TRAIT),
       class_restrictions=('GameplayObjectPreference', )), 
     'preference_type':TunableList(description='\n            The gameplay object preference types to check for the existence of on the Sim for the object.\n            ',
       tunable=TunableEnumEntry(tunable_type=GameplayObjectPreferenceTypes,
       default=(GameplayObjectPreferenceTypes.UNSURE))), 
     'targetless':Tunable(description='\n            If True, we will ignore Targets tuning, and just check the preference type without\n            considering any specific target. \n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'sims':self.sims, 
         'targets':self.targets}

    @cached_test
    def __call__(self, sims, targets):
        for sim in sims:
            current_preference_type = sim.trait_tracker.get_gameplay_object_preference_type(self.gameplay_object_preference)
            if self.targetless:
                if current_preference_type in self.preference_type:
                    return TestResult.TRUE
                    continue
                for target in targets:
                    if not isinstance(target, Definition):
                        target = target.definition
                    if self.gameplay_object_preference.preference_item == target and current_preference_type in self.preference_type:
                        return TestResult.TRUE

        if self.targetless:
            return TestResult(False, "Sim {}'s gameplay object preference {} does not match: {}", sims, self.gameplay_object_preference, self.preference_type)
        return TestResult(False, "The picked object {} does not match Sim {}'s gameplay object preference: {}", targets, sims, self.preference_type)