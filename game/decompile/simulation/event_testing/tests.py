# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\tests.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 50334 bytes
from _sims4_collections import frozendict
import itertools
from developmental_milestones.developmental_milestone_tests import DevelopmentalMilestoneTest, DevelopmentalMilestoneCompletionTest
from high_school_graduation.graduation_tests import GraduationTest
from laundry.laundry_tests import LaundryHeroObjectTest
from live_events.live_event_tests import LiveEventStateTest
from bucks.currency_tests import BucksTest
from caches import cached
from civic_policies.street_civic_policy_tests import StreetCivicPolicyTest
from clans.clan_tests import HasClanLeaderTest
from crafting.crafting_tests import CraftingRecipeTest
from crafting.food_restrictions_tests import FoodRestrictionTest
from curfew.curfew_tests import CurfewTest
from eco_footprint.eco_footprint_tests import StreetEcoFootprintTest
from event_testing.scholarship_tests import ScholarshipStatusTest
from event_testing.test_variants import CareerGigTest, StyleActiveTest, CareerGigCustomerLotTest, CareerGigResultTest
from fame.fame_tests import LifestyleBrandTest, FameMomentTest
from familiars.familiar_tests import FamiliarTest, HasFamiliarTest
from fishing.fishing_tests import FishingTest
from gameplay_scenarios.scenario_tests import ScenarioRoleTest, ScenarioGoalCompletedTest, ScenarioPhaseTriggeredTest
from global_flags.global_flag_test import GlobalFlagTest
from global_policies.global_policy_tests import GlobalPolicyStateTest
from holidays.holiday_tests import TraditionTest, HolidayTest, ObjectSearchedHolidayTest
from live_festivals.live_festival_tests import ActiveLiveFestivalTest
from lot_decoration.lot_decoration_tests import LotDecorationTest
from lunar_cycle.lunar_cycle_tests import LunarPhaseTest
from narrative.narrative_tests import NarrativeTest
from notebook.notebook_tests import NotebookCategoriesTest
from objects.object_tests import ActiveRoutingObjectsTest, CountTest, SoundMatchesStoredAudioComponentTest
from objects.slot_tests import TunableSlotTest, RelatedSlotsTest
from rabbit_hole.rabbit_hole_test import RabbitHoleTest
from routing.walkstyle.wading_tests import WadingIntervalTest
from routing.walkstyle.walkstyle_tests import WalkstyleCostTest
from seasons.season_tests import SeasonTest
from services.roommate_service_utils.roommate_tests import RoommateTests
from sims.body_type_level.body_type_level_tests import PreferredBodyTypeLevelTest
from sims.favorites.favorites_tests import FavoritesTest, HasAnyFavoriteOfTypeTest
from sims.household_utilities.utility_tests import UtilityTest, UtilitiesComponentTest
from sims.occult.occult_tests import OccultFormAvailabilityTest
from sims.outfits.outfit_tests import OutfitTest, OutfitBodyTypeTest, OutfitCASPartTagsTest, OutfitPrevalentTrendTagTest
from sims.university.university_tests import UniversityEnrollmentTest, UniversityClassroomTest, UniversityTests, UniversityProfessorTest, UniversityHousingConfigurationTest
from sims4.localization import TunableLocalizedStringFactory
from situations.ambient.wildlife_encounter_director import WildlifeEncounterTestByGroup
from situations.situation_goal_tests import SituationGoalTest
from social_media import social_media_tests
from teleport.teleport_tests import TeleportCostTest
from venues.civic_policies import venue_civic_policy_tests
from weather.weather_tests import WeatherForecastOverrideTest, WeatherTest, WeatherTypeTest
import aspirations.aspiration_tests, business.business_tests, clubs.club_tests, conditional_layers.conditional_layer_tests, drama_scheduler.drama_node_tests, event_testing.constraint_tests, event_testing.game_option_tests, event_testing.resolver, event_testing.results, event_testing.state_tests, event_testing.statistic_tests, event_testing.test_based_score_threshold, event_testing.test_variants, gsi_handlers, objects.footprint_tests, objects.gardening.gardening_tests, objects.object_tests, objects.animals.animal_tests, organizations.organization_tests, relationships.relationship_tests, restaurants.restaurant_tests, retail.retail_tests, routing.formation.formation_tests, server.online_tests, services, sickness.sickness_tests, sims.households.household_tests, sims.sim_info_tests, sims.swim_location_test, sims.unlock_tracker_tests, sims4.log, sims4.repr_utils, sims4.tuning.instance_manager, sims4.tuning.tunable, sims4.utils, socials.social_tests, statistics.skill_tests, temple.temple_tests, traits.gameplay_object_preference_tests, traits.preference_tests, travel_group.travel_group_tests, vet.vet_clinic_tests, world.floor_feature_test, world.pick_tests, world.pool_size_test, world.world_tests, zone_tests
from whims.whim_tests import WhimTest
logger = sims4.log.Logger('Tests')

