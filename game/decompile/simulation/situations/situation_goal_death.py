# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_death.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 2147 bytes
import sims, services
from event_testing.resolver import DataResolver
from interactions import ParticipantType
from sims4.tuning.tunable_base import GroupNames
from situations.situation_goal import SituationGoal

class SituationGoalDeath(SituationGoal):
    DEATH_TYPE = 'death_type'
    INSTANCE_TUNABLES = {'_goal_test': sims.sim_info_tests.DeadTest.TunableFactory(locked_args={'subject':ParticipantType.Actor, 
                    'tooltip':None},
                     tuning_group=(GroupNames.TESTS))}

    def __init__(self, *args, reader=None, **kwargs):
        (super().__init__)(args, reader=reader, **kwargs)
        self._death_type = None
        if reader is not None:
            self._death_type = reader.read_uint64(self.DEATH_TYPE, None)

    def setup(self):
        super().setup()
        services.get_event_manager().register(self, self._goal_test.test_events)

    def _decommision(self):
        services.get_event_manager().unregister(self, self._goal_test.test_events)
        super()._decommision()

    def create_seedling(self):
        seedling = super().create_seedling()
        writer = seedling.writer
        if self._death_type is not None:
            writer.write_uint64(self.DEATH_TYPE, self._death_type)
        return seedling

    def get_death_type_info(self):
        return self._death_type

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        if not resolver(self._goal_test):
            return False
        self._death_type = sim_info.death_type
        return super()._run_goal_completion_tests(sim_info, event, resolver)