# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_object_interaction.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 8368 bytes
from event_testing.results import TestResult
from event_testing.tests_with_data import TunableParticipantRanInteractionTest
from interactions import ParticipantType, ParticipantTypeSim
from sims4.tuning.tunable import TunableVariant, Tunable, TunableEnumEntry
from sims4.tuning.tunable_base import GroupNames
from situations.situation_goal import SituationGoal
import event_testing.state_tests, event_testing.test_variants, objects.object_tests, services, sims.sim_info_tests, statistics.skill_tests, world.world_tests, sims4.log
logger = sims4.log.Logger('SituationGoalObjectInteraction')

class TunableSituationGoalActorObjectPostTestVariant(TunableVariant):

    def __init__(self, description='A single tunable test.', **kwargs):
        (super().__init__)(state=event_testing.state_tests.TunableStateTest(locked_args={'who':ParticipantType.Object,  'tooltip':None}), statistic=event_testing.statistic_tests.StatThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         skill_tag=statistics.skill_tests.SkillTagThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         mood=sims.sim_info_tests.MoodTest.TunableFactory(locked_args={'who':ParticipantTypeSim.Actor,  'tooltip':None}), 
         location=world.world_tests.LocationTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         sim_info=sims.sim_info_tests.SimInfoTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         trait=sims.sim_info_tests.TraitTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         topic=event_testing.test_variants.TunableTopicTest(locked_args={'subject':ParticipantType.Actor,  'target_sim':ParticipantType.TargetSim,  'tooltip':None}), 
         buff=sims.sim_info_tests.BuffTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         motive=event_testing.statistic_tests.MotiveThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         situation_job=event_testing.test_variants.TunableSituationJobTest(locked_args={'participant':ParticipantType.Actor,  'tooltip':None}), 
         object_criteria=objects.object_tests.ObjectCriteriaTest.TunableFactory(locked_args={'tooltip': None}), 
         description=description, **kwargs)


class TunableSituationGoalActorObjectPostTestSet(event_testing.tests.TestListLoadingMixin):
    DEFAULT_LIST = event_testing.tests.TestList()

    def __init__(self, description=None, **kwargs):
        if description is None:
            description = 'A list of tests.  All tests must succeed to pass the TestSet.'
        (super().__init__)(description=description, tunable=TunableSituationGoalActorObjectPostTestVariant(), **kwargs)


class SituationGoalObjectInteraction(SituationGoal):
    ACTUAL_OBJECT_DEFINITION_ID = 'actual_object_definition_id'
    INSTANCE_TUNABLES = {'_goal_test':TunableParticipantRanInteractionTest(locked_args={'participant':ParticipantType.Actor, 
      'tooltip':None},
       tuning_group=GroupNames.TESTS), 
     '_post_tests':TunableSituationGoalActorObjectPostTestSet(description='\n                A set of tests that must all pass when the player satisfies the goal_test \n                for the goal to be consider completed.',
       tuning_group=GroupNames.TESTS), 
     '_persist_object':Tunable(description='\n            Whether or not to persist the object that caused this goal to be completed.\n            To show in the UI, for example.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.PERSISTENCE), 
     '_persist_participant':TunableEnumEntry(description='\n            Store the tuned participant that contributed to causing this goal to be completed.\n            To show in the UI, for example. Note: This will overwrite the PersistObject tunable.\n            ',
       tunable_type=ParticipantType,
       default=None,
       tuning_group=GroupNames.PERSISTENCE)}

    def __init__(self, *args, reader=None, **kwargs):
        (super().__init__)(args, reader=reader, **kwargs)
        self._actual_target_object_definition_id = None
        if reader is not None:
            if self._persist_object or self._persist_participant:
                self._actual_target_object_definition_id = reader.read_uint64(self.ACTUAL_OBJECT_DEFINITION_ID, None)

    def create_seedling(self):
        seedling = super().create_seedling()
        writer = seedling.writer
        if self._actual_target_object_definition_id is not None:
            if self._persist_object or self._persist_participant:
                writer.write_uint64(self.ACTUAL_OBJECT_DEFINITION_ID, self._actual_target_object_definition_id)
        return seedling

    def get_actual_target_object_definition_id(self):
        return self._actual_target_object_definition_id

    @classmethod
    def can_be_given_as_goal(cls, actor, situation, **kwargs):
        result = (super(SituationGoalObjectInteraction, cls).can_be_given_as_goal)(actor, situation, **kwargs)
        if not result:
            return result
        return TestResult.TRUE

    def setup(self):
        super().setup()
        services.get_event_manager().register_tests(self, (self._goal_test,))

    def _decommision(self):
        services.get_event_manager().unregister_tests(self, (self._goal_test,))
        super()._decommision()

    def _record_given_object(self, obj):
        object_definition = obj.definition if obj is not None else None
        if object_definition is not None:
            self._actual_target_object_definition_id = object_definition.id

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        if not resolver(self._goal_test):
            return False
        result = super()._run_goal_completion_tests(sim_info, event, resolver)
        if result:
            if self._persist_object:
                if resolver.interaction.target is not None:
                    self._record_given_object(resolver.interaction.target)
                else:
                    logger.warn('The target object of this interaction is None.')
            if self._persist_participant:
                self._record_given_object(resolver.interaction.get_participant(participant_type=(self._persist_participant)))
        return result