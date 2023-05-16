# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sickness\sickness_commands.py
# Compiled at: 2017-08-16 18:31:58
# Size of source mod 2**32: 2877 bytes
from server_commands.argument_helpers import OptionalSimInfoParam, TunableInstanceParam, get_optional_target
import services, sims4

@sims4.commands.Command('sickness.make_sick', command_type=(sims4.commands.CommandType.Automation))
def make_sick(opt_target: OptionalSimInfoParam=None, _connection=None):
    target = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
    if target is None:
        return False
    services.get_sickness_service().make_sick(target)


@sims4.commands.Command('sickness.add', command_type=(sims4.commands.CommandType.Automation))
def add_sickness(sickness_type: TunableInstanceParam(sims4.resources.Types.SICKNESS), opt_target: OptionalSimInfoParam=None, _connection=None):
    target = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
    if target is None:
        return False
    services.get_sickness_service().make_sick(target, sickness=sickness_type)


@sims4.commands.Command('sickness.remove', command_type=(sims4.commands.CommandType.Automation))
def remove_sickness(opt_target: OptionalSimInfoParam=None, _connection=None):
    target = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
    if target is None:
        return False
    services.get_sickness_service().remove_sickness(target)


@sims4.commands.Command('sickness.distribute_sicknesses')
def distribute_sicknesses(_connection=None):
    services.get_sickness_service().trigger_sickness_distribution()


@sims4.commands.Command('sickness.update_diagnosis')
def update_diagnosis(opt_target: OptionalSimInfoParam=None, _connection=None):
    target = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
    return target is None or target.has_sickness_tracking() or False
    target.current_sickness.update_diagnosis(target)


@sims4.commands.Command('sickness.clear_diagnosis')
def clear_diagnosis(opt_target: OptionalSimInfoParam=None, _connection=None):
    target = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
    return target is None or target.has_sickness_tracking() or False
    target.sickness_tracker.clear_diagnosis_data()