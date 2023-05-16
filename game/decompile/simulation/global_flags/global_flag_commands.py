# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\global_flags\global_flag_commands.py
# Compiled at: 2021-06-01 17:47:18
# Size of source mod 2**32: 736 bytes
import services, sims4.commands
from global_flags.global_flags import GlobalFlags

@sims4.commands.Command('flags.add_flag', command_type=(sims4.commands.CommandType.Automation))
def add_flag(flag: GlobalFlags, connection=None):
    services.global_flag_service().add_flag(flag)


@sims4.commands.Command('flags.remove_flag', command_type=(sims4.commands.CommandType.Automation))
def remove_flag(flag: GlobalFlags, connection=None):
    services.global_flag_service().remove_flag(flag)