def _get_debug_loaded_tuning_callbak(tuning_loaded_callback, callback):
    return callback


def _verify_tooltip_tuning(instance_class, tunable_name, source, value):
    test_with_tooltip = None
    for test in value:
        if test.has_tooltip():
            test_with_tooltip = test


class TunableTestVariant(sims4.tuning.tunable.TunableVariant):
    TEST_VARIANTS = {'active_live_festival':ActiveLiveFestivalTest.TunableFactory, 
     'active_routing_objects':objects.object_tests.ActiveRoutingObjectsTest.TunableFactory, 
     'age_up_test':sims.sim_info_tests.AgeUpTest.TunableFactory, 
     'animal_test':objects.animals.animal_tests.AnimalTest.TunableFactory, 
     'appropriateness':sims.sim_info_tests.AppropriatenessTest.TunableFactory, 
     'aspiration_track_complete':aspirations.aspiration_tests.CompletedAspirationTrackTest.TunableFactory, 
     'at_work':event_testing.test_variants.AtWorkTest.TunableFactory, 
     'autonomy_scoring_preference':objects.object_tests.ObjectScoringPreferenceTest.TunableFactory, 
     'bills':event_testing.test_variants.TunableBillsTest, 
     'birthday_test':sims.sim_info_tests.BirthdayTest.TunableFactory, 
     'bucks_perks_test':event_testing.test_variants.BucksPerkTest.TunableFactory, 
     'bucks_test':BucksTest.TunableFactory, 
     'buff':sims.sim_info_tests.BuffTest.TunableFactory, 
     'business_allows_new_customers':business.business_tests.BusinessAllowsNewCustomersTest.TunableFactory, 
     'business_settings':business.business_tests.BusinessSettingTest.TunableFactory, 
     'can_create_user_facing_situation':event_testing.test_variants.CanCreateUserFacingSituationTest.TunableFactory, 
     'can_see_object':objects.object_tests.CanSeeObjectTest.TunableFactory, 
     'career_assignment_test':event_testing.test_variants.CareerAssignmentTest.TunableFactory, 
     'career_daily_task_completed_test':event_testing.test_variants.CareerDailyTaskCompletedTest.TunableFactory, 
     'career_gig_test':CareerGigTest.TunableFactory, 
     'career_gig_customer_lot_test':CareerGigCustomerLotTest.TunableFactory, 
     'career_gig_result_test':CareerGigResultTest.TunableFactory, 
     'career_gig_history_test':event_testing.test_variants.CareerGigHistoryTest.TunableFactory, 
     'career_previous_career_test':event_testing.test_variants.CareerPreviousCareerTest.TunableFactory, 
     'career_test':event_testing.test_variants.TunableCareerTest.TunableFactory, 
     'club_gathering_test':clubs.club_tests.TunableClubGatheringTest, 
     'club_test':clubs.club_tests.ClubTest.TunableFactory, 
     'collection_test':event_testing.test_variants.TunableCollectionThresholdTest, 
     'commodity_advertised':event_testing.statistic_tests.CommodityAdvertisedTest.TunableFactory, 
     'commodity_desired_by_other_sims':event_testing.statistic_tests.CommodityDesiredByOtherSims.TunableFactory, 
     'compatibility_level':relationships.relationship_tests.CompatibilityLevelTest.TunableFactory, 
     'conditional_layer_loaded':conditional_layers.conditional_layer_tests.ConditionalLayerLoadedTest.TunableFactory, 
     'consumable_test':objects.object_tests.ConsumableTest.TunableFactory, 
     'content_mode':server.online_tests.ContentModeTest.TunableFactory, 
     'count':CountTest.TunableFactory, 
     'crafting_recipe':CraftingRecipeTest.TunableFactory, 
     'crafted_item':objects.object_tests.CraftedItemTest.TunableFactory, 
     'crafted_with_ingredients':objects.object_tests.CraftedWithIngredientsTest.TunableFactory, 
     'curfew':CurfewTest.TunableFactory, 
     'custom_name':objects.object_tests.CustomNameTest.TunableFactory, 
     'day_and_time':event_testing.test_variants.TunableDayTimeTest, 
     'dead_test':sims.sim_info_tests.DeadTest.TunableFactory, 
     'detective_clues':event_testing.test_variants.DetectiveClueTest.TunableFactory, 
     'developmental_milestone':DevelopmentalMilestoneTest.TunableFactory, 
     'developmental_milestone_completion':DevelopmentalMilestoneCompletionTest.TunableFactory, 
     'diagnostic_action_test':sickness.sickness_tests.DiagnosticActionTest.TunableFactory, 
     'distance':world.world_tests.DistanceTest.TunableFactory, 
     'drama_node':drama_scheduler.drama_node_tests.DramaNodeTest.TunableFactory, 
     'drama_node_bucket':drama_scheduler.drama_node_tests.DramaNodeBucketTest.TunableFactory, 
     'dress_code_test':restaurants.restaurant_tests.DressCodeTest.TunableFactory, 
     'during_work_hours':event_testing.test_variants.TunableDuringWorkHoursTest, 
     'eco_footprint':StreetEcoFootprintTest.TunableFactory, 
     'ensemble':event_testing.test_variants.EnsembleTest.TunableFactory, 
     'existence':objects.object_tests.ExistenceTest.TunableFactory, 
     'fame_moment_test':FameMomentTest.TunableFactory, 
     'familiar':FamiliarTest.TunableFactory, 
     'favorites':FavoritesTest.TunableFactory, 
     'festival_running':drama_scheduler.drama_node_tests.FestivalRunningTest.TunableFactory, 
     'filter_test':sims.sim_info_tests.FilterTest.TunableFactory, 
     'fire':event_testing.test_variants.FireTest.TunableFactory, 
     'fishing_test':FishingTest.TunableFactory, 
     'food_restriction_test':FoodRestrictionTest.TunableFactory, 
     'game_component':objects.object_tests.GameTest.TunableFactory, 
     'game_option':event_testing.game_option_tests.SimInfoGameplayOptionsTest.TunableFactory, 
     'gameplay_object_preference_test':traits.gameplay_object_preference_tests.GameplayObjectPreferenceTest.TunableFactory, 
     'gender_preference':sims.sim_info_tests.GenderPreferenceTest.TunableFactory, 
     'genealogy':sims.sim_info_tests.GenealogyTest.TunableFactory, 
     'gig_preference':traits.preference_tests.GigPreferenceTest.TunableFactory, 
     'global_flag':GlobalFlagTest.TunableFactory, 
     'global_policy_state':GlobalPolicyStateTest.TunableFactory, 
     'graduation':GraduationTest.TunableFactory, 
     'greeted':event_testing.test_variants.GreetedTest.TunableFactory, 
     'has_any_favorite_of_type':HasAnyFavoriteOfTypeTest.TunableFactory, 
     'has_child_of_type':objects.object_tests.HasObjectOfTypeAsChildTest.TunableFactory, 
     'has_child_object_on_part':objects.object_tests.HasChildObjectOnPartTest.TunableFactory, 
     'has_clan_leader_test':HasClanLeaderTest.TunableFactory, 
     'has_familiar':HasFamiliarTest.TunableFactory, 
     'has_free_part':objects.object_tests.HasFreePartTest.TunableFactory, 
     'has_head_parented_object':objects.object_tests.HasHeadParentedObjectTest.TunableFactory, 
     'has_in_use_part':objects.object_tests.HasInUsePartTest.TunableFactory, 
     'has_lot_owner':event_testing.test_variants.HasLotOwnerTest.TunableFactory, 
     'has_parent_object':objects.object_tests.HasParentObjectTest.TunableFactory, 
     'has_photo_filter':event_testing.test_variants.HasPhotoFilterTest.TunableFactory, 
     'has_portal_test':event_testing.test_variants.HasPortalTest.TunableFactory, 
     'has_timed_aspirations':aspirations.aspiration_tests.HasTimedAspirationTest.TunableFactory, 
     'home_region':world.world_tests.HomeRegionTest.TunableFactory, 
     'holiday_test':HolidayTest.TunableFactory, 
     'holiday_tradition':TraditionTest.TunableFactory, 
     'holiday_object_already_searched':ObjectSearchedHolidayTest.TunableFactory, 
     'household_can_post_alert':event_testing.test_variants.HouseholdCanPostAlertTest.TunableFactory, 
     'household_has_missing_pet':event_testing.test_variants.HouseholdMissingPetTest.TunableFactory, 
     'household_size':event_testing.test_variants.HouseholdSizeTest.TunableFactory, 
     'identity':event_testing.test_variants.TunableIdentityTest, 
     'in_footprint':objects.footprint_tests.InFootprintTest.TunableFactory, 
     'in_inventory':objects.object_tests.InInventoryTest.TunableFactory, 
     'in_use':objects.object_tests.InUseTest.TunableFactory, 
     'inappropriateness':sims.sim_info_tests.InappropriatenessTest.TunableFactory, 
     'interaction_restored_from_load':event_testing.test_variants.InteractionRestoredFromLoadTest.TunableFactory, 
     'interaction_source_test':event_testing.test_variants.InteractionSourceTest.TunableFactory, 
     'inventory':objects.object_tests.InventoryTest.TunableFactory, 
     'is_carrying_object':objects.object_tests.IsCarryingObjectTest.TunableFactory, 
     'is_entitled':server.online_tests.IsEntitledTest.TunableFactory, 
     'is_in_current_temple_room':temple.temple_tests.IsInCurrentTempleRoomTest.TunableFactory, 
     'is_live_event_active':server.online_tests.IsLiveEventActive.TunableFactory, 
     'is_online':server.online_tests.IsOnlineTest.TunableFactory, 
     'is_temple_trigger_interaction':temple.temple_tests.IsTriggerInteractionTest.TunableFactory, 
     'in_home_neighborhood':world.world_tests.InHomeNeighborhoodTest.TunableFactory, 
     'in_home_region':world.world_tests.InHomeRegionTest.TunableFactory, 
     'knowledge':sims.sim_info_tests.KnowledgeTest.TunableFactory, 
     'laundry_hero_object':LaundryHeroObjectTest.TunableFactory, 
     'lifestyle_brand':LifestyleBrandTest.TunableFactory, 
     'live_event_state':LiveEventStateTest.TunableFactory, 
     'location':world.world_tests.LocationTest.TunableFactory, 
     'locked_portal_count':event_testing.test_variants.LockedPortalCountTest.TunableFactory, 
     'lot_decorations':LotDecorationTest.TunableFactory, 
     'lot_has_floor_feature':event_testing.test_variants.LotHasFloorFeatureTest.TunableFactory, 
     'lot_has_front_door':event_testing.test_variants.FrontDoorTest.TunableFactory, 
     'lot_has_garden':objects.gardening.gardening_tests.LotHasGardenTest.TunableFactory, 
     'lot_owner':event_testing.test_variants.LotOwnerTest.TunableFactory, 
     'lunar_phase':LunarPhaseTest.TunableFactory, 
     'mood':sims.sim_info_tests.MoodTest.TunableFactory, 
     'motive':event_testing.statistic_tests.MotiveThresholdTest.TunableFactory, 
     'narrative':NarrativeTest.TunableFactory, 
     'new_social_media_posts':social_media_tests.NewSocialMediaPostTest.TunableFactory, 
     'next_festival':drama_scheduler.drama_node_tests.NextFestivalTest.TunableFactory, 
     'nearby_floor_feature':world.floor_feature_test.NearbyFloorFeatureTest.TunableFactory, 
     'notebook_categories_test':NotebookCategoriesTest.TunableFactory, 
     'occult_form_availability':OccultFormAvailabilityTest.TunableFactory, 
     'object_connectivity':objects.object_tests.ObjectConnectivityTest.TunableFactory, 
     'object_criteria':objects.object_tests.ObjectCriteriaTest.TunableFactory, 
     'object_definition_criteria':objects.object_tests.ObjectDefinitionCriteriaTest.TunableFactory, 
     'object_environment_score':objects.object_tests.ObjectEnvironmentScoreTest.TunableFactory, 
     'object_has_no_children':objects.object_tests.ObjectHasNoChildrenTest.TunableFactory, 
     'object_ownership':objects.object_tests.ObjectOwnershipTest.TunableFactory, 
     'object_pair_id_chance':objects.object_tests.ObjectIdPairTest.TunableFactory, 
     'object_preference_test':traits.preference_tests.ObjectPreferenceTest.TunableFactory, 
     'object_purchase_test':objects.object_tests.ObjectPurchasedTest.TunableFactory, 
     'object_spawn_firemeter':objects.object_tests.ObjectSpawnFiremeterTest.TunableFactory, 
     'object_relationship':objects.object_tests.ObjectRelationshipTest.TunableFactory, 
     'object_routable_surface':objects.object_tests.ObjectRoutableSurfaceTest.TunableFactory, 
     'object_fashion_outfit_prevalent_trend':objects.object_tests.ObjectFashionOutfitPrevalentTrendTest.TunableFactory, 
     'participant_running_interaction':event_testing.test_variants.ParticipantRunningInteractionTest.TunableFactory, 
     'object_type_relationship':relationships.relationship_tests.ObjectTypeRelationshipTest.TunableFactory, 
     'organization_membership_test':organizations.organization_tests.OrganizationMembershipTest.TunableFactory, 
     'outfit':OutfitTest.TunableFactory, 
     'outfit_body_types':OutfitBodyTypeTest.TunableFactory, 
     'party_age':event_testing.test_variants.TunablePartyAgeTest, 
     'party_size':event_testing.test_variants.TunablePartySizeTest, 
     'phone_silenced_test':event_testing.test_variants.PhoneSilencedTest.TunableFactory, 
     'pick_info_test':world.pick_tests.PickInfoTest.TunableFactory, 
     'player_population':sims.households.household_tests.PlayerPopulationTest.TunableFactory, 
     'pool_size_test':world.pool_size_test.PoolSizeTest.TunableFactory, 
     'portal_locked_test':event_testing.test_variants.PortalLockedTest.TunableFactory, 
     'posture':event_testing.test_variants.PostureTest.TunableFactory, 
     'caspart_tags_test':OutfitCASPartTagsTest.TunableFactory, 
     'outfit_prevalent_trend_tag_test':OutfitPrevalentTrendTagTest.TunableFactory, 
     'preferred_body_type_level':PreferredBodyTypeLevelTest.TunableFactory, 
     'pregnancy':sims.sim_info_tests.PregnancyTest.TunableFactory, 
     'rabbit_hole':RabbitHoleTest.TunableFactory, 
     'ranked_statistic':event_testing.statistic_tests.RankedStatThresholdTest.TunableFactory, 
     'region':event_testing.test_variants.RegionTest.TunableFactory, 
     'relationship':relationships.relationship_tests.TunableRelationshipTest, 
     'relationship_comparative':relationships.relationship_tests.ComparativeRelationshipTest.TunableFactory, 
     'relationship_modified_by_statistic':relationships.relationship_tests.RelationshipModifiedByStatisticTest.TunableFactory, 
     'relationship_bit_count_comparison':relationships.relationship_tests.RelationshipBitComparisonTest.TunableFactory, 
     'relationship_bit_count':relationships.relationship_tests.RelationshipBitCountTest.TunableFactory, 
     'relative_statistic':event_testing.statistic_tests.RelativeStatTest.TunableFactory, 
     'restaurant':restaurants.restaurant_tests.RestaurantTest.TunableFactory, 
     'restaurant_course_item_count':restaurants.restaurant_tests.RestaurantCourseItemCountTest.TunableFactory, 
     'restaurant_dining_spot':restaurants.restaurant_tests.DiningSpotTest.TunableFactory, 
     'restaurant_payment':restaurants.restaurant_tests.RestaurantPaymentTest.TunableFactory, 
     'retail_test':retail.retail_tests.RetailTest.TunableFactory, 
     'reward_part_test':event_testing.test_variants.RewardPartTest.TunableFactory, 
     'roommate_tests':RoommateTests.TunableFactory, 
     'routability':event_testing.test_variants.RoutabilityTest.TunableFactory, 
     'routing_slave_formation':routing.formation.formation_tests.RoutingSlaveTest.TunableFactory, 
     'satisfaction_points':sims.sim_info_tests.SatisfactionPointTest.TunableFactory, 
     'scenario_role':ScenarioRoleTest.TunableFactory, 
     'scenario_goal_completed_test':ScenarioGoalCompletedTest.TunableFactory, 
     'scenario_phase_triggered_test':ScenarioPhaseTriggeredTest.TunableFactory, 
     'scholarship_status_test':ScholarshipStatusTest.TunableFactory, 
     'season':SeasonTest.TunableFactory, 
     'selected_aspiration_test':aspirations.aspiration_tests.SelectedAspirationTest.TunableFactory, 
     'selected_aspiration_track_test':aspirations.aspiration_tests.SelectedAspirationTrackTest.TunableFactory, 
     'service_npc_hired_test':event_testing.test_variants.TunableServiceNpcHiredTest, 
     'sickness_test':sickness.sickness_tests.SicknessTest.TunableFactory, 
     'sim_info':sims.sim_info_tests.SimInfoTest.TunableFactory, 
     'sim_info_gameplay_options':sims.sim_info_tests.SimInfoGameplayOptionsTest.TunableFactory, 
     'sims_in_constraint':event_testing.constraint_tests.SimsInConstraintTests.TunableFactory, 
     'simoleon_value':event_testing.test_variants.TunableSimoleonsTest, 
     'situation_availability':event_testing.test_variants.TunableSituationAvailabilityTest, 
     'situation_count_test':event_testing.test_variants.TunableSituationCountTest, 
     'situation_goal_test':SituationGoalTest.TunableFactory, 
     'situation_in_joinable_state_test':event_testing.test_variants.TunableSituationInJoinableStateTest, 
     'situation_job_test':event_testing.test_variants.TunableSituationJobTest, 
     'situation_medal_test':event_testing.test_variants.TunableSituationMedalTest.TunableFactory, 
     'situation_object_comparison_test':objects.object_tests.SituationObjectComparisonTest.TunableFactory, 
     'situation_special_object_test':objects.object_tests.ScheduledSituationSpecialObjectTest.TunableFactory, 
     'situation_running_test':event_testing.test_variants.TunableSituationRunningTest, 
     'skill_all_unlocked_maxed_out':statistics.skill_tests.SkillAllUnlockedMaxedOut.TunableFactory, 
     'skill_has_unlocked_all':statistics.skill_tests.SkillHasUnlockedAll.TunableFactory, 
     'skill_tag':statistics.skill_tests.SkillTagThresholdTest.TunableFactory, 
     'skill_test':statistics.skill_tests.SkillRangeTest.TunableFactory, 
     'skill_dynamically_referenced_test':statistics.skill_tests.SkillDynamicallyReferencedTest.TunableFactory, 
     'skill_in_use':statistics.skill_tests.SkillInUseTest.TunableFactory, 
     'skin_tone':sims.sim_info_tests.SkinToneTest.TunableFactory, 
     'slot_test':TunableSlotTest, 
     'slot_test_related':RelatedSlotsTest.TunableFactory, 
     'social_boredom':event_testing.test_variants.SocialBoredomTest.TunableFactory, 
     'social_context':socials.social_tests.SocialContextTest.TunableFactory, 
     'social_group':event_testing.test_variants.SocialGroupTest.TunableFactory, 
     'sound_matches_stored_audio_component':SoundMatchesStoredAudioComponentTest.TunableFactory, 
     'state':event_testing.state_tests.TunableStateTest, 
     'state_white_black':event_testing.state_tests.WhiteBlackStateTest.TunableFactory, 
     'statistic':event_testing.statistic_tests.StatThresholdTest.TunableFactory, 
     'statistic_from_participant':event_testing.statistic_tests.StatFromParticipantThresholdTest.TunableFactory, 
     'statistic_in_category':event_testing.statistic_tests.TunableStatOfCategoryTest.TunableFactory, 
     'statistic_in_motion':event_testing.statistic_tests.StatInMotionTest.TunableFactory, 
     'statistic_is_equivalent':event_testing.statistic_tests.StatisticEquivalencyTest.TunableFactory, 
     'stored_object_info':sims.sim_info_tests.StoredObjectInfoTest.TunableFactory, 
     'stored_object_info_existence':sims.sim_info_tests.StoredObjectInfoExistenceTest.TunableFactory, 
     'street_civic_policy_test':StreetCivicPolicyTest.TunableFactory, 
     'style_active':StyleActiveTest.TunableFactory, 
     'swim_location':sims.swim_location_test.SwimLocationTest.TunableFactory, 
     'teleport_cost_test':TeleportCostTest.TunableFactory, 
     'test_based_score_threshold':event_testing.test_based_score_threshold.TunableTestBasedScoreThresholdTest, 
     'test_set_reference':lambda**__: sims4.tuning.tunable.TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
       class_restrictions=('TestSetInstance', ),
       pack_safe=True), 
     'time_until_festival':drama_scheduler.drama_node_tests.TimeUntilFestivalTest.TunableFactory, 
     'topic':event_testing.test_variants.TunableTopicTest, 
     'total_event_simoleons_earned':event_testing.test_variants.TunableTotalSimoleonsEarnedTest, 
     'total_time_played':event_testing.test_variants.TunableTotalTimePlayedTest, 
     'trait':sims.sim_info_tests.TraitTest.TunableFactory, 
     'trait_comparison':sims.sim_info_tests.TraitComparisonTest.TunableFactory, 
     'travel_group':travel_group.travel_group_tests.TravelGroupTest.TunableFactory, 
     'university_enrollment_test':UniversityEnrollmentTest.TunableFactory, 
     'university_classroom':UniversityClassroomTest.TunableFactory, 
     'university_housing_configuration_test':UniversityHousingConfigurationTest.TunableFactory, 
     'university_professor_test':UniversityProfessorTest.TunableFactory, 
     'university_test':UniversityTests.TunableFactory, 
     'unlock_earned':event_testing.test_variants.TunableUnlockedTest, 
     'unlock_tracker':sims.unlock_tracker_tests.UnlockTrackerTest.TunableFactory, 
     'unlock_tracker_amount':sims.unlock_tracker_tests.UnlockTrackerAmountTest.TunableFactory, 
     'user_facing_situation_running_test':event_testing.test_variants.TunableUserFacingSituationRunningTest, 
     'user_running_interaction':event_testing.test_variants.UserRunningInteractionTest.TunableFactory, 
     'utilities':UtilityTest.TunableFactory, 
     'utilities_component':UtilitiesComponentTest.TunableFactory, 
     'venue_availability':world.world_tests.VenueAvailabilityTest.TunableFactory, 
     'venue_civic_policy_test':venue_civic_policy_tests.VenueCivicPolicyTest.TunableFactory, 
     'vet_clinic_tests':vet.vet_clinic_tests.VetTest.TunableFactory, 
     'visitation_rights':event_testing.test_variants.RequiresVisitationRightsTest.TunableFactory, 
     'wading_interval_test':WadingIntervalTest.TunableFactory, 
     'walkstyle_cost':WalkstyleCostTest.TunableFactory, 
     'weather_forecast_override':WeatherForecastOverrideTest.TunableFactory, 
     'weather':WeatherTest.TunableFactory, 
     'weather_type':WeatherTypeTest.TunableFactory, 
     'whim':WhimTest.TunableFactory, 
     'wildlife_encounter_by_group':WildlifeEncounterTestByGroup.TunableFactory, 
     'zone':zone_tests.ZoneTest.TunableFactory}

    @staticmethod
    @cached(maxsize=None)
    def cached_tunable_test(factory, locked_args):
        return factory(locked_args=locked_args)

    def __init__(self, description='A single tunable test.', test_locked_args={}, **kwargs):
        kwargs.update(((test_name, TunableTestVariant.cached_tunable_test(test_factory, frozendict(test_locked_args))) for test_name, test_factory in TunableTestVariant.TEST_VARIANTS.items()))
        (super().__init__)(description=description, **kwargs)


