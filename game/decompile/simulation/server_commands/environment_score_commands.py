# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\environment_score_commands.py
# Compiled at: 2014-06-05 14:17:21
# Size of source mod 2**32: 781 bytes
import sims4.commands
from broadcasters.environment_score import environment_score_mixin

@sims4.commands.Command('environment_score.enable')
def environment_score_enable(_connection=None):
    environment_score_mixin.environment_score_enabled = True


@sims4.commands.Command('environment_score.disable')
def environment_score_disable(_connection=None):
    environment_score_mixin.environment_score_enabled = False