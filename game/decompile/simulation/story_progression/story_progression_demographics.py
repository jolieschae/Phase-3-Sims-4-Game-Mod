# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_demographics.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 11709 bytes
import services
from event_testing.resolver import SingleSimResolver
from event_testing.tests import TunableTestSet
from filters.neighborhood_population_service import NeighborhoodPopulationService
from gsi_handlers.story_progression_handlers import GSIStoryProgressionDemographicData
from sims.culling.culling_tuning import CullingTuning
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, Tunable
from story_progression.story_progression_lot_selection import StoryProgressionLotSelection
from venues.venue_enums import VenueTypes
from world.region import get_region_description_id_from_zone_id

class BaseDemographicFunction(HasTunableSingletonFactory, AutoFactoryInit):

    def __call__(self, gsi_data, **kwargs):
        raise NotImplementedError


class SimTestDemographicFunction(BaseDemographicFunction):
    FACTORY_TUNABLES = {'initial_tests':TunableTestSet(description='\n            The initial set of tests that are run in order to determine which Sims\n            should this demographic test check against.  Leave this empty to test\n            against all Sims.\n            Example: If we are trying to figure out the rate of employment for Teens.\n            A test to check if the Sim Info is a Teen should be here.\n            '), 
     'demographic_tests':TunableTestSet(description='\n            A set of tests that the Sim must pass to actually be in consideration.\n            These tests will be run after the initial tests so the final demographic\n            number will end up being:\n            number of sims that pass demographic tests/number of sims that pass initial tests\n            ')}

    def __call__(self, gsi_data, **kwargs):
        sim_infos_to_check = []
        sim_infos_that_pass = []
        for sim_info in services.sim_info_manager().values():
            if gsi_data is not None:
                demographic_gsi_data = GSIStoryProgressionDemographicData()
                demographic_gsi_data.item_id = sim_info.id
                demographic_gsi_data.item_name = sim_info.full_name
                gsi_data.demographic_data.append(demographic_gsi_data)
            resolver = SingleSimResolver(sim_info)
            result = self.initial_tests.run_tests(resolver)
            if not result:
                if gsi_data is not None:
                    demographic_gsi_data.reason = 'Failed Initial Tests: ' + result.reason
                    continue
            sim_infos_to_check.append(sim_info)
            result = self.demographic_tests.run_tests(resolver)
            if not result:
                if gsi_data is not None:
                    demographic_gsi_data.reason = 'Failed Demographic Tests: ' + result.reason
                    continue
                sim_infos_that_pass.append(sim_info)

        demographic_value = len(sim_infos_that_pass) / len(sim_infos_to_check) if len(sim_infos_to_check) != 0 else None
        return (demographic_value, sim_infos_that_pass, None, None)


class TotalSimDemographicFunction(BaseDemographicFunction):

    def __call__(self, gsi_data, **kwargs):
        sim_infos = list(services.sim_info_manager().values())
        total_sim_cap = CullingTuning.total_sim_cap
        demographic_value = len(sim_infos) / total_sim_cap if total_sim_cap != 0 else None
        return (demographic_value, sim_infos, None, None)


