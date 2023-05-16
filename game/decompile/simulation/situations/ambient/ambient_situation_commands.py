# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\ambient\ambient_situation_commands.py
# Compiled at: 2018-02-28 17:47:17
# Size of source mod 2**32: 2571 bytes
from world.lot_tuning import LotTuningMaps
import sims4.commands

def _get_lot_tuning(_connection):
    lot_tuning = LotTuningMaps.get_lot_tuning()
    if lot_tuning is None:
        sims4.commands.output("Could not find any LotTuning for the current lot. Please check world.lot_tuning's maps for adding a LotTuning guidance.", _connection)
    return lot_tuning


@sims4.commands.Command('walkby.print_lot_tuning')
def print_lot_tuning(_connection=None):
    lot_tuning = _get_lot_tuning(_connection)
    if lot_tuning is not None:
        sims4.commands.output('{}'.format(lot_tuning), _connection)


@sims4.commands.Command('walkby.print_desired_sim_count')
def print_desired_sim_count(_connection=None):
    lot_tuning = _get_lot_tuning(_connection)
    if lot_tuning is None:
        return 0
    walkby = lot_tuning.walkby
    if walkby is None:
        sims4.commands.output('{} does not have an associated WalkbyTuning.'.format(lot_tuning), _connection)
        return 0
    count = walkby.get_desired_sim_count()
    sims4.commands.output('Desired Sims: lower_bound:{} upper_bound:{}.'.format(count.lower_bound, count.upper_bound), _connection)
    return count


@sims4.commands.Command('walkby.pick_ambient_walkby_situation')
def pick_ambient_walkby_situation(_connection=None):
    lot_tuning = _get_lot_tuning(_connection)
    if lot_tuning is None:
        return
    walkby = lot_tuning.walkby
    if walkby is None:
        sims4.commands.output('{} does not have an associated WalkbyTuning.'.format(lot_tuning), _connection)
        return
    situation = walkby.get_ambient_walkby_situation(None)
    sims4.commands.output('Ambient Walkby Situation: {}.'.format(situation), _connection)
    return situation