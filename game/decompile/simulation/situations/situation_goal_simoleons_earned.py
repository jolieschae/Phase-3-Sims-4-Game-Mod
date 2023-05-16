# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_simoleons_earned.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 5193 bytes
import event_testing
from event_testing.results import TestResult
import services
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import AutoFactoryInit, TunableSingletonFactory, TunableRange, TunableSet, TunableEnumEntry
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexproperty
from situations.situation_goal import SituationGoal
from tag import Tag

class EarningsOfInterest(AutoFactoryInit):
    FACTORY_TUNABLES = {'tags':TunableSet(description='\n                A set of tags that will match an affordance instead of looking\n                for a specific one. If you leave this empty, all Simoleons earned will be counted.\n                ',
       tunable=TunableEnumEntry(Tag, Tag.INVALID)), 
     'amount_to_earn':TunableRange(description='\n                The amount of time in Simoleons earned from all relevant activities for this\n                goal to pass.\n                ',
       tunable_type=int,
       default=10,
       minimum=1)}
    expected_kwargs = (
     (
      'amount', event_testing.test_constants.FROM_EVENT_DATA),
     (
      'tags', event_testing.test_constants.FROM_EVENT_DATA))

    def get_expected_args(self):
        return dict(self.expected_kwargs)

    def __call__(self, amount=None, tags=None):
        if amount is None:
            return TestResult(False, 'Amount is None')
        elif not len(self.tags) == 0:
            if not tags is not None or self.tags & tags:
                if amount > 0:
                    return TestResult.TRUE
        else:
            return TestResult(False, 'No money earned')
        return TestResult(False, 'Failed relevant tags check: Earnings do not have any matching tags in {}.', self.tags)


TunableEarningsOfInterest = TunableSingletonFactory.create_auto_factory(EarningsOfInterest)

class SituationGoalSimoleonsEarned(SituationGoal):
    SIMOLEONS_EARNED = 'simoleons_earned'
    REMOVE_INSTANCE_TUNABLES = ('_post_tests', )
    INSTANCE_TUNABLES = {'_goal_test': TunableEarningsOfInterest(description='\n                Interaction and Simoleon amount that this situation goal will use.\n                Example: Earn 1000 Simoleons from Bartending activities.\n                ',
                     tuning_group=(GroupNames.TESTS))}

    def __init__(self, *args, reader=None, **kwargs):
        (super().__init__)(args, reader=reader, **kwargs)
        self._total_simoleons_earned = 0
        self._test_events = set()
        if reader is not None:
            simoleons_earned = reader.read_uint64(self.SIMOLEONS_EARNED, 0)
            self._total_simoleons_earned = simoleons_earned

    def setup(self):
        super().setup()
        self._test_events.add(event_testing.test_events.TestEvent.SimoleonsEarned)
        services.get_event_manager().register(self, self._test_events)

    def create_seedling(self):
        seedling = super().create_seedling()
        writer = seedling.writer
        writer.write_uint64(self.SIMOLEONS_EARNED, self._total_simoleons_earned)
        return seedling

    def _decommision(self):
        services.get_event_manager().unregister(self, self._test_events)
        super()._decommision()

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        if not resolver(self._goal_test):
            return False
        else:
            amount_to_add = resolver.get_resolved_arg('amount')
            self._total_simoleons_earned += amount_to_add
            if self._total_simoleons_earned >= self._goal_test.amount_to_earn:
                super()._on_goal_completed()
            else:
                self._on_iteration_completed()

    @property
    def completed_iterations(self):
        return self._total_simoleons_earned

    @flexproperty
    def max_iterations(cls, inst):
        return cls._goal_test.amount_to_earn


lock_instance_tunables(SituationGoalSimoleonsEarned, _iterations=1)