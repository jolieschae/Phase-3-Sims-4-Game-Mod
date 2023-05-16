# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\tutorials\tutorial_tip_commands.py
# Compiled at: 2018-09-05 17:15:44
# Size of source mod 2**32: 1220 bytes
from server_commands.argument_helpers import TunableInstanceParam
import services, sims4

@sims4.commands.Command('tutorial.activate_tutorial_tip', command_type=(sims4.commands.CommandType.Live))
def activate_tutorial_tip(tutorial_tip: TunableInstanceParam(sims4.resources.Types.TUTORIAL_TIP), _connection=None):
    tutorial_tip.activate()
    return True


@sims4.commands.Command('tutorial.deactivate_tutorial_tip', command_type=(sims4.commands.CommandType.Live))
def deactivate_tutorial_tip(tutorial_tip: TunableInstanceParam(sims4.resources.Types.TUTORIAL_TIP), _connection=None):
    tutorial_tip.deactivate()
    return True


@sims4.commands.Command('tutorial.set_tutorial_mode', command_type=(sims4.commands.CommandType.Live))
def set_tutorial_mode(mode: int=0, _connection=None):
    tutorial_service = services.get_tutorial_service()
    if tutorial_service is not None:
        tutorial_service.set_tutorial_mode(mode)
    return True