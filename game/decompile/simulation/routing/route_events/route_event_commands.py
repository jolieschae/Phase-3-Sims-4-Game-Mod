# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\route_events\route_event_commands.py
# Compiled at: 2018-03-30 23:28:07
# Size of source mod 2**32: 745 bytes
from sims4.commands import CommandType
import gsi_handlers, sims4.commands

@sims4.commands.Command('route_events.toggle_gsi_update_log', command_type=(CommandType.DebugOnly))
def route_events_toggle_gsi_update_log(_connection=None):
    enabled = not gsi_handlers.route_event_handlers.update_log_enabled
    gsi_handlers.route_event_handlers.update_log_enabled = enabled
    if enabled:
        sims4.commands.output('Route Event Update Log: Enabled', _connection)
    else:
        sims4.commands.output('Route Event Update Log: Disabled', _connection)
    return True