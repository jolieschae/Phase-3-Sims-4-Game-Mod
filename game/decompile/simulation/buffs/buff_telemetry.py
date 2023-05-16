# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\buffs\buff_telemetry.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 1147 bytes
import services, sims4.log, telemetry_helper
from sims4.telemetry import TelemetryWriter
TELEMETRY_GROUP_BUFF = 'BUFF'
TELEMETRY_HOOK_ADD_BUFF = 'BADD'
TELEMETRY_HOOK_REMOVE_BUFF = 'BRMV'
TELEMETRY_FIELD_BUFF_ID = 'idbf'
buff_telemetry_writer = TelemetryWriter(TELEMETRY_GROUP_BUFF)
logger = sims4.log.Logger('BuffTelemetry', default_owner='jdimailig')

def write_buff_telemetry(hook_tag, buff, sim):
    if not sim.is_simulating:
        return
    else:
        current_zone = services.current_zone()
        return current_zone is None or current_zone.is_zone_running or None
    logger.debug('{}: buff:{}', hook_tag, buff.buff_type)
    with telemetry_helper.begin_hook(buff_telemetry_writer, hook_tag, sim=sim) as (hook):
        hook.write_int(TELEMETRY_FIELD_BUFF_ID, buff.buff_type.guid64)