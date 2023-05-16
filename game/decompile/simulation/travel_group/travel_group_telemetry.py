# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\travel_group\travel_group_telemetry.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 1798 bytes
import sims4.telemetry, telemetry_helper
from world.region import get_region_description_id_from_zone_id
TELEMETRY_GROUP_TRAVEL_GROUPS = 'TGRP'
TELEMETRY_HOOK_TRAVEL_GROUP_ADD = 'TGAD'
TELEMETRY_HOOK_TRAVEL_GROUP_START = 'TGST'
TELEMETRY_HOOK_TRAVEL_GROUP_EXTEND = 'TGEX'
TELEMETRY_HOOK_TRAVEL_GROUP_END = 'TGEN'
TELEMETRY_HOOK_TRAVEL_GROUP_REMOVE = 'TGRM'
TELEMETRY_TRAVEL_GROUP_ID = 'tgid'
TELEMETRY_TRAVEL_GROUP_ZONE_ID = 'tgzo'
TELEMETRY_TRAVEL_GROUP_SIZE = 'tgsz'
TELEMETRY_TRAVEL_GROUP_DURATION = 'tgdu'
TELEMETRY_TRAVEL_GROUP_REGION_DESC_ID = 'rgni'
TELEMETRY_TRAVEL_GROUP_TYPE = 'type'
TELEMETRY_TRAVEL_GROUP_SITUATION_ID = 'stid'
travel_group_telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_TRAVEL_GROUPS)

def write_travel_group_telemetry(group, hook_tag, sim_info):
    with telemetry_helper.begin_hook(travel_group_telemetry_writer, hook_tag, sim_info=sim_info,
      valid_for_npc=True) as (hook):
        hook.write_int(TELEMETRY_TRAVEL_GROUP_ID, group.id)
        hook.write_int(TELEMETRY_TRAVEL_GROUP_ZONE_ID, group.zone_id)
        hook.write_int(TELEMETRY_TRAVEL_GROUP_SIZE, len(group))
        hook.write_int(TELEMETRY_TRAVEL_GROUP_DURATION, int(group.duration_time_in_minutes))
        hook.write_int(TELEMETRY_TRAVEL_GROUP_REGION_DESC_ID, int(get_region_description_id_from_zone_id(group.zone_id)))
        hook.write_int(TELEMETRY_TRAVEL_GROUP_TYPE, group.group_type)
        hook.write_int(TELEMETRY_TRAVEL_GROUP_SITUATION_ID, 0 if group.situation is None else group.situation.guid64)