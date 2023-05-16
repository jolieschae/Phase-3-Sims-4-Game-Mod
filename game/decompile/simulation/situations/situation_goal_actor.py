# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_actor.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 17074 bytes
from careers.career_enums import TestEventCareersOrigin
from clubs.club_tests import ClubTest
from event_testing.test_events import TestEvent
from event_testing.resolver import DataResolver
from event_testing.results import TestResult
from interactions import ParticipantType, ParticipantTypeSim
from relationships.relationship_tests import TunableScenarioRelationshipTest
from sims4.tuning.tunable import TunableVariant, Tunable, OptionalTunable, TunableSet, TunableEnumEntry
from sims4.tuning.tunable_base import GroupNames
from situations.situation_goal import SituationGoal, get_common_situation_goal_tests
import event_testing.test_variants, services, sims.sim_info_tests, sims4.tuning.tunable, statistics.skill_tests, world.world_tests, zone_tests

class TunableSituationGoalActorPostTestVariant(TunableVariant):

    def __init__(self, description='A single tunable test.', **kwargs):
        (super().__init__)(statistic=event_testing.statistic_tests.StatThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), ranked_statistic=event_testing.statistic_tests.RankedStatThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         skill_tag=statistics.skill_tests.SkillTagThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         mood=sims.sim_info_tests.MoodTest.TunableFactory(locked_args={'who':ParticipantTypeSim.Actor,  'tooltip':None}), 
         sim_info=sims.sim_info_tests.SimInfoTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         location=world.world_tests.LocationTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         lot_owner=event_testing.test_variants.LotOwnerTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         sim_filter=sims.sim_info_tests.FilterTest.TunableFactory(locked_args={'filter_target':ParticipantType.Actor,  'tooltip':None}), 
         trait=sims.sim_info_tests.TraitTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         buff=sims.sim_info_tests.BuffTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         motive=event_testing.statistic_tests.MotiveThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         skill_test=statistics.skill_tests.SkillRangeTest.TunableFactory(locked_args={'tooltip': None}), 
         situation_job=event_testing.test_variants.TunableSituationJobTest(locked_args={'participant':ParticipantType.Actor,  'tooltip':None}), 
         career=event_testing.test_variants.TunableCareerTest.TunableFactory(locked_args={'subjects':ParticipantType.Actor,  'tooltip':None}), 
         collection=event_testing.test_variants.TunableCollectionThresholdTest(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         club=ClubTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'club':ClubTest.CLUB_USE_ANY,  'tooltip':None}), 
         zone=zone_tests.ZoneTest.TunableFactory(locked_args={'tooltip': None}), 
         scenario_relationship=TunableScenarioRelationshipTest(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         description=description, **kwargs)


class TunableSituationGoalActorPostTestSet(event_testing.tests.TestListLoadingMixin):
    DEFAULT_LIST = event_testing.tests.TestList()

    def __init__(self, description=None, **kwargs):
        if description is None:
            description = 'A list of tests.  All tests must succeed to pass the TestSet.'
        (super().__init__)(description=description, tunable=TunableSituationGoalActorPostTestVariant(), **kwargs)


