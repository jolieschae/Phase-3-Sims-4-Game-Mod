# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\loot.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 42080 bytes
from adoption.adoption_interaction_loot import AddAdoptedSimToFamilyLootOp
from aspirations.timed_aspiration_loot_op import TimedAspirationLootOp
from broadcasters.broadcaster_loot_op import BroadcasterOneShotLootOp
from bucks.bucks_loot_op import BucksLoot, AwardPerkLoot, RecyclingBucksLoot
from buffs.dynamic_buff_loot_op import DynamicBuffLootOp
from business.business_ops import ModifyCustomerFlow
from careers.career_gig_ops import AddCareerGigOp
from careers.career_ops import CareerLevelOp, CareerLootOp, CareerStayLateOp
from clans.clan_tuning import ClanLootOp
from clubs.club_ops import SetClubGatheringVibe
from crafting.crafting_loots import RefundCraftingProcessLoot, SetupCraftedObjectLoot
from crafting.food_restrictions import FoodRestrictionOp
from delivery.scheduled_delivery_loot_op import ScheduledDeliveryLoot
from developmental_milestones.developmental_milestone_ops import DevelopmentalMilestoneStateChangeLootOp, DevelopmentalMilestoneReevaluateRelationshipGoalOp
from drama_scheduler.drama_node_ops import ScheduleDramaNodeLoot, CancelScheduledDramaNodeLoot
from drama_scheduler.festival_contest_ops import FestivalContestAwardWinners, FestivalContestAddScoreMultiplier
from event_testing.test_event_loots import ProcessEventOp
from event_testing.tests import TunableTestSet
from fame.fame_loot_ops import SquadLootOp
from global_policies.global_policy_loots import GlobalPolicyAddProgress
from headlines.headline_op import HeadlineOp
from high_school_graduation.graduation_ops import GraduationUpdateSims
from holidays.holiday_loot_ops import HolidaySearchLootOp
from interactions import ParticipantType, ParticipantTypeSingle
from interactions.inventory_loot import InventoryLoot
from interactions.money_payout import MoneyChange
from interactions.object_rewards import ObjectRewardsOperation
from interactions.social.greeting_socials.greetings import GreetingLootOp
from interactions.utils import LootType
from interactions.utils.apply_loot_to_inventory_items_loot import ApplyLootToHiddenInventoryItemsLoot
from interactions.utils.apply_overlay_loot import ApplyCanvasOverlay
from interactions.utils.audio import PlayAudioOp
from interactions.utils.compressed_multiple_inventory_loot import CompressedMultipleInventoryLoot
from interactions.utils.looping_loot_op import LoopingLootOp
from interactions.utils.loot_ops import LifeExtensionLootOp, StateChangeLootOp, AddTraitLootOp, RemoveTraitLootOp, HouseholdFundsInterestLootOp, FireLootOp, UnlockLootOp, DialogLootOp, FireDeactivateSprinklerLootOp, ExtinguishNearbyFireLootOp, AwardWhimBucksLootOp, DiscoverClueLootOp, BreakThroughLootOperation, NewCrimeLootOp, RemoveNotebookEntry, DestroyObjectsFromInventoryLootOp, DestroyTargetObjectsLootOp, LockDoor, UnlockDoor, SummonNPC, TravelToTargetSim, UnlockHiddenAspirationTrack, SetPrimaryAspirationTrack, IncrementCommunityChallengeCount, SlotObjects, DoNothingLootOp, ResetAspiration, RefreshInventoryItemsDecayModifiers, ForceSpawnObjects, PutNearLoot, SimInteractionDialogLootOp, AddTraitListLootOp
from interactions.utils.object_marketplace_loot import ObjectMarketplaceLootOp
from interactions.utils.object_fashion_marketplace_loot import ObjectFashionMarketplaceLootOp
from interactions.utils.reactions import ReactionLootOp
from laundry.laundry_loots import GenerateClothingPile
from objects.animals.animal_loot_ops import AnimalLootOp, UpdateAnimalPreferenceKnowledgeLootOp
from objects.components.linked_object_component import UpdateLinkedObjectComponentOp
from routing.object_routing.set_routing_info_and_state_op import SetRoutingInfoAndStateOp
from interactions.utils.visual_effect import PlayVisualEffectLootOp
from narrative.narrative_loot_ops import NarrativeLootOp, NarrativeGroupProgression
from notebook.notebook_entry_ops import NotebookEntryLootOp
from objects.components import game_component
from objects.components.hidden_inventory_tuning import HiddenInventoryTransferLoot
from objects.components.name_component import NameResetLootOp, TransferNameLootOp, SetNameFromObjectRelationship
from objects.components.object_relationship_component import ObjectRelationshipLootOp
from objects.components.ownable_component import TransferOwnershipLootOp
from objects.components.stored_object_info_component import StoreObjectInfoLootOp, RemoveObjectInfoLootOp
from objects.components.stored_sim_info_component import TransferStoredSimInfo, RemoveSimInfoLootOp, StoreSimInfoLootOp
from objects.components.tooltip_component import TransferCustomTooltip
from objects.components.transfer_painting_state import TransferPaintingStateLoot
from objects.components.utils.lost_and_found_op import LostAndFoundOp
from objects.gardening.gardening_loot_ops import CreatePlantAtLocationLootOperation
from objects.lighting.lighting_utils import LightingOp
from objects.object_creation import ObjectCreationOp
from objects.object_tag_tuning import ApplyTagsToObject
from objects.puddles.puddle_loot_op import CreatePuddlesLootOp
from organizations.organization_loot_ops import OrganizationMembershipLoot
from pets.missing_pet_tuning import MakePetMissing, PostMissingPetAlert
from relationships.relationship_bit_add import RelationshipBitOnFilteredSims
from relationships.relationship_bit_change import RelationshipBitChange
from relationships.relationship_knowledge_ops import KnowOtherSimTraitOp, KnowOtherSimCareerOp, KnowOtherSimsStat, KnowOtherSimMajorOp, KnowOtherSimSexualOrientationOp
from relationships.relationship_lock_change import UnlockRelationshipBitLock
from relics.relic_loot import AddRelicCombo
from restaurants.restaurant_ops import ClaimRestaurantTable, ClaimRestaurantSeat, ReleaseRestaurantTable, RestaurantExpediteGroupOrder
from rewards.cas_part_loot_op import CASUnlockLootOp, StoreCASPartsLootOp
from rewards.reward_operation import RewardOperation
from routing.path_planner.path_plan_loots import UpdateAllowedWadingDepths
from services.roommate_service_utils.roommate_loot_ops import RoommateLootOp
from sickness.sickness_loot_ops import GiveSicknessLootOp, RemoveSicknessLootOp
from sims.body_type_level.body_type_level_loot import SetBodyTypeToPreferredLevel
from sims.favorites.favorites_loot import SetFavoriteLootOp
from sims.household_utilities.utility_loot_op import UtilityModifierOp, UtilityUsageOp
from sims.university.university_loot_ops import UniversityCourseGradeNotification, UniversityLootOp, ShowHighChanceScholarshipsLoot, ApplyForScholarshipLoot, GetScholarshipStatusLoot, ShowScholarshipDynamicSignLoot, ScholarshipActionLoot
from sims4.sim_irq_service import yield_to_irq
from sims4.tuning.instances import TunedInstanceMetaclass, HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableList, Tunable, TunableVariant, HasTunableReference, HasTunableSingletonFactory, AutoFactoryInit, TunableTuple, TunableReference
from sims4.utils import classproperty, flexmethod
import assertions, sims4.log, sims4.resources
from situations.complex.mother_plant_battle_ops import MotherplantBattleSituationStateChange
from situations.service_npcs.butler.butler_loot_ops import ButlerSituationStateChange
from situations.situation_ops import SetSituationSpecialObjectLootOp
from situations.tunable import CreateSituationLootOp, DestroySituationLootOp
from social_media.social_media_loot import SocialMediaPostLoot, SocialMediaReactionLoot, SocialMediaAddFriendLoot
from statistics.statistic_ops import TunableStatisticChange, SkillEffectivenessLoot, DynamicSkillLootOp, NormalizeStatisticsOp, StatisticOperation, DynamicVariantSkillLootOp
from story_progression.story_progression_loot import SeedStoryArc
from topics.tunable import TopicUpdate
from traits.gameplay_object_preference_loot import AddGameplayObjectPreferenceLootOp
from tunable_multiplier import TunableMultiplier
from weather.weather_loot_ops import WeatherSetOverrideForecastLootOp, WeatherStartEventLootOp, WeatherSetSeasonLootOp
from whims.whim_loot_ops import RefreshWhimsLootOp, PushWhimsetLootOp
from world.floor_feature_loot import FloorFeatureRemoveOp
import buffs.buff_ops, services, sims.gender_preference
from world.lot_level_loot import SetDustOverlayOp, ApplyLootToLotLevel, PlayAudioStingOnLotLevel, ApplyLootToAllLotLevels
logger = sims4.log.Logger('Interactions')