class CompoundTestList(list):
    __slots__ = ()

    def __repr__(self):
        result = super().__repr__()
        return sims4.repr_utils.standard_repr(self, result)

    def run_tests(self, resolver, skip_safe_tests=False, search_for_tooltip=False):
        if search_for_tooltip:
            group_result = event_testing.results.TestResult.TRUE
            for test_group in self:
                result = event_testing.results.TestResult(True)
                failed_result = None
                for test in test_group:
                    if skip_safe_tests:
                        if test.safe_to_skip:
                            continue
                    result &= resolver(test)
                    if result:
                        continue
                    if group_result:
                        group_result = result
                    if result.tooltip is not None:
                        if failed_result is None:
                            failed_result = result
                    else:
                        failed_result = None
                        break

                if failed_result is not None:
                    group_result = failed_result
                if result:
                    return result

            return group_result
        result = event_testing.results.TestResult.TRUE
        for test_group in self:
            for test in test_group:
                if skip_safe_tests:
                    if test.safe_to_skip:
                        result = event_testing.results.TestResult.TRUE
                        continue
                result = resolver(test)
                if not result:
                    break

            if result:
                break

        return result


class CompoundTestListLoadingMixin(sims4.tuning.tunable.TunableList):

    def load_etree_node(self, node, source, expect_error):
        value = super().load_etree_node(node, source, expect_error)
        if value is not None:
            return CompoundTestList(value)


