# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 65443 bytes
import random
from aspirations.aspiration_tests import CompletedAspirationTrackTest
from clock import interval_in_sim_minutes
from clubs.club_tests import ClubTest
from crafting.photography_tests import TookPhotoTest
from distributor.shared_messages import IconInfoData, build_icon_info_msg
from drama_scheduler.drama_node_tests import FestivalRunningTest
from event_testing.common_event_tests import ParticipantTypeTargetAllRelationships
from event_testing.resolver import GlobalResolver, DoubleSimResolver, SingleSimResolver, DataResolver
from event_testing.results import TestResult
from interactions import ParticipantType, ParticipantTypeActorTargetSim, ParticipantTypeSim
from interactions.money_payout import MoneyChange
from interactions.utils.display_mixin import get_display_mixin
from interactions.utils.loot_ops import DialogLootOp, StateChangeLootOp, AwardWhimBucksLootOp, AddTraitLootOp, RemoveTraitLootOp
from interactions.utils.reactions import ReactionLootOp
from interactions.utils.success_chance import SuccessChance
from interactions.utils.death import DeathTracker
from relationships.relationship_tests import TunableRelationshipTest, TunableScenarioRelationshipTest
from seasons.season_tests import SeasonTest
from sims4.callback_utils import CallableList
from sims4.tuning.instances import HashedTunedInstanceMetaclass, TunedInstanceMetaclass
from sims4.tuning.tunable import Tunable, TunableEnumEntry, TunableList, TunableReference, TunableSet, TunableTuple, TunableVariant, TunableResourceKey, TunableSimMinute, HasTunableReference, OptionalTunable
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod, flexproperty, classproperty
from situations.situation_types import SituationGoalDisplayType
from statistics.statistic_ops import TunableStatisticChange
from tag import Tag
from tunable_time import TunableTimeOfDay
from ui.ui_dialog import UiDialogOk
from ui.ui_dialog_notification import UiDialogNotification, TunableUiDialogNotificationSnippet
import alarms, buffs.buff_ops, enum, event_testing.state_tests, event_testing.test_variants, event_testing.tests, objects.object_tests, services, sims.sim_info_tests, sims4.resources, situations, statistics.skill_tests, world.world_tests, zone_tests

class TunableWeightedSituationGoalReference(TunableTuple):

    def __init__(self, pack_safe=False, **kwargs):
        super().__init__(weight=Tunable(float, 1.0, description='Higher number means higher chance of being selected.'),
          goal=TunableReference((services.get_instance_manager(sims4.resources.Types.SITUATION_GOAL)),
          description='A goal in the set.',
          pack_safe=pack_safe))


class TunableSituationGoalPreTestVariant(TunableVariant):

    def __init__(self, description='A single tunable test.', **kwargs):
        (super().__init__)(bucks_perks_test=event_testing.test_variants.BucksPerkTest.TunableFactory(locked_args={'tooltip': None}), 
         buff=sims.sim_info_tests.BuffTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         career=event_testing.test_variants.TunableCareerTest.TunableFactory(locked_args={'tooltip': None}), 
         club=ClubTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'club':ClubTest.CLUB_USE_ANY,  'tooltip':None}), 
         collection=event_testing.test_variants.TunableCollectionThresholdTest(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         detective_clues=event_testing.test_variants.DetectiveClueTest.TunableFactory(locked_args={'participant':ParticipantType.Actor,  'tooltip':None}), 
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
         season=SeasonTest.TunableFactory(locked_args={'tooltip': None}), 
         sim_filter=sims.sim_info_tests.FilterTest.TunableFactory(locked_args={'filter_target':ParticipantType.Actor,  'tooltip':None}), 
         sim_info=sims.sim_info_tests.SimInfoTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         situation_job=event_testing.test_variants.TunableSituationJobTest(locked_args={'participant':ParticipantType.Actor,  'tooltip':None}), 
         situation_running=event_testing.test_variants.TunableSituationRunningTest(locked_args={'tooltip': None}), 
         skill_tag=statistics.skill_tests.SkillTagThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         skill_test=statistics.skill_tests.SkillRangeTest.TunableFactory(locked_args={'tooltip': None}), 
         state=event_testing.state_tests.TunableStateTest(locked_args={'who':ParticipantType.Object,  'tooltip':None}), 
         statistic=event_testing.statistic_tests.StatThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         time_of_day=event_testing.test_variants.TunableDayTimeTest(locked_args={'tooltip': None}), 
         trait=sims.sim_info_tests.TraitTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
         zone=zone_tests.ZoneTest.TunableFactory(locked_args={'tooltip': None}), 
         description=description, **kwargs)


