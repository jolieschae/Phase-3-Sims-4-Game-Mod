# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\set_posture_with_target_element.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 11150 bytes
import _math, animation, element_utils, elements, services, sims4
from animation.arb_element import distribute_arb_element
from animation.posture_manifest import Hand
from interactions import ParticipantType
from interactions.aop import AffordanceObjectPair
from interactions.context import InteractionContext, QueueInsertStrategy
from interactions.priority import Priority
from interactions.utils.interaction_elements import XevtTriggeredElement
from objects.set_location_element import TunableTransform
from postures.posture_specs import PostureSpecVariable
from postures.posture_state import PostureState
from postures.transition import PostureTransition
from sims4.tuning.tunable import TunableEnumEntry, OptionalTunable, TunableReference, TunableTuple, TunableVariant, HasTunableSingletonFactory, AutoFactoryInit
from sims4.tuning.tunable_hash import TunableStringHash32
logger = sims4.log.Logger('SetPostureWithTarget', default_owner='yozhang')

def _create_new_posture(sim, source_affordance, posture_target):
    var_map = {PostureSpecVariable.HAND: Hand.LEFT}
    aop = AffordanceObjectPair(source_affordance, posture_target, source_affordance, None)
    body_operation = aop.get_provided_posture_change()
    new_posture_spec = body_operation.apply(sim.posture_state.get_posture_spec(var_map))
    new_posture_state = PostureState(sim, sim.posture_state, new_posture_spec, var_map)
    new_posture = new_posture_state.body
    old_posture = sim.posture_state.body
    return (
     new_posture, new_posture_state, old_posture, var_map, aop)


class _SnapObject(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'snap_actor_participant':TunableEnumEntry(description='\n            The actor object or sim we want to snap.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'snap_target_participant':TunableEnumEntry(description='\n            The target object or sim we want to snap onto.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Object), 
     'offset_transform':TunableTransform(description='\n            The offset to apply. By default we apply the exact transform of the target to the actor.\n            Use this tuning to adjust the position and orientation of the snapped object.\n            ')}

    def run(self, interaction):
        snap_actor_object = interaction.get_participant(self.snap_actor_participant)
        snap_target_object = interaction.get_participant(self.snap_target_participant)
        if snap_target_object is None or snap_actor_object is None:
            logger.error("Can't snap for SetPostureWithTarget because actor or target is None: {}", interaction)
            return False
        base_transform = snap_target_object.transform
        snap_transform = _math.Transform.concatenate(self.offset_transform, base_transform)
        snap_actor_object.transform = snap_transform
        if snap_actor_object.is_sim:
            snap_actor_object.update_intended_position_on_active_lot()
        return True


class _ParentObject(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'child_participant':TunableEnumEntry(description='\n            The child object.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'parent_participant':TunableEnumEntry(description='\n            The parent object we are parenting to.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Object), 
     'joint_name':TunableStringHash32(description='\n            The name of the joint to use for the parenting.\n            ')}

    def run(self, interaction):
        child_object = interaction.get_participant(self.child_participant)
        parent_object = interaction.get_participant(self.parent_participant)
        if child_object is None or parent_object is None:
            logger.error("Can't parent for SetPostureWithTarget because child or parent object is None: {}", interaction)
            return False
        child_object.set_parent(parent_object, (sims4.math.Transform.IDENTITY()), joint_name_or_hash=(self.joint_name))
        return True


class SetPostureWithTarget(XevtTriggeredElement):
    FACTORY_TUNABLES = {'posture_participant':TunableEnumEntry(description='\n            The participant that we will set posture on.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'target_participant':OptionalTunable(description='\n            The posture target participant.\n            ',
       tunable=TunableEnumEntry(tunable_type=ParticipantType,
       default=(ParticipantType.Object))), 
     'source_affordance':TunableReference(description='\n            The source interaction that will provide the posture.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION)), 
     'mimic_animation_event':TunableVariant(description='\n            Snap or parent objects accordingly. (We skipped enter/exit anim clips, \n            if there are snap or parent events authored in those clips, we might\n            want to mimic them here)\n            ',
       snap_object=_SnapObject.TunableFactory(),
       parent_object=_ParentObject.TunableFactory(),
       locked_args={'disabled': None},
       default='disabled')}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._sim = None
        self._posture_target = None

    def _do_behavior(self):
        posture_type = None if self.source_affordance is None else self.source_affordance.provided_posture_type
        if posture_type is None:
            logger.error("Source affordance {} doesn't provide posture.", self.source_affordance)
            return
        self._sim = self.interaction.get_participant(self.posture_participant)
        if self._sim is None:
            logger.error('Trying to set a posture on a None participant.\n  Interaction: {}\n  Participant:{}', self.interaction, self.posture_participant)
            return
        self._posture_target = self.interaction.get_participant(self.target_participant)
        if self._posture_target is not None:
            if self._posture_target.parts is not None:
                compatible_parts = (part for part in self._posture_target.parts if part.supports_posture_type(posture_type))
                if compatible_parts:
                    self._posture_target = next(compatible_parts)
        sim_timeline = services.time_service().sim_timeline
        return sim_timeline.schedule(elements.GeneratorElement(self._set_posture_gen))

    def _set_posture_gen(self, timeline):
        new_posture, new_posture_state, old_posture, var_map, aop = _create_new_posture(self._sim, self.source_affordance, self._posture_target)
        if self.mimic_animation_event:
            if not self.mimic_animation_event.run(self.interaction):
                return False
        transition_arb = animation.arb.Arb()
        locked_params = new_posture.get_locked_params(None)
        old_posture.append_exit_to_arb(transition_arb, new_posture_state, new_posture, var_map)
        new_posture.append_transition_to_arb(transition_arb, old_posture, locked_params=locked_params)
        distribute_arb_element(transition_arb)
        context = InteractionContext((self._sim), (InteractionContext.SOURCE_POSTURE_GRAPH), priority=(Priority.High),
          insert_strategy=(QueueInsertStrategy.FIRST),
          must_run_next=False)
        result = aop.interaction_factory(context)
        if not result:
            logger.error('Failed to create source interaction.')
            return False
        new_posture.source_interaction = result.interaction
        new_posture.source_interaction.disable_transitions = True
        aop.execute_interaction(new_posture.source_interaction)
        posture_transition = PostureTransition(new_posture, new_posture_state, context, var_map)
        posture_transition.must_run = True
        yield from element_utils.run_child(timeline, posture_transition)
        if False:
            yield None