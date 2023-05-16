# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gameplay_scenarios\scenario_tests_set.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 16192 bytes
import services, sims4
from aspirations.aspiration_tests import CompletedAspirationTrackTest
from clubs.club_tests import ClubTest
from event_testing.tests import TestListLoadingMixin
from filters.tunable import TunableSimFilter
from gameplay_scenarios.scenario_tests import ScenarioRoleTest, ScenarioGoalCompletedTest, ScenarioPhaseTriggeredTest
from interactions import ParticipantType, ParticipantTypeSim
from relationships.relationship_tests import TunableRelationshipTest, TunableScenarioRelationshipTest
from seasons.season_tests import SeasonTest
from sims4.tuning.tunable import TunableVariant, HasTunableFactory, AutoFactoryInit, TunableList, TunableTuple, TunableReference
import event_testing.state_tests, event_testing.test_variants, objects.object_tests, sims.sim_info_tests, statistics.skill_tests, world.world_tests, zone_tests
from sims4.tuning.tunable_base import GroupNames

class TunablePhaseTestSetVariant(TunableVariant):

    def __init__(self, *args, description='A single tunable test.', **kwargs):
        (super().__init__)(args, aspiration_track_completed=CompletedAspirationTrackTest.TunableFactory(), 
         bucks_perks_test=event_testing.test_variants.BucksPerkTest.TunableFactory(locked_args={'participant':ParticipantType.TargetSim,  'tooltip':None}), 
         buff=sims.sim_info_tests.BuffTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         career=event_testing.test_variants.TunableCareerTest.TunableFactory(locked_args={'tooltip': None}), 
         career_daily_task_completed_test=event_testing.test_variants.CareerDailyTaskCompletedTest.TunableFactory(locked_args={'participant':ParticipantType.Actor,  'tooltip':None}), 
         club=ClubTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'club':ClubTest.CLUB_USE_ANY,  'tooltip':None}), 
         collected_single_item=event_testing.test_variants.CollectedItemTest.TunableFactory(locked_args={'tooltip': None}), 
         collection=event_testing.test_variants.TunableCollectionThresholdTest(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         dead_test=sims.sim_info_tests.DeadTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         has_lot_owner=event_testing.test_variants.HasLotOwnerTest.TunableFactory(locked_args={'tooltip': None}), 
         household_size=event_testing.test_variants.HouseholdSizeTest.TunableFactory(locked_args={'participant':ParticipantType.Actor,  'tooltip':None}), 
         inventory=objects.object_tests.InventoryTest.TunableFactory(locked_args={'tooltip': None}), 
         location=world.world_tests.LocationTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         locked_portal_count=event_testing.test_variants.LockedPortalCountTest.TunableFactory(locked_args={'tooltip': None}), 
         lot_owner=event_testing.test_variants.LotOwnerTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         mood=sims.sim_info_tests.MoodTest.TunableFactory(locked_args={'who':ParticipantTypeSim.Actor,  'tooltip':None}), 
         motive=event_testing.statistic_tests.MotiveThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         nearby_floor_feature=world.floor_feature_test.NearbyFloorFeatureTest.TunableFactory(locked_args={'radius_actor':ParticipantType.Actor,  'tooltip':None}), 
         object_criteria=objects.object_tests.ObjectCriteriaTest.TunableFactory(locked_args={'tooltip': None}), 
         ranked_statistic=event_testing.statistic_tests.RankedStatThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         relationship=TunableRelationshipTest(locked_args={'subject':ParticipantType.Actor,  'test_event':0,  'tooltip':None}), 
         relative_statistic=event_testing.statistic_tests.RelativeStatTest.TunableFactory(locked_args={'source':ParticipantType.Actor,  'target':ParticipantType.TargetSim}), 
         satisfaction_points=sims.sim_info_tests.SatisfactionPointTest.TunableFactory(locked_args={'tooltip': None}), 
         scenario_relationship=TunableScenarioRelationshipTest(locked_args={'subject':ParticipantType.Actor,  'test_event':0,  'tooltip':None}), 
         scenario_role_test=ScenarioRoleTest.TunableFactory(), 
         scenario_goal_complete_test=ScenarioGoalCompletedTest.TunableFactory(locked_args={'tooltip': None}), 
         scenario_phase_triggered_test=ScenarioPhaseTriggeredTest.TunableFactory(locked_args={'tooltip': None}), 
         season=SeasonTest.TunableFactory(locked_args={'tooltip': None}), 
         sim_filter=sims.sim_info_tests.FilterTest.TunableFactory(locked_args={'filter_target':ParticipantType.Actor,  'tooltip':None}), 
         simoleons=event_testing.test_variants.TunableSimoleonsTest(locked_args={'tooltip': None}), 
         sim_info=sims.sim_info_tests.SimInfoTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         situation_job=event_testing.test_variants.TunableSituationJobTest(locked_args={'participant':ParticipantType.Actor,  'tooltip':None}), 
         skill_tag=statistics.skill_tests.SkillTagThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         skill_test=statistics.skill_tests.SkillRangeTest.TunableFactory(locked_args={'tooltip': None}), 
         state=event_testing.state_tests.TunableStateTest(locked_args={'who':ParticipantType.Object,  'tooltip':None}), 
         statistic=event_testing.statistic_tests.StatThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         time_of_day=event_testing.test_variants.TunableDayTimeTest(locked_args={'tooltip': None}), 
         topic=event_testing.test_variants.TunableTopicTest(locked_args={'subject':ParticipantType.Actor,  'target_sim':ParticipantType.TargetSim,  'tooltip':None}), 
         trait=sims.sim_info_tests.TraitTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         venue_availability=world.world_tests.VenueAvailabilityTest.TunableFactory(locked_args={'tooltip': None}), 
         zone=zone_tests.ZoneTest.TunableFactory(locked_args={'tooltip': None}), 
         description=description, **kwargs)


