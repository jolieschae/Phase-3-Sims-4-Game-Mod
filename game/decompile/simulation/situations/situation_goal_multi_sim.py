# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_multi_sim.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 23010 bytes
import event_testing
from buffs.buff import Buff
from event_testing.results import TestResult
import services, sims4.tuning
from sims4.math import MAX_INT32
from sims4.tuning.tunable import AutoFactoryInit, TunableReference, TunableSet, Tunable, TunableSingletonFactory, TunableEnumWithFilter, TunableVariant, HasTunableSingletonFactory, TunableList
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexproperty
from situations.situation_goal import SituationGoal
from statistics.mood import Mood
import sims4.log, tag
logger = sims4.log.Logger('Situations')

class TunableSituationGoalSimCountVariant(TunableVariant):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, fixed=TunableSituationGoalSimCount_Fixed.TunableFactory(), 
         sims_in_situation=TunableSituationGoalSimCount_SimsInSituation.TunableFactory(), 
         default='fixed', **kwargs)

    def should_refresh_when_sim_count_changes(self, sim, job_type):
        raise NotImplementedError

    def test_sim_info(self, sim_info, situation):
        raise NotImplementedError

    def get_max_iterations(self, situation, for_ui=False):
        raise NotImplementedError


class TunableSituationGoalSimCount_Fixed(HasTunableSingletonFactory):
    FACTORY_TUNABLES = {'count': Tunable(description='\n            A fixed count of how many sims are required (default).\n            ',
                tunable_type=int,
                default=2)}

    def __init__(self, count, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.count = count

    def should_refresh_when_sim_count_changes(self, sim, job_type):
        return False

    def test_sim_info(self, sim_info, situation):
        return True

    def get_max_iterations(self, situation, for_ui=False):
        return self.count


class TunableSituationGoalSimCount_SimsInSituation(HasTunableSingletonFactory):
    FACTORY_TUNABLES = {'required_jobs': TunableList(description='\n            If this list is non-empty then only sims with the given job(s) will be counted.\n            ',
                        tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB))))}

    def __init__(self, required_jobs, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.required_jobs = required_jobs

    def should_refresh_when_sim_count_changes(self, sim, job_type):
        if self.required_jobs:
            return job_type in self.required_jobs
        return True

    def test_sim_info(self, sim_info, situation):
        if situation is None:
            logger.error('TunableSituationGoalSimCount_SimsInSituation variant being evaluated but situation is None.')
            return False
        else:
            if not situation.is_sim_info_in_situation(sim_info):
                return False
            if self.required_jobs:
                sim = sim_info.get_sim_instance()
                if sim is None:
                    return False
                job = situation.get_current_job_for_sim(sim)
                if job is None or job not in self.required_jobs:
                    return False
        return True

    def get_max_iterations(self, situation, for_ui=False):
        if situation is None:
            if for_ui:
                return 0
        else:
            logger.error('TunableSituationGoalSimCount_SimsInSituation variant being evaluated but situation is None.')
            return MAX_INT32
            if not for_ui:
                situation_manager = services.get_zone_situation_manager()
                return situation_manager is None or situation_manager.sim_assignment_complete or MAX_INT32
            if not self.required_jobs:
                count = len(list(situation.all_sims_in_situation_gen()))
            else:
                count = 0
                for sim in situation.all_sims_in_situation_gen():
                    job = situation.get_current_job_for_sim(sim)
                    if job in self.required_jobs:
                        count += 1

        return count


class MultipleSimInteractionOfInterest(AutoFactoryInit):
    FACTORY_TUNABLES = {'affordance':TunableReference(description='\n                The affordance in question that is being run by all the sims.\n                ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION),
       class_restrictions='SuperInteraction',
       allow_none=True), 
     'tags':TunableSet(description='\n                A set of tags that match the affordance being run by all the sims. \n                ',
       tunable=TunableEnumWithFilter(tunable_type=(tag.Tag), default=(tag.Tag.INVALID),
       filter_prefixes=(tag.INTERACTION_PREFIX))), 
     'sim_count':TunableSituationGoalSimCountVariant(description='\n                The number of sims simultaneously running the appropriate interactions.\n                ')}
    expected_kwargs = (
     (
      'interaction', event_testing.test_constants.FROM_EVENT_DATA),)

    def get_expected_args(self):
        return dict(self.expected_kwargs)

    def __call__(self, interaction=None):
        if interaction.get_interaction_type() is self.affordance:
            return TestResult.TRUE
        if self.tags & interaction.get_category_tags():
            return TestResult.TRUE
        return TestResult(False, 'Failed affordance check: {} is not {} and does not have any matching tags in {}.', interaction.affordance, self.affordance, self.tags)

    def custom_keys_gen(self):
        if self.affordance:
            yield self.affordance
        for tag in self.tags:
            yield tag


TunableMultipleSimInteractionOfInterest = TunableSingletonFactory.create_auto_factory(MultipleSimInteractionOfInterest)

class SituationGoalMultipleSimsInInteraction(SituationGoal):
    INSTANCE_TUNABLES = {'_goal_test':TunableMultipleSimInteractionOfInterest(tuning_group=GroupNames.TESTS), 
     '_select_all_instantiated_sims':sims4.tuning.tunable.Tunable(bool, False, description='\n                If true, the goal system selects all instantiated sims in the zone.\n                ')}

    def __init__(self, *args, reader=None, **kwargs):
        (super().__init__)(args, reader=reader, **kwargs)
        self._sims_running_interaction = set()
        self._test_events = set()

    def setup(self):
        super().setup()

        def test_affordance(sim):
            return sim.si_state.is_running_affordance(self._goal_test.affordance) or sim.get_running_interactions_by_tags(self._goal_test.tags)

        for sim in self.all_sims_interested_in_goal_gen(all_instanced_sims_are_interested=(self._select_all_instantiated_sims)):
            if test_affordance(sim):
                self._sims_running_interaction.add(sim.id)

        for custom_key in self._goal_test.custom_keys_gen():
            services.get_event_manager().register_with_custom_key(self, event_testing.test_events.TestEvent.InteractionStart, custom_key)
            services.get_event_manager().register_with_custom_key(self, event_testing.test_events.TestEvent.InteractionComplete, custom_key)

    def _decommision(self):
        for custom_key in self._goal_test.custom_keys_gen():
            services.get_event_manager().unregister_with_custom_key(self, event_testing.test_events.TestEvent.InteractionStart, custom_key)
            services.get_event_manager().unregister_with_custom_key(self, event_testing.test_events.TestEvent.InteractionComplete, custom_key)

        super()._decommision()

    def _valid_event_sim_of_interest(self, sim_info):
        return self._select_all_instantiated_sims or sim_info in self.all_sim_infos_interested_in_goal_gen()

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        if not resolver(self._goal_test):
            return False
        elif not self._goal_test.sim_count.test_sim_info(sim_info, self._situation):
            return False
            if event == event_testing.test_events.TestEvent.InteractionStart:
                self._sims_running_interaction.add(sim_info.id)
        else:
            self._sims_running_interaction.discard(sim_info.id)
        self._on_iteration_completed()
        if self.completed_iterations >= self.max_iterations:
            return True
        return False

    def should_refresh_when_sim_count_changes(self, sim, job_type):
        return self._goal_test.sim_count.should_refresh_when_sim_count_changes(sim, job_type)

    @property
    def completed_iterations(self):
        return len(self._sims_running_interaction)

    @flexproperty
    def max_iterations(cls, inst):
        if inst is None:
            return cls._goal_test.sim_count.get_max_iterations(None, for_ui=True)
        return inst._goal_test.sim_count.get_max_iterations(inst._situation)

    @property
    def numerical_token(self):
        return self._goal_test.sim_count.get_max_iterations((self._situation), for_ui=True)


sims4.tuning.instances.lock_instance_tunables(SituationGoalMultipleSimsInInteraction, _iterations=1,
  should_reevaluate_on_load=False)

class MultipleSimMoodOfInterest(AutoFactoryInit):
    FACTORY_TUNABLES = {'mood':Mood.TunableReference(description='\n                The mood that we are hoping for the sims to achieve.\n                '), 
     'sim_count':TunableSituationGoalSimCountVariant(description='\n                The number of sims the tuned mood at the same time.\n                ')}


TunableMultipleSimMoodOfInterest = TunableSingletonFactory.create_auto_factory(MultipleSimMoodOfInterest)

class SituationGoalMultipleSimsInMood(SituationGoal):
    INSTANCE_TUNABLES = {'_goal_test':TunableMultipleSimMoodOfInterest(tuning_group=GroupNames.TESTS), 
     '_select_all_instantiated_sims':sims4.tuning.tunable.Tunable(bool, False, description='\n                If true, the goal system selects all instantiated sims in the zone.\n                '), 
     '_give_goal_even_if_it_would_auto_pass':Tunable(description='\n                If checked then this goal will be given even if the goal would\n                instantly complete.  An example wanting this is the Play Date\n                Where there is only one possible goal and we want to give the\n                player the score for completing it.\n                ',
       tunable_type=bool,
       default=False)}

    @classmethod
    def can_be_given_as_goal(cls, actor, situation, scenario=None, **kwargs):
        result = (super(SituationGoalMultipleSimsInMood, cls).can_be_given_as_goal)(actor, situation, **kwargs)
        if not result:
            return result
        if cls._give_goal_even_if_it_would_auto_pass:
            return TestResult.TRUE
        sims_in_the_mood = set()
        for sim in SituationGoal.all_sims_interested_in_goal_gen(sim_info=actor, situation=situation, scenario=scenario, all_instanced_sims_are_interested=(cls._select_all_instantiated_sims)):
            if sim.get_mood() is cls._goal_test.mood:
                sims_in_the_mood.add(sim.id)

        if len(sims_in_the_mood) >= cls._goal_test.sim_count.get_max_iterations(situation):
            return TestResult(False, 'Test Auto Passes: {} sims in {} mood')
        return TestResult.TRUE

    def __init__(self, *args, reader=None, **kwargs):
        (super().__init__)(args, reader=reader, **kwargs)
        self._sims_in_the_mood = set()
        self._test_events = set()

    def setup(self):
        super().setup()
        for sim in self.all_sims_interested_in_goal_gen(all_instanced_sims_are_interested=(self._select_all_instantiated_sims)):
            if sim.get_mood() is self._goal_test.mood:
                self._sims_in_the_mood.add(sim.id)

        self._test_events.add(event_testing.test_events.TestEvent.MoodChange)
        services.get_event_manager().register(self, self._test_events)

    def _decommision(self):
        services.get_event_manager().unregister(self, self._test_events)
        super()._decommision()

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        if not self._select_all_instantiated_sims:
            if sim_info not in self.all_sim_infos_interested_in_goal_gen():
                return False
        elif not self._goal_test.sim_count.test_sim_info(sim_info, self._situation):
            return False
            if sim_info.get_mood() is self._goal_test.mood:
                self._sims_in_the_mood.add(sim_info.id)
        else:
            self._sims_in_the_mood.discard(sim_info.id)
        self._on_iteration_completed()
        if self.completed_iterations >= self.max_iterations:
            return True
        return False

    def should_refresh_when_sim_count_changes(self, sim, job_type):
        return self._goal_test.sim_count.should_refresh_when_sim_count_changes(sim, job_type)

    @property
    def completed_iterations(self):
        return len(self._sims_in_the_mood)

    @flexproperty
    def max_iterations(cls, inst):
        if inst is None:
            return cls._goal_test.sim_count.get_max_iterations(None, for_ui=True)
        return inst._goal_test.sim_count.get_max_iterations(inst._situation)

    @property
    def numerical_token(self):
        return self._goal_test.sim_count.get_max_iterations((self._situation), for_ui=True)


sims4.tuning.instances.lock_instance_tunables(SituationGoalMultipleSimsInMood, _iterations=1)

class MultipleSimBuffOfInterest(AutoFactoryInit):
    FACTORY_TUNABLES = {'buff_type':Buff.TunablePackSafeReference(description='\n                The buff that we are hoping for the sims to have.\n                '), 
     'sim_count':TunableSituationGoalSimCountVariant(description='\n                The number of sims with the buff at the same time.\n                ')}


TunableMultipleSimBuffOfInterest = TunableSingletonFactory.create_auto_factory(MultipleSimBuffOfInterest)

class SituationGoalMultipleSimsWithBuff(SituationGoal):
    INSTANCE_TUNABLES = {'_goal_test':TunableMultipleSimBuffOfInterest(tuning_group=GroupNames.TESTS), 
     '_select_all_instantiated_sims':sims4.tuning.tunable.Tunable(bool, False, description='\n                If true, the goal system selects all instantiated sims in the zone.\n                '), 
     '_give_goal_even_if_it_would_auto_pass':Tunable(description='\n                If checked then this goal will be given even if the goal would\n                instantly complete.  An example wanting this is the Play Date\n                Where there is only one possible goal and we want to give the\n                player the score for completing it.\n                ',
       tunable_type=bool,
       default=False)}

    @classmethod
    def can_be_given_as_goal(cls, actor, situation, scenario=None, **kwargs):
        result = super(SituationGoalMultipleSimsWithBuff, cls).can_be_given_as_goal(actor, situation)
        if not result:
            return result
        if cls._goal_test.buff_type is None:
            return TestResult(False, 'Unknown _goal_test.buff_type')
        if cls._give_goal_even_if_it_would_auto_pass:
            return TestResult.TRUE
        sims_with_the_buff = set()
        for sim in SituationGoal.all_sims_interested_in_goal_gen(sim_info=None, situation=None, scenario=None, all_instanced_sims_are_interested=(cls._select_all_instantiated_sims)):
            if sim.has_buff(cls._goal_test.buff_type):
                sims_with_the_buff.add(sim.id)

        if len(sims_with_the_buff) >= cls._goal_test.sim_count.get_max_iterations(situation):
            return TestResult(False, 'Test Auto Passes: {} sims with buff {}', len(sims_with_the_buff), cls._goal_test.buff_type)
        return TestResult.TRUE

    def __init__(self, *args, reader=None, **kwargs):
        (super().__init__)(args, reader=reader, **kwargs)
        self._sims_with_the_buff = set()
        self._test_events = set()

    def setup(self):
        super().setup()
        if self._goal_test.buff_type is not None:
            for sim in self.all_sims_interested_in_goal_gen(all_instanced_sims_are_interested=(self._select_all_instantiated_sims)):
                if sim.has_buff(self._goal_test.buff_type):
                    self._sims_with_the_buff.add(sim.id)

        custom_key = self._goal_test.buff_type
        services.get_event_manager().register_with_custom_key(self, event_testing.test_events.TestEvent.BuffBeganEvent, custom_key)
        services.get_event_manager().register_with_custom_key(self, event_testing.test_events.TestEvent.BuffEndedEvent, custom_key)

    def _decommision(self):
        custom_key = self._goal_test.buff_type
        services.get_event_manager().unregister_with_custom_key(self, event_testing.test_events.TestEvent.BuffBeganEvent, custom_key)
        services.get_event_manager().unregister_with_custom_key(self, event_testing.test_events.TestEvent.BuffEndedEvent, custom_key)
        super()._decommision()

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        if not self._select_all_instantiated_sims:
            if sim_info not in self.all_sim_infos_interested_in_goal_gen():
                return False
        elif not self._goal_test.sim_count.test_sim_info(sim_info, self._situation):
            return False
            if sim_info.has_buff(self._goal_test.buff_type):
                self._sims_with_the_buff.add(sim_info.id)
        else:
            self._sims_with_the_buff.discard(sim_info.id)
        self._on_iteration_completed()
        if self.completed_iterations >= self.max_iterations:
            return True
        return False

    def should_refresh_when_sim_count_changes(self, sim, job_type):
        return self._goal_test.sim_count.should_refresh_when_sim_count_changes(sim, job_type)

    @property
    def completed_iterations(self):
        return len(self._sims_with_the_buff)

    @flexproperty
    def max_iterations(cls, inst):
        if inst is None:
            return cls._goal_test.sim_count.get_max_iterations(None, for_ui=True)
        return inst._goal_test.sim_count.get_max_iterations(inst._situation)

    @property
    def numerical_token(self):
        return self._goal_test.sim_count.get_max_iterations((self._situation), for_ui=True)


sims4.tuning.instances.lock_instance_tunables(SituationGoalMultipleSimsWithBuff, _iterations=1)