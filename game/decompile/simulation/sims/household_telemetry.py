# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\household_telemetry.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 5683 bytes
from sims.household_enums import HouseholdChangeOrigin
from world.region import get_region_description_id_from_zone_id
import services, sims4.telemetry, telemetry_helper
TELEMETRY_GROUP_STORY_PROGRESSION = 'STRY'
TELEMETRY_GROUP_HOUSEHOLD = 'HOHO'
TELEMETRY_HOOK_PLAYED_SIM_INFO_WORLD = 'PSIW'
TELEMETRY_HOOK_TOWNIE_SIM_INFO_WORLD = 'TSIW'
TELEMETRY_HOOK_REGION_ID = 'rdid'
TELEMETRY_HOOK_PLAYED_HOUSEHOLD_COUNT = 'rphc'
TELEMETRY_HOOK_PLAYED_SIM_INFO_COUNT = 'rsic'
TELEMETRY_HOOK_OCCUPIED_LOT_COUNT = 'rolc'
TELEMETRY_HOOK_TOTAL_LOT_COUNT = 'rtlc'
TELEMETRY_HOOK_TOWNIE_HOUSEHOLD_COUNT = 'rthc'
TELEMETRY_HOOK_TOWNIE_SIM_INFOS_COUNT = 'rtsi'
TELEMETRY_HOOK_HOUSEHOLD_SIM_ADDED = 'ADSI'
TELEMETRY_HOOK_SIM_AGE = 'sage'
TELEMETRY_HOOK_SIM_ID = 'simi'
TELEMETRY_HOOK_SIM_HOUSEHOLD = 'hous'
TELEMETRY_HOOK_REASON = 'resn'
household_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_HOUSEHOLD)
story_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_STORY_PROGRESSION)

class HouseholdRegionTelemetryData:

    def __init__(self, region_description_id=None):
        self.region_description_id = region_description_id
        self.played_household_count = 0
        self.played_sim_info_count = 0
        self.region_occupied_lot_count = 0
        self.region_total_lot_count = None
        self.townie_household_count = 0
        self.townie_sim_info_count = 0

    @property
    def is_townie_data(self):
        return self.region_description_id == 0

    def _send_telemetry(self):
        telemetry_hook = TELEMETRY_HOOK_TOWNIE_SIM_INFO_WORLD if self.is_townie_data else TELEMETRY_HOOK_PLAYED_SIM_INFO_WORLD
        with telemetry_helper.begin_hook(story_writer, telemetry_hook) as (hook):
            hook.write_int(TELEMETRY_HOOK_REGION_ID, self.region_description_id)
            hook.write_int(TELEMETRY_HOOK_PLAYED_HOUSEHOLD_COUNT, self.played_household_count)
            hook.write_int(TELEMETRY_HOOK_PLAYED_SIM_INFO_COUNT, self.played_sim_info_count)
            if self.is_townie_data:
                hook.write_int(TELEMETRY_HOOK_TOWNIE_HOUSEHOLD_COUNT, self.townie_household_count)
                hook.write_int(TELEMETRY_HOOK_TOWNIE_SIM_INFOS_COUNT, self.townie_sim_info_count)
            else:
                hook.write_int(TELEMETRY_HOOK_OCCUPIED_LOT_COUNT, self.region_occupied_lot_count)
                hook.write_int(TELEMETRY_HOOK_TOTAL_LOT_COUNT, self.region_total_lot_count)

    @classmethod
    def send_household_region_telemetry(cls):
        household_manager = services.household_manager()
        if household_manager is None:
            return
        persistence_service = services.get_persistence_service()
        per_region_data = dict()
        for household in household_manager.values():
            is_townie_household = household.home_zone_id == 0
            region_description_id = 0 if is_townie_household else get_region_description_id_from_zone_id(household.home_zone_id)
            region_data = per_region_data.get(region_description_id, None)
            if region_data is None:
                region_data = HouseholdRegionTelemetryData(region_description_id=region_description_id)
                per_region_data[region_description_id] = region_data
            if household.is_played_household:
                region_data.played_household_count += 1
                region_data.played_sim_info_count += len(household)
            if is_townie_household:
                region_data.townie_household_count += 1
                region_data.townie_sim_info_count += len(household)
            else:
                region_data.region_occupied_lot_count += 1
            if region_data.region_total_lot_count is None:
                neighborhood_proto = persistence_service.get_neighborhood_proto_buf_from_zone_id(household.home_zone_id)
                region_data.region_total_lot_count = len(neighborhood_proto.lots)

        for region_data in per_region_data.values():
            region_data._send_telemetry()


def send_sim_added_telemetry(sim_info, reason=HouseholdChangeOrigin.UNKNOWN):
    with telemetry_helper.begin_hook(household_writer, TELEMETRY_HOOK_HOUSEHOLD_SIM_ADDED, sim_info=sim_info) as (hook):
        hook.write_int(TELEMETRY_HOOK_SIM_AGE, sim_info.age)
        hook.write_int(TELEMETRY_HOOK_REASON, reason)