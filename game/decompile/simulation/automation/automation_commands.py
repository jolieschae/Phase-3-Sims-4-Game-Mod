# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\automation\automation_commands.py
# Compiled at: 2017-05-26 17:30:18
# Size of source mod 2**32: 651 bytes
from automation import automation_utils
import sims4.commands

@sims4.commands.Command('qa.automation.enable_events', command_type=(sims4.commands.CommandType.Automation))
def automation_events(enabled: bool=True, _connection=None):
    automation_utils.dispatch_automation_events = enabled