def get_common_situation_goal_tests():
    return {'aspiration_track_completed':CompletedAspirationTrackTest.TunableFactory(), 
     'buff':sims.sim_info_tests.BuffTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'blacklist':None,  'tooltip':None}), 
     'buff_added':sims.sim_info_tests.BuffAddedTest.TunableFactory(locked_args={'tooltip': None}), 
     'mood':sims.sim_info_tests.MoodTest.TunableFactory(locked_args={'who': ParticipantTypeSim.Actor}, description='A test to run to determine if the player has attained a specific mood.'), 
     'skill_tag':statistics.skill_tests.SkillTagThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
     'statistic':event_testing.statistic_tests.StatThresholdTest.TunableFactory(stat_class_restriction_override=(('Statistic', 'Skill', 'Commodity'), ), locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
     'ranked_statistic':event_testing.statistic_tests.RankedStatThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
     'career':event_testing.test_variants.TunableCareerTest.TunableFactory(locked_args={'tooltip': None}), 
     'career_daily_task_completed_test':event_testing.test_variants.CareerDailyTaskCompletedTest.TunableFactory(locked_args={'participant':ParticipantType.Actor,  'tooltip':None}), 
     'collection':event_testing.test_variants.TunableCollectionThresholdTest(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
     'inventory':objects.object_tests.InventoryTest.TunableFactory(locked_args={'tooltip': None}), 
     'collected_single_item':event_testing.test_variants.CollectedItemTest.TunableFactory(locked_args={'tooltip': None}), 
     'club':ClubTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'club':ClubTest.CLUB_USE_ANY,  'tooltip':None}), 
     'situation_running':event_testing.test_variants.TunableSituationRunningTest(), 
     'took_photo':TookPhotoTest.TunableFactory(), 
     'satisfaction_points':sims.sim_info_tests.SatisfactionPointTest.TunableFactory(locked_args={'tooltip': None}), 
     'simoleons':event_testing.test_variants.TunableSimoleonsTest(locked_args={'tooltip': None}), 
     'household_size':event_testing.test_variants.HouseholdSizeTest.TunableFactory(locked_args={'participant':ParticipantType.Actor,  'tooltip':None}), 
     'relationships':TunableRelationshipTest(participant_type_override=(ParticipantTypeTargetAllRelationships, ParticipantTypeTargetAllRelationships.AllRelationships), locked_args={'subject':ParticipantType.Actor,  'tooltip':None}), 
     'scenario_relationships':TunableScenarioRelationshipTest(locked_args={'subject':ParticipantType.Actor,  'tooltip':None})}


class TunableSituationGoalPreTestSet(event_testing.tests.TestListLoadingMixin):
    DEFAULT_LIST = event_testing.tests.TestList()

    def __init__(self, description=None, **kwargs):
        if description is None:
            description = 'A list of tests.  All tests must succeed to pass the TestSet.'
        (super().__init__)(description=description, tunable=TunableSituationGoalPreTestVariant(), **kwargs)


class TunableSituationGoalPostTestVariant(TunableVariant):

    def __init__(self, description='A single tunable test.', **kwargs):
        (super().__init__)(buff=sims.sim_info_tests.BuffTest.TunableFactory(participant_type_override=(ParticipantTypeActorTargetSim, ParticipantTypeActorTargetSim.Actor), locked_args={'tooltip': None}), 
         career=event_testing.test_variants.TunableCareerTest.TunableFactory(locked_args={'tooltip': None}), 
         club=ClubTest.TunableFactory(locked_args={'subject':ParticipantType.Actor,  'club':ClubTest.CLUB_USE_ANY,  'tooltip':None}), 
         collection=event_testing.test_variants.TunableCollectionThresholdTest(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         inventory=objects.object_tests.InventoryTest.TunableFactory(locked_args={'tooltip': None}), 
         location=world.world_tests.LocationTest.TunableFactory(locked_args={'tooltip': None}), 
         lot_owner=event_testing.test_variants.LotOwnerTest.TunableFactory(locked_args={'tooltip': None}), 
         mood=sims.sim_info_tests.MoodTest.TunableFactory(participant_type_override=(ParticipantTypeActorTargetSim, ParticipantTypeActorTargetSim.Actor), locked_args={'tooltip': None}), 
         motive=event_testing.statistic_tests.MotiveThresholdTest.TunableFactory(participant_type_override=(ParticipantTypeActorTargetSim, ParticipantTypeActorTargetSim.Actor), locked_args={'tooltip': None}), 
         object_criteria=objects.object_tests.ObjectCriteriaTest.TunableFactory(locked_args={'tooltip': None}), 
         ranked_statistic=event_testing.statistic_tests.RankedStatThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor,  'tooltip':None}), 
         relationship=TunableRelationshipTest(locked_args={'subject':ParticipantType.Actor,  'test_event':0,  'tooltip':None}), 
         relative_statistic=event_testing.statistic_tests.RelativeStatTest.TunableFactory(locked_args={'source':ParticipantType.Actor,  'target':ParticipantType.TargetSim}), 
         scenario_relationship=TunableScenarioRelationshipTest(locked_args={'subject':ParticipantType.Actor,  'test_event':0,  'tooltip':None}), 
         sim_filter=sims.sim_info_tests.FilterTest.TunableFactory(locked_args={'tooltip': None}), 
         sim_info=sims.sim_info_tests.SimInfoTest.TunableFactory(participant_type_override=(ParticipantTypeActorTargetSim, ParticipantTypeActorTargetSim.Actor), locked_args={'tooltip': None}), 
         situation_job=event_testing.test_variants.TunableSituationJobTest(locked_args={'participant':ParticipantType.Actor,  'tooltip':None}), 
         skill_tag=statistics.skill_tests.SkillTagThresholdTest.TunableFactory(participant_type_override=(ParticipantTypeActorTargetSim, ParticipantTypeActorTargetSim.Actor), locked_args={'tooltip': None}), 
         skill_test=statistics.skill_tests.SkillRangeTest.TunableFactory(locked_args={'tooltip': None}), 
         state=event_testing.state_tests.TunableStateTest(locked_args={'who':ParticipantType.Object,  'tooltip':None}), 
         statistic=event_testing.statistic_tests.StatThresholdTest.TunableFactory(participant_type_override=(ParticipantTypeActorTargetSim, ParticipantTypeActorTargetSim.Actor), locked_args={'tooltip': None}), 
         time_of_day=event_testing.test_variants.TunableDayTimeTest(locked_args={'tooltip': None}), 
         topic=event_testing.test_variants.TunableTopicTest(locked_args={'subject':ParticipantType.Actor,  'target_sim':ParticipantType.TargetSim,  'tooltip':None}), 
         trait=sims.sim_info_tests.TraitTest.TunableFactory(participant_type_override=(ParticipantTypeActorTargetSim, ParticipantTypeActorTargetSim.Actor), locked_args={'tooltip': None}), 
         zone=zone_tests.ZoneTest.TunableFactory(locked_args={'tooltip': None}), 
         description=description, **kwargs)


