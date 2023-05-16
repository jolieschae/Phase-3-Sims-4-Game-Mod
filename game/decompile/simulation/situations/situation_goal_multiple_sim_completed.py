# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_multiple_sim_completed.py
# Compiled at: 2022-03-10 20:35:10
# Size of source mod 2**32: 7191 bytes
from interactions import ParticipantType
from event_testing.resolver import SingleSimResolver
from event_testing.tests_with_data import TunableParticipantRanInteractionTest
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
from situations.situation_goal import SituationGoal, get_common_situation_goal_tests
from sims4.tuning.tunable import TunableVariant, Tunable, OptionalTunable, TunableList, TunableReference, TunableRange
import collections, sims4, services
logger = sims4.log.Logger('SituationGoalMultipleSimsCompleted', default_owner='jmorrow')

class SituationGoalMultipleSimsCompleted(SituationGoal):
    SIM_IDS = 'sim_ids'
    COMPLETION_COUNTS = 'completion_counts'
    INSTANCE_TUNABLES = {'_goal_test':sims4.tuning.tunable.TunableVariant(**get_common_situation_goal_tests(), **{'interaction':TunableParticipantRanInteractionTest(locked_args={'participant':ParticipantType.Actor,  'tooltip':None}), 
      'default':'interaction', 
      'description':'Primary test which triggers evaluation of goal completion.', 
      'tuning_group':GroupNames.TESTS}), 
     '_iterations_per_sim':TunableRange(description='\n            The number of times the goal test must pass on each sim.\n            ',
       tunable_type=int,
       default=1,
       minimum=1), 
     '_number_of_sims_that_must_complete_test':OptionalTunable(description='\n            This will define how many sims must complete the goal test\n            in order for the goal as a whole to be considered complete. Each sim\n            must complete the test the number of times specified by the \n            Iterations Per Sim tunable.\n            \n            If this is disabled and the list of Scenario Roles is empty, then all\n            sims of interest must complete the goal.\n            \n            If this is disabled and the list of roles is not empty, then all sims\n            with the tuned Scenario Role must complete the goal.\n            ',
       tunable=TunableRange(tunable_type=int,
       default=1,
       minimum=1)), 
     '_select_all_instantiated_sims':Tunable(description='\n            If checked, the goal system selects all instantiated sims in the zone.\n            ',
       tunable_type=bool,
       default=False), 
     '_scenario_roles':TunableList(description='\n            If non-empty, then this SituationGoal will only consider sims with\n            one of the tuned scenario roles.\n            ',
       tunable=TunableReference(description='\n                The other role in the relationship.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
       class_restrictions=('ScenarioRole', )))}

    def __init__(self, *args, reader=None, **kwargs):
        (super().__init__)(args, reader=reader, **kwargs)
        self._sim_id_to_completion_count = collections.defaultdict(int)
        self._max_sims = 0
        self._completed_sims = 0
        if reader is not None:
            sim_ids = reader.read_uint64s(self.SIM_IDS, [])
            completion_counts = reader.read_uint64s(self.COMPLETION_COUNTS, [])
            for sim_id, completion_count in zip(sim_ids, completion_counts):
                self._sim_id_to_completion_count[sim_id] = completion_count

    def setup(self):
        super().setup()
        services.get_event_manager().register_tests(self, (self._goal_test,))

    def _decommision(self):
        services.get_event_manager().unregister_tests(self, (self._goal_test,))
        super()._decommision()

    def create_seedling(self):
        seedling = super().create_seedling()
        writer = seedling.writer
        writer.write_uint64s(self.SIM_IDS, self._sim_id_to_completion_count.keys())
        writer.write_uint64s(self.COMPLETION_COUNTS, self._sim_id_to_completion_count.values())
        return seedling

    def reevaluate_goal_completion(self):
        for sim_info in self.all_sim_infos_interested_in_goal_gen():
            self._evaluate_goal_test(sim_info, SingleSimResolver(sim_info))

        self._evaluate_goal_completion()

    def _evaluate_goal_test(self, sim_info, resolver):
        if not resolver(self._goal_test):
            return False
        self._sim_id_to_completion_count[sim_info.id] += 1
        return True

    def _evaluate_goal_completion(self):
        prev_max_sims = self._max_sims
        prev_completed_sims = self._completed_sims
        interested_sim_infos = tuple(self.all_sim_infos_interested_in_goal_gen(all_instanced_sim_infos_including_babies_are_interested=(self._select_all_instantiated_sims)))
        if self._number_of_sims_that_must_complete_test is None:
            self._max_sims = len(interested_sim_infos)
        else:
            self._max_sims = self._number_of_sims_that_must_complete_test
        self._completed_sims = 0
        for sim_info in interested_sim_infos:
            if self._sim_id_to_completion_count[sim_info.id] >= self._iterations_per_sim:
                self._completed_sims += 1
                if self._completed_sims >= self._max_sims:
                    self._on_goal_completed()
                    return

        if prev_max_sims != self._max_sims or prev_completed_sims != self._completed_sims:
            self._on_goal_completed_callbacks(self, False)

    @property
    def numerical_token(self):
        return self._max_sims

    @property
    def secondary_numerical_token(self):
        return self._completed_sims

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        if self._evaluate_goal_test(sim_info, resolver):
            self._evaluate_goal_completion()


sims4.tuning.instances.lock_instance_tunables(SituationGoalMultipleSimsCompleted, _iterations=1)