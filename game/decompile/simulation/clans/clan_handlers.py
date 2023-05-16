# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\clans\clan_handlers.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 2014 bytes
import services
from clans.clan_service import ClanService
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
clan_schema = GsiGridSchema(label='Clans')
clan_schema.add_field('clan_id', label='Clan Id', width=1, unique_field=True)
clan_schema.add_field('clan_name', label='Clan Name', width=2)
clan_schema.add_field('leader_id', label='Leader Id', width=1)
clan_schema.add_field('leader_name', label='Leader Name', width=2)
clan_schema.add_field('alliance_state', label='Alliance State', width=2)
with clan_schema.add_view_cheat('clans.remove_clan_leader', label='Revoke Leader') as (remove_leader_command):
    remove_leader_command.add_token_param('clan_id')
with clan_schema.add_view_cheat('clans.replace_clan_leader', label='Replace Leader') as (make_new_leader_command):
    make_new_leader_command.add_token_param('clan_id')

@GsiHandler('clans', clan_schema)
def generate_clans_view():
    clans = []
    clan_service = services.clan_service()
    if clan_service is not None:
        for clan_tuning_data in ClanService.CLAN_DATA:
            clan_guid = clan_tuning_data.guid64
            leader_sim_id = clan_service.clan_guid_to_leader_sim_id_map.get(clan_guid)
            leader_sim_name = ''
            if leader_sim_id is not None:
                leader_sim_info = services.sim_info_manager().get(leader_sim_id)
                leader_sim_name = leader_sim_info.full_name if leader_sim_info is not None else '<missing sim info>'
            clan_data = {'clan_id':str(clan_guid),  'clan_name':str(clan_tuning_data), 
             'leader_id':str(leader_sim_id), 
             'leader_name':leader_sim_name, 
             'alliance_state':str(clan_service.current_clan_alliance_state)}
            clans.append(clan_data)

    return clans