class TunableSituationGoalPostTestSet(event_testing.tests.TestListLoadingMixin):
    DEFAULT_LIST = event_testing.tests.TestList()

    def __init__(self, description=None, **kwargs):
        if description is None:
            description = 'A list of tests.  All tests must succeed to pass the TestSet.'
        (super().__init__)(description=description, tunable=TunableSituationGoalPostTestVariant(), **kwargs)


class TunableSituationGoalEnvironmentPreTestVariant(TunableVariant):

    def __init__(self, description='A single tunable test.', **kwargs):
        (super().__init__)(object_criteria=objects.object_tests.ObjectCriteriaTest.TunableFactory(locked_args={'tooltip': None}), region=event_testing.test_variants.RegionTest.TunableFactory(locked_args={'tooltip':None,  'subject':None}), 
         festival_running=FestivalRunningTest.TunableFactory(locked_args={'tooltip': None}), 
         description=description, **kwargs)


class TunableSituationGoalEnvironmentPreTestSet(event_testing.tests.TestListLoadingMixin):
    DEFAULT_LIST = event_testing.tests.TestList()

    def __init__(self, description=None, **kwargs):
        if description is None:
            description = 'A list of tests.  All tests must succeed to pass the TestSet.'
        (super().__init__)(description=description, tunable=TunableSituationGoalEnvironmentPreTestVariant(), **kwargs)


class SituationGoalLootActions(HasTunableReference, metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ACTION)):
    INSTANCE_TUNABLES = {'goal_loot_actions': TunableList(TunableVariant(statistics=TunableStatisticChange(locked_args={'subject':ParticipantType.Actor, 
                           'advertise':False, 
                           'chance':SuccessChance.ONE}),
                            money_loot=MoneyChange.TunableFactory(locked_args={'subject':ParticipantType.Actor, 
                           'chance':SuccessChance.ONE, 
                           'display_to_user':None, 
                           'statistic_multipliers':None}),
                            buff=buffs.buff_ops.BuffOp.TunableFactory(locked_args={'subject':ParticipantType.Actor, 
                           'chance':SuccessChance.ONE}),
                            remove_buff=buffs.buff_ops.BuffRemovalOp.TunableFactory(description='\n                    This must NOT be used to remove buffs that are added by RoleStates.\n                    ',
                            locked_args={'subject':ParticipantType.Actor, 
                           'chance':SuccessChance.ONE}),
                            notification_and_dialog=DialogLootOp.TunableFactory(locked_args={'subject':ParticipantType.Actor, 
                           'advertise':False, 
                           'chance':SuccessChance.ONE}),
                            reaction=ReactionLootOp.TunableFactory(locked_args={'subject':ParticipantType.Actor, 
                           'advertise':False, 
                           'chance':SuccessChance.ONE}),
                            state_change=StateChangeLootOp.TunableFactory(locked_args={'advertise':False, 
                           'chance':SuccessChance.ONE}),
                            award_whim_bucks=AwardWhimBucksLootOp.TunableFactory(locked_args={'advertise':False, 
                           'chance':SuccessChance.ONE}),
                            add_trait=AddTraitLootOp.TunableFactory(locked_args={'subject':ParticipantType.Actor, 
                           'advertise':False, 
                           'chance':SuccessChance.ONE}),
                            remove_trait=RemoveTraitLootOp.TunableFactory(locked_args={'subject':ParticipantType.Actor, 
                           'advertise':False, 
                           'chance':SuccessChance.ONE})))}

    def __iter__(self):
        return iter(self.goal_loot_actions)