class ResidentialLotDemographicFunction(BaseDemographicFunction):
    FACTORY_TUNABLES = {'check_filled_lots': Tunable(description='\n            If checked we will check the number of residential lots that have Sims who live on them\n            against the total number of residential lots with at least one bed or have a Sim living there, else we will\n            do the opposite and check the number of empty residential lots with at least one bed against the\n            number of total residential lots that have at least one bed or a Sim living there.\n            ',
                            tunable_type=bool,
                            default=False)}

    @classmethod
    def get_residential_lots_demographics(cls, gsi_data, neighborhood_proto_buff, check_filled_lots):
        households = []
        zones = []
        total_zones = []
        venue_manager = services.get_instance_manager(Types.VENUE)
        persistence_service = services.get_persistence_service()
        household_manager = services.household_manager()
        if neighborhood_proto_buff is None:
            neighborhoods_to_check = persistence_service.get_neighborhoods_proto_buf_gen()
        else:
            neighborhoods_to_check = (
             neighborhood_proto_buff,)
        for neighborhood_proto in neighborhoods_to_check:
            for lot_owner_info in neighborhood_proto.lots:
                if gsi_data is not None:
                    demographic_gsi_data = GSIStoryProgressionDemographicData()
                    if not check_filled_lots:
                        demographic_gsi_data.item_id = lot_owner_info.zone_instance_id
                        demographic_gsi_data.item_name = lot_owner_info.lot_name
                    gsi_data.demographic_data.append(demographic_gsi_data)
                venue_tuning = venue_manager.get(lot_owner_info.venue_key)
                if venue_tuning is not None:
                    if venue_tuning.venue_type != VenueTypes.RESIDENTIAL:
                        if gsi_data is not None:
                            demographic_gsi_data.reason = 'Lot is not residential.'
                            continue
                for lot_owner in lot_owner_info.lot_owner:
                    if lot_owner.household_id > 0:
                        household = household_manager.get(lot_owner.household_id)
                        if household is None:
                            continue
                        else:
                            total_zones.append(lot_owner_info.zone_instance_id)
                            if check_filled_lots:
                                if gsi_data is not None:
                                    demographic_gsi_data.item_id = lot_owner.household_id
                                    household = household_manager.get(lot_owner.household_id)
                                    demographic_gsi_data.item_name = household.name
                                households.append(lot_owner.household_id)
                                zones.append(lot_owner_info.zone_instance_id)
                            else:
                                if gsi_data is not None:
                                    demographic_gsi_data.reason = 'Lot has a household living on it.'
                        break
                else:
                    if lot_owner_info.lot_template_id == 0:
                        if gsi_data is not None:
                            demographic_gsi_data.reason = check_filled_lots or 'Lot has template id of 0.'
                            continue
                    zone_data = persistence_service.get_zone_proto_buff(lot_owner_info.zone_instance_id)
                    if zone_data.gameplay_zone_data.HasField('bed_info_data'):
                        total_beds = zone_data.gameplay_zone_data.bed_info_data.num_beds
                        if total_beds == 0:
                            total_beds = zone_data.gameplay_zone_data.bed_info_data.alternative_sleeping_spots
                    else:
                        house_description_id = persistence_service.get_house_description_id(lot_owner_info.zone_instance_id)
                        region_id = get_region_description_id_from_zone_id(lot_owner_info.zone_instance_id)
                        household_population_data = StoryProgressionLotSelection.REGION_TO_HOUSEHOLD_POPULATION_DATA.get(region_id)
                        if household_population_data is None:
                            if gsi_data is not None:
                                demographic_gsi_data.reason = check_filled_lots or f"There is no household population data in StoryProgressionLotSelection.REGION_TO_HOUSEHOLD_POPULATION_DATA for region: {region_id}"
                                continue
                        household_data = household_population_data.household_description_to_lot_data.get(house_description_id)
                        if not household_data:
                            if gsi_data is not None:
                                demographic_gsi_data.reason = check_filled_lots or 'There is no household templates in Household Description To Templates for zone.'
                                continue
                            total_beds = household_data.total_beds
                    if total_beds > 0:
                        total_zones.append(lot_owner_info.zone_instance_id)
                        check_filled_lots or zones.append(lot_owner_info.zone_instance_id)

        if not total_zones:
            return (None, None, None, None)
        demographic_value = len(zones) / len(total_zones) if len(total_zones) != 0 else None
        return (demographic_value, None, households, zones)

    def __call__(self, gsi_data, neighborhood_proto_buff=None):
        return self.get_residential_lots_demographics(gsi_data, neighborhood_proto_buff, self.check_filled_lots)