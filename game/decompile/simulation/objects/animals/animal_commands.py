# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\animals\animal_commands.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 5502 bytes
import services, sims4
from animation.animation_constants import CreatureType
from global_flags.global_flags import GlobalFlags
from objects.components.state_references import TunablePackSafeStateValueReference
from objects.components.types import ANIMAL_OBJECT_COMPONENT, ANIMAL_HOME_COMPONENT
from server_commands.argument_helpers import RequiredTargetParam, OptionalTargetParam, get_optional_target
from sims4.commands import CommandType
from sims4.common import Pack
from sims.sim_info_types import Species
from sims4.tuning.tunable import TunableEnumFlags, TunableEnumEntry
from tag import Tag

class AnimalCommandTuning:
    DISABLE_BIRDS_GLOBAL_FLAGS = TunableEnumFlags(description='\n        Flags to set to disable the spawning of birds.\n        ',
      enum_type=GlobalFlags)
    DISABLE_BIRDS_TAG = TunableEnumEntry(description='\n        Tag to use to destroy all birds when disabling birds.\n        ',
      tunable_type=Tag,
      invalid_enums=(
     Tag.INVALID,),
      default=(Tag.INVALID),
      pack_safe=True)
    DISABLE_BIRDS_HOME_TAG = TunableEnumEntry(description='\n        Tag to disable the spawning of vfx on the actual bird homes.\n        ',
      tunable_type=Tag,
      invalid_enums=(
     Tag.INVALID,),
      default=(Tag.INVALID),
      pack_safe=True)
    DISABLE_BIRD_HOME_STATE = TunablePackSafeStateValueReference(description='\n        State used to disable bird homes.\n        ')
    ENABLE_BIRD_HOME_STATE = TunablePackSafeStateValueReference(description='\n        State used to enable bird homes.\n        ')


@sims4.commands.Command('animals.assign_to_home')
def assign_to_home(animal: RequiredTargetParam, home: OptionalTargetParam=None, _connection=None):
    animal_service = services.animal_service()
    if animal_service is None:
        sims4.commands.output('Assign to home failed. Animal Service is None. Is EP11 installed?', _connection)
        return False
    else:
        animal = animal.get_target()
        if animal is None:
            return False
        return animal.has_component(ANIMAL_OBJECT_COMPONENT) or False
    home_obj = None
    if home is not None:
        home_obj = get_optional_target(home, _connection)
        return home_obj is None or home_obj.has_component(ANIMAL_HOME_COMPONENT) or False
    return animal_service.assign_animal(animal.id, home_obj)


@sims4.commands.Command('animals.set_creature_aging_enabled', pack=(Pack.EP11), command_type=(sims4.commands.CommandType.Live))
def set_creature_aging_enabled(enabled: bool=True, _connection=None):
    animal_service = services.animal_service()
    if animal_service is None:
        sims4.commands.output('Setting creature aging failed. Animal Service is None. Is EP11 installed?', _connection)
        return False
    animal_service.set_aging_enabled(enabled)
    services.get_aging_service().set_species_aging_enabled(Species.FOX, enabled)
    return True


@sims4.commands.Command('animals.remove_all', command_type=(CommandType.Automation))
def remove_all(creature_type: CreatureType, _connection=None):
    objs_to_delete = []
    for obj in services.object_manager().get_all_objects_with_component_gen(ANIMAL_OBJECT_COMPONENT):
        if creature_type == obj.animalobject_component.creature_type:
            objs_to_delete.append(obj)

    for obj in objs_to_delete:
        sims4.commands.output('Destroyed object {} at position {}, parent_type {}.'.format(obj, obj.position, obj.parent_type), _connection)
        obj.destroy(cause='Destroyed by cheat command animals.remove_all')

    sims4.commands.output('Animal cleanup complete', _connection)
    return True


@sims4.commands.Command('animals.set_birds_allowed', command_type=(CommandType.Automation))
def set_birds_allowed(enabled: bool, _connection=None):
    if enabled:
        services.global_flag_service().remove_flag(AnimalCommandTuning.DISABLE_BIRDS_GLOBAL_FLAGS)
        for obj in services.object_manager().get_objects_with_tag_gen(AnimalCommandTuning.DISABLE_BIRDS_HOME_TAG):
            obj.set_state(AnimalCommandTuning.ENABLE_BIRD_HOME_STATE.state, AnimalCommandTuning.ENABLE_BIRD_HOME_STATE)

        sims4.commands.output('Birds Enabled', _connection)
    else:
        services.global_flag_service().add_flag(AnimalCommandTuning.DISABLE_BIRDS_GLOBAL_FLAGS)
        for obj in tuple(services.object_manager().get_objects_with_tag_gen(AnimalCommandTuning.DISABLE_BIRDS_TAG)):
            obj.destroy(cause='Destroyed by cheat set_birds_allowed.')

        for obj in services.object_manager().get_objects_with_tag_gen(AnimalCommandTuning.DISABLE_BIRDS_HOME_TAG):
            obj.set_state(AnimalCommandTuning.DISABLE_BIRD_HOME_STATE.state, AnimalCommandTuning.DISABLE_BIRD_HOME_STATE)

        sims4.commands.output('Birds Disabled', _connection)
    return True