class _TunableTestSetBase(CompoundTestListLoadingMixin):
    DEFAULT_LIST = CompoundTestList()

    def __init__(self, description=None, callback=None, test_locked_args={}, **kwargs):
        if description is None:
            description = '\n                A list of tests groups.  At least one must pass all its sub-\n                tests to pass the TestSet.\n                \n                ORs of ANDs\n                '
        (super().__init__)(description=description, callback=_get_debug_loaded_tuning_callbak(self._on_tunable_loaded_callback, callback), 
         tunable=sims4.tuning.tunable.TunableList(description='\n                             A list of tests.  All of these must pass for the\n                             group to pass.\n                             ',
  tunable=TunableTestVariant(test_locked_args=test_locked_args)), **kwargs)
        self.cache_key = '{}_{}'.format('TunableTestSet', self._template.cache_key)

    def _on_tunable_loaded_callback(self, instance_class, tunable_name, source, value):
        for test_set in value:
            _verify_tooltip_tuning(instance_class, tunable_name, source, test_set)


class TunableTestSet(_TunableTestSetBase, is_fragment=True):

    def __init__(self, **kwargs):
        (super().__init__)(test_locked_args={'tooltip': None}, **kwargs)


class TunableTestSetWithTooltip(_TunableTestSetBase, is_fragment=True):

    def __init__(self, **kwargs):
        (super().__init__)(test_locked_args={}, **kwargs)