class LootOperationList:

    def __init__(self, resolver, loot_list):
        self._loot_actions = tuple(loot_list)
        self._resolver = resolver

    def apply_operations(self):
        for loot_action in self._loot_actions:
            yield_to_irq()
            loot_action.apply_to_resolver(self._resolver)


class LootActionVariant(TunableVariant):

    def __init__(self, *args, statistic_pack_safe=False, **kwargs):
        (super().__init__)(args, actions=TunableReference(description='\n                Apply a set of loot operations.\n                ',
  manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
  class_restrictions=('LootActions', 'RandomWeightedLoot'),
  pack_safe=True), 
         animal_loot=AnimalLootOp.TunableFactory(target_participant_type_options={'description':'\n                    The participant type to target.\n                    ', 
 'participant_type_enum':ParticipantTypeSingle, 
 'default_participant':ParticipantTypeSingle.Object}), 
         apply_canvas_overlay=ApplyCanvasOverlay.TunableFactory(), 
         audio=PlayAudioOp.TunableFactory(), 
         statistics=TunableStatisticChange(statistic_override=StatisticOperation.get_statistic_override(pack_safe=statistic_pack_safe)), 
         relationship_bits_loot=RelationshipBitChange.TunableFactory(description='A list of relationship bit operations to perform'), 
         relationship_bits_lock=UnlockRelationshipBitLock.TunableFactory(), 
         relationship_bits_with_filter=RelationshipBitOnFilteredSims.TunableFactory(), 
         money_loot=MoneyChange.TunableFactory(), 
         object_marketplace=ObjectMarketplaceLootOp.TunableFactory(), 
         object_fashion_marketplace=ObjectFashionMarketplaceLootOp.TunableFactory(), 
         topic_loot=TopicUpdate.TunableFactory(target_participant_type_options={'optional': True}), 
         buff=buffs.buff_ops.BuffOp.TunableFactory(), 
         buff_removal=buffs.buff_ops.BuffRemovalOp.TunableFactory(), 
         buff_transfer=buffs.buff_ops.BuffTransferOp.TunableFactory(target_participant_type_options={'description':'\n                    Buffs are transferred from this Sim to the Subject.\n                    ', 
 'default_participant':ParticipantType.Actor}), 
         normalize_stat=NormalizeStatisticsOp.TunableFactory(target_participant_type_options={'description':'\n                    The Sim from which to transfer the listed stats from.\n                    ', 
 'default_participant':ParticipantType.Actor}), 
         skill_effectiveness=SkillEffectivenessLoot.TunableFactory(), 
         take_turn=game_component.TakeTurn.TunableFactory(), 
         team_score=game_component.TeamScore.TunableFactory(), 
         team_score_points=game_component.TeamScorePoints.TunableFactory(), 
         set_game_outcome=game_component.SetGameOutcome.TunableFactory(), 
         game_over=game_component.GameOver.TunableFactory(), 
         reset_high_score=game_component.ResetHighScore.TunableFactory(), 
         reset_game=game_component.ResetGame.TunableFactory(), 
         setup_game=game_component.SetupGame.TunableFactory(), 
         dynamic_skill_loot=DynamicSkillLootOp.TunableFactory(locked_args={'exclusive_to_owning_si': False}), 
         dynamic_variant_skill_loot=DynamicVariantSkillLootOp.TunableFactory(), 
         fix_gender_preference=sims.gender_preference.GenderPreferenceOp.TunableFactory(), 
         inventory_loot=InventoryLoot.TunableFactory(subject_participant_type_options={'description':'\n                     The participant type who has the inventory that the\n                     object goes into during this loot.\n                     ', 
 'optional':True},
  target_participant_type_options={'description':'\n                    The participant type of the object which would get to\n                    switch inventory in the loot\n                    ', 
 'default_participant':ParticipantType.CarriedObject}), 
         dynamic_buff_loot=DynamicBuffLootOp.TunableFactory(), 
         object_rewards=ObjectRewardsOperation.TunableFactory(), 
         reward=RewardOperation.TunableFactory(), 
         cas_unlock=CASUnlockLootOp.TunableFactory(), 
         transfer_ownership=TransferOwnershipLootOp.TunableFactory(), 
         create_object=ObjectCreationOp.TunableFactory(), 
         create_puddles=CreatePuddlesLootOp.TunableFactory(target_participant_type_options={'description':'\n                    The participant of the interaction whom the puddle\n                    should be placed near.\n                    ', 
 'default_participant':ParticipantType.Object}), 
         create_situation=CreateSituationLootOp.TunableFactory(), 
         destroy_situation=DestroySituationLootOp.TunableFactory(), 
         set_situation_special_object=SetSituationSpecialObjectLootOp.TunableFactory(), 
         life_extension=LifeExtensionLootOp.TunableFactory(), 
         notification_and_dialog=DialogLootOp.TunableFactory(), 
         sim_interaction_dialog=SimInteractionDialogLootOp.TunableFactory(), 
         state_change=StateChangeLootOp.TunableFactory(), 
         trait_add=AddTraitLootOp.TunableFactory(), 
         trait_remove=RemoveTraitLootOp.TunableFactory(), 
         trait_list_add=AddTraitListLootOp.TunableFactory(), 
         know_other_sims_trait=KnowOtherSimTraitOp.TunableFactory(target_participant_type_options={'description':'\n                    The Sim or Sims whose information the subject Sim is learning.\n                    ', 
 'default_participant':ParticipantType.TargetSim}), 
         know_other_sims_career=KnowOtherSimCareerOp.TunableFactory(target_participant_type_options={'description':'\n                    The Sim or Sims whose information the subject Sim is learning.\n                    ', 
 'default_participant':ParticipantType.TargetSim}), 
         know_other_sims_sexual_orientation=KnowOtherSimSexualOrientationOp.TunableFactory(target_participant_type_options={'description':'\n                    The Sim or Sims whose information the subject Sim is learning.\n                    ', 
 'default_participant':ParticipantType.TargetSim}), 
         know_other_sims_statistics=KnowOtherSimsStat.TunableFactory(target_participant_type_options={'description':'\n                    The Sim or Sims whose information the subject Sim is learning.\n                    ', 
 'default_participant':ParticipantType.TargetSim}), 
         know_other_sims_major=KnowOtherSimMajorOp.TunableFactory(target_participant_type_options={'description':'\n                    The Sim or Sims whose information the subject Sim is learning.\n                    ', 
 'default_participant':ParticipantType.TargetSim}), 
         object_relationship=ObjectRelationshipLootOp.TunableFactory(target_participant_type_options={'description':'\n                    The object whose relationship to modify.\n                    ', 
 'default_participant':ParticipantType.Object}), 
         interest_income=HouseholdFundsInterestLootOp.TunableFactory(), 
         career_level=CareerLevelOp.TunableFactory(), 
         career_loot=CareerLootOp.TunableFactory(career_options={'pack_safe': True}), 
         career_stay_late=CareerStayLateOp.TunableFactory(), 
         fire=FireLootOp.TunableFactory(), 
         unlock_item=UnlockLootOp.TunableFactory(), 
         fire_deactivate_sprinkler=FireDeactivateSprinklerLootOp.TunableFactory(), 
         fire_clean_scorch=FloorFeatureRemoveOp.TunableFactory(), 
         extinguish_nearby_fire=ExtinguishNearbyFireLootOp.TunableFactory(), 
         award_whim_bucks=AwardWhimBucksLootOp.TunableFactory(), 
         discover_clue=DiscoverClueLootOp.TunableFactory(), 
         new_crime=NewCrimeLootOp.TunableFactory(), 
         create_notebook_entry=NotebookEntryLootOp.TunableFactory(), 
         breakthrough_moment=BreakThroughLootOperation.TunableFactory(), 
         compressed_multiple_inventory_loot=CompressedMultipleInventoryLoot.TunableFactory(), 
         destroy_objects_from_inventory=DestroyObjectsFromInventoryLootOp.TunableFactory(), 
         destroy_target_objects=DestroyTargetObjectsLootOp.TunableFactory(), 
         bucks_loot=BucksLoot.TunableFactory(), 
         award_perk=AwardPerkLoot.TunableFactory(), 
         refresh_inventory_items_decay_modifiers=RefreshInventoryItemsDecayModifiers.TunableFactory(), 
         refresh_whims=RefreshWhimsLootOp.TunableFactory(), 
         push_whimset=PushWhimsetLootOp.TunableFactory(), 
         remove_notebook_entry=RemoveNotebookEntry.TunableFactory(), 
         lock_door=LockDoor.TunableFactory(), 
         unlock_door=UnlockDoor.TunableFactory(), 
         utility=UtilityModifierOp.TunableFactory(), 
         utility_usage=UtilityUsageOp.TunableFactory(), 
         reaction=ReactionLootOp.TunableFactory(), 
         greeting=GreetingLootOp.TunableFactory(), 
         event=ProcessEventOp.TunableFactory(), 
         schedule_drama_node=ScheduleDramaNodeLoot.TunableFactory(), 
         cancel_scheduled_drama_node=CancelScheduledDramaNodeLoot.TunableFactory(), 
         set_club_gathering_vibe=SetClubGatheringVibe.TunableFactory(), 
         summon_npc=SummonNPC.TunableFactory(), 
         travel_to_target_sim=TravelToTargetSim.TunableFactory(), 
         increment_community_challenge_count=IncrementCommunityChallengeCount.TunableFactory(), 
         unlock_hidden_aspiration_track=UnlockHiddenAspirationTrack.TunableFactory(), 
         set_primary_aspiration_track=SetPrimaryAspirationTrack.TunableFactory(), 
         claim_table=ClaimRestaurantTable.TunableFactory(), 
         claim_seat=ClaimRestaurantSeat.TunableFactory(), 
         release_table=ReleaseRestaurantTable.TunableFactory(), 
         restaurant_expedite_order=RestaurantExpediteGroupOrder.TunableFactory(), 
         business_modify_customer_flow=ModifyCustomerFlow.TunableFactory(), 
         butler_state_change=ButlerSituationStateChange.TunableFactory(), 
         slot_objects=SlotObjects.TunableFactory(), 
         looping_loot_ops=LoopingLootOp.TunableFactory(), 
         give_sickness=GiveSicknessLootOp.TunableFactory(), 
         remove_sickness=RemoveSicknessLootOp.TunableFactory(), 
         apply_tags_to_object=ApplyTagsToObject.TunableFactory(), 
         make_pet_missing=MakePetMissing.TunableFactory(), 
         name_reset=NameResetLootOp.TunableFactory(), 
         post_missing_pet_alert=PostMissingPetAlert.TunableFactory(), 
         vfx=PlayVisualEffectLootOp.TunableFactory(), 
         add_relic_combo=AddRelicCombo.TunableFactory(), 
         oneshot_broadcaster=BroadcasterOneShotLootOp.TunableFactory(), 
         store_cas_parts=StoreCASPartsLootOp.TunableFactory(), 
         store_object_info=StoreObjectInfoLootOp.TunableFactory(), 
         remove_object_info=RemoveObjectInfoLootOp.TunableFactory(), 
         store_sim_info=StoreSimInfoLootOp.TunableFactory(), 
         recycling_bucks_loot=RecyclingBucksLoot.TunableFactory(), 
         remove_stored_sim_info=RemoveSimInfoLootOp.TunableFactory(), 
         weather_set_override_forecast=WeatherSetOverrideForecastLootOp.TunableFactory(locked_args={'subject': ParticipantType.Actor}), 
         weather_set_season=WeatherSetSeasonLootOp.TunableFactory(locked_args={'subject': ParticipantType.Actor}), 
         weather_start_event=WeatherStartEventLootOp.TunableFactory(locked_args={'subject': ParticipantType.Actor}), 
         hidden_inventory_transfer=HiddenInventoryTransferLoot.TunableFactory(), 
         transfer_painting_state=TransferPaintingStateLoot.TunableFactory(), 
         squad_loot=SquadLootOp.TunableFactory(), 
         stored_sim_info_transfer=TransferStoredSimInfo.TunableFactory(), 
         custom_tooltip_transfer=TransferCustomTooltip.TunableFactory(), 
         transfer_name_loot=TransferNameLootOp.TunableFactory(), 
         reset_aspiration=ResetAspiration.TunableFactory(), 
         narrative=NarrativeLootOp.TunableFactory(), 
         narrative_progression=NarrativeGroupProgression.TunableFactory(), 
         scheduled_delivery=ScheduledDeliveryLoot.TunableReference(), 
         motherplant_battle_change=MotherplantBattleSituationStateChange.TunableFactory(), 
         global_policy_add_progress=GlobalPolicyAddProgress.TunableFactory(locked_args={'text': None}), 
         festival_contest_get_reward=FestivalContestAwardWinners.TunableFactory(), 
         festival_contest_add_score_multiplier=FestivalContestAddScoreMultiplier.TunableFactory(), 
         set_name_from_object_relationship=SetNameFromObjectRelationship.TunableFactory(), 
         create_plant=CreatePlantAtLocationLootOperation.TunableFactory(), 
         set_favorite=SetFavoriteLootOp.TunableFactory(target_participant_type_options={'optional': True}), 
         roommate_ops=RoommateLootOp.TunableFactory(), 
         university_course_grade_notification=UniversityCourseGradeNotification.TunableFactory(), 
         university_loot=UniversityLootOp.TunableFactory(), 
         organization_membership_loot=OrganizationMembershipLoot.TunableFactory(), 
         scholarship_show_high_chance_loot=ShowHighChanceScholarshipsLoot.TunableFactory(), 
         scholarship_apply_loot=ApplyForScholarshipLoot.TunableFactory(), 
         scholarship_get_status_loot=GetScholarshipStatusLoot.TunableFactory(), 
         scholarship_action_loot=ScholarshipActionLoot.TunableFactory(), 
         scholarship_show_info_sign=ShowScholarshipDynamicSignLoot.TunableFactory(), 
         apply_loot_to_hidden_inventory_items=ApplyLootToHiddenInventoryItemsLoot.TunableFactory(), 
         refund_crafting_process=RefundCraftingProcessLoot.TunableFactory(), 
         lost_and_found=LostAndFoundOp.TunableFactory(), 
         set_routing_info_and_state=SetRoutingInfoAndStateOp.TunableFactory(), 
         add_career_gig=AddCareerGigOp.TunableFactory(), 
         force_spawn_objects=ForceSpawnObjects.TunableFactory(), 
         food_restriction_loot=FoodRestrictionOp.TunableFactory(), 
         lighting_loot=LightingOp.TunableFactory(), 
         headline_loot=HeadlineOp.TunableFactory(), 
         set_dust_overlay=SetDustOverlayOp.TunableFactory(), 
         apply_loot_to_lot_level_objects=ApplyLootToLotLevel.TunableFactory(), 
         apply_loot_to_all_lot_level_objects=ApplyLootToAllLotLevels.TunableFactory(), 
         play_audio_on_lot_level=PlayAudioStingOnLotLevel.TunableFactory(), 
         update_animal_preference_knowledge=UpdateAnimalPreferenceKnowledgeLootOp.TunableFactory(), 
         setup_crafted_object=SetupCraftedObjectLoot.TunableFactory(), 
         update_allowed_wading_depths=UpdateAllowedWadingDepths.TunableFactory(), 
         holiday_search_loot=HolidaySearchLootOp.TunableFactory(target_participant_type_options={'description':'\n                    The object being searched during the active holiday.\n                    ', 
 'default_participant':ParticipantType.Object}), 
         put_near=PutNearLoot.TunableFactory(), 
         seed_story_arc=SeedStoryArc.TunableFactory(), 
         clan_loot=ClanLootOp.TunableFactory(), 
         graduation=GraduationUpdateSims.TunableFactory(), 
         social_media_post=SocialMediaPostLoot.TunableFactory(), 
         social_media_reaction=SocialMediaReactionLoot.TunableFactory(), 
         social_media_add_friend=SocialMediaAddFriendLoot.TunableFactory(), 
         body_type_to_preferred_level=SetBodyTypeToPreferredLevel.TunableFactory(), 
         add_gameplay_object_preference=AddGameplayObjectPreferenceLootOp.TunableFactory(), 
         developmental_milestone_state_change=DevelopmentalMilestoneStateChangeLootOp.TunableFactory(), 
         timed_aspiration=TimedAspirationLootOp.TunableFactory(), 
         generate_clothing_pile=GenerateClothingPile.TunableFactory(), 
         reevaluate_relationship_goal=DevelopmentalMilestoneReevaluateRelationshipGoalOp.TunableFactory(), 
         update_linked_object_component=UpdateLinkedObjectComponentOp.TunableFactory(), 
         add_adopted_sim_to_family=AddAdoptedSimToFamilyLootOp.TunableFactory(), **kwargs)


