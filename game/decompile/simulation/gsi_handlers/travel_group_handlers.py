# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\travel_group_handlers.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 5028 bytes
import services, sims4.hash_util
from gsi_handlers.gsi_utils import parse_filter_to_list
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
from sims4.resources import get_resource_key, Types, get_debug_name
from world.region import get_region_description_id_from_zone_id
travel_groups_schema = GsiGridSchema(label='Travel Groups')
travel_groups_schema.add_field('groupId', label='Group Id', width=1, unique_field=True)
travel_groups_schema.add_field('numSims', label='# Sims', width=1)
travel_groups_schema.add_field('zoneId', label='Zone Id', width=1)
travel_groups_schema.add_field('lot', label='Lot', width=3)
travel_groups_schema.add_field('world', label='World', width=3)
travel_groups_schema.add_field('region', label='Region', width=3)
travel_groups_schema.add_field('startTime', label='Start Time', width=2, type=(GsiFieldVisualizers.TIME))
travel_groups_schema.add_field('duration', label='Vacation Duration', width=2)
travel_groups_schema.add_field('playerGroup', label='Is Player Group', width=1)
travel_groups_schema.add_field('groupType', label='Group Type', width=2)
travel_groups_schema.add_field('situation', label='Situation', width=4)
travel_groups_schema.add_filter('played')
travel_groups_schema.add_filter('npc')
with travel_groups_schema.add_has_many('members', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('zoneId', label='Zone Id', width=1)
    sub_schema.add_field('sim', label='Sim', width=2)
    sub_schema.add_field('lot', label='Lot', width=2)
    sub_schema.add_field('world', label='World', width=2)
    sub_schema.add_field('region', label='Region', width=2)
    sub_schema.add_field('household', label='Household', width=4)

@GsiHandler('travel_groups', travel_groups_schema)
def generate_travel_groups_data(*_, filter=None, **__):
    filter_list = parse_filter_to_list(filter)
    all_group_data = []
    persistance_service = services.get_persistence_service()

    def get_region_world_and_lot_info(zone_id):
        region_desc_id = get_region_description_id_from_zone_id(zone_id)
        zone_data = persistance_service.get_zone_proto_buff(zone_id)
        world_desc_id = services.get_world_description_id(zone_data.world_id)
        lot_desc_id = zone_data.lot_description_id
        return (get_resource_key(region_desc_id, Types.REGION_DESCRIPTION),
         get_resource_key(world_desc_id, Types.WORLD_DESCRIPTION),
         get_resource_key(lot_desc_id, Types.LOT_DESCRIPTION))

    travel_group_manager = services.travel_group_manager()
    if travel_group_manager is None:
        return all_group_data
    for travel_group in tuple(travel_group_manager.values()):
        if not (filter_list is None or 'played' in filter_list and travel_group.played or 'npc' in filter_list):
            zone_id = travel_group.zone_id
            region, world, lot = get_region_world_and_lot_info(zone_id)
            group_entry = {'groupId':str(travel_group.id), 
             'numSims':str(len(travel_group)), 
             'zoneId':hex(zone_id), 
             'lot':get_debug_name(lot, table_type=sims4.hash_util.KEYNAMEMAPTYPE_OBJECTINSTANCES), 
             'world':get_debug_name(world, table_type=sims4.hash_util.KEYNAMEMAPTYPE_OBJECTINSTANCES), 
             'region':get_debug_name(region, table_type=sims4.hash_util.KEYNAMEMAPTYPE_OBJECTINSTANCES), 
             'startTime':str(travel_group.create_timestamp), 
             'duration':str(travel_group.duration_time_span) if travel_group.end_timestamp else 'Infinite', 
             'playerGroup':str(travel_group.played), 
             'groupType':str(travel_group.group_type), 
             'situation':str(travel_group.situation)}
            group_members_data = []
            for member in travel_group:
                sim_zone_id = member.zone_id
                member_data = {'sim':str(member), 
                 'zoneId':hex(sim_zone_id), 
                 'household':str(member.household)}
                if sim_zone_id:
                    sim_region, sim_world, sim_lot = get_region_world_and_lot_info(sim_zone_id)
                    member_data['lot'] = get_debug_name(sim_lot, table_type=(sims4.hash_util.KEYNAMEMAPTYPE_OBJECTINSTANCES))
                    member_data['world'] = get_debug_name(sim_world, table_type=(sims4.hash_util.KEYNAMEMAPTYPE_OBJECTINSTANCES))
                    member_data['region'] = get_debug_name(sim_region, table_type=(sims4.hash_util.KEYNAMEMAPTYPE_OBJECTINSTANCES))
                group_members_data.append(member_data)

            group_entry['members'] = group_members_data
            all_group_data.append(group_entry)

    return all_group_data