# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_tests.py
# Compiled at: 2018-11-05 18:23:32
# Size of source mod 2**32: 1947 bytes
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from interactions import ParticipantType
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableList, TunableReference
import services, sims4.resources

class SituationGoalTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'who':TunableEnumEntry(description='\n            The person(s) to test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'situation_goals':TunableList(description='\n            One of the goals must be active in a situation that the Sim is in.\n            ',
       tunable=TunableReference(description='\n                A situation goal, that if active, will cause this test to return\n                True.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_GOAL))))}

    def get_expected_args(self):
        return {'test_targets': self.who}

    def __call__(self, test_targets=()):
        situation_manager = services.get_zone_situation_manager()
        for target in test_targets:
            sim = target.get_sim_instance()
            situations = situation_manager.get_situations_sim_is_in(sim)
            for situation in situations:
                for goal in situation.get_active_goals():
                    if type(goal) in self.situation_goals:
                        return TestResult.TRUE

        return TestResult(False, 'None of the situation goals were active. {}', self.situation_goals)