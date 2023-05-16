# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\eco_footprint\eco_footprint_telemetry.py
# Compiled at: 2020-01-31 16:42:48
# Size of source mod 2**32: 1429 bytes
import sims4, telemetry_helper
TELEMETRY_GROUP_ECO_FOOTPRINT = 'NBHD'
TELEMETRY_HOOK_ECO_FOOTPRINT_STATE_CHANGE = 'FOOT'
TELEMETRY_FIELD_NEIGHBORHOOD = 'nbhd'
TELEMETRY_FIELD_OLD_FOOTPRINT_STATE = 'oldf'
TELEMETRY_FIELD_NEW_FOOTPRINT_STATE = 'newf'
TELEMETRY_FIELD_CONVERGENCE_VALUE = 'cnvg'
_telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_ECO_FOOTPRINT)

def send_eco_footprint_state_change_telemetry(world_description_id, old_state, new_state, convergence_value):
    with telemetry_helper.begin_hook(_telemetry_writer, TELEMETRY_HOOK_ECO_FOOTPRINT_STATE_CHANGE) as (hook):
        hook.write_guid(TELEMETRY_FIELD_NEIGHBORHOOD, world_description_id)
        hook.write_enum(TELEMETRY_FIELD_OLD_FOOTPRINT_STATE, old_state)
        hook.write_enum(TELEMETRY_FIELD_NEW_FOOTPRINT_STATE, new_state)
        hook.write_float(TELEMETRY_FIELD_CONVERGENCE_VALUE, convergence_value)