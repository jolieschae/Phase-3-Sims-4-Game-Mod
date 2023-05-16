# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gameplay_scenarios\scenario_tests.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 5906 bytes
from event_testing.test_events import TestEvent
from interactions import ParticipantTypeSingleSim
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableReference, TunableEnumEntry, Tunable
import services, sims4

class ScenarioRoleTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'scenario':TunableReference(description='\n            If tuned, we will test if the target sim is part of this scenario.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SNIPPET),
       class_restrictions=('Scenario', ),
       allow_none=True), 
     'role':TunableReference(description='\n            If tuned, we will test if the target sim has this role. \n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SNIPPET),
       class_restrictions=('ScenarioRole', ),
       allow_none=True), 
     'target_sim':TunableEnumEntry(description='\n            The target Sim of this test.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'invert':Tunable(description='\n            If checked, inverts the normal result of the test.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'target_sims': self.target_sim}

    def get_test_result_based_on_value(self, value, message, *args):
        if self.invert:
            value = not value
        if value:
            return TestResult.TRUE
        return TestResult(False, message, *args, **{'tooltip': self.tooltip})

    def __call__(self, target_sims):
        target_sim = next(iter(target_sims), None)
        if target_sim is None:
            return self.get_test_result_based_on_value(False, 'Target is None.')
        if target_sim.household is None:
            return self.get_test_result_based_on_value(False, 'No active household.')
        if target_sim.household.scenario_tracker is None:
            return self.get_test_result_based_on_value(False, 'Scenario_tracker is empty.')
        scenario = target_sim.household.scenario_tracker.active_scenario
        if scenario is None:
            return self.get_test_result_based_on_value(False, '{} is not part of a scenario.', target_sim)
        if self.scenario is not None:
            if self.scenario is not type(scenario):
                return self.get_test_result_based_on_value(False, '{} is not part of the tuned scenario {}.', target_sim, self.scenario)
        if self.role is not None:
            if self.role.guid64 != scenario.get_role_id_for_sim(target_sim.id):
                return self.get_test_result_based_on_value(False, '{} has different scenario role than {}.', target_sim, self.role)
        return self.get_test_result_based_on_value(True, '{} does not pass the ScenarioRoleTest.', target_sim, self.role)


class ScenarioGoalCompletedTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    test_events = (
     TestEvent.ScenarioGoalCompleted,)
    FACTORY_TUNABLES = {'situation_goal': TunableReference(description='\n            The situation goal to be checked if it is completed in the scenario.\n            ',
                         manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_GOAL)))}

    def get_expected_args(self):
        return {}

    def __call__(self):
        household = services.active_household()
        if household is None:
            return TestResult(False, 'No active household.', tooltip=(self.tooltip))
        if household.scenario_tracker is None:
            return TestResult(False, 'scenario_tracker is empty.', tooltip=(self.tooltip))
        active_scenario = household.scenario_tracker.active_scenario
        if active_scenario.is_goal_completed(self.situation_goal.guid64):
            return TestResult.TRUE
        return TestResult(False, '{} is not completed in {}.', (self.situation_goal), active_scenario, tooltip=(self.tooltip))


class ScenarioPhaseTriggeredTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    test_events = (
     TestEvent.ScenarioPhaseTriggered,)
    FACTORY_TUNABLES = {'scenario_phase': TunableReference(description='\n            The phase to be checked if it is triggered in the scenario.\n            ',
                         manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
                         class_restrictions=('ScenarioPhase', ))}

    def get_expected_args(self):
        return {}

    def __call__(self):
        household = services.active_household()
        if household is None:
            return TestResult(False, 'No active household.', tooltip=(self.tooltip))
        if household.scenario_tracker is None:
            return TestResult(False, 'scenario_tracker is empty.', tooltip=(self.tooltip))
        active_scenario = household.scenario_tracker.active_scenario
        if self.scenario_phase.guid64 in active_scenario.triggered_phases_guids:
            return TestResult.TRUE
        return TestResult(False, 'Phase:{} is not triggered in {}.', (self.scenario_phase), active_scenario, tooltip=(self.tooltip))