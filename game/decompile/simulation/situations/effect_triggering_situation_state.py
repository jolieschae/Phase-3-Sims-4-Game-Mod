# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\effect_triggering_situation_state.py
# Compiled at: 2021-04-12 15:25:20
# Size of source mod 2**32: 18690 bytes
from event_testing.resolver import SingleSimResolver
from sims4.resources import Types
from situations.situation_guest_list import SituationGuestList
from tunable_time import TunableTimeSpan, TunableTimeOfDay
from zone_tests import ZoneTest
from sims.unlock_tracker_tests import UnlockTrackerAmountTest
from event_testing.statistic_tests import StatThresholdTest, RankedStatThresholdTest
from statistics.skill_tests import SkillTagThresholdTest
from aspirations.aspiration_tests import SelectedAspirationTest, SelectedAspirationTrackTest
from seasons.season_tests import SeasonTest
from event_testing.common_event_tests import ParticipantTypeTargetAllRelationships, ParticipantTypeActorHousehold
from relationships.relationship_tests import TunableRelationshipTest, RelationshipBitTest
from crafting.photography_tests import TookPhotoTest
from world.world_tests import LocationTest
from event_testing.tests_with_data import GenerationTest, OffspringCreatedTest, TunableParticipantRanAwayActionTest, TunableParticipantRanInteractionTest, TunableSimoleonsEarnedTest, WhimCompletedTest
from drama_scheduler.drama_node_tests import FestivalRunningTest
from objects.object_tests import CraftedItemTest, InventoryTest, ObjectCriteriaTest, ObjectPurchasedTest
from clubs.club_tests import ClubTest
from sims.sim_info_tests import BuffAddedTest, BuffTest, MoodTest, TraitTest
from event_testing.test_variants import BucksPerkTest, CareerPromotedTest, TunableCareerTest, CollectedItemTest, TunableCollectionThresholdTest, EventRanSuccessfullyTest, HouseholdSizeTest, PurchasePerkTest, TunableSimoleonsTest, TunableSituationRunningTest, TunableUnlockedTest, AtWorkTest
from interactions import ParticipantType, ParticipantTypeSim, ParticipantTypeActorTargetSim, ParticipantTypeSingleSim
import services
from sims4.tuning.tunable import HasTunableFactory, TunableVariant, AutoFactoryInit, Tunable, TunableList, TunableTuple, TunableReference, HasTunableSingletonFactory

