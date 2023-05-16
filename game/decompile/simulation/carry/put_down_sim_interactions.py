# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\carry\put_down_sim_interactions.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 22176 bytes
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    from routing import Location
from _math import Vector3, Transform
from carry.carry_elements import CarryElementHelper
from carry.carry_postures import CarrySystemTerrainTarget, CarrySystemCustomAnimationTarget, CarryingObject
from carry.put_down_interactions import create_put_down_on_ground_constraint, PutAwayBase
from element_utils import build_critical_section_with_finally
from event_testing.results import TestResult
from interactions import ParticipantType
from interactions.aop import AffordanceObjectPair
from interactions.base.basic import TunableBasicContentSet
from interactions.base.super_interaction import SuperInteraction
from interactions.constraints import Anywhere
from placement import FGLSearchFlag, FGLSearchFlagsDefault, FGLTuning
from postures import posture_graph
from sims4.tuning.tunable import TunableVariant, AutoFactoryInit, HasTunableSingletonFactory, OptionalTunable, TunableReference
from sims4.utils import flexmethod, classproperty
from singletons import UNSET
from socials.jigs.jig_type_explicit import SoloJigExplicit
import interactions.constraints, services, sims4.log
logger = sims4.log.Logger('PutDownSimInteractions', default_owner='yozhang')

class _PutDownBehaviorRunInteraction(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'affordance': OptionalTunable(description='\n            The interaction to run once the Sim is put down.\n            ',
                     tunable=SuperInteraction.TunableReference(description='\n                The interaction to run once the Sim is put down.\n                '),
                     disabled_name='Use_Default_Affordance',
                     enabled_name='Use_Specific_Affordance')}

    def get_provided_posture(self):
        if self.affordance is None:
            return posture_graph.SIM_DEFAULT_POSTURE_TYPE
        return self.affordance.provided_posture_type

    def get_target_si(self, interaction):
        sim = interaction.carry_target or interaction.target
        if self.affordance is None:
            interaction = sim.create_default_si()
        else:
            for running_interaction in sim.get_all_running_and_queued_interactions():
                if running_interaction.transition is None or running_interaction.is_finishing:
                    continue
                if running_interaction.get_interaction_type() is not self.affordance:
                    continue
                if running_interaction.target is not interaction.target:
                    continue
                return (
                 running_interaction, TestResult.TRUE)

            context = interaction.context.clone_for_sim(sim, carry_target=None, continuation_id=None)
            aop = AffordanceObjectPair(self.affordance, interaction.target, self.affordance, None)
            interaction = aop.interaction_factory(context).interaction
        return (
         interaction, TestResult.TRUE)


