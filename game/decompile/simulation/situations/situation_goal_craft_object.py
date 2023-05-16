# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_craft_object.py
# Compiled at: 2017-02-03 01:14:23
# Size of source mod 2**32: 1958 bytes
from sims4.tuning.tunable_base import GroupNames
import objects.object_tests, services, situations.situation_goal, situations.situation_goal_actor

class SituationGoalCraftObject(situations.situation_goal.SituationGoal):
    INSTANCE_TUNABLES = {'crafted_item_test':objects.object_tests.CraftedItemTest.TunableFactory(description='\n                A test to run to determine if the player can have this goal. If crafted_tagged_item \n                is set, the player may craft any item that has the specified tag.',
       tuning_group=GroupNames.TESTS), 
     '_post_tests':situations.situation_goal_actor.TunableSituationGoalActorPostTestSet(description='\n                A set of tests that must all pass when the player satisfies the crafted_item_test \n                for the goal to be consider completed.\nThese test can only consider the actor and \n                the environment. \ne.g. Make a Scotch and Soda while drunk.',
       tuning_group=GroupNames.TESTS)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)

    def setup(self):
        super().setup()
        services.get_event_manager().register(self, self.crafted_item_test.test_events)

    def _decommision(self):
        services.get_event_manager().unregister(self, self.crafted_item_test.test_events)
        super()._decommision()

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        if not resolver(self.crafted_item_test):
            return False
        return super()._run_goal_completion_tests(sim_info, event, resolver)