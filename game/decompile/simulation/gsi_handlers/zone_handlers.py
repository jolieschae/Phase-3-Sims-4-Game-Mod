# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\zone_handlers.py
# Compiled at: 2014-04-14 18:29:07
# Size of source mod 2**32: 623 bytes
import services
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiSchema
zone_view_schema = GsiSchema()
zone_view_schema.add_field('zoneId')

@GsiHandler('zone_view', zone_view_schema)
def generate_zone_view_data():
    zone_list = []
    for zone in services._zone_manager.objects:
        if zone.is_instantiated:
            zone_list.append({'zoneId':hex(zone.id),  'zoneName':'ZoneName'})

    return zone_list