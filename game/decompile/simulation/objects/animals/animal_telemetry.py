# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\animals\animal_telemetry.py
# Compiled at: 2021-03-09 17:00:10
# Size of source mod 2**32: 680 bytes
import sims4, telemetry_helper
TELEMETRY_GROUP_ANIMAL = 'ANML'
writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_ANIMAL)
TELEMETRY_HOOK_ADD_ANIMAL = 'AADD'
TELEMETRY_FIELD_DEFINITION = 'type'
TELEMETRY_FIELD_INSTANCE = 'anid'

def send_animal_added_telemetry(animal):
    with telemetry_helper.begin_hook(writer, TELEMETRY_HOOK_ADD_ANIMAL) as (hook):
        definition_id = animal.definition.id if hasattr(animal, 'definition') else 0
        hook.write_int(TELEMETRY_FIELD_DEFINITION, definition_id)
        hook.write_int(TELEMETRY_FIELD_INSTANCE, animal.id)