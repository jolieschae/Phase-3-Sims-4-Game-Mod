# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\vet\vet_commands.py
# Compiled at: 2017-05-11 15:42:01
# Size of source mod 2**32: 963 bytes
import sims4.commands
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target
from vet.vet_clinic_utils import get_vet_clinic_zone_director

@sims4.commands.Command('vet.bill_owner_for_treatment', command_type=(sims4.commands.CommandType.Live))
def bill_owner_for_treatment(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output("Sim {} doesn't exist.".format(opt_sim), _connection)
        return False
    zone_director = get_vet_clinic_zone_director()
    if zone_director is None:
        sims4.commands.Command('Not currently on a vet clinic lot.', _connection)
        return False
    zone_director.bill_owner_for_treatment(sim)
    return True