class SituationGoalActor(SituationGoal):
    INSTANCE_TUNABLES = {'_goal_test':sims4.tuning.tunable.TunableVariant(**get_common_situation_goal_tests(), **{'default':'buff', 
      'description':'Primary test which triggers evaluation of goal completion.', 
      'tuning_group':GroupNames.TESTS}), 
     '_post_tests':TunableSituationGoalActorPostTestSet(description='\n           A set of tests that must all pass when the player satisfies the goal_test \n           for the goal to be consider completed.\nThese test can only consider the \n           actor and the environment. \ne.g. Practice in front of mirror while drunk.\n           ',
       tuning_group=GroupNames.TESTS), 
     'ignore_goal_precheck':Tunable(description='\n            Checking this box will skip the normal goal pre-check in the case that other tuning makes the goal\n            continue to be valid. For example, for a collection test, we may want to give the goal to collect\n            an additional object even though the test that we have collected this object before will already\n            pass. This allows us to tune a more specific pre-test to check for the amount we want to collect.',
       tunable_type=bool,
       default=False), 
     'use_numeric_test_results':Tunable(description='\n            If checked, then we will display the numerical test results from\n            a Goal Test in the goal panel UI instead of the normal iteration\n            counts (if the goal supports numerical test results).\n            \n            An example where this is useful is with a simoleon test, where we are\n            testing that a household has a certain amount of money. In this example,\n            the current and target household funds will be used in place of the\n            normal completed and max iterations.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.UI)}

    @classmethod
    def can_be_given_as_goal(cls, actor, situation, **kwargs):
        result = (super(SituationGoalActor, cls).can_be_given_as_goal)(actor, situation, **kwargs)
        if not result:
            return result
        if actor is not None:
            if not cls.ignore_goal_precheck:
                resolver = event_testing.resolver.DataResolver(actor.sim_info)
                result = resolver(cls._goal_test)
                if result:
                    return TestResult(False, 'Goal test already passes and so cannot be given as goal.')
        return TestResult.TRUE

    def _register_events(self):
        services.get_event_manager().register_tests(self, (self._goal_test,))

    def _unregister_events(self):
        services.get_event_manager().unregister_tests(self, (self._goal_test,))

    def setup(self):
        super().setup()
        self._register_events()

    def _decommision(self):
        self._unregister_events()
        super()._decommision()

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        result = resolver(self._goal_test)
        if result.is_numeric:
            if self.use_numeric_test_results:
                prev_count = self._count
                prev_iterations = self._iterations
                self._count = int(result.current_value)
                self._iterations = int(result.goal_value)
                if not result:
                    if not prev_count != self._count:
                        if prev_iterations != self._iterations:
                            self._on_iteration_completed()
                            return False
        else:
            return result or False
        return super()._run_goal_completion_tests(sim_info, event, resolver)


class SituationGoalActorTrait(SituationGoalActor):
    TRAIT_GUID = 'trait_guid'
    INSTANCE_TUNABLES = {'_goal_test': sims.sim_info_tests.TraitTest.TunableFactory(description='\n            Primary test which triggers evaluation of goal completion.\n            ',
                     locked_args={'subject':ParticipantType.Actor, 
                    'tooltip':None, 
                    'blacklist_traits':None, 
                    'blacklist_trait_types':None, 
                    'num_blacklist_allowed':0},
                     tuning_group=(GroupNames.TESTS))}

    def __init__(self, *args, reader=None, **kwargs):
        (super().__init__)(args, reader=reader, **kwargs)
        self._trait_guid = None
        if reader is not None:
            self._trait_guid = reader.read_uint64(self.TRAIT_GUID, None)

    def _register_events(self):
        for trait in self._goal_test.whitelist_traits:
            services.get_event_manager().register_with_custom_key(self, TestEvent.TraitAddEvent, trait.guid64)

        for trait_type in self._goal_test.whitelist_trait_types:
            services.get_event_manager().register_with_custom_key(self, TestEvent.TraitAddEvent, trait_type)

    def _unregister_events(self):
        for trait in self._goal_test.whitelist_traits:
            services.get_event_manager().unregister_with_custom_key(self, TestEvent.TraitAddEvent, trait.guid64)

        for trait_type in self._goal_test.whitelist_trait_types:
            services.get_event_manager().unregister_with_custom_key(self, TestEvent.TraitAddEvent, trait_type)

    def create_seedling(self):
        seedling = super().create_seedling()
        writer = seedling.writer
        if self._trait_guid is not None:
            writer.write_uint64(self.TRAIT_GUID, self._trait_guid)
        return seedling

    def get_trait_guid(self):
        return self._trait_guid

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        if not resolver(self._goal_test):
            return False
        trait_guid = resolver.event_kwargs.get('trait_guid')
        self._trait_guid = trait_guid
        return super()._run_goal_completion_tests(sim_info, event, resolver)


class SituationGoalActorCareer(SituationGoalActor):
    CAREER_GUID = 'career_guid'
    CAREER_TRACK = 'career_track'
    CAREER_LEVEL = 'career_level'
    INSTANCE_TUNABLES = {'_goal_test':sims4.tuning.tunable.TunableVariant(description='\n            Primary test which triggers evaluation of goal completion.\n            ',
       career=event_testing.test_variants.TunableCareerTest.TunableFactory(locked_args={'tooltip': None}),
       career_promoted=event_testing.test_variants.CareerPromotedTest.TunableFactory(locked_args={'tooltip': None}),
       career_changed=event_testing.test_variants.CareerChangedTest.TunableFactory(locked_args={'tooltip': None}),
       tuning_group=GroupNames.TESTS), 
     '_evaluate_on_test_event_origin':OptionalTunable(description='\n            Specify when to evaluate the goal test based on the origin of where the \n            Career TestEvents are sent from. \n            If disabled, the goal test will run for every Career TestEvent processed.\n            ',
       tunable=TunableSet(description='            \n                The goal test will only evaluate when the Career TestEvents come from \n                one of these tuned origins. \n            \n                Ex. GotJob goal should only run when the TestEvent.CareerEvent originates from JOIN_CAREER.  \n                ',
       tunable=TunableEnumEntry(description='\n                    The origin from which the request to process Career TestEvents is from. \n                    ',
       tunable_type=TestEventCareersOrigin,
       default=(TestEventCareersOrigin.UNSPECIFIED),
       invalid_enums=(
      TestEventCareersOrigin.UNSPECIFIED,))),
       disabled_name='any_origin',
       enabled_name='specific_origins',
       tuning_group=GroupNames.TESTS)}

    def __init__(self, *args, reader=None, **kwargs):
        (super().__init__)(args, reader=reader, **kwargs)
        self._career_guid = None
        self._career_track = None
        self._career_level = None
        if reader is not None:
            self._career_guid = reader.read_uint64(self.CAREER_GUID, None)
            self._career_track = reader.read_uint64(self.CAREER_TRACK, None)
            self._career_level = reader.read_uint64(self.CAREER_LEVEL, None)

    def create_seedling(self):
        seedling = super().create_seedling()
        writer = seedling.writer
        if self._career_guid is not None:
            writer.write_uint64(self.CAREER_GUID, self._career_guid)
        if self._career_track is not None:
            writer.write_uint64(self.CAREER_TRACK, self._career_track)
        if self._career_level is not None:
            writer.write_uint64(self.CAREER_LEVEL, self._career_level)
        return seedling

    def get_career_guid(self):
        return self._career_guid

    def get_career_level(self):
        return self._career_level

    def get_career_track(self):
        return self._career_track

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        if self._evaluate_on_test_event_origin:
            test_event_origin = resolver.event_kwargs.get('test_event_origin')
            if test_event_origin is not None:
                if test_event_origin not in self._evaluate_on_test_event_origin:
                    return False
        else:
            return resolver(self._goal_test) or False
        career_level = resolver.event_kwargs.get('level')
        career_track = resolver.event_kwargs.get('track')
        if career_track is not None:
            self._career_track = career_track.guid64
        if career_level is not None:
            self._career_level = career_level
        return super()._run_goal_completion_tests(sim_info, event, resolver)