class PutDownSimInteraction(PutAwayBase):
    INSTANCE_SUBCLASSES_ONLY = True
    INSTANCE_TUNABLES = {'basic_content':TunableBasicContentSet(no_content=True, default='no_content'), 
     'put_down_behavior':TunableVariant(description='\n            Define what the carried Sim does once they are put down.\n            ',
       run_affordance=_PutDownBehaviorRunInteraction.TunableFactory(),
       default='run_affordance'), 
     'putdown_jig':OptionalTunable(description='\n            The jig to use for finding a place to putdown the sim.\n            ',
       tunable=SoloJigExplicit.TunableFactory())}

    def __init__(self, *args, **kwargs):
        self._target_si = None
        (super().__init__)(*args, **kwargs)

    @classproperty
    def is_putdown(cls):
        return True

    @classmethod
    def get_provided_posture(cls):
        return cls.put_down_behavior.get_provided_posture()

    @classproperty
    def can_holster_incompatible_carries(cls):
        return False

    def _get_putdown_jig_transform(self, starting_location: 'Location') -> 'Transform':
        fgl_flags = FGLSearchFlagsDefault
        fgl_kwargs = {'ignored_object_ids':{sim.id for sim in self.required_sims()},  'max_results':1, 
         'max_steps':FGLTuning.MAX_PUTDOWN_STEPS, 
         'search_flags':fgl_flags}
        actor_transform, routing_surface = self.putdown_jig.get_transform((self.carry_target), starting_location_override=starting_location, fgl_kwargs=fgl_kwargs)
        if actor_transform is None:
            return
        return actor_transform

    def build_basic_content(self, sequence, **kwargs):
        sequence = (super(SuperInteraction, self).build_basic_content)(sequence, **kwargs)

        def change_cancelable_for_target_si(cancelable):
            if self._target_si is not None:
                target_si = self._target_si[0]
                target_si._cancelable_by_user = cancelable
                target_si.sim.ui_manager.update_interaction_cancel_status(target_si)

        def unparent_carried_sim(*_, **__):
            sim = self.carry_target or self.target
            routing_surface = sim.routing_surface
            new_location = sim.location.clone(parent=None, transform=(sim.location.world_transform), routing_surface=routing_surface)
            sim.set_location_without_distribution(new_location)
            sim.update_intended_position_on_active_lot(update_ui=True)

        carry_system_target = self._get_carry_system_target(unparent_carried_sim)
        target_si_cancelable = self._target_si[0]._cancelable_by_user
        carry_element_helper = CarryElementHelper(interaction=self, carry_system_target=carry_system_target,
          sequence=sequence)
        sequence = carry_element_helper.exit_carry_while_holding(use_posture_animations=True)
        sequence = build_critical_section_with_finally((lambda _: change_cancelable_for_target_si(False)), sequence, (lambda _: change_cancelable_for_target_si(target_si_cancelable)))
        return sequence

    def perform_gen(self, timeline):
        self._must_run_instance = True
        return super().perform_gen(timeline)

    def _exited_pipeline(self, *args, **kwargs):
        if self._target_si is not None:
            target_interaction, _ = self._target_si
            if target_interaction is not None:
                target_interaction.unregister_on_finishing_callback(self._on_target_si_finished)
        return (super()._exited_pipeline)(*args, **kwargs)

    def _on_target_si_finished(self, interaction):
        interaction.unregister_on_finishing_callback(self._on_target_si_finished)
        if self._target_si is not None:
            target_interaction, _ = self._target_si
            if target_interaction is interaction:
                self._target_si = None

    def get_target_si(self):
        if self._target_si is None:
            self._target_si = self.put_down_behavior.get_target_si(self)
            target_interaction, _ = self._target_si
            if target_interaction is not None:
                target_interaction.register_on_finishing_callback(self._on_target_si_finished)
        return self._target_si

    def _get_carry_system_target(self, callback):
        raise NotImplementedError

    def set_target(self, target):
        if self._target_si is not None:
            if self._target_si[0].target is self.target:
                self._target_si[0].set_target(target)
        super().set_target(target)


class PutDownSimInObjectInteraction(PutDownSimInteraction):

    def _get_carry_system_target(self, callback):
        carry_system_target = CarrySystemCustomAnimationTarget(self.carry_target, True)
        carry_system_target.carry_event_callback = callback
        return carry_system_target


