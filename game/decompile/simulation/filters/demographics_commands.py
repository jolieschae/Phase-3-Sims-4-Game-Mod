# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\filters\demographics_commands.py
# Compiled at: 2020-08-28 17:52:06
# Size of source mod 2**32: 1587 bytes
import services, sims4.commands
from sims4.resources import get_resource_key, Types, get_debug_name

@sims4.commands.Command('demographics.print')
def print_demographics(_connection=None):
    demographics_service = services.get_demographics_service()
    candidate_world_ids = services.get_persistence_service().get_world_ids()
    population_counts = demographics_service.get_population_counts()
    target_counts = demographics_service.get_target_populations(candidate_world_ids)
    definition_manager = services.definition_manager()
    for world_id in candidate_world_ids:
        world_description_id = services.get_world_description_id(world_id)
        world_resource_key = get_resource_key(world_description_id, Types.WORLD_DESCRIPTION)
        sims4.commands.output('World ID          = {}\nTarget Population = {}\nPopulation        = {}\n'.format(get_debug_name(world_resource_key, table_type=(sims4.hash_util.KEYNAMEMAPTYPE_OBJECTINSTANCES)), target_counts[world_id], population_counts[world_id]), _connection)