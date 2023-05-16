# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\global_policies\global_policy_commands.py
# Compiled at: 2019-02-20 17:31:10
# Size of source mod 2**32: 581 bytes
from server_commands.argument_helpers import TunableInstanceParam
import services, sims4

@sims4.commands.Command('global_policy.set_progress', command_type=(sims4.commands.CommandType.Automation))
def set_global_policy_progress(policy: TunableInstanceParam(sims4.resources.Types.SNIPPET), progress_amount: int, _connection=None):
    services.global_policy_service().add_global_policy_progress(policy, progress_amount)