class ScenarioTest(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'scenario_test': TunableTuple(description='\n            A tuple of tests and actor_role.             \n            ',
                        test=TunablePhaseTestSetVariant(description='\n                A test that can be used in various parts of the scenario.\n                It can be selected from a pool of tests that are put together for scenario use.\n                '),
                        actor_role=TunableReference(description='\n                If this is not empty and subject of the test is actor;\n                the test will be applied to everyone in the scenario with selected role.\n                ',
                        manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
                        class_restrictions=('ScenarioRole', ),
                        allow_none=True),
                        actor_sim_filter=TunableReference(description='\n                An alternative way(to actor_role) to access sim_info for the tests requiring "Actor". \n                This will not create a new sim like in situations. \n                It is just a reference for the sim filter in the scenario_npc_sims.           \n                ',
                        manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER)),
                        class_restrictions=TunableSimFilter,
                        tuning_group=(GroupNames.SIM_FILTER),
                        allow_none=True),
                        secondary_actor_role=TunableReference(description='\n                The role of secondary targets for the tests.\n                Fill secondary target only for tests requiring pair of sims. Like relationship tests.\n                ',
                        manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
                        class_restrictions=('ScenarioRole', ),
                        allow_none=True),
                        secondary_actor_sim_filter=TunableReference(description='\n                An alternative way(to secondary_actor_role) to access sim_info for the tests requiring second sim.           \n                ',
                        manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER)),
                        class_restrictions=TunableSimFilter,
                        tuning_group=(GroupNames.SIM_FILTER),
                        allow_none=True))}


class ScenarioTestSet(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'scenario_tests': TunableList(description='\n            List of tuples containing a test and actor role.\n            Test can be selected from a set of tests that is tailored for scenario use.\n            ',
                         tunable=ScenarioTest.TunableFactory(description='\n                A tuple containing a test and actor role.\n                If actor_role is set the test will run for everyone in the scenario with selected role.\n                '))}