class TestList(list):
    __slots__ = ('_failfast_tests', )

    def __init__(self, iterable=()):
        super().__init__(iterable)
        self._failfast_tests = list(self)

    def __repr__(self):
        result = super().__repr__()
        return sims4.repr_utils.standard_repr(self, result)

    def run_tests(self, resolver, skip_safe_tests=False, search_for_tooltip=False):
        if search_for_tooltip:
            result = event_testing.results.TestResult.TRUE
            failed_result = None
            for test in self:
                if skip_safe_tests:
                    if test.safe_to_skip:
                        continue
                result &= resolver(test)
                if result:
                    continue
                if result.tooltip is not None:
                    if failed_result is None:
                        failed_result = result
                else:
                    failed_result = None
                    break

            if failed_result is not None:
                result = failed_result
            return result
        test_list = self._failfast_tests
        for i, test in enumerate(test_list):
            if skip_safe_tests:
                if test.safe_to_skip:
                    continue
                else:
                    result = resolver(test)
                    if result or test.allow_failfast_tests and i != 0:
                        del test_list[i]
                        test_list.insert(0, test)
                return result

        return event_testing.results.TestResult.TRUE


class TestListLoadingMixin(sims4.tuning.tunable.TunableList):

    def load_etree_node(self, node, source, expect_error):
        value = super().load_etree_node(node, source, expect_error)
        if value is not None:
            return TestList(value)


