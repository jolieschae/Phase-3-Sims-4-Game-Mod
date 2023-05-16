# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\filters\neighborhood_population_service.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 18543 bytes
import operator, random
from event_testing.resolver import SingleSimResolver
from event_testing.tests import TunableTestSet
from filters.household_template import HouseholdTemplate
from sims.household_enums import HouseholdChangeOrigin
from sims.sim_info_types import Age
from sims4.service_manager import Service
from sims4.tuning.geometric import TunableCurve, TunableWeightedUtilityCurve
from sims4.tuning.tunable import TunableList, Tunable, TunableMapping, TunableTuple, AutoFactoryInit, HasTunableSingletonFactory, TunableRegionDescription, TunableHouseDescription, TunableRange, TunableWorldDescription
import clock, element_utils, elements, services, sims4.log
logger = sims4.log.Logger('NeighborhoodPopulation')
GENERATE_HOUSEHOLD_ID = 0

class _BasePopulationRequest:

    def __init__(self, account, num_to_fill, neighborhood_id, completion_callback):
        self._account = account
        self._num_to_fill = num_to_fill
        self._neighborhood_id = neighborhood_id
        self._completion_callback = completion_callback

    def _create_household_from_template_and_add_to_zone(self, household_template, neighborhood_proto, zone_id, creation_source: str='neigh_pop_service : Unknown', household_change_origin=HouseholdChangeOrigin.NEIGH_POP_SERVICE_UNKNOWN):
        household = household_template.create_household(zone_id, (self._account), creation_source=creation_source,
          household_change_origin=household_change_origin)
        self._move_household_into_zone(household, neighborhood_proto, zone_id)

    def _move_household_into_zone(self, household, neighborhood_proto, zone_id):
        household.move_into_zone(zone_id)

    def process_completed(self, result):
        if self._completion_callback is not None:
            self._completion_callback(result)


class _CreateHomelessHouseholdRequest(_BasePopulationRequest):

    def process_request_gen(self, timeline):
        households = [(template_data.weight, template_data.household_template) for template_data in NeighborhoodPopulationService.HOMELESS_HOUSEHOLD_TEMPLATES]
        if not households:
            return
        while self._num_to_fill > 0:
            household_template = sims4.random.weighted_random_item(households)
            self._create_household_from_template_and_add_to_zone(household_template, None, 0, creation_source='neigh_pop_service: homeless',
              household_change_origin=(HouseholdChangeOrigin.NEIGH_POP_SERVICE_HOMELESS))
            self._num_to_fill -= 1
            yield from element_utils.run_child(timeline, element_utils.sleep_until_next_tick_element())

        if False:
            yield None


class _FillRentableLotRequest(_BasePopulationRequest):
    CAN_RENT_TESTS = TunableTestSet(description='\n        A set of tests that must pass for a Sim to be able to rent a lot as either the leader or a member of the travel\n        group.\n        ')

    def __init__(self, *args, available_zone_ids=None, region_renting_data=None):
        (super().__init__)(*args)
        self._region_renting_data = region_renting_data
        self._available_zone_ids = available_zone_ids

    def _get_max_travel_group_size(self, zone_id):
        max_group_size = 0
        persistence_service = services.get_persistence_service()
        zone_data = persistence_service.get_zone_proto_buff(zone_id)
        if zone_data.gameplay_zone_data.HasField('bed_info_data'):
            total_beds = min(zone_data.gameplay_zone_data.bed_info_data.num_beds, max(self._region_renting_data.bed_count_to_travel_group_size.keys()))
            max_group_size_interval = self._region_renting_data.bed_count_to_travel_group_size.get(total_beds)
            max_group_size = max_group_size_interval.random_int() if max_group_size_interval is not None else 0
        else:
            house_description_id = persistence_service.get_house_description_id(zone_id)
            travel_group_size = self._region_renting_data.household_description_to_ideal_travel_group_size.get(house_description_id)
            if travel_group_size is None:
                return (0, 0)
            max_group_size = travel_group_size.random_int()
            total_beds = max_group_size
        return (max_group_size, total_beds)

    def _find_households_to_rent_lot(self):
        possible_travel_groups = []
        household_manager = services.household_manager()
        for household in household_manager.values():
            if household.hidden:
                continue
            if household.any_member_in_travel_group():
                continue
            sim_infos_that_can_lead_travel_group = []
            sim_infos_available_for_vacation = []
            for sim_info in household:
                if sim_info.is_instanced():
                    continue
                else:
                    resolver = SingleSimResolver(sim_info)
                    if not _FillRentableLotRequest.CAN_RENT_TESTS.run_tests(resolver):
                        continue
                    if sim_info.is_young_adult_or_older and sim_info.is_human:
                        sim_infos_that_can_lead_travel_group.append(sim_info)
                if not sim_info.is_baby:
                    sim_infos_available_for_vacation.append(sim_info)

            if sim_infos_that_can_lead_travel_group:
                possible_travel_groups.append((sim_infos_that_can_lead_travel_group, sim_infos_available_for_vacation))

        return possible_travel_groups

    def _send_sims_on_vacation(self, zone_id, sim_infos_to_send_to_vacation, duration):
        create_timestamp = services.time_service().sim_now
        end_timestamp = create_timestamp + clock.interval_in_sim_days(duration)
        travel_group_manager = services.travel_group_manager()
        travel_group_created = travel_group_manager.create_travel_group_and_rent_zone(sim_infos=sim_infos_to_send_to_vacation, zone_id=zone_id,
          played=False,
          create_timestamp=create_timestamp,
          end_timestamp=end_timestamp)
        if travel_group_created:
            for sim_info in sim_infos_to_send_to_vacation:
                sim_info.inject_into_inactive_zone(zone_id)

            return True
        return False

    def process_request_gen(self, timeline):
        if self._region_renting_data is None:
            return
        while self._num_to_fill > 0 and self._available_zone_ids:
            zone_id = random.choice(self._available_zone_ids)
            self._available_zone_ids.remove(zone_id)
            max_group_size, total_sleeping_spots = self._get_max_travel_group_size(zone_id)
            if max_group_size == 0 or total_sleeping_spots == 0:
                continue
            possible_travel_groups = self._find_households_to_rent_lot()
            if possible_travel_groups:
                sim_infos_that_can_lead_travel_group, sim_infos_available_for_vacation = random.choice(possible_travel_groups)
                sim_to_lead_group = random.choice(sim_infos_that_can_lead_travel_group)
                sim_infos_available_for_vacation.remove(sim_to_lead_group)
                random_sample_size = max_group_size - 1
                sim_infos_to_send_to_vacation = []
                if random_sample_size > 0:
                    if random_sample_size < len(sim_infos_available_for_vacation):
                        sim_infos_to_send_to_vacation = random.sample(sim_infos_available_for_vacation, random_sample_size)
                    else:
                        sim_infos_to_send_to_vacation = sim_infos_available_for_vacation
                sim_infos_to_send_to_vacation.append(sim_to_lead_group)
            else:
                household_template = self._region_renting_data.travel_group_size_to_household_template(max_group_size)
                if household_template is None:
                    continue
                household = household_template.create_household(zone_id, (self._account),
                  creation_source='neigh_pop_service:rentable_lot',
                  household_change_origin=(HouseholdChangeOrigin.NEIGH_POP_SERVICE_RENT))
                sim_infos_to_send_to_vacation = [sim_info for sim_info in household]
            if self._send_sims_on_vacation(zone_id, sim_infos_to_send_to_vacation, self._region_renting_data.duration.random_int()):
                self._num_to_fill -= 1
            yield from element_utils.run_child(timeline, element_utils.sleep_until_next_tick_element())

        if False:
            yield None


