# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_object_criteria.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 4623 bytes
from event_testing.resolver import DataResolver
from event_testing.results import TestResultNumeric
from objects.object_tests import ObjectCriteriaTest
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory
from sims4.tuning.tunable_base import GroupNames
import objects.object_tests, services, sims4.tuning, situations.situation_goal
from sims4.utils import flexproperty

class SituationGoalObjectCount(situations.situation_goal.SituationGoal, AutoFactoryInit, HasTunableSingletonFactory):
    INSTANCE_TUNABLES = {'object_criteria_test': objects.object_tests.ObjectCriteriaTest.TunableFactory(description='\n            Object criteria test to run to figure out how many objects\n            of the objects we care for are on the lot.\n            ',
                               tuning_group=(GroupNames.TESTS))}

    def __init__(self, *args, reader=None, **kwargs):
        (super().__init__)(args, reader=reader, **kwargs)
        self._current_count = 0
        resolver = DataResolver(self._sim_info)
        resolver.set_additional_metric_key_data(self)
        test_result = resolver(self.object_criteria_test)
        if isinstance(test_result, TestResultNumeric):
            self._current_count = test_result.current_value

    def setup(self):
        super().setup()
        services.get_event_manager().register(self, self.object_criteria_test.test_events)

    def _decommision(self):
        services.get_event_manager().unregister(self, self.object_criteria_test.test_events)
        super()._decommision()

    def handle_event(self, sim_info, event, resolver):
        self._test_and_send_info(resolver)

    def _test_and_send_info(self, resolver):
        test_result = resolver(self.object_criteria_test)
        prev_count = self._current_count
        if isinstance(test_result, TestResultNumeric):
            self._current_count = test_result.current_value
        elif self._current_count >= self.max_iterations or test_result:
            super()._on_goal_completed()
        else:
            if prev_count < self._current_count:
                self._on_iteration_completed()

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        return False

    @property
    def completed_iterations(self):
        return self._current_count

    @flexproperty
    def max_iterations(cls, inst):
        inst_or_cls = inst if inst is not None else cls
        subject_specific_tests = inst_or_cls.object_criteria_test.subject_specific_tests
        if subject_specific_tests.subject_type == ObjectCriteriaTest.ALL_OBJECTS:
            return int(subject_specific_tests.quantity.value)
        return 1


sims4.tuning.instances.lock_instance_tunables(SituationGoalObjectCount, score_on_iteration_complete=None,
  _iterations=1)