class TunableScenarioBreakTestSetVariant(TunableVariant):

    def __init__(self, *args, description='A single tunable test.', **kwargs):
        (super().__init__)(args, aspiration_track_completed=CompletedAspirationTrackTest.TunableFactory(), 
         bucks_perks_test=event_testing.test_variants.BucksPerkTest.TunableFactory(locked_args={'participant':ParticipantType.TargetSim,  'tooltip':None}), 
         buff=sims.sim_info_tests.BuffTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         career=event_testing.test_variants.TunableCareerTest.TunableFactory(locked_args={'tooltip': None}), 
         club=ClubTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'club':ClubTest.CLUB_USE_ANY,  'tooltip':None}), 
         collected_single_item=event_testing.test_variants.CollectedItemTest.TunableFactory(locked_args={'tooltip': None}), 
         dead_test=sims.sim_info_tests.DeadTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         household_size=event_testing.test_variants.HouseholdSizeTest.TunableFactory(locked_args={'participant':ParticipantType.Actor,  'tooltip':None}), 
         inventory=objects.object_tests.InventoryTest.TunableFactory(locked_args={'tooltip': None}), 
         location=world.world_tests.LocationTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         mood=sims.sim_info_tests.MoodTest.TunableFactory(locked_args={'who':ParticipantTypeSim.Actor,  'tooltip':None}), 
         motive=event_testing.statistic_tests.MotiveThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         object_criteria=objects.object_tests.ObjectCriteriaTest.TunableFactory(locked_args={'tooltip': None}), 
         ranked_statistic=event_testing.statistic_tests.RankedStatThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         satisfaction_points=sims.sim_info_tests.SatisfactionPointTest.TunableFactory(locked_args={'tooltip': None}), 
         season=SeasonTest.TunableFactory(locked_args={'tooltip': None}), 
         scenario_goal_complete_test=ScenarioGoalCompletedTest.TunableFactory(locked_args={'tooltip': None}), 
         simoleons=event_testing.test_variants.TunableTotalSimoleonsEarnedTest(), 
         skill_tag=statistics.skill_tests.SkillTagThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         state=event_testing.state_tests.TunableStateTest(locked_args={'who':ParticipantType.Object,  'tooltip':None}), 
         statistic=event_testing.statistic_tests.StatThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         trait=sims.sim_info_tests.TraitTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         zone=zone_tests.ZoneTest.TunableFactory(locked_args={'tooltip': None}), 
         description=description, 
         default='buff', **kwargs)


class TunableScenarioBreakTest(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'scenario_test': TunableTuple(description='\n            A tuple of tests and actor_role.             \n            ',
                        test=TunableScenarioBreakTestSetVariant(description='\n                A test that can be used in various part of the scenario.\n                It can be selected from a pool of tests that are put together for scenario use.\n                '),
                        actor_role=TunableReference(description='\n                If set actor_role is set and target sim of the test is actor;\n                the test will be applied to everyone in the scenario with selected role.\n                ',
                        manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
                        class_restrictions=('ScenarioRole', ),
                        allow_none=True),
                        actor_sim_filter=TunableReference(description='\n                An alternative way(to actor_role) to access sim_info for the tests requiring "Actor". \n                This will not create a new sim like in situations. \n                It is just a reference for the sim filter in the scenario_npc_sims.           \n                ',
                        manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER)),
                        class_restrictions=TunableSimFilter,
                        tuning_group=(GroupNames.SIM_FILTER),
                        allow_none=True))}


class TunableScenarioBreakTestSet(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'scenario_tests': TunableList(description='\n            List of tuples containing a test and actor role.\n            Intended to be used for checking events that may change status of scenario.\n            i.e termination of phases/scenarios or resetting goal sequences.\n            ',
                         tunable=TunableScenarioBreakTest.TunableFactory(description='\n                A tuple containing a test and actor role.\n                If actor_role is set the test will run for everyone in the scenario with selected role.\n                '))}