class UiSituationGoalStatus(enum.Int):
    COMPLETED = 0
    CANCELED = 1


SituationGoalDisplayMixin = get_display_mixin(has_icon=True, has_tooltip=True, use_string_tokens=True, has_secondary_icon=True)

class SituationGoal(SituationGoalDisplayMixin, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SITUATION_GOAL)):
    INSTANCE_SUBCLASSES_ONLY = True
    IS_TARGETED = False
    ACTUAL_ZONE_ID = 'actual_zone_id'
    INSTANCE_TUNABLES = {'_pre_tests':TunableSituationGoalPreTestSet(description='\n            A set of tests on the player sim and environment that all must\n            pass for the goal to be given to the player. e.g. Player Sim\n            has cooking skill level 7.\n            ',
       tuning_group=GroupNames.TESTS), 
     '_post_tests':TunableSituationGoalPostTestSet(description='\n            A set of tests that must all pass when the player satisfies the\n            goal_test for the goal to be consider completed. e.g. Player\n            has Drunk Buff when Kissing another sim at Night.\n            ',
       tuning_group=GroupNames.TESTS), 
     '_cancel_on_travel':Tunable(description='\n            If set, this situation goal will cancel (technically, complete\n            with score overridden to 0 so that situation score is not\n            progressed) if situation changes zone.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.TESTS), 
     '_environment_pre_tests':TunableSituationGoalEnvironmentPreTestSet(description='\n            A set of sim independent pre tests.\n            e.g. There are five desks.\n            ',
       tuning_group=GroupNames.TESTS), 
     'role_tags':TunableSet(TunableEnumEntry(Tag, Tag.INVALID), description='\n            This goal will only be given to Sims in SituationJobs or Role\n            States marked with one of these tags.\n            '), 
     '_cooldown':TunableSimMinute(description='\n            The cooldown of this situation goal.  Goals that have been\n            completed will not be chosen again for the amount of time that\n            is tuned.\n            ',
       default=600,
       minimum=0), 
     '_iterations':Tunable(description='\n             Number of times the player must perform the action to complete the goal\n             ',
       tunable_type=int,
       default=1), 
     '_score':Tunable(description='\n            The number of points received for completing the goal.\n            ',
       tunable_type=int,
       default=10), 
     '_tested_score_overrides':TunableList(description='\n            A list of test, score pairs. We will go through the entries in order and the first\n            set of tests that pass will return the associated score as the score override. If none\n            of the entries tests pass then we will default to the normal score.\n            ',
       tunable=TunableTuple(description='\n                A set of tests that when they pass results in a score override of the associated\n                score.\n                ',
       tests=(TunableSituationGoalPostTestSet()),
       score=Tunable(description='\n                    The score override to use when the associated tests pass.\n                    ',
       tunable_type=int,
       default=10))), 
     'score_on_iteration_complete':OptionalTunable(description='\n            If enabled then we will add an amount of score to the situation\n            with every iteration of the situation goal completing.\n            ',
       tunable=Tunable(description='\n                An amount of score that should be applied when an iteration\n                completes.\n                ',
       tunable_type=int,
       default=10)), 
     '_pre_goal_loot_list':TunableList(description='\n            A list of pre-defined loot actions that will applied to every\n            sim in the situation when this situation goal is started.\n             \n            Do not use this loot list in an attempt to undo changes made by\n            the RoleStates to the sim. For example, do not attempt\n            to remove buffs or commodities added by the RoleState.\n            ',
       tunable=SituationGoalLootActions.TunableReference()), 
     '_goal_loot_list':TunableList(description='\n            A list of pre-defined loot actions that will applied to every\n            sim in the situation when this situation goal is completed.\n             \n            Do not use this loot list in an attempt to undo changes made by\n            the RoleStates to the sim. For example, do not attempt\n            to remove buffs or commodities added by the RoleState.\n            ',
       tunable=SituationGoalLootActions.TunableReference()), 
     'noncancelable':Tunable(description='\n            Checking this box will prevent the player from canceling this goal in the whim system.',
       tunable_type=bool,
       default=False), 
     'should_reevaluate_on_load':Tunable(description='\n            If checked, indicates that the goal should be reevaluated for completion when it\n            is loaded. This is important for goals that can be achieved during\n            rotational play while the goal is not active. By default, this\n            is left unchecked for performance reasons.\n            \n            Currently, this is only supported for gameplay scenarios. Talk to\n            your GPE partner if you have a new use-case for this tuning field.\n            ',
       tunable_type=bool,
       default=False), 
     'goal_awarded_notification':OptionalTunable(description='\n            If enabled, this goal will have a notification associated with it.\n            It is up to whatever system awards the goal (e.g. the Whim system)\n            to display the notification when necessary.\n            ',
       tunable=TunableUiDialogNotificationSnippet()), 
     'goal_completion_notification':OptionalTunable(tunable=UiDialogNotification.TunableFactory(description='\n                A TNS that will fire when this situation goal is completed.\n                ')), 
     'goal_completion_notification_and_modal_target':OptionalTunable(description='\n            If enabled then we will use the tuned situation job to pick a\n            random sim in the owning situation with that job to be the target\n            sim of the notification and modal dialog.\n            ',
       tunable=TunableReference(description='\n                The situation job that will be used to find a sim in the owning\n                situation to be the target sim.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)))), 
     '_scenario_roles':TunableList(description='\n            If non-empty, then this SituationGoal will only consider sims with\n            one of the tuned scenario roles.\n            ',
       tunable=TunableReference(description='\n                The other role in the relationship.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
       class_restrictions=('ScenarioRole', ))), 
     'audio_sting_on_complete':TunableResourceKey(description='\n            The sound to play when this goal is completed.\n            ',
       resource_types=(
      sims4.resources.Types.PROPX,),
       default=None,
       allow_none=True,
       tuning_group=GroupNames.AUDIO), 
     'goal_completion_modal_dialog':OptionalTunable(tunable=UiDialogOk.TunableFactory(description='\n                A modal dialog that will fire when this situation goal is\n                completed.\n                ')), 
     'is_visible':Tunable(description='\n            Whether or not this goal should be displayed in the live mode UI\n            when this goal is part of a live mode situation or\n            scenario.\n            ',
       tunable_type=bool,
       default=True,
       tuning_group=GroupNames.UI), 
     'display_type':TunableEnumEntry(description='\n            How this goal is presented in user-facing situations.\n            ',
       tunable_type=SituationGoalDisplayType,
       default=SituationGoalDisplayType.NORMAL,
       tuning_group=GroupNames.UI), 
     'tutorial_tip_group':OptionalTunable(description='\n            When tutorial tip group is set, clicking on this goal in the scenario panel\n            will activate all tutorial tips tuned in the group.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.TUTORIAL_TIP)),
       class_restrictions='TutorialTipGroup')), 
     'expiration_time':OptionalTunable(description='\n            If enabled, this goal will expire at the specified time.  If Force Same Day is true, will immediately expire\n            if already past the specified time of the current day regardless of when the situation started.  If False, \n            will only immediately expire if the situation itself started BEFORE the specified time.  Not recommended for\n            Situations that last multiple days as will expire within the first 24 hours.\n            ',
       tunable=TunableTuple(description='\n                Data about the expiration time.\n                ',
       time=TunableTimeOfDay(description='\n                    When this situation goal should expire.\n                    '),
       force_same_day=Tunable(description='\n                    If true, will immediately expire if already past the specified time of the current day regardless of\n                    when the situation started.  If False, will only immediately expire if the situation started before\n                    the specified time.\n                    ',
       tunable_type=bool,
       default=False))), 
     '_persist_zone':Tunable(description='\n            Whether or not to persist the zone where this goal completed.\n            To show in the UI, for example.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.PERSISTENCE)}

    @classmethod
    def can_be_given_as_goal(cls, actor, situation, scenario=None, **kwargs):
        if actor is not None:
            resolver = event_testing.resolver.DataResolver(sim_info=(actor.sim_info))
            result = cls._pre_tests.run_tests(resolver)
            if not result:
                return result
            else:
                resolver = GlobalResolver()
        else:
            environment_test_result = cls._environment_pre_tests.run_tests(resolver)
            return environment_test_result or environment_test_result
        return TestResult.TRUE

    def __init__(self, sim_info=None, situation=None, scenario=None, goal_id=0, count=0, locked=False, completed_time=None, secondary_sim_info=None, reader=None, **kwargs):
        self._sim_info = sim_info
        self._secondary_sim_info = secondary_sim_info
        self._situation = situation
        self._scenario = scenario
        self.id = goal_id
        self._on_goal_completed_callbacks = CallableList()
        self._completed_time = completed_time
        self._count = count
        self._locked = locked
        self._score_override = None
        self._goal_status_override = None
        self._setup = False
        self._expiration_alarm_handle = None
        self._actual_zone_id = None
        if reader is not None:
            if self._persist_zone:
                self._actual_zone_id = reader.read_uint64(self.ACTUAL_ZONE_ID, None)

    def setup(self):
        self._setup = True
        if self.expiration_time is not None:
            now = services.time_service().sim_now
            time_span = now.time_till_next_day_time(self.expiration_time.time)
            self._expiration_alarm_handle = alarms.add_alarm(self, time_span, self._expire_callback)

    def destroy(self):
        self.decommision()
        self._sim_info = None
        self._situation = None

    def decommision(self):
        if self._setup:
            self._decommision()

    def _decommision(self):
        self._on_goal_completed_callbacks.clear()
        if self._expiration_alarm_handle is not None:
            alarms.cancel_alarm(self._expiration_alarm_handle)
            self._expiration_alarm_handle = None

    @flexproperty
    def sub_goals(cls, inst):
        return ()

    def create_seedling(self):
        actor_id = 0 if self._sim_info is None else self._sim_info.sim_id
        target_sim_info = self.get_required_target_sim_info()
        target_id = 0 if target_sim_info is None else target_sim_info.sim_id
        secondary_target_id = 0 if self._secondary_sim_info is None else self._secondary_sim_info.sim_id
        seedling = situations.situation_serialization.GoalSeedling((type(self)), actor_id,
          target_id,
          secondary_target_id,
          (self._count),
          (self._locked),
          (self._completed_time),
          sub_goals=(self.sub_goals))
        writer = seedling.writer
        if self._actual_zone_id is not None:
            if self._persist_zone:
                writer.write_uint64(self.ACTUAL_ZONE_ID, self._actual_zone_id)
        return seedling

    def register_for_on_goal_completed_callback(self, listener):
        self._on_goal_completed_callbacks.append(listener)

    def unregister_for_on_goal_completed_callback(self, listener):
        self._on_goal_completed_callbacks.remove(listener)

    def get_gsi_name(self):
        if self._iterations <= 1:
            return self.__class__.__name__
        return '{} {}/{}'.format(self.__class__.__name__, self._count, self._iterations)

    def get_gsi_data(self):
        goal_name = self.get_gsi_name()
        target_sim = self.get_actual_target_sim_info()
        unlocked_with_sim_info = target_sim.full_name if target_sim is not None else 'n/a'
        target_object_id = self.get_actual_target_object_definition_id()
        definition_tuning = services.definition_manager().get_object_tuning(target_object_id) if target_object_id is not None else None
        unlocked_with_object = definition_tuning.__name__ if definition_tuning is not None else 'n/a'
        unlocked_zone_id = self.get_actual_zone_id()
        unlocked_in_zone = services.get_persistence_service().get_zone_proto_buff(unlocked_zone_id).name if unlocked_zone_id is not None else 'n/a'
        unlocked_career_track_guid = self.get_career_track()
        career_track = services.get_instance_manager(sims4.resources.Types.CAREER_TRACK).get(unlocked_career_track_guid) if unlocked_career_track_guid is not None else None
        unlocked_career_track = career_track.__name__ if career_track is not None else 'n/a'
        unlocked_career_level_guid = self.get_career_level()
        career_level = career_track.career_levels[unlocked_career_level_guid] if (career_track is not None and unlocked_career_level_guid is not None) else None
        unlocked_career_level = career_level.__name__ if career_level is not None else 'n/a'
        unlocked_trait_guid = self.get_trait_guid()
        goal_trait = services.get_instance_manager(sims4.resources.Types.TRAIT).get(unlocked_trait_guid) if unlocked_trait_guid is not None else None
        unlocked_trait = goal_trait.__name__ if goal_trait is not None else 'n/a'
        unlocked_death_type = self.get_death_type_info()
        ghost_trait = DeathTracker.DEATH_TYPE_GHOST_TRAIT_MAP.get(unlocked_death_type) if unlocked_death_type is not None else None
        unlocked_death_trait = ghost_trait.__name__ if ghost_trait is not None else 'n/a'
        return {
         'goal': 'goal_name', 
         'unlocked_with_sim_info': 'unlocked_with_sim_info', 
         'unlocked_with_object': 'unlocked_with_object', 
         'unlocked_in_zone': 'unlocked_in_zone', 
         'unlocked_career_track': 'unlocked_career_track', 
         'unlocked_career_level': 'unlocked_career_level', 
         'unlocked_trait': 'unlocked_trait', 
         'unlocked_death_trait': 'unlocked_death_trait'}

    def __str__(self):
        return self.__class__.__name__

    def on_goal_offered(self):
        if self._situation is None:
            return
        if self._pre_goal_loot_list:
            for sim in self.all_sim_infos_interested_in_goal_gen():
                resolver = sim.get_resolver()
                for loots in self._pre_goal_loot_list:
                    for loot in loots.goal_loot_actions:
                        loot.apply_to_resolver(resolver)

    @flexmethod
    def all_sims_interested_in_goal_gen(cls, inst, sim_info=None, situation=None, scenario=None, all_instanced_sims_are_interested=False):
        if all_instanced_sims_are_interested:
            yield from services.sim_info_manager().instanced_sims_gen()
        else:
            if inst is not None:
                sim_info = inst._sim_info
                situation = inst._situation
                scenario = inst._scenario
            elif sim_info is not None:
                sim = sim_info.get_sim_instance()
                if sim is not None:
                    yield sim
            elif situation is not None:
                yield from situation.all_sims_in_situation_gen()
            else:
                if scenario is not None:
                    yield from scenario.sims_of_interest_gen(cls._scenario_roles)

    @flexmethod
    def all_sim_infos_interested_in_goal_gen(cls, inst, sim_info=None, situation=None, scenario=None, all_instanced_sim_infos_including_babies_are_interested=False):
        if all_instanced_sim_infos_including_babies_are_interested:
            yield from services.sim_info_manager().instanced_sim_info_including_baby_gen()
        else:
            if inst is not None:
                sim_info = inst._sim_info
                situation = inst._situation
                scenario = inst._scenario
            elif sim_info is not None:
                yield sim_info
            else:
                if situation is not None:
                    yield from (sim.sim_info for sim in situation.all_sims_in_situation_gen())
                else:
                    if scenario is not None:
                        yield from scenario.sim_infos_of_interest_gen(cls._scenario_roles)

    def _display_goal_completed_dialogs(self):
        actor_sim_info = services.active_sim_info()
        target_sim_info = None
        if self.goal_completion_notification_and_modal_target is not None:
            possible_sims = list(self._situation.all_sims_in_job_gen(self.goal_completion_notification_and_modal_target))
            if possible_sims:
                target_sim_info = random.choice(possible_sims)
            if target_sim_info is None:
                return
        resolver = DoubleSimResolver(actor_sim_info, target_sim_info)
        if self.goal_completion_notification is not None:
            notification = self.goal_completion_notification(actor_sim_info, resolver=resolver)
            notification.show_dialog()
        if self.goal_completion_modal_dialog is not None:
            dialog = self.goal_completion_modal_dialog(actor_sim_info, resolver=resolver)
            dialog.show_dialog()

    def _on_goal_completed(self, start_cooldown=True):
        if start_cooldown:
            self._completed_time = services.time_service().sim_now
        if self._scenario is not None:
            scenario_tracker = self._scenario.household.scenario_tracker
            scenario_tracker.send_goal_completed_telemetry(self)
        if self._persist_zone:
            self._actual_zone_id = self._sim_info.zone_id if self._sim_info is not None else None
        if self._goal_loot_list:
            loot_sims = tuple(self.all_sim_infos_interested_in_goal_gen())
            for loots in self._goal_loot_list:
                for loot in loots.goal_loot_actions:
                    for sim in loot_sims:
                        loot.apply_to_resolver(sim.get_resolver())

        self._display_goal_completed_dialogs()
        with situations.situation_manager.DelayedSituationDestruction():
            self._on_goal_completed_callbacks(self, True)

    def _on_iteration_completed(self):
        self._on_goal_completed_callbacks(self, False)

    def force_complete(self, target_sim=None, score_override=None, start_cooldown=True):
        self._score_override = score_override
        self._count = self._iterations
        self._on_goal_completed(start_cooldown=start_cooldown)

    def reset_count(self):
        self._count = 0

    def _expire_callback(self, _):
        self.force_complete(score_override=0)

    def _valid_event_sim_of_interest(self, sim_info):
        if self._sim_info is sim_info:
            return True
        if self._scenario is not None:
            if sim_info not in self._scenario.household:
                return False
            if self._scenario_roles:
                if self._scenario.get_role_for_sim(sim_info.id) not in self._scenario_roles:
                    return False
            return True
        if self._sim_info is None:
            return True
        return False

    def _increment_completion_count(self):
        self._count += 1
        if self._count >= self._iterations:
            self._on_goal_completed()
            return True
        self._on_iteration_completed()
        return False

    def _reevaluate_completion(self, sim):
        self._on_iteration_completed()
        if self.completed_iterations >= self.max_iterations:
            self._increment_completion_count()

    def reevaluate_goal_completion(self, resolver=None):
        for sim_info in self.all_sim_infos_interested_in_goal_gen():
            _resolver = resolver or SingleSimResolver(sim_info_to_test=sim_info, additional_metric_key_data=self)
            if self._run_goal_completion_tests(sim_info, None, _resolver) and self._increment_completion_count():
                return

    def handle_event(self, sim_info, event, resolver):
        if not self._valid_event_sim_of_interest(sim_info):
            return
        resolver.set_additional_metric_key_data(self)
        if self._run_goal_completion_tests(sim_info, event, resolver):
            self._increment_completion_count()

    def on_add_sim_to_situation(self, sim, job_type):
        if self.should_reevaluate_when_sim_count_changes(sim, job_type):
            self._reevaluate_completion(sim)

    def on_remove_sim_from_situation(self, sim, job_type):
        if self.should_reevaluate_when_sim_count_changes(sim, job_type):
            self._reevaluate_completion(sim)

    def should_reevaluate_when_sim_count_changes(self, sim, job_type):
        return False

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        return self._post_tests.run_tests(resolver)

    def should_autocomplete_on_load(self, previous_zone_id):
        if self._cancel_on_travel:
            zone_id = services.current_zone_id()
            if previous_zone_id != zone_id:
                return True
        return False

    def get_actual_target_sim_info(self):
        pass

    def get_actual_target_object_definition_id(self):
        pass

    def get_actual_zone_id(self):
        return self._actual_zone_id

    @property
    def sim_info(self):
        return self._sim_info

    def get_required_target_sim_info(self):
        pass

    def get_secondary_sim_info(self):
        return self._secondary_sim_info

    def get_career_guid(self):
        pass

    def get_career_level(self):
        pass

    def get_career_track(self):
        pass

    def get_death_type_info(self):
        pass

    def get_trait_guid(self):
        pass

    @property
    def created_time(self):
        pass

    @property
    def completed_time(self):
        return self._completed_time

    @property
    def is_completed(self):
        return self._completed_time is not None

    def is_on_cooldown(self):
        if self._completed_time is None:
            return False
        time_since_last_completion = services.time_service().sim_now - self._completed_time
        return time_since_last_completion < interval_in_sim_minutes(self._cooldown)

    def get_localization_tokens(self):
        target_sim_info = self.get_required_target_sim_info()
        return (self.numerical_token,
         self._sim_info,
         target_sim_info,
         self._secondary_sim_info,
         self.completed_iterations)

    def get_display_name(self):
        display_name = self.display_name
        if display_name is not None:
            return display_name(*self.get_localization_tokens())

    def get_display_tooltip(self):
        display_tooltip = self.display_tooltip
        if display_tooltip is not None:
            return display_tooltip(*self.get_localization_tokens())

    @property
    def score(self):
        if self._score_override is not None:
            return self._score_override
        tested_score_override = self.get_tested_score_override()
        if tested_score_override is not None:
            return tested_score_override
        return self._score

    @property
    def goal_status_override(self):
        return self._goal_status_override

    @property
    def completed_iterations(self):
        return self._count

    @flexproperty
    def max_iterations(cls, inst):
        if inst is not None:
            return inst._iterations
        return cls._iterations

    @property
    def numerical_token(self):
        return self.max_iterations

    @property
    def secondary_numerical_token(self):
        return self.completed_iterations

    @property
    def display_data(self):
        return self._display_data

    @property
    def locked(self):
        return self._locked

    def toggle_locked_status(self):
        self._locked = not self._locked

    def _should_auto_expire(self):
        if not self.expiration_time:
            return False
        expiration_time = self.expiration_time.time
        now = services.time_service().sim_now
        start_time = self._situation.situation_start_time
        if self.expiration_time.force_same_day:
            if expiration_time < now.time_of_day():
                return True
        return start_time < start_time.time_of_next_day_time(expiration_time) < now

    def validate_completion(self):
        if self._completed_time is not None:
            return
        if self._should_auto_expire():
            self.force_complete(score_override=0)
            return
        if self.completed_iterations < self.max_iterations:
            return
        self.force_complete()

    def show_goal_awarded_notification(self):
        if self.goal_awarded_notification is None:
            return
        icon_override = IconInfoData(icon_resource=(self.display_icon))
        secondary_icon_override = IconInfoData(obj_instance=(self._sim_info))
        notification = self.goal_awarded_notification(self._sim_info)
        notification.show_dialog(additional_tokens=(self.get_localization_tokens()), icon_override=icon_override,
          secondary_icon_override=secondary_icon_override)

    def build_goal_message(self, goal_msg):
        goal_msg.goal_id = self.id
        goal_name = self.get_display_name()
        if goal_name is not None:
            goal_msg.goal_name = goal_name
        else:
            ui_max_iterations = self.numerical_token
            goal_msg.max_iterations = ui_max_iterations
            if self.completed_time is None:
                goal_msg.current_iterations = self.secondary_numerical_token
            else:
                goal_msg.current_iterations = ui_max_iterations
        goal_tooltip = self.get_display_tooltip()
        if goal_tooltip is not None:
            goal_msg.goal_tooltip = goal_tooltip
        if self.audio_sting_on_complete is not None:
            goal_msg.audio_sting.type = self.audio_sting_on_complete.type
            goal_msg.audio_sting.group = self.audio_sting_on_complete.group
            goal_msg.audio_sting.instance = self.audio_sting_on_complete.instance
        build_icon_info_msg(IconInfoData(icon_resource=(self.display_icon)), goal_name, goal_msg.icon_info)
        if self._display_data:
            build_icon_info_msg(IconInfoData(icon_resource=(self._display_data.instance_display_secondary_icon)), None, goal_msg.secondary_icon_info)
        goal_msg.display_type = self.display_type.value
        goal_msg.is_complete = self.is_completed
        if self.tutorial_tip_group is not None:
            goal_msg.tutorial_tip_group_guid = self.tutorial_tip_group.guid64
        if self.expiration_time:
            goal_msg.expiration_time = services.time_service().sim_now.time_of_next_day_time(self.expiration_time.time).absolute_ticks()

    def get_tested_score_override(self):
        resolver = SingleSimResolver(self.sim_info)
        for override in self._tested_score_overrides:
            if override.tests.run_tests(resolver):
                return override.score