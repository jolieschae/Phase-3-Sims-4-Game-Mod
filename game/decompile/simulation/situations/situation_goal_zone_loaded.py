# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_zone_loaded.py
# Compiled at: 2015-02-26 18:07:38
# Size of source mod 2**32: 1449 bytes
from event_testing import test_events
import services
from sims4.tuning.tunable_base import GroupNames
from situations.situation_goal import SituationGoal
from situations.situation_goal_actor import TunableSituationGoalActorPostTestSet

class SituationGoalZoneLoaded(SituationGoal):
    INSTANCE_TUNABLES = {'_post_tests': TunableSituationGoalActorPostTestSet(description='\n                A set of tests that must all pass when zone has finished loading.\n                ',
                      tuning_group=(GroupNames.TESTS))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._test_events = set()

    def setup(self):
        super().setup()
        self._test_events.add(test_events.TestEvent.SimTravel)
        services.get_event_manager().register(self, self._test_events)

    def _decommision(self):
        services.get_event_manager().unregister(self, self._test_events)
        super()._decommision()