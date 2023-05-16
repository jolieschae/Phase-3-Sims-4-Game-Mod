# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\profiler_commands.py
# Compiled at: 2014-10-29 15:00:09
# Size of source mod 2**32: 892 bytes
from sims4.commands import CommandType
import sims4.commands, sims4.profiler

@sims4.commands.Command('pyprofile.on', command_type=(CommandType.Automation))
def pyprofile_on(_connection=None):
    sims4.profiler.enable_profiler()
    return True


@sims4.commands.Command('pyprofile.off', command_type=(CommandType.Automation))
def pyprofile_off(_connection=None):
    sims4.profiler.disable_profiler()
    sims4.profiler.flush()
    return True


@sims4.commands.Command('pyprofile.flush', command_type=(CommandType.Automation))
def pyprofile_flush(_connection=None):
    sims4.profiler.flush()
    return True