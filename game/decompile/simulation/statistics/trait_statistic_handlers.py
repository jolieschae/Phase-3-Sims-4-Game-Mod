# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\trait_statistic_handlers.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 2011 bytes
from gsi_handlers.sim_handlers import _get_sim_info_by_id
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
trait_statistics_schema = GsiGridSchema(label='Statistics/Trait Statistic', sim_specific=True)
trait_statistics_schema.add_field('trait_statistic_name', label='Name')
trait_statistics_schema.add_field('trait_statistic_value', label='Value', type=(GsiFieldVisualizers.FLOAT))
trait_statistics_schema.add_field('trait_statistic_min_daily_cap', label='Min Daily Cap', type=(GsiFieldVisualizers.FLOAT))
trait_statistics_schema.add_field('trait_statistic_max_daily_cap', label='Max Daily Cap', type=(GsiFieldVisualizers.FLOAT))
trait_statistics_schema.add_field('trait_statistic_state', label='State')
trait_statistics_schema.add_field('trait_statistic_group_limited', label='Group Limited')

@GsiHandler('trait_statistic_view', trait_statistics_schema)
def generate_trait_statistic_view_data(sim_id: int=None):
    trait_statistic_data = []
    cur_sim_info = _get_sim_info_by_id(sim_id)
    if cur_sim_info is not None:
        trait_statistic_tracker = cur_sim_info.trait_statistic_tracker
        if trait_statistic_tracker is not None:
            for statistic in list(trait_statistic_tracker):
                entry = {'trait_statistic_name':type(statistic).__name__, 
                 'trait_statistic_value':statistic.get_value(), 
                 'trait_statistic_min_daily_cap':statistic._get_minimum_decay_level(), 
                 'trait_statistic_max_daily_cap':statistic._get_maximum_decay_level(), 
                 'trait_statistic_state':str(statistic.state), 
                 'trait_statistic_group_limited':str(statistic.group_limited)}
                trait_statistic_data.append(entry)

    return trait_statistic_data