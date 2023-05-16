# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\pets\missing_pet_handlers.py
# Compiled at: 2017-10-03 18:04:54
# Size of source mod 2**32: 1745 bytes
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
import services
missing_pet_schema = GsiGridSchema(label='Missing Pets')
missing_pet_schema.add_field('household_id', label='Household Id')
missing_pet_schema.add_field('household', label='Household')
missing_pet_schema.add_field('run_test_absolute', label='Run Tests - Absolute Time')
missing_pet_schema.add_field('run_test_time_left', label='Run Tests - Time Left')
missing_pet_schema.add_field('sim_id', label='Sim Id')
missing_pet_schema.add_field('sim', label='Sim')
missing_pet_schema.add_field('return_time_absolute', label='Return Time - Absolute Time')
missing_pet_schema.add_field('return_time_left', label='Return Time - Time Left')
missing_pet_schema.add_field('cooldown_absolute', label='Cooldown - Absolute Time')
missing_pet_schema.add_field('cooldown_time_left', label='Cooldown - Time Left')
with missing_pet_schema.add_view_cheat('pets.return_pet', label='Return Pet') as (return_pet_cheat):
    return_pet_cheat.add_token_param('household_id')
with missing_pet_schema.add_view_cheat('pets.post_alert', label='Post Alert') as (post_alert_cheat):
    post_alert_cheat.add_token_param('household_id')

@GsiHandler('missing_pets_schema_view', missing_pet_schema)
def generate_missing_pet_view():
    missing_pet_data = []
    for household in services.household_manager().values():
        gsi_data = household.missing_pet_tracker.get_missing_pet_data_for_gsi()
        missing_pet_data.append(gsi_data)

    return missing_pet_data