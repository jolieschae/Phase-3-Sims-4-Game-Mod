# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\posture_animation_data.py
# Compiled at: 2021-01-11 13:39:23
# Size of source mod 2**32: 18478 bytes
from animation import get_throwaway_animation_context
from animation.animation_utils import StubActor
from animation.asm import create_asm
from animation.posture_manifest import AnimationParticipant
from interactions.constraint_variants import TunableConstraintVariant
from interactions.utils.animation_reference import TunableAnimationReference
from sims.occult.occult_enums import OccultType
from sims.sim_info_types import Species
from sims4.tuning.tunable import TunableTuple, TunableResourceKey, Tunable, AutoFactoryInit, HasTunableSingletonFactory, TunableMapping, TunableEnumEntry, TunableFactory, OptionalTunable, TunableList
from sims4.tuning.tunable_base import SourceQueries
import sims4.resources
logger = sims4.log.Logger('Posture Animation Data')

def build_boundary_conditions_for_posture(anim_data, posture_type):
    logger.debug('building boundary conditions for {}', posture_type)
    for actor_param_name_tuning in anim_data.actor_param_name_list:
        actor_param_name = getattr(anim_data, actor_param_name_tuning)
        stub_actor = StubActor(1)
        asm = create_asm(anim_data._asm_key, get_throwaway_animation_context())
        asm.set_actor(actor_param_name, stub_actor)
        target_name = anim_data._target_name
        part_owner_actor_name = anim_data._part_owner_actor_name
        if target_name is not None:
            posture_target = StubActor(2)
            asm.add_potentially_virtual_actor(actor_param_name, stub_actor, target_name, posture_target)
            if part_owner_actor_name is not None:
                asm.set_actor(part_owner_actor_name, posture_target, suffix=None, actor_participant=(AnimationParticipant.CONTAINER))
        asm.get_boundary_conditions_list(stub_actor, (anim_data._enter_state_name), posture=posture_type,
          base_object_name=target_name)
        asm.get_boundary_conditions_list(stub_actor, (anim_data._exit_state_name), from_state_name=(anim_data._state_name),
          entry=False,
          posture=posture_type,
          base_object_name=target_name)


