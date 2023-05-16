# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\adoption\adoption_commands.py
# Compiled at: 2017-09-14 14:43:34
# Size of source mod 2**32: 832 bytes
from server_commands.argument_helpers import OptionalSimInfoParam, get_optional_target
from sims4.commands import CommandType
import services, sims4.commands

@sims4.commands.Command('adoption.remove_sim_info', command_type=(CommandType.Live))
def remove_sim_info(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        return False
    adoption_service = services.get_adoption_service()
    adoption_service.remove_sim_info(sim_info)
    return True