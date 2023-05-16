# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\reputation\reputation_commands.py
# Compiled at: 2018-07-19 16:35:24
# Size of source mod 2**32: 1553 bytes
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target
import sims4.commands

@sims4.commands.Command('reputation.set_allow_reputation', command_type=(sims4.commands.CommandType.Automation))
def set_allow_reputation(allow_reputation: bool, opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('No target Sim to manipulate the reputation of.', _connection)
        return False
    sim.allow_reputation = allow_reputation
    sims4.commands.output("{}'s allow_reputation setting is set to {}".format(sim, sim.allow_reputation), _connection)
    return True


@sims4.commands.Command('reputation.show_allow_reputation', command_type=(sims4.commands.CommandType.Automation))
def show_allow_reputation(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('No target Sim to get the value of allow_reputation from.', _connection)
        return False
    sims4.commands.output("{}'s allow_reputation setting is set to {}".format(sim, sim.allow_reputation), _connection)
    return True