# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\fashion_trends\fashion_trend_commands.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 733 bytes
import sims4.commands
from sims4.common import Pack
import services

@sims4.commands.Command('fashion_trends.refresh_thrift_store_inventory', pack=(Pack.EP12), command_type=(sims4.commands.CommandType.DebugOnly))
def fashion_trends_refresh_thrift_store(_connection=None):
    fashion_trend_service = services.fashion_trend_service()
    if fashion_trend_service is None:
        sims4.commands.automation_output('Pack not loaded', _connection)
        sims4.commands.cheat_output('Pack not loaded', _connection)
        return
    fashion_trend_service.debug_randomize_thrift_store_inventory()