class LootActions(HasTunableReference, HasTunableSingletonFactory, AutoFactoryInit, metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ACTION)):
    INSTANCE_TUNABLES = {'run_test_first':Tunable(description='\n           If left unchecked, iterate over the actions and if its test succeeds\n           apply the action at that moment.\n           \n           If checked, run through all the loot actions and collect all actions\n           that passes their test.  Then apply all the actions that succeeded.\n           ',
       tunable_type=bool,
       default=False), 
     'loot_actions':TunableList(description='\n           List of loots operations that will be awarded.\n           ',
       tunable=LootActionVariant(statistic_pack_safe=True)), 
     'tests':TunableTestSet(description='\n           Tests to run before applying any of the loot actions.\n           \n           These are run before run_test_first is evaluated so it will not\n           affect these tests.\n           ')}
    FACTORY_TUNABLES = INSTANCE_TUNABLES
    _simoleon_loot = None

    @classmethod
    def _tuning_loaded_callback(cls):
        cls._simoleon_loot = None
        for action in cls.loot_actions:
            if hasattr(action, 'get_simoleon_delta'):
                if cls._simoleon_loot is None:
                    cls._simoleon_loot = []
                cls._simoleon_loot.append(action)

    @classmethod
    def _verify_tuning_callback(cls):
        cls._validate_recursion()

    @classmethod
    @assertions.not_recursive
    def _validate_recursion(cls):
        for action in cls.loot_actions:
            if action.loot_type == LootType.ACTIONS:
                try:
                    action._validate_recursion()
                except AssertionError:
                    logger.error('{} is an action in {} but that creates a circular dependency', action, cls, owner='epanero')

    @classproperty
    def loot_type(self):
        return LootType.ACTIONS

    @classmethod
    def get_simoleon_delta(cls, *args, **kwargs):
        total_funds_category = None
        total_funds_delta = 0
        if cls._simoleon_loot is not None:
            for action in cls._simoleon_loot:
                funds_delta, funds_category = (action.get_simoleon_delta)(*args, **kwargs)
                if funds_category is not None:
                    total_funds_category = funds_category
                total_funds_delta += funds_delta

        return (
         total_funds_delta, total_funds_category)

    @flexmethod
    def get_loot_ops_gen--- This code section failed: ---

 L. 512         0  LOAD_FAST                'inst'
                2  LOAD_CONST               None
                4  COMPARE_OP               is-not
                6  POP_JUMP_IF_FALSE    12  'to 12'
                8  LOAD_FAST                'inst'
               10  JUMP_FORWARD         14  'to 14'
             12_0  COME_FROM             6  '6'
               12  LOAD_FAST                'cls'
             14_0  COME_FROM            10  '10'
               14  STORE_FAST               'inst_or_cls'

 L. 513        16  LOAD_FAST                'resolver'
               18  LOAD_CONST               None
               20  COMPARE_OP               is-not
               22  POP_JUMP_IF_FALSE    46  'to 46'
               24  LOAD_FAST                'inst_or_cls'
               26  LOAD_ATTR                tests
               28  POP_JUMP_IF_FALSE    46  'to 46'

 L. 514        30  LOAD_FAST                'inst_or_cls'
               32  LOAD_ATTR                tests
               34  LOAD_METHOD              run_tests
               36  LOAD_FAST                'resolver'
               38  CALL_METHOD_1         1  '1 positional argument'
               40  POP_JUMP_IF_TRUE     46  'to 46'

 L. 515        42  LOAD_CONST               None
               44  RETURN_VALUE     
             46_0  COME_FROM            40  '40'
             46_1  COME_FROM            28  '28'
             46_2  COME_FROM            22  '22'

 L. 517        46  LOAD_FAST                'resolver'
               48  LOAD_CONST               None
               50  COMPARE_OP               is
               52  POP_JUMP_IF_TRUE     60  'to 60'
               54  LOAD_FAST                'inst_or_cls'
               56  LOAD_ATTR                run_test_first
               58  POP_JUMP_IF_TRUE    128  'to 128'
             60_0  COME_FROM            52  '52'

 L. 518        60  SETUP_LOOP          244  'to 244'
               62  LOAD_FAST                'inst_or_cls'
               64  LOAD_ATTR                loot_actions
               66  GET_ITER         
               68  FOR_ITER            124  'to 124'
               70  STORE_FAST               'action'

 L. 519        72  LOAD_FAST                'action'
               74  LOAD_ATTR                loot_type
               76  LOAD_GLOBAL              LootType
               78  LOAD_ATTR                ACTIONS
               80  COMPARE_OP               ==
               82  POP_JUMP_IF_FALSE   112  'to 112'

 L. 520        84  LOAD_FAST                'action'
               86  LOAD_ATTR                get_loot_ops_gen
               88  BUILD_TUPLE_0         0 
               90  LOAD_STR                 'resolver'
               92  LOAD_FAST                'resolver'
               94  BUILD_MAP_1           1 
               96  LOAD_FAST                'kwargs'
               98  BUILD_MAP_UNPACK_WITH_CALL_2     2 
              100  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
              102  GET_YIELD_FROM_ITER
              104  LOAD_CONST               None
              106  YIELD_FROM       
              108  POP_TOP          
              110  JUMP_BACK            68  'to 68'
            112_0  COME_FROM            82  '82'

 L. 522       112  LOAD_FAST                'action'
              114  LOAD_CONST               False
              116  BUILD_TUPLE_2         2 
              118  YIELD_VALUE      
              120  POP_TOP          
              122  JUMP_BACK            68  'to 68'
              124  POP_BLOCK        
              126  JUMP_FORWARD        244  'to 244'
            128_0  COME_FROM            58  '58'

 L. 524       128  BUILD_LIST_0          0 
              130  STORE_FAST               'actions_that_can_be_applied'

 L. 525       132  SETUP_LOOP          180  'to 180'
              134  LOAD_FAST                'inst_or_cls'
              136  LOAD_ATTR                loot_actions
              138  GET_ITER         
            140_0  COME_FROM           164  '164'
              140  FOR_ITER            178  'to 178'
              142  STORE_FAST               'action'

 L. 526       144  LOAD_FAST                'action'
              146  LOAD_ATTR                loot_type
              148  LOAD_GLOBAL              LootType
              150  LOAD_ATTR                ACTIONS
              152  COMPARE_OP               ==
              154  POP_JUMP_IF_TRUE    166  'to 166'
              156  LOAD_FAST                'action'
              158  LOAD_METHOD              test_resolver
              160  LOAD_FAST                'resolver'
              162  CALL_METHOD_1         1  '1 positional argument'
              164  POP_JUMP_IF_FALSE   140  'to 140'
            166_0  COME_FROM           154  '154'

 L. 527       166  LOAD_FAST                'actions_that_can_be_applied'
              168  LOAD_METHOD              append
              170  LOAD_FAST                'action'
              172  CALL_METHOD_1         1  '1 positional argument'
              174  POP_TOP          
              176  JUMP_BACK           140  'to 140'
              178  POP_BLOCK        
            180_0  COME_FROM_LOOP      132  '132'

 L. 529       180  SETUP_LOOP          244  'to 244'
              182  LOAD_FAST                'actions_that_can_be_applied'
              184  GET_ITER         
              186  FOR_ITER            242  'to 242'
              188  STORE_FAST               'action'

 L. 530       190  LOAD_FAST                'action'
              192  LOAD_ATTR                loot_type
              194  LOAD_GLOBAL              LootType
              196  LOAD_ATTR                ACTIONS
              198  COMPARE_OP               ==
              200  POP_JUMP_IF_FALSE   230  'to 230'

 L. 531       202  LOAD_FAST                'action'
              204  LOAD_ATTR                get_loot_ops_gen
              206  BUILD_TUPLE_0         0 
              208  LOAD_STR                 'resolver'
              210  LOAD_FAST                'resolver'
              212  BUILD_MAP_1           1 
              214  LOAD_FAST                'kwargs'
              216  BUILD_MAP_UNPACK_WITH_CALL_2     2 
              218  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
              220  GET_YIELD_FROM_ITER
              222  LOAD_CONST               None
              224  YIELD_FROM       
              226  POP_TOP          
              228  JUMP_BACK           186  'to 186'
            230_0  COME_FROM           200  '200'

 L. 533       230  LOAD_FAST                'action'
              232  LOAD_CONST               True
              234  BUILD_TUPLE_2         2 
              236  YIELD_VALUE      
              238  POP_TOP          
              240  JUMP_BACK           186  'to 186'
              242  POP_BLOCK        
            244_0  COME_FROM_LOOP      180  '180'
            244_1  COME_FROM           126  '126'
            244_2  COME_FROM_LOOP       60  '60'