class TunableHouseholdTemplateWeightTuple(TunableTuple):

    def __init__(self, **kwargs):
        (super().__init__)(household_template=HouseholdTemplate.TunableReference(description='\n                Household template that will be created for neighborhood population\n                ',
  pack_safe=True), 
         weight=Tunable(description='\n                Weight of this template being chosen.\n                ',
  tunable_type=float,
  default=1), **kwargs)


class HouseholdPopulationData(AutoFactoryInit, HasTunableSingletonFactory):
    FACTORY_TUNABLES = {'household_description_to_templates':TunableMapping(description='\n            Mapping of House Description ID to household templates and weight.  This\n            is used to fill households for the different type of regions.\n            ',
       key_name='House Description',
       key_type=TunableHouseDescription(pack_safe=True),
       value_name='Household Templates',
       value_type=TunableList(tunable=(TunableHouseholdTemplateWeightTuple()))), 
     'household_description_to_lot_data':TunableMapping(description='\n            Mapping of House Description ID to household templates and weight.  This\n            is used to fill households for the different type of regions and acts\n            as the default if the player has not visited the lot before.\n            ',
       key_name='House Description',
       key_type=TunableHouseDescription(pack_safe=True),
       value_name='Household Templates',
       value_type=TunableTuple(description='\n                The default data used for this lot if the player has never visited it.\n                ',
       total_beds=TunableRange(description='\n                    The total number of beds on this lot.\n                    ',
       tunable_type=int,
       default=0,
       minimum=0),
       has_kids_beds=Tunable(description='\n                    If the lot has kids beds.\n                    ',
       tunable_type=bool,
       default=False),
       has_double_beds=Tunable(description='\n                    If the lot has double beds.\n                    ',
       tunable_type=bool,
       default=False)))}


class NeighborhoodPopulationService(Service):
    HOMELESS_HOUSEHOLD_TEMPLATES = TunableList(description='\n        A List of household templates that will be considered for homelesss\n        households.\n        ',
      tunable=(TunableHouseholdTemplateWeightTuple()))

    def __init__(self):
        self._requests = []
        self._processing_element_handle = None

    def _process_population_request_gen(self, timeline):
        while self._requests:
            request = self._requests.pop(0)
            try:
                yield from request.process_request_gen(timeline)
                request.process_completed(True)
            except GeneratorExit:
                raise
            except BaseException:
                request.process_completed(False)
                logger.exception('Exception raised while processing creating npc households')

            if self._requests:
                yield from element_utils.run_child(timeline, element_utils.sleep_until_next_tick_element())

        self._processing_element_handle = None
        if False:
            yield None

    def add_homeless_household_request(self, num_to_fill, completion_callback):
        account = self._get_account()
        if account is None:
            return False
        request = _CreateHomelessHouseholdRequest(account, num_to_fill, None, completion_callback)
        self._add_request(request)
        return True

    def add_rentable_lot_request(self, num_to_fill, neighborhood_id, completion_callback, available_zones, region_renting_data):
        account = self._get_account()
        if account is None:
            return False
        request = _FillRentableLotRequest(account, num_to_fill,
          neighborhood_id,
          completion_callback,
          available_zone_ids=available_zones,
          region_renting_data=region_renting_data)
        self._add_request(request)
        return True

    def _get_account(self):
        client = services.client_manager().get_first_client()
        if client.account is not None or client.household is not None:
            return client.account

    @property
    def is_processing_requests(self):
        return self._processing_element_handle or len(self._requests) > 0

    def _add_request(self, request):
        self._requests.append(request)
        if self._processing_element_handle is None:
            timeline = services.time_service().sim_timeline
            element = elements.GeneratorElement(self._process_population_request_gen)
            self._processing_element_handle = timeline.schedule(element)