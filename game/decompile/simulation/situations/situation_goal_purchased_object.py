# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_purchased_object.py
# Compiled at: 2020-07-15 16:36:24
# Size of source mod 2**32: 1514 bytes
from sims4.tuning.tunable_base import GroupNames
import event_testing.tests, objects.object_tests, services, sims4.tuning.instances, situations.situation_goal

class SituationGoalPurchasedObject(situations.situation_goal.SituationGoal):
    INSTANCE_TUNABLES = {'purchased_object_test': objects.object_tests.ObjectPurchasedTest.TunableFactory(tuning_group=(GroupNames.TESTS))}

    def setup(self):
        super().setup()
        services.get_event_manager().register(self, self.purchased_object_test.test_events)

    def _decommision(self):
        services.get_event_manager().unregister(self, self.purchased_object_test.test_events)
        super()._decommision()

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        if not resolver(self.purchased_object_test):
            return False
        return super()._run_goal_completion_tests(sim_info, event, resolver)

    @property
    def numerical_token(self):
        return int(self.purchased_object_test.value)


sims4.tuning.instances.lock_instance_tunables(SituationGoalPurchasedObject, _iterations=1,
  _post_tests=(event_testing.tests.TestList()))