class _TunableAnimationData(TunableTuple):
    ASM_SOURCE = '_asm_key'
    ACTOR_PARAM_NAMES_LOCKED_ARGS = {'actor_param_name_list': ('_actor_param_name', )}

    def __init__(self, *args, locked_args=None, **kwargs):
        locked_args_merged = dict(self.ACTOR_PARAM_NAMES_LOCKED_ARGS)
        if locked_args:
            locked_args_merged.update(locked_args)
        (super().__init__)(args, _asm_key=TunableResourceKey(description='\n                The posture ASM.\n                ',
  default=None,
  resource_types=[
 sims4.resources.Types.STATEMACHINE],
  category='asm',
  pack_safe=True), 
         _actor_param_name=Tunable(description="\n                The name of the actor parameter in this posture's ASM. By\n                default, this is x, and you should probably not change it.\n                ",
  tunable_type=str,
  default='x',
  source_location=(self.ASM_SOURCE),
  source_query=(SourceQueries.ASMActorSim)), 
         _target_name=Tunable(description="\n                The actor name for the target object of this posture. Leave\n                empty for postures with no target. In the case of a posture\n                that targets an object, it should be the name of the object\n                actor in this posture's ASM.\n                ",
  tunable_type=str,
  default=None,
  source_location=(self.ASM_SOURCE),
  source_query=(SourceQueries.ASMActorAll)), 
         _part_owner_actor_name=Tunable(description='\n                This tunable is used when the object has parts. In most cases, the\n                state machines will only have one actor for the part that is\n                involved in animation. In that case, this field should not be set.\n                \n                e.g. The Sit posture requires the sitTemplate actor to be set, but\n                does not make a distinction between, for instance, Chairs and Sofas,\n                because no animation ever involves the whole object.\n                \n                However, there may be cases when, although we are dealing with\n                parts, the animation will need to also reference the entire object.\n                In that case, the ASM will have an extra actor to account for the\n                whole object, in addition to the part. Set this field to be that\n                actor name.\n                \n                e.g. The Sleep posture on the bed animates the Sim on one part.\n                However, the sheets and pillows need to animate on the entire bed.\n                In that case, we need to set this field on Bed so that the state\n                machine can have this actor set.\n                ',
  tunable_type=str,
  default=None,
  source_location=(self.ASM_SOURCE),
  source_query=(SourceQueries.ASMActorAll)), 
         _jig_name=Tunable(description='\n                The actor name for the jig created by this posture, if a jig is\n                tuned.\n                ',
  tunable_type=str,
  default=None,
  source_location=(self.ASM_SOURCE),
  source_query=(SourceQueries.ASMActorObject)), 
         _enter_state_name=Tunable(description='\n                The name of the entry state for the posture in the ASM. All\n                postures should have two public states, not including entry\n                and exit. This should be the first of the two states.\n                ',
  tunable_type=str,
  default=None,
  source_location=(self.ASM_SOURCE),
  source_query=(SourceQueries.ASMState)), 
         _exit_state_name=Tunable(description='\n                The name of the exit state in the ASM. By default, this is\n                exit.\n                ',
  tunable_type=str,
  default='exit',
  source_location=(self.ASM_SOURCE),
  source_query=(SourceQueries.ASMState)), 
         _state_name=Tunable(description='\n                The main state name for the looping posture pose in the\n                ASM. All postures should have two public states, not\n                including entry and exit. This should be the second of the\n                two states.\n                ',
  tunable_type=str,
  default=None,
  source_location=(self.ASM_SOURCE),
  source_query=(SourceQueries.ASMState)), 
         _idle_animation=TunableAnimationReference(description='\n                The animation for a Sim to play while in this posture and\n                waiting for interaction behavior to start.\n                ',
  callback=None,
  pack_safe=True), 
         _idle_animation_occult_overrides=TunableMapping(description='\n                A mapping of occult type to idle animation override data.\n                ',
  key_type=TunableEnumEntry(description='\n                    The occult type of the Sim.\n                    ',
  tunable_type=OccultType,
  default=(OccultType.HUMAN)),
  value_type=TunableAnimationReference(description='\n                    Idle animation overrides to use for a Sim based on their \n                    occult type.\n                    ',
  callback=None,
  pack_safe=True)), 
         _set_locomotion_surface=Tunable(description='\n                If checked, then the Sim\'s locomotion surface is set to the\n                target of this posture, if it exists.\n                \n                The locomotion surface affects the sound of the Sim\'s footsteps\n                when locomoting. Generally, this should be unset, since most\n                Sims don\'t route on objects as part of postures. For the cases\n                where they do, however, we need to ensure the sound is properly\n                overridden.\n                \n                e.g. The "Sit" posture for Cats includes sitting on objects.\n                Some of those transitions involve Cats walking across the sofa.\n                We need to ensure that the sound of the footsteps matches the\n                fabric, instead of the floor/ground.\n                ',
  tunable_type=bool,
  default=False), 
         _carry_constraint=OptionalTunable(description='\n                If enabled, Sims in this posture need to be picked up using this\n                specific constraint.\n                ',
  tunable=TunableList(tunable=TunableConstraintVariant(description='\n                        A constraint that must be fulfilled in order to pick up\n                        this Sim.\n                        ')),
  enabled_name='Override',
  disabled_name='From_Carryable_Component'), 
         locked_args=locked_args_merged, **kwargs)


class _AnimationDataBase(HasTunableSingletonFactory, AutoFactoryInit):

    def get_animation_data(self, sim, target):
        raise NotImplementedError

    def get_provided_postures_gen(self):
        raise NotImplementedError

    def get_supported_postures_gen(self):
        raise NotImplementedError

    def build_boundary_conditions(self, posture_type):
        raise NotImplementedError


class AnimationDataUniversal(_AnimationDataBase):

    @TunableFactory.factory_option
    def animation_data_options(locked_args=None, **tunable_data_entries):
        return {'_animation_data': _TunableAnimationData(locked_args=locked_args, **tunable_data_entries)}

    def get_animation_data(self, sim, target):
        return self._animation_data

    def get_provided_postures_gen(self):
        asm = create_asm(self._animation_data._asm_key, get_throwaway_animation_context())
        provided_postures = asm.provided_postures
        if provided_postures:
            for species in Species:
                if species == Species.INVALID:
                    continue
                yield (
                 species, provided_postures, asm)

    def get_supported_postures_gen(self):
        asm = create_asm(self._animation_data._asm_key, get_throwaway_animation_context())
        supported_postures = asm.get_supported_postures_for_actor(self._animation_data._actor_param_name)
        for species in Species:
            if species == Species.INVALID:
                continue
            yield (
             species, supported_postures, asm)

    def build_boundary_conditions(self, posture_type):
        build_boundary_conditions_for_posture(self._animation_data, posture_type)


