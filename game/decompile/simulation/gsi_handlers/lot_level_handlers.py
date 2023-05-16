# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\lot_level_handlers.py
# Compiled at: 2020-10-06 16:36:55
# Size of source mod 2**32: 1114 bytes
import services
from gsi_handlers.commodity_tracker_gsi_util import create_schema_for_commodity_tracker, generate_data_from_commodity
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
schema = create_schema_for_commodity_tracker(label='Lot Level Commodity Data')
schema.add_field('level_index', label='Lot Level')

@GsiHandler('lot_level_commodity_data_view', schema)
def generate_lot_level_commodity_data_view():
    lot = services.active_lot()
    lot_levels = list(lot.lot_levels.values())
    lot_levels.sort(key=(lambda level: level.level_index))
    stat_data = []
    for lot_level in lot_levels:
        for stat in lot_level.get_all_stats_gen():
            entry = generate_data_from_commodity(stat, lot_level.statistic_component)
            entry['level_index'] = lot_level.level_index
            stat_data.append(entry)

    return stat_data