class TunableGlobalTestSet(TestListLoadingMixin, is_fragment=True):
    DEFAULT_LIST = TestList()

    def __init__(self, description=None, callback=None, **kwargs):
        if description is None:
            description = 'A list of tests.  All tests must succeed to pass the TestSet.'
        (super().__init__)(description=description, tunable=TunableTestVariant(), 
         callback=_get_debug_loaded_tuning_callbak(self._on_tunable_loaded_callback, callback), **kwargs)
        self.cache_key = '{}_{}'.format('TunableGlobalTestSet', self._template.cache_key)

    def _on_tunable_loaded_callback(self, instance_class, tunable_name, source, value):
        test_with_tooltip = None
        for test in value:
            if not hasattr(test, 'tooltip'):
                for sub_test in itertools.chain.from_iterable(test.test):
                    sub_tooltip = getattr(sub_test, 'tooltip', None)
                    if sub_tooltip is not None:
                        tooltip = sub_tooltip
                        break
                else:
                    continue

            else:
                tooltip = test.tooltip
            if tooltip is None:
                if test_with_tooltip is not None:
                    test_name = getattr(test_with_tooltip[0], '__name__', type(test_with_tooltip[0]).__name__)
                    logger.error('TestSet in {} has a test ({}) which specifies a tooltip (0x{:x}) which precedes tests without tooltips.', instance_class.__name__, test_name, test_with_tooltip[1]._string_id)
                    break
            else:
                test_with_tooltip = (
                 test, tooltip)

        _verify_tooltip_tuning(instance_class, tunable_name, source, value)
        test_with_tooltip = None
        for test in value:
            if not hasattr(test, 'tooltip'):
                for sub_test in itertools.chain.from_iterable(test.test):
                    sub_tooltip = getattr(sub_test, 'tooltip', None)
                    if sub_tooltip is not None:
                        tooltip = sub_tooltip
                        break
                else:
                    continue

            else:
                tooltip = test.tooltip
            if tooltip is None:
                if test_with_tooltip is not None:
                    test_name = getattr(test_with_tooltip[0], '__name__', type(test_with_tooltip[0]).__name__)
                    logger.error('TestSet in {} has a test ({}) which specifies a tooltip (0x{:x}) which precedes tests without tooltips.', instance_class.__name__, test_name, test_with_tooltip[1]._string_id)
                    break
            else:
                test_with_tooltip = (
                 test, tooltip)


