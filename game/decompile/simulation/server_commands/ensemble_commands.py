# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\ensemble_commands.py
# Compiled at: 2015-08-18 21:31:52
# Size of source mod 2**32: 1995 bytes
from server_commands.argument_helpers import RequiredTargetParam, TunableInstanceParam
import services, sims4.commands

@sims4.commands.Command('ensembles.create_ensemble')
def create_ensemble(ensemble_type: TunableInstanceParam(sims4.resources.Types.ENSEMBLE), *sims: RequiredTargetParam, _connection=None):
    ensemble_sims = [sim.get_target() for sim in sims]
    services.ensemble_service().create_ensemble(ensemble_type, ensemble_sims)
    sims4.commands.output('Created Ensemble with sims {}'.format(ensemble_sims), _connection)


@sims4.commands.Command('ensembles.remove_sim_from_ensemble')
def remove_sim_from_ensemble(ensemble_type: TunableInstanceParam(sims4.resources.Types.ENSEMBLE), sim: RequiredTargetParam, _connection=None):
    services.ensemble_service().remove_sim_from_ensemble(ensemble_type, sim.get_target())
    sims4.commands.output('Removed {} from ensembles.'.format(sim.get_target()), _connection)


@sims4.commands.Command('ensembles.get_sims_in_sims_ensembles')
def get_sims_in_sims_ensembles(sim: RequiredTargetParam, _connection=None):
    sim_inst = sim.get_target()
    ensemble_sims = sim_inst.get_ensemble_sims()
    sims4.commands.output('Sims in ensemble with {}: {}'.format(sim_inst, ensemble_sims), _connection)