class CustomStatesSituationTriggerDataTestVariant(TunableVariant):

    def __init__(self, *args, description='A tunable test supported for use as a situation trigger.', **kwargs):
        (super().__init__)(args, at_work=AtWorkTest.TunableFactory(locked_args={'subject':ParticipantType.Actor, 
 'tooltip':None}), 
         bucks_perk_unlocked=BucksPerkTest.TunableFactory(description='\n                A test for which kind of bucks perk is being unlocked\n                ',
  locked_args={'tooltip': None}), 
         buff_added=BuffAddedTest.TunableFactory(locked_args={'tooltip': None}), 
         career_promoted=CareerPromotedTest.TunableFactory(locked_args={'tooltip': None}), 
         career_test=TunableCareerTest.TunableFactory(locked_args={'subjects':ParticipantType.Actor, 
 'tooltip':None}), 
         club_tests=ClubTest.TunableFactory(locked_args={'tooltip':None, 
 'club':ClubTest.CLUB_FROM_EVENT_DATA, 
 'room_for_new_members':None, 
 'subject_passes_membership_criteria':None, 
 'subject_can_join_more_clubs':None}), 
         collected_item_test=CollectedItemTest.TunableFactory(locked_args={'tooltip': None}), 
         collection_test=TunableCollectionThresholdTest(locked_args={'who':ParticipantType.Actor, 
 'tooltip':None}), 
         crafted_item=CraftedItemTest.TunableFactory(locked_args={'tooltip': None}), 
         event_ran_successfully=EventRanSuccessfullyTest.TunableFactory(description='\n                This is a simple test that always returns true whenever one of\n                the tuned test events is processed.\n                ',
  locked_args={'tooltip': None}), 
         festival_running=FestivalRunningTest.TunableFactory(description='\n                This is a test that triggers when the festival begins.\n                ',
  locked_args={'tooltip': None}), 
         generation_created=GenerationTest.TunableFactory(locked_args={'tooltip': None}), 
         has_buff=BuffTest.TunableFactory(locked_args={'subject':ParticipantType.Actor, 
 'tooltip':None}), 
         household_size=HouseholdSizeTest.TunableFactory(locked_args={'participant':ParticipantType.Actor, 
 'tooltip':None}), 
         inventory=InventoryTest.TunableFactory(locked_args={'tooltip': None}), 
         location_test=LocationTest.TunableFactory(location_tests={
 'is_outside': False, 
 'is_natural_ground': False, 
 'is_in_slot': False, 
 'is_on_active_lot': False, 
 'is_on_level': False}), 
         mood_test=MoodTest.TunableFactory(locked_args={'who':ParticipantTypeSim.Actor, 
 'tooltip':None}), 
         object_criteria=ObjectCriteriaTest.TunableFactory(locked_args={'tooltip': None}), 
         object_purchase_test=ObjectPurchasedTest.TunableFactory(locked_args={'tooltip': None}), 
         offspring_created_test=OffspringCreatedTest.TunableFactory(locked_args={'tooltip': None}), 
         purchase_perk_test=PurchasePerkTest.TunableFactory(description='\n                A test for which kind of perk is being purchased.\n                '), 
         photo_taken=TookPhotoTest.TunableFactory(description='\n                A test for player taken photos.\n                '), 
         ran_away_action_test=TunableParticipantRanAwayActionTest(locked_args={'participant':ParticipantTypeActorTargetSim.Actor, 
 'tooltip':None}), 
         ran_interaction_test=TunableParticipantRanInteractionTest(locked_args={'participant':ParticipantType.Actor, 
 'tooltip':None}), 
         relationship=TunableRelationshipTest(participant_type_override=(
 ParticipantTypeTargetAllRelationships,
 ParticipantTypeTargetAllRelationships.AllRelationships),
  locked_args={'tooltip': None}), 
         relationship_bit=RelationshipBitTest.TunableFactory(locked_args={'subject':ParticipantType.Actor, 
 'target':ParticipantType.TargetSim, 
 'tooltip':None}), 
         season_test=SeasonTest.TunableFactory(locked_args={'tooltip': None}), 
         selected_aspiration_test=SelectedAspirationTest.TunableFactory(locked_args={'who':ParticipantTypeSingleSim.Actor, 
 'tooltip':None}), 
         selected_aspiration_track_test=SelectedAspirationTrackTest.TunableFactory(locked_args={'who':ParticipantTypeSingleSim.Actor, 
 'tooltip':None}), 
         simoleons_earned=TunableSimoleonsEarnedTest(locked_args={'tooltip': None}), 
         simoleon_value=TunableSimoleonsTest(locked_args={'tooltip': None}), 
         situation_running_test=TunableSituationRunningTest(locked_args={'tooltip': None}), 
         skill_tag=SkillTagThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor, 
 'tooltip':None}), 
         statistic=StatThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor, 
 'tooltip':None}), 
         ranked_statistic=RankedStatThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor, 
 'tooltip':None}), 
         trait=TraitTest.TunableFactory(participant_type_override=(
 ParticipantTypeActorHousehold,
 ParticipantTypeActorHousehold.Actor),
  locked_args={'tooltip': None}), 
         unlock_earned=TunableUnlockedTest(locked_args={'participant':ParticipantType.Actor, 
 'tooltip':None}), 
         unlock_tracker_amount=UnlockTrackerAmountTest.TunableFactory(locked_args={'subject':ParticipantType.Actor, 
 'tooltip':None}), 
         whim_completed_test=WhimCompletedTest.TunableFactory(locked_args={'tooltip': None}), 
         zone=ZoneTest.TunableFactory(locked_args={'tooltip': None}), 
         default='ran_interaction_test', 
         description=description, **kwargs)


HAS_TRIGGERED_KEY = 'has_triggered_{}'

class BaseSituationTrigger(HasTunableFactory, AutoFactoryInit):

    def __init__(self, owner, index, effect, **kwargs):
        (super().__init__)(**kwargs)
        self._owner = owner
        self._index = index
        self._effect = effect
        self._has_triggered = False

    def _setup(self, reader):
        raise NotImplementedError

    def on_activate(self, reader):
        if reader is not None:
            self._has_triggered = reader.read_bool(HAS_TRIGGERED_KEY.format(self._index), False)
            if self._has_triggered:
                return
        self._setup(reader)

    def save(self, writer):
        writer.write_bool(HAS_TRIGGERED_KEY.format(self._index), self._has_triggered)

    def destroy(self):
        self._owner = None
        self._index = None
        self._effect = None
        self._has_triggered = None


