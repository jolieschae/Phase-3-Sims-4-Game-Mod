# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\royalty_commands.py
# Compiled at: 2014-06-24 17:41:50
# Size of source mod 2**32: 843 bytes
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target
import sims4.commands

@sims4.commands.Command('royalty.give_royalties')
def give_royalties(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('Target Sim could not be found.', _connection)
        return False
    royalty_tracker = sim.sim_info.royalty_tracker
    if royalty_tracker is None:
        sims4.commands.output('Royalty Tracker not found for Sim.', _connection)
        return False
    royalty_tracker.update_royalties_and_get_paid()
    return True