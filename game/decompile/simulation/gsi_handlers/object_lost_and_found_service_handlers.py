# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\object_lost_and_found_service_handlers.py
# Compiled at: 2021-05-21 15:26:58
# Size of source mod 2**32: 4976 bytes
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
import services
olaf_service_objects_schema = GsiGridSchema(label='Object Lost & Found')
olaf_service_objects_schema.add_field('object', label='Object')
olaf_service_objects_schema.add_field('zone', label='Zone')
olaf_service_objects_schema.add_field('street', label='Street')
olaf_service_objects_schema.add_field('sim', label='Sim')
olaf_service_objects_schema.add_field('household', label='Household')
olaf_service_objects_schema.add_field('minutes_until_lost', label='Minutes Until Lost')
olaf_service_deleted_clone_schema = GsiGridSchema(label='Object Lost & Found/To Be Deleted')
olaf_service_deleted_clone_schema.add_field('object', label='Object')
olaf_service_deleted_clone_schema.add_field('zone', label='Zone')
olaf_service_deleted_clone_schema.add_field('street', label='Street')

def _olaf_zone_str(zone_id, zone):
    if zone:
        return '{}:{}'.format(str(zone), zone.lot.get_lot_name())
    return str(zone_id)


def _olaf_obj_str(zone, object_id):
    obj_str = str(object_id)
    if zone is not None:
        if zone.is_instantiated:
            obj = zone.object_manager.get(object_id)
            if obj:
                obj_str = str(obj)
    return obj_str


@GsiHandler('object_lost_and_found_service_objects', olaf_service_objects_schema)
def generate_object_lost_and_found_service_data(*args, zone_id: int=None, filter=None, **kwargs):
    lost_and_found = services.get_object_lost_and_found_service()
    zone_manager = services.get_zone_manager()
    sim_info_manager = services.sim_info_manager()
    household_manager = services.household_manager()
    if not (lost_and_found and zone_manager and sim_info_manager and household_manager):
        return []
    registered_objects = []
    for locator in lost_and_found.registered_object_locators:
        if zone_id is not None:
            if zone_id != locator.zone_id:
                continue
        zone = zone_manager.get(locator.zone_id)
        sim_str = str(locator.sim_id)
        sim_info = sim_info_manager.get(locator.sim_id)
        if sim_info:
            sim_str = '{}:{}'.format(str(sim_info), locator.sim_id)
        household_str = str(locator.household_id)
        household = household_manager.get(locator.household_id)
        if household:
            household_str = '{}:{}'.format(household.name, locator.household_id)
        time_elapsed = services.time_service().sim_now - locator.time_stamp
        time_remaining_until_lost = max(locator.time_before_lost - time_elapsed.in_minutes(), 0)
        registered_objects.append({'object':_olaf_obj_str(zone, locator.object_id), 
         'zone':_olaf_zone_str(locator.zone_id, zone), 
         'street':locator.open_street_id, 
         'sim':sim_str, 
         'household':household_str, 
         'minutes_until_lost':time_remaining_until_lost})

    return registered_objects


@GsiHandler('object_lost_and_found_service_clones', olaf_service_deleted_clone_schema)
def generate_olaf_service_deleted_clone_schema_data(*args, zone_id: int=None, filter=None, **kwargs):
    lost_and_found = services.get_object_lost_and_found_service()
    zone_manager = services.get_zone_manager()
    return lost_and_found and zone_manager or []
    clones_to_delete_by_zone = lost_and_found.clones_to_delete_by_zone
    clones_to_delete_by_street = lost_and_found.clones_to_delete_by_street
    clones_to_delete = []
    object_ids = set()
    for zone_id, objects in clones_to_delete_by_zone.items():
        if zone_id is not None:
            if zone_id != zone_id:
                continue
        zone = zone_manager.get(zone_id)
        for object_id in objects:
            street_str = 'n/a'
            for street_id, objects in clones_to_delete_by_street.items():
                if object_id in objects:
                    street_str = str(street_id)
                    break

            clones_to_delete.append({'object':_olaf_obj_str(zone, object_id), 
             'zone':_olaf_zone_str(zone_id, zone), 
             'street':street_str})
            object_ids.add(object_id)

    if zone_id is None:
        for street_id, objects in clones_to_delete_by_street.items():
            for object_id in objects:
                if object_id in object_ids:
                    continue
                clones_to_delete.append({'object':_olaf_obj_str(services.current_zone(), object_id), 
                 'zone':'n/a', 
                 'street':street_id})

    return clones_to_delete