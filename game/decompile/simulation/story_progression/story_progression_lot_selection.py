# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_lot_selection.py
# Compiled at: 2022-03-10 20:35:10
# Size of source mod 2**32: 8560 bytes
import services
from filters.neighborhood_population_service import HouseholdPopulationData
from sims.sim_info_types import Age
from sims4.tuning.geometric import TunableCurve, TunableWeightedUtilityCurve
from sims4.tuning.tunable import TunableMapping, TunableRegionDescription, Tunable, TunableRange
from world.region import get_region_description_id_from_zone_id

class StoryProgressionLotSelection:
    REGION_TO_HOUSEHOLD_POPULATION_DATA = TunableMapping(description='\n        Mapping of Region Description ID to household population data.  This is\n        used to fill households for the different type of regions.\n        ',
      key_name='Region Description',
      key_type=TunableRegionDescription(pack_safe=True),
      value_name='Household Population Data',
      value_type=(HouseholdPopulationData.TunableFactory()))
    NUM_BEDS_TO_IDEAL_HOUSEHOLD_CURVE = TunableMapping(description='\n        Based on the number of beds and the number of sims in the household, a\n        multiplier will be applied to the household to determine if household\n        will be selected and added to zone.\n        ',
      key_name='Num Beds',
      key_type=Tunable(tunable_type=int,
      default=1),
      value_name='Ideal Household Curve',
      value_type=TunableCurve(x_axis_name='num_sim_in_household',
      y_axis_name='bonus_multiplier'))
    RELATIONSHIP_DEPTH_WEIGHT = Tunable(description='\n        Multiplier used to modify relationship depth to determine how\n        important depth is in weight.  The higher the multiplier the\n        more relationship depth is added to weight score.  The lower the\n        weight the less likely household will be moved in.\n        ',
      tunable_type=float,
      default=0.5)
    RELATIONSHIP_TRACK_MULTIPLIER = Tunable(description='\n        Multiply the number of tracks by this multiplier to provide an\n        additional score to determine if household should be moved in. The\n        higher the multiplier the more the number of tracks bonus is added to\n        weight.  The lower the weight the less likely household will be moved\n        in.\n        ',
      tunable_type=float,
      default=2)
    RELATIONSHIP_UTILITY_CURVE = TunableWeightedUtilityCurve(description='\n        Based on the relationship score for a household apply a multiplier to\n        weight for determining score for moving household in.\n        ',
      x_axis_name='overall_score_for_household',
      y_axis_name='multiplier_to_apply')
    KID_TO_KID_BED_MULTIPLIER = TunableRange(description='\n        When trying to populate a lot if lot has a kids bed and household has a\n        kid in it.  This multiplier will be applied to the weight of household\n        when selecting household to move in.\n        ',
      tunable_type=float,
      default=1,
      minimum=1)
    SIGNIFICANT_OTHER_MULTIPLIER = TunableRange(description='\n        When trying to populate a lot and if lot has a double bed and household\n        contains a pair of sims that are considered significant other.  This\n        multiplier will be applied to the weight of household when selecting\n        household to move in.\n        ',
      tunable_type=float,
      default=1,
      minimum=1)

    @classmethod
    def get_household_templates_and_bed_data(cls, zone_id):
        total_beds = 0
        lot_has_double_bed = False
        lot_has_kid_bed = False
        persistence_service = services.get_persistence_service()
        zone_data = persistence_service.get_zone_proto_buff(zone_id)
        household_population_data = cls.REGION_TO_HOUSEHOLD_POPULATION_DATA.get(get_region_description_id_from_zone_id(zone_id))
        if household_population_data is None:
            return (
             total_beds, lot_has_double_bed, lot_has_kid_bed)
            if zone_data.gameplay_zone_data.HasField('bed_info_data'):
                total_beds = zone_data.gameplay_zone_data.bed_info_data.num_beds
                lot_has_double_bed = zone_data.gameplay_zone_data.bed_info_data.double_bed_exist
                lot_has_kid_bed = zone_data.gameplay_zone_data.bed_info_data.kid_bed_exist
                if total_beds == 0:
                    total_beds = zone_data.gameplay_zone_data.bed_info_data.alternative_sleeping_spots
        else:
            house_description_id = persistence_service.get_house_description_id(zone_id)
            household_data = household_population_data.household_description_to_lot_data.get(house_description_id)
            if household_data:
                total_beds = household_data.total_beds
                lot_has_double_bed = household_data.has_double_beds
                lot_has_kid_bed = household_data.has_kids_beds
        return (
         total_beds, lot_has_double_bed, lot_has_kid_bed)

    @classmethod
    def get_household_weight(cls, household, total_beds, lot_has_double_beds, lot_has_kid_beds):
        if not household.available_to_populate_zone():
            return 0
        else:
            num_sims = len(household)
            if not num_sims:
                return 0
                nums_sims_to_weight_bonus = cls.NUM_BEDS_TO_IDEAL_HOUSEHOLD_CURVE.get(total_beds)
                if nums_sims_to_weight_bonus is not None:
                    weight = nums_sims_to_weight_bonus.get(num_sims)
            else:
                weight = 1
        if weight <= 0:
            return 0
        household_has_married_sims = False
        household_has_kids = False
        total_household_relationship_weight = 0
        sim_info_manager = services.sim_info_manager()
        for sim_info in household:
            if lot_has_double_beds:
                spouse_sim_id = sim_info.spouse_sim_id
                if not spouse_sim_id:
                    if household.get_sim_info_by_id(spouse_sim_id):
                        household_has_married_sims = True
            if lot_has_kid_beds:
                if sim_info.age <= Age.TEEN:
                    household_has_kids = True
            total_sim_info_weight = 0
            for relationship in sim_info.relationship_tracker:
                target_sim_info = sim_info_manager.get(relationship.get_other_sim_id(sim_info.sim_id))
                if target_sim_info is not None and target_sim_info.is_player_sim:
                    total_sim_info_weight = relationship.get_relationship_depth(sim_info.sim_id) * cls.RELATIONSHIP_DEPTH_WEIGHT
                    total_sim_info_weight += len(relationship.relationship_track_tracker) * cls.RELATIONSHIP_TRACK_MULTIPLIER

            total_household_relationship_weight += total_sim_info_weight

        total_household_relationship_weight /= num_sims
        if cls.RELATIONSHIP_UTILITY_CURVE is not None:
            weight *= cls.RELATIONSHIP_UTILITY_CURVE.get(total_household_relationship_weight)
        if household_has_kids:
            weight *= cls.KID_TO_KID_BED_MULTIPLIER
        if household_has_married_sims:
            weight *= cls.SIGNIFICANT_OTHER_MULTIPLIER
        return weight

    @classmethod
    def get_available_households(cls, possible_households, total_beds, lot_has_double_beds, lot_has_kid_beds):
        weighted_households = []
        for household in possible_households:
            weight = cls.get_household_weight(household, total_beds, lot_has_double_beds, lot_has_kid_beds)
            weighted_households.append((weight, household.id))

        return weighted_households