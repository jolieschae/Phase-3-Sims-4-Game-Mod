# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\style_commands.py
# Compiled at: 2020-03-31 18:05:09
# Size of source mod 2**32: 597 bytes
from sims4.commands import CommandType
from sims.sim_info_types import Gender
import services, sims4.commands

@sims4.commands.Command('style.clear_style', command_type=(CommandType.Live))
def clear_style(gender: Gender, _connection=None):
    style_service = services.get_style_service()
    if style_service is None:
        return
    style_service.clear_style_outfit_data(gender)