class PutDownSimOnRoutableSurfaceInteraction(PutDownSimInteraction):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._terrain_transform = UNSET

    def _get_best_location(self, obj, target):
        routing_surface = getattr(self.target, 'provided_routing_surface', None)
        if routing_surface is None:
            routing_surface = target.routing_surface
        if self._terrain_transform is UNSET:
            if self.putdown_jig is not None:
                putdown_jig_transform = self._get_putdown_jig_transform(target.location)
                if putdown_jig_transform is not None:
                    translation, orientation = putdown_jig_transform.translation, putdown_jig_transform.orientation
                    self._terrain_transform = Transform(translation, orientation) if translation is not None else None
                else:
                    logger.error('{} failed to find a good location using the putdown jig.', self)
            elif target.is_terrain:
                self._terrain_transform = target.transform
            if self._terrain_transform is UNSET:
                translation, orientation, _ = CarryingObject.get_good_location_on_floor(obj, starting_transform=(target.transform), starting_routing_surface=routing_surface, additional_search_flags=(FGLSearchFlag.STAY_IN_CURRENT_BLOCK))
                self._terrain_transform = Transform(translation, orientation) if translation is not None else None
        return (
         self._terrain_transform, routing_surface)

    def _get_carry_system_target(self, callback):
        transform, routing_surface = self._get_best_location(self.carry_target, self.target)
        transform = Transform(transform.translation, self.sim.orientation)
        surface_height = services.terrain_service.terrain_object().get_routing_surface_height_at(transform.translation.x, transform.translation.z, routing_surface)
        transform.translation = Vector3(transform.translation.x, surface_height, transform.translation.z)
        return CarrySystemTerrainTarget((self.sim), (self.carry_target), True, transform, routing_surface=routing_surface,
          custom_event_callback=callback)

    @flexmethod
    def _constraint_gen(cls, inst, sim, target, participant_type=ParticipantType.Actor, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        yield from (super(PutDownSimInteraction, inst_or_cls)._constraint_gen)(sim, target, participant_type=participant_type, **kwargs)
        if participant_type != ParticipantType.Actor:
            return
        if inst is not None:
            transform, routing_surface = inst._get_best_location(inst.carry_target, inst.target)
            if transform is None:
                yield interactions.constraints.Nowhere('Unable to find good location to execute Put Down')
            yield create_put_down_on_ground_constraint(sim, (inst.carry_target), transform, routing_surface=routing_surface)


class PutDownSimAnywhereInteraction(PutDownSimInteraction):

    def __init__(self, *args, slot_types_and_costs, world_cost, sim_inventory_cost, object_inventory_cost, terrain_transform, terrain_routing_surface, objects_with_inventory, visibility_override=None, display_name_override=None, debug_name=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._terrain_transform = UNSET
        self._terrain_routing_surface = terrain_routing_surface
        self._world_cost = world_cost

    def _get_carry_system_target(self, callback):
        self._get_best_location()
        if self._terrain_transform is UNSET or self._terrain_transform is None:
            return
        return CarrySystemTerrainTarget((self.sim), (self.target), True, (self._terrain_transform), custom_event_callback=callback)

    def _adjust_location(self):
        if self.putdown_jig is not None:
            if self._terrain_transform is not None:
                terrain_location = sims4.math.Location(self._terrain_transform, self._terrain_routing_surface)
                putdown_jig_transform = self._get_putdown_jig_transform(terrain_location)
                translation, orientation = putdown_jig_transform.translation, putdown_jig_transform.orientation
                self._terrain_transform = Transform(translation, orientation) if translation is not None else None

    def _get_best_location(self):
        if self._terrain_transform is not UNSET:
            if self._terrain_transform is not None:
                return
        carryable_component = self._target.carryable_component
        if carryable_component is not None:
            terrain_transform, terrain_routing_surface = carryable_component._get_terrain_transform(self)
            if terrain_transform is None or terrain_routing_surface is None:
                logger.error('Failed to get terrain transform or terrain routing surface for PutDownSimAnywhereInteraction interaction: {}', self)
                return
            surface_height = services.terrain_service.terrain_object().get_routing_surface_height_at(terrain_transform.translation.x, terrain_transform.translation.z, terrain_routing_surface)
            terrain_transform.translation = Vector3(terrain_transform.translation.x, surface_height, terrain_transform.translation.z)
            terrain_transform.orientation = self.sim.transform.orientation
            self._terrain_transform = terrain_transform
            self._terrain_routing_surface = terrain_routing_surface
            self._adjust_location()

    @flexmethod
    def _constraint_gen(cls, inst, sim, target, participant_type=ParticipantType.Actor, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        yield from (super(PutDownSimInteraction, inst_or_cls)._constraint_gen)(sim, target, participant_type=participant_type, **kwargs)
        if participant_type != ParticipantType.Actor:
            return
        if inst is not None:
            inst._get_best_location()
            if inst._terrain_transform is UNSET or inst._terrain_transform is None:
                yield Anywhere()
                return
            constraint = create_put_down_on_ground_constraint(sim, target, (inst._terrain_transform), routing_surface=(inst._terrain_routing_surface),
              cost=(inst._world_cost))
            if target.sim_info.is_toddler:
                transform_constraint = interactions.constraints.Transform((sim.transform), routing_surface=(sim.routing_surface))
                transform_constraint = transform_constraint.intersect(constraint)
                if transform_constraint.valid:
                    constraint = transform_constraint
            yield constraint