# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\__init__.py
# Compiled at: 2022-11-01 20:51:01
# Size of source mod 2**32: 985 bytes
from sims4.commands import CommandType
import paths, services, sims4.commands

def is_command_available(command_type: CommandType):
    if command_type >= CommandType.Live:
        return True
    else:
        if command_type >= CommandType.Cheat:
            cheat_service = services.get_cheat_service()
            cheats_enabled = cheat_service.cheats_enabled
            if cheats_enabled:
                return True
        if command_type >= CommandType.Automation and paths.AUTOMATION_MODE:
            return True
    return False


sims4.commands.is_command_available = is_command_available