class TestSetInstance(metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    INSTANCE_TUNABLES = {'test':TunableTestSetWithTooltip(), 
     'invert_test':sims4.tuning.tunable.OptionalTunable(description='\n            If enabled, the results of running the test(s) will be negated\n            ',
       tunable=sims4.tuning.tunable.TunableTuple(description='\n                Properties that are only used if the results of the test are inverted\n                ',
       tooltip=sims4.tuning.tunable.OptionalTunable(description='\n                    If enabled, the provided tooltip will be the failure message in the \n                    case where the test set passes, but inversion is enabled, so the \n                    end result is failure. \n            \n                    We do not propagate a tooltip when tests pass, only failed tests\n                    ',
       tunable=TunableLocalizedStringFactory(description='\n                        Tooltip to show when a test passes, but has been inverted to fail\n                        '))))}
    expected_kwargs = (
     (
      'resolver', event_testing.resolver.RESOLVER_PARTICIPANT),)
    participants_for_early_testing = None

    def __new__(cls, resolver, **kwargs):
        result = cls.test.run_tests(resolver, resolver.skip_safe_tests, resolver.search_for_tooltip)
        if result:
            if cls.invert_test is not None:
                return event_testing.results.TestResult(False, 'Tests passed, but result was inverted', tooltip=(cls.invert_test.tooltip),
                  icon=(result.icon),
                  influence_by_active_mood=(result.influence_by_active_mood))
        elif cls.invert_test is not None:
            return event_testing.results.TestResult.TRUE
        return result

    @classmethod
    def supports_early_testing(cls):
        return True

    @classmethod
    def has_tooltip(cls):
        return any((test.has_tooltip() for test in itertools.chain.from_iterable(cls.test)))

    @sims4.utils.flexproperty
    def safe_to_skip(cls, inst):
        return False

    @sims4.utils.flexmethod
    def get_expected_args(cls, inst):
        return dict(cls.expected_kwargs)

    @property
    def allow_failfast_tests(self):
        return True