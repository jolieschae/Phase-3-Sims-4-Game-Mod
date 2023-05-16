# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\gameplay_object_preference_commands.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 3204 bytes
import sims4
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target, TunableInstanceParam
from traits.preference_enums import GameplayObjectPreferenceTypes
from traits.trait_type import TraitType

@sims4.commands.Command('traits.equip_gameplay_object_preference', command_type=(sims4.commands.CommandType.Live))
def equip_gameplay_object_preference(trait_object: TunableInstanceParam(sims4.resources.Types.TRAIT), preference_type: GameplayObjectPreferenceTypes=GameplayObjectPreferenceTypes.NONE, opt_sim: OptionalTargetParam=None, _connection=None):
    if trait_object.trait_type is TraitType.GAMEPLAY_OBJECT_PREFERENCE:
        sim = get_optional_target(opt_sim, _connection)
        if sim is not None:
            trait_tracker = sim.sim_info.trait_tracker
            if trait_tracker is None:
                sims4.commands.output("Sim {} doesn't have trait tracker".format(sim), _connection)
                return False
            sim.sim_info.trait_tracker.add_gameplay_object_preference(trait_object, preference_type)
            return True
    return False


@sims4.commands.Command('traits.remove_gameplay_object_preference', command_type=(sims4.commands.CommandType.Live))
def remove_gameplay_object_preference(trait_object: TunableInstanceParam(sims4.resources.Types.TRAIT), opt_sim: OptionalTargetParam=None, _connection=None):
    if trait_object.trait_type is TraitType.GAMEPLAY_OBJECT_PREFERENCE:
        sim = get_optional_target(opt_sim, _connection)
        if sim is not None:
            trait_tracker = sim.sim_info.trait_tracker
            if trait_tracker is None:
                sims4.commands.output("Sim {} doesn't have trait tracker".format(sim), _connection)
            sim.sim_info.trait_tracker.remove_gameplay_object_preference(trait_object)
            return True
    return False


@sims4.commands.Command('traits.clear_gameplay_object_preferences', command_type=(sims4.commands.CommandType.Automation))
def clear_gameplay_object_preferences(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        trait_tracker = sim.sim_info.trait_tracker
        if trait_tracker is None:
            sims4.commands.output("Sim {} doesn't have trait tracker".format(sim), _connection)
            return False
        trait_tracker.remove_all_gameplay_object_preferences()
        return True
    return False