class AnimationDataByActorSpecies(_AnimationDataBase):

    @TunableFactory.factory_option
    def animation_data_options(locked_args=None, **tunable_data_entries):
        return {'_actor_species_mapping': TunableMapping(description='\n                A mapping from actor species to animation data.\n                ',
                                     key_type=TunableEnumEntry(description='\n                    Species these animations are intended for.\n                    ',
                                     tunable_type=Species,
                                     default=(Species.HUMAN),
                                     invalid_enums=(
                                    Species.INVALID,)),
                                     value_type=_TunableAnimationData(locked_args=locked_args, **tunable_data_entries))}

    def get_animation_data(self, sim, target):
        return self._actor_species_mapping.get(sim.species)

    def get_animation_species(self):
        return self._actor_species_mapping.keys()

    def get_provided_postures_gen(self):
        for species, animation_data in self._actor_species_mapping.items():
            asm = create_asm(animation_data._asm_key, get_throwaway_animation_context())
            provided_postures = asm.provided_postures
            if not provided_postures:
                continue
            yield (
             species, provided_postures, asm)

    def get_supported_postures_gen(self):
        for species, animation_data in self._actor_species_mapping.items():
            asm = create_asm(animation_data._asm_key, get_throwaway_animation_context())
            supported_postures = asm.get_supported_postures_for_actor(animation_data._actor_param_name)
            yield (species, supported_postures, asm)

    def build_boundary_conditions(self, posture_type):
        for _species, animation_data in self._actor_species_mapping.items():
            build_boundary_conditions_for_posture(animation_data, posture_type)


class AnimationDataByActorAndTargetSpecies(_AnimationDataBase):

    @TunableFactory.factory_option
    def animation_data_options(locked_args=None, **tunable_data_entries):
        return {'_actor_species_mapping': TunableMapping(description='\n                A mapping from actor species to target-based animation data\n                mappings.\n                ',
                                     key_type=TunableEnumEntry(description='\n                    Species these animations are intended for.\n                    ',
                                     tunable_type=Species,
                                     default=(Species.HUMAN),
                                     invalid_enums=(
                                    Species.INVALID,)),
                                     value_type=TunableMapping(description='\n                    A mapping of target species to animation data.\n                    ',
                                     key_type=TunableEnumEntry(description='\n                        Species these animations are intended for.\n                        ',
                                     tunable_type=Species,
                                     default=(Species.HUMAN),
                                     invalid_enums=(
                                    Species.INVALID,)),
                                     value_type=_TunableAnimationData(locked_args=locked_args, **tunable_data_entries)))}

    def get_animation_data(self, sim, target):
        actor_animation_data = self._actor_species_mapping.get(sim.species)
        if actor_animation_data is not None:
            return actor_animation_data.get(target.species)

    def get_provided_postures_gen(self):
        for species, target_species_data in self._actor_species_mapping.items():
            animation_data = next(iter(target_species_data.values()))
            asm = create_asm(animation_data._asm_key, get_throwaway_animation_context())
            provided_postures = asm.provided_postures
            if not provided_postures:
                continue
            yield (
             species, provided_postures, asm)

    def get_supported_postures_gen(self):
        for species, target_species_data in self._actor_species_mapping.items():
            animation_data = next(iter(target_species_data.values()))
            asm = create_asm(animation_data._asm_key, get_throwaway_animation_context())
            supported_postures = asm.get_supported_postures_for_actor(animation_data._actor_param_name)
            yield (species, supported_postures, asm)

    def build_boundary_conditions(self, posture_type):
        for _species, target_species_data in self._actor_species_mapping.items():
            for target_species_animation_data in target_species_data.values():
                build_boundary_conditions_for_posture(target_species_animation_data, posture_type)