# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\animals\animal_handlers.py
# Compiled at: 2021-06-30 21:13:04
# Size of source mod 2**32: 4716 bytes
import services
from gsi_handlers.gsi_utils import parse_filter_to_list
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
INSTANTIATED_ANIMALS_FILTER = 'Instantiated Animals'
INSTANTIATED_HOMES_FILTER = 'Instantiated Homes'
NOT_INSTANTIATED_STR = 'Not in current zone'
HOMELESS_STR = 'Homeless'
animal_management_schema = GsiGridSchema(label='Animal Management')
animal_management_schema.add_field('animal_obj_id', label='Animal Object Id', width=0.2)
animal_management_schema.add_field('animal_obj', label='Animal Object')
animal_management_schema.add_field('home_obj_id', label='Animal Home Object Id', width=0.2)
animal_management_schema.add_field('home_obj', label='Animal Home Object')
with animal_management_schema.add_has_many('animal_home_data', GsiGridSchema, label='Animal Home Data') as (sub_schema):
    sub_schema.add_field('data', label='Data')
    sub_schema.add_field('value', label='Value')
with animal_management_schema.add_view_cheat('objects.focus_camera_on_object', label='Focus On Selected Animal') as (cheat):
    cheat.add_token_param('animal_obj_id')
with animal_management_schema.add_view_cheat('objects.focus_camera_on_object', label='Focus On Selected Home') as (cheat):
    cheat.add_token_param('home_obj_id')
animal_management_schema.add_filter(INSTANTIATED_ANIMALS_FILTER)
animal_management_schema.add_filter(INSTANTIATED_HOMES_FILTER)

@GsiHandler('animal_management', animal_management_schema)
def generate_animal_management_data(filter=None):
    animal_management_data = []
    filter_list = parse_filter_to_list(filter)
    object_manager = services.object_manager()
    animal_service = services.animal_service()
    if animal_service is None:
        return animal_management_data
    for animal_id, home_data in animal_service.animal_assignment_map.items():
        entry = {}
        animal = object_manager.get(animal_id)
        if animal is not None:
            entry['animal_obj'] = str(animal)
            entry['animal_obj_id'] = str(animal_id)
        else:
            if filter_list is None or INSTANTIATED_ANIMALS_FILTER not in filter_list:
                entry['animal_obj'] = NOT_INSTANTIATED_STR
                entry['animal_obj_id'] = str(animal_id)
            else:
                continue
            entry['animal_home_data'] = []
            if home_data is not None:
                home_id = home_data.id
                current_occupancy = home_data.current_occupancy
                max_occupancy = home_data.max_occupancy
                animal_types = home_data.animal_types
                persist_assignment_in_household_inventory = home_data.persist_assignment_in_household_inventory
                owner_household_id = home_data.owner_household_id
                zone_id = home_data.zone_id
                open_street_id = home_data.open_street_id
                entry['animal_home_data'].append({'data':'Current Occupancy',  'value':str(current_occupancy)})
                entry['animal_home_data'].append({'data':'Max Occupancy',  'value':str(max_occupancy)})
                entry['animal_home_data'].append({'data':'Animal Types',  'value':str(animal_types)})
                entry['animal_home_data'].append({'data':'Persist Assignment in Household Inventory',  'value':str(persist_assignment_in_household_inventory)})
                entry['animal_home_data'].append({'data':'Owner Household ID',  'value':str(owner_household_id)})
                entry['animal_home_data'].append({'data':'Zone ID',  'value':str(zone_id)})
                entry['animal_home_data'].append({'data':'Open Street ID',  'value':str(open_street_id)})
                home = object_manager.get(home_id)
        if home_data is None:
            entry['home_obj'] = HOMELESS_STR
        else:
            if home is not None:
                entry['home_obj'] = str(home)
                entry['home_obj_id'] = str(home_id)
            else:
                if filter_list is None or INSTANTIATED_HOMES_FILTER not in filter_list:
                    entry['home_obj'] = NOT_INSTANTIATED_STR
                    entry['home_obj_id'] = str(home_id)
                else:
                    continue
                animal_management_data.append(entry)

    return animal_management_data