Parse error at or near `COME_FROM' instruction at offset 244_1

    @classmethod
    def apply_to_resolver_and_get_display_texts(cls, resolver):
        display_texts = []
        for action, test_ran in cls.get_loot_ops_gen(resolver=resolver):
            try:
                logger.info('Action applied: {}', action)
                success, _ = action.apply_to_resolver(resolver, skip_test=test_ran)
                if success:
                    display_texts.append(action.get_display_text(resolver=resolver))
            except Exception as ex:
                try:
                    logger.exception('Exception when applying action {} for loot {}', action, cls)
                    raise ex
                finally:
                    ex = None
                    del ex

        return display_texts

    @flexmethod
    def apply_to_resolver(cls, inst, resolver, skip_test=False):
        inst_or_cls = inst if inst is not None else cls
        for action, test_ran in inst_or_cls.get_loot_ops_gen(resolver):
            try:
                action.apply_to_resolver(resolver, skip_test=test_ran)
            except Exception as ex:
                try:
                    logger.exception('Exception when applying action {} for loot {}', action, cls)
                    raise ex
                finally:
                    ex = None
                    del ex


LootActions.TunableFactory(description='[rez] <Unused>')

class WeightedSingleSimLootActions(HasTunableReference, HasTunableSingletonFactory, AutoFactoryInit, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ACTION)):
    INSTANCE_TUNABLES = {'loot_actions': TunableList(description='\n            A list of weighted Loot Actions that operate only on one Sim.\n            ',
                       tunable=TunableTuple(buff_loot=(DynamicBuffLootOp.TunableFactory()),
                       weight=Tunable(description='\n                    Accompanying weight of the loot.\n                    ',
                       tunable_type=int,
                       default=1)))}

    def __iter__(self):
        return iter(self.loot_actions)

    @classmethod
    def pick_loot_op(cls):
        weighted_loots = [(loot.weight, loot.buff_loot) for loot in cls.loot_actions]
        loot_op = sims4.random.weighted_random_item(weighted_loots)
        return loot_op


class RandomWeightedLoot(HasTunableReference, HasTunableSingletonFactory, AutoFactoryInit, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ACTION)):
    INSTANCE_TUNABLES = {'random_loot_actions':TunableList(description='\n            List of weighted loot actions that can be run.\n            ',
       tunable=TunableTuple(description='\n                Weighted actions that will be randomly selected when\n                the loot is executed.  The loots will be tested\n                before running to guarantee the random action is valid. \n                ',
       action=LootActionVariant(do_nothing=(DoNothingLootOp.TunableFactory())),
       weight=TunableMultiplier.TunableFactory(description='\n                    The weight of this potential initial moment relative\n                    to other items within this list.\n                    '))), 
     'tests':TunableTestSet(description='\n            Tests to run before applying any of the loot actions.\n            ')}
    _simoleon_loot = None

    @classmethod
    def _tuning_loaded_callback(cls):
        cls._simoleon_loot = None
        for random_action in cls.random_loot_actions:
            if hasattr(random_action.action, 'get_simoleon_delta'):
                if cls._simoleon_loot is None:
                    cls._simoleon_loot = []
                cls._simoleon_loot.append(random_action.action)

    @classproperty
    def loot_type(self):
        return LootType.ACTIONS

    @classmethod
    @assertions.not_recursive
    def _validate_recursion(cls):
        for random_action in cls.random_loot_actions:
            if random_action.action.loot_type == LootType.ACTIONS:
                try:
                    random_action.action._validate_recursion()
                except AssertionError:
                    logger.error('{} is an action in {} but that creates a circular dependency', (random_action.action), cls, owner='camilogarcia')

    @flexmethod
    def get_loot_ops_gen(cls, inst, resolver=None, auto_select=True):
        inst_or_cls = inst if inst is not None else cls
        if resolver is not None:
            if inst_or_cls.tests:
                if not inst_or_cls.tests.run_tests(resolver):
                    return
        elif resolver is None:
            for random_action in inst_or_cls.random_loot_actions:
                if random_action.action.loot_type == LootType.ACTIONS:
                    yield from random_action.action.get_loot_ops_gen(resolver=resolver)
                else:
                    yield (
                     random_action.action, False)

        else:
            if auto_select:
                weighted_random_actions = [(ra.weight.get_multiplier(resolver), ra.action) for ra in inst_or_cls.random_loot_actions]
                actions = []
                while weighted_random_actions:
                    potential_action_index = sims4.random.weighted_random_index(weighted_random_actions)
                    if potential_action_index is None:
                        return
                        potential_action = weighted_random_actions.pop(potential_action_index)[1]
                        if potential_action is None:
                            continue
                        if potential_action.loot_type == LootType.ACTIONS:
                            valid_actions = []
                            for action, _ in potential_action.get_loot_ops_gen(resolver=resolver):
                                if action.test_resolver(resolver):
                                    valid_actions.append(action)

                            if valid_actions:
                                actions = valid_actions
                                break
                    elif potential_action.test_resolver(resolver):
                        actions = (
                         potential_action,)
                        break

                for action in actions:
                    if action.loot_type == LootType.ACTIONS:
                        yield from action.get_loot_ops_gen(resolver=resolver)
                    else:
                        yield (
                         action, True)

            else:
                yield (
                 inst_or_cls, False)

    @flexmethod
    def apply_to_resolver(cls, inst, resolver, skip_test=False):
        inst_or_cls = inst if inst is not None else cls
        for action, test_ran in inst_or_cls.get_loot_ops_gen(resolver):
            try:
                action.apply_to_resolver(resolver, skip_test=test_ran)
            except BaseException as ex:
                try:
                    logger.exception('Exception when applying action {} for loot {}', action, cls)
                    raise ex
                finally:
                    ex = None
                    del ex

    @classmethod
    def test_resolver(cls, *_, **__):
        return True

    @flexmethod
    def apply_to_interaction_statistic_change_element(cls, inst, resolver):
        inst_or_cls = inst if inst is not None else cls
        inst_or_cls.apply_to_resolver(resolver, skip_test=True)

    @classmethod
    def get_stat(cls, _interaction):
        pass

    @classmethod
    def get_simoleon_delta(cls, *args, **kwargs):
        total_funds_category = None
        total_funds_delta = 0
        if cls._simoleon_loot is not None:
            for action in cls._simoleon_loot:
                funds_delta, funds_category = (action.get_simoleon_delta)(*args, **kwargs)
                if funds_category is not None:
                    total_funds_category = funds_category
                total_funds_delta += funds_delta

        return (
         total_funds_delta, total_funds_category)