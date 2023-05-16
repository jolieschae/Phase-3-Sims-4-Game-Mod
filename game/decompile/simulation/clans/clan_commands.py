# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\clans\clan_commands.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 1590 bytes
import services
from server_commands.argument_helpers import TunableInstanceParam
from sims4.commands import CommandType
import sims4

@sims4.commands.Command('clans.show_clan_information', command_type=(sims4.commands.CommandType.Live))
def show_clan_information(clan: TunableInstanceParam(sims4.resources.Types.CLAN), _connection=None):
    clan_service = services.clan_service()
    if clan_service is None:
        return
    clan_service.show_clan_information(clan, services.active_sim_info())


@sims4.commands.Command('clans.remove_clan_leader', command_type=(sims4.commands.CommandType.DebugOnly))
def remove_clan_leader(clan: TunableInstanceParam(sims4.resources.Types.CLAN), _connection=None):
    clan_service = services.clan_service()
    if clan_service is None:
        return
    clan_service.remove_clan_leader(clan)


@sims4.commands.Command('clans.replace_clan_leader', command_type=(sims4.commands.CommandType.DebugOnly))
def replace_clan_leader(clan: TunableInstanceParam(sims4.resources.Types.CLAN), _connection=None):
    clan_service = services.clan_service()
    if clan_service is None:
        return
    clan_service.remove_clan_leader(clan)
    clan_service.create_clan_leader(clan)