DURATION_ALARM_KEY = 'duration_alarm_{}'

class DurationTrigger(BaseSituationTrigger):
    FACTORY_TUNABLES = {'duration': TunableTimeSpan(description='\n            The amount of time that will expire before this duration effect is triggered.\n            ')}

    def _duration_complete(self, _):
        self._has_triggered = True
        self._effect(self._owner)

    def _setup(self, reader):
        self._owner._create_or_load_alarm_with_timespan((DURATION_ALARM_KEY.format(self._index)), (self.duration()),
          (self._duration_complete),
          reader=reader,
          should_persist=True)


DAY_TIME_ALARM_KEY = 'day_time_alarm_{}'

class TimeOfDayTrigger(BaseSituationTrigger):
    FACTORY_TUNABLES = {'time': TunableTimeOfDay(description='\n            The time of day that this trigger will occur at.\n            ')}

    def _duration_complete(self, _):
        self._has_triggered = True
        self._effect(self._owner)

    def _setup(self, reader):
        now = services.game_clock_service().now()
        self._owner._create_or_load_alarm_with_timespan((DURATION_ALARM_KEY.format(self._index)), (now.time_till_next_day_time(self.time)),
          (self._duration_complete),
          reader=reader,
          should_persist=False)


class TestEventTrigger(BaseSituationTrigger):
    FACTORY_TUNABLES = {'test':CustomStatesSituationTriggerDataTestVariant(description='\n            A test that will be listened to in order to act as a trigger.  These tests will not be checked\n            when entering the state to see if they are already complete.\n            '), 
     'only_trigger_for_situation_sims':Tunable(description='\n            If checked then we will only perform this trigger if the Sim linked to the even is in the\n            situation.\n            ',
       tunable_type=bool,
       default=True)}

    def _setup(self, reader):
        services.get_event_manager().register_tests(self, (self.test,))

    def destroy(self):
        if not self._has_triggered:
            services.get_event_manager().unregister_tests(self, (self.test,))
        super().destroy()

    def handle_event(self, sim_info, event, resolver):
        if self._has_triggered:
            return
        else:
            if self.only_trigger_for_situation_sims:
                if not self._owner.owner.is_sim_info_in_situation(sim_info):
                    return
            return resolver(self.test) or None
        self._has_triggered = True
        self._effect(self._owner)
        services.get_event_manager().unregister_tests(self, (self.test,))


class CustomStatesSituationEndSituation(HasTunableSingletonFactory, AutoFactoryInit):

    def __call__(self, situation_state):
        situation_state.owner._self_destruct()


class CustomStatesSituationGiveLoot(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'loot_actions': TunableList(description='\n            A list of loot actions to apply.\n            ',
                       tunable=TunableReference(description='\n                The loot to apply.\n                ',
                       manager=(services.get_instance_manager(Types.ACTION)),
                       class_restrictions=('LootActions', 'RandomWeightedLoot'),
                       pack_safe=True))}

    def __call__(self, situation_state):
        for sim in situation_state.owner.all_sims_in_situation_gen():
            resolver = SingleSimResolver(sim.sim_info)
            for loot_action in self.loot_actions:
                loot_action.apply_to_resolver(resolver)


class CustomStatesSituationReplaceSituation(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'new_situation': TunableReference(description='\n            The new situation to be created.\n            \n            This situation will be created using the default guest list (predefined if the situation has one else an\n            empty one) and non-user facing.  If we want either Sims transferred between this situation and the next one\n            or the following situation to be user facing GPE would just need to add new tuning within this factory to\n            add the logic.\n            ',
                        manager=(services.get_instance_manager(Types.SITUATION)))}

    def __call__(self, situation_state):
        situation_state.owner._self_destruct()
        guest_list = self.new_situation.get_predefined_guest_list()
        if guest_list is None:
            guest_list = SituationGuestList(invite_only=True)
        services.get_zone_situation_manager().create_situation((self.new_situation), guest_list=guest_list,
          user_facing=False)