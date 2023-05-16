# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\carry\carry_elements.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 70464 bytes
import functools
from animation import ClipEventType
from animation.animation_utils import flush_all_animations, disable_asm_auto_exit
from animation.arb import Arb
from animation.arb_element import distribute_arb_element
from carry.carry_tuning import CarryPostureStaticTuning, CarryTuning
from carry.carry_utils import hand_to_track, track_to_hand, SCRIPT_EVENT_ID_START_CARRY, SCRIPT_EVENT_ID_STOP_CARRY
from element_utils import build_element, build_critical_section, must_run, build_critical_section_with_finally
from event_testing.resolver import SingleSimResolver
from interactions import ParticipantType, ParticipantTypeSingleSim
from interactions.aop import AffordanceObjectPair
from interactions.context import QueueInsertStrategy, InteractionContext
from interactions.priority import Priority
from objects import ALL_HIDDEN_REASONS
from objects.components.types import CARRYABLE_COMPONENT
from postures import PostureTrack
from postures.context import PostureContext
from postures.posture_specs import PostureSpecVariable, PostureOperation, PostureAspectBody, PostureAspectSurface
from postures.transition import PostureTransition
from sims4.log import StackVar
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, HasTunableSingletonFactory, TunableEnumEntry, TunableVariant, TunableTuple, TunablePackSafeReference, OptionalTunable
from sims4.tuning.tunable_hash import TunableStringHash32
from singletons import DEFAULT
import element_utils, elements, services, sims4.log, sims4.resources
from postures.posture_state import PostureState
logger = sims4.log.Logger('Carry', default_owner='yozhang')

def _create_enter_carry_posture(sim, posture_state, carry_target, track):
    if not carry_target.has_component(CARRYABLE_COMPONENT):
        raise RuntimeError('Carry target {}({}) is not carryable!\n\nSI State:\n    {}'.format(carry_target, getattr(carry_target, 'definition', '#DEFINITION_UNKNOWN#'), '\n    '.join((str(si) for si in sim.si_state))))
    hand = track_to_hand(track)
    var_map = {PostureSpecVariable.CARRY_TARGET: carry_target, 
     PostureSpecVariable.HAND: hand, 
     PostureSpecVariable.POSTURE_TYPE_CARRY_OBJECT: carry_target.get_carry_object_posture(carrying_hand=hand)}
    pick_up_operation = PostureOperation.PickUpObject(PostureSpecVariable.POSTURE_TYPE_CARRY_OBJECT, PostureSpecVariable.CARRY_TARGET)
    new_source_aop = pick_up_operation.associated_aop(sim, var_map)
    new_posture_spec = pick_up_operation.apply((posture_state.get_posture_spec(var_map)), enter_carry_while_holding=True)
    if new_posture_spec is None:
        raise RuntimeError('Failed to create new_posture_spec in enter_carry_while_holding!\n\nSI State:\n    {}'.format('\n    '.join((str(si) for si in sim.si_state))))
    new_posture_state = PostureState(sim, posture_state, new_posture_spec, var_map)
    new_posture = new_posture_state.get_aspect(track)
    from carry.carry_postures import CarryingNothing
    if new_posture is None or isinstance(new_posture, CarryingNothing):
        raise RuntimeError('Failed to create a valid new_posture ({}) from new_posture_state ({}) in enter_carry_while_holding!\n\nSI State:\n    {}'.format(new_posture, new_posture_state, '\n    '.join((str(si) for si in sim.si_state))))
    new_posture.external_transition = True
    return (
     new_posture_state, new_posture, new_source_aop, var_map)


def _create_exit_carry_posture(sim, target, interaction, use_posture_animations, preserve_posture=None):
    failure_result = (None, None, None, None, None)
    slot_manifest = interaction.slot_manifest
    old_carry_posture = sim.posture_state.get_carry_posture(target)
    if old_carry_posture is None:
        return failure_result
        spec_surface = sim.posture_state.spec.surface
        has_slot_surface = spec_surface is not None and spec_surface.slot_type is not None
        if not target.transient:
            if has_slot_surface and slot_manifest is not None:
                put_down_operation = PostureOperation.PutDownObjectOnSurface(PostureSpecVariable.POSTURE_TYPE_CARRY_NOTHING, spec_surface.target, spec_surface.slot_type, PostureSpecVariable.CARRY_TARGET)
    else:
        put_down_operation = PostureOperation.PutDownObject(PostureSpecVariable.POSTURE_TYPE_CARRY_NOTHING, PostureSpecVariable.CARRY_TARGET)
    var_map = {PostureSpecVariable.CARRY_TARGET: target, 
     PostureSpecVariable.HAND: track_to_hand(old_carry_posture.track), 
     PostureSpecVariable.POSTURE_TYPE_CARRY_NOTHING: CarryPostureStaticTuning.POSTURE_CARRY_NOTHING, 
     PostureSpecVariable.SLOT: slot_manifest, 
     PostureSpecVariable.SLOT_TEST_DEFINITION: interaction.create_target}
    current_spec = sim.posture_state.get_posture_spec(var_map)
    if current_spec is None:
        if preserve_posture is None:
            logger.warn('Failed to get posture spec for var_map: {} for {}', sim.posture_state, var_map)
        return failure_result
    new_posture_spec = put_down_operation.apply(current_spec)
    if new_posture_spec is None:
        if preserve_posture is None:
            logger.warn('Failed to apply put_down_operation: {}', put_down_operation)
        return failure_result
    if not new_posture_spec.validate_destination((new_posture_spec,), var_map, interaction.affordance, sim):
        if preserve_posture is None:
            logger.warn('Failed to validate put down spec {}  with var map {}', new_posture_spec, var_map)
        return failure_result
    carry_posture_overrides = {}
    if preserve_posture is not None:
        carry_posture_overrides[preserve_posture.track] = preserve_posture
    new_posture_state = PostureState(sim, (sim.posture_state), new_posture_spec, var_map, carry_posture_overrides=carry_posture_overrides)
    new_posture = new_posture_state.get_aspect(old_carry_posture.track)
    new_posture.source_interaction = interaction.super_interaction
    new_posture.external_transition = not use_posture_animations
    posture_context = PostureContext(interaction.context.source, interaction.priority, None)
    transition = PostureTransition(new_posture, new_posture_state, posture_context, var_map, locked_params=(interaction.locked_params))
    transition.must_run = True
    return (
     old_carry_posture, new_posture, new_posture_state, transition, var_map)


def run_fixup_carryable_sims(sims_to_run_carry):

    def make_carry_gen(sim_infos_for_carry):

        def _enter_carry_immediately_element_gen(timeline):
            carryable_sims = dict()
            carrying_sims = []
            fixup_rule = CarryTuning.CARRYABLE_SIMS_FIXUP_RULES

            def _get_priority_score(resolver):
                return fixup_rule.priority_test_sums.get_modified_value(resolver)

            for sim_info in sim_infos_for_carry:
                sim_to_fixup = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
                if sim_to_fixup is None:
                    continue
                else:
                    resolver = SingleSimResolver(sim_info)
                    if fixup_rule.carryable_sim_eligibility_tests.run_tests(resolver):
                        carryable_sims[sim_to_fixup] = _get_priority_score(resolver)
                if fixup_rule.carrying_sim_eligibility_tests.run_tests(resolver):
                    carrying_sims.append(sim_to_fixup)

            sorted_carryable_sims = [k for k, v in sorted((carryable_sims.items()), key=(lambda x: x[1]),
              reverse=True)]
            sorted_carry_rules = sorted((fixup_rule.carry_hand_affordance_mappings.items()), key=(lambda x: x[0]))
            for carry_track, affordance_joint_pairs in sorted_carry_rules:
                for sim in carrying_sims:
                    if not sorted_carryable_sims:
                        return
                        processed = False
                        for affordance_joint_pair in affordance_joint_pairs:
                            owning_affordance = affordance_joint_pair.owning_affordance
                            if owning_affordance is None:
                                continue
                            for carryable_sim in sorted_carryable_sims:
                                carry_element_helper = CarryElementHelper(sim=sim, carry_target=carryable_sim,
                                  owning_affordance=owning_affordance,
                                  carry_track=carry_track)
                                carry_element = carry_element_helper.build_enter_carry_immediately_element(parenting_joint=(affordance_joint_pair.parenting_joint))
                                if carry_element is not None:
                                    sorted_carryable_sims.remove(carryable_sim)
                                    processed = True
                                    yield from element_utils.run_child(timeline, carry_element)
                                    break

                            if processed:
                                break

            if False:
                yield None

        return _enter_carry_immediately_element_gen

    timeline = services.time_service().sim_timeline
    timeline.schedule(elements.GeneratorElement(make_carry_gen(sims_to_run_carry)), timeline.now)


class CarryElementHelper:

    def __init__(self, sim=DEFAULT, carry_target=DEFAULT, interaction=None, sim_participant_type=ParticipantType.Actor, si_target_participant_type=None, si_target_override=None, carry_target_participant_type=None, owning_affordance=None, carry_track=DEFAULT, asm_context=None, create_owning_si_fn=DEFAULT, callback=None, sequence=(), carry_system_target=None, priority_override=None):
        self.sim = sim
        self.carry_target = carry_target
        self.interaction = interaction
        self.owning_affordance = owning_affordance
        self.carry_track = carry_track if carry_track is not None else DEFAULT
        self.asm_context = asm_context
        self.create_owning_si_fn = create_owning_si_fn
        self.callback = callback
        self.sequence = sequence
        self.carry_system_target = carry_system_target
        self.priority_override = priority_override
        self.si = None
        self.si_target = None
        if self.interaction is not None:
            self.si = interaction.super_interaction
            if self.sim is DEFAULT:
                self.sim = self.interaction.get_participant(sim_participant_type) if sim_participant_type is not None else None
            elif si_target_override is None:
                self.si_target = self.si.get_participant(si_target_participant_type) if si_target_participant_type is not None else None
            else:
                self.si_target = si_target_override
            if carry_target_participant_type is not None:
                if self.carry_target is DEFAULT:
                    self.carry_target = self.interaction.get_participant(carry_target_participant_type)
            if self.carry_target is DEFAULT:
                self.carry_target = self.interaction.carry_target or self.interaction.target
            if self.carry_track is DEFAULT:
                self.carry_track = self.interaction.carry_track
        if self.si_target is None:
            self.si_target = self.carry_target
        if self.sim is DEFAULT or self.sim is None:
            raise ValueError('carry sim not defined.')
        if self.carry_target is DEFAULT or self.carry_target is None:
            raise ValueError('carry target not defined.')
        self.owning_interaction_context = None
        self.anim_was_played = False

    def _get_default_create_owning_si_fn(self):
        self.owning_interaction_context.carry_target = self.carry_target
        aop = AffordanceObjectPair(self.owning_affordance, self.si_target, self.owning_affordance, None)
        return (aop, self.owning_interaction_context)

    def _do_exit_carry(self, old_carry_posture, new_posture, var_map):
        arb_exit = Arb()
        old_carry_posture.append_exit_to_arb(arb_exit, None, new_posture, var_map, exit_while_holding=True)
        new_posture.append_transition_to_arb(arb_exit, old_carry_posture, in_xevt_handler=True)
        distribute_arb_element(arb_exit, master=(self.sim))

    def _do_enter_carry(self, old_posture, new_carry_posture_state, new_carry_posture, var_map, event_data=None):
        if self.anim_was_played:
            if event_data is not None:
                logger.warn('Animation({}) calling to start a carry multiple times', event_data.event_data.get('clip_name'))
            else:
                logger.warn('Carry element ({}) calling to start a carry multiple times', self)
            return
        self.anim_was_played = True
        arb = Arb()
        locked_params = new_carry_posture.get_locked_params(None)
        if old_posture is not None:
            old_posture.append_exit_to_arb(arb, new_carry_posture_state, new_carry_posture, var_map)
        new_carry_posture.append_transition_to_arb(arb, old_posture, locked_params=locked_params, in_xevt_handler=True)
        distribute_arb_element(arb)

    def _do_push_si_gen(self, timeline, new_source_aop, new_posture):
        if self.interaction is not None:
            source_interaction_context = InteractionContext((self.sim), (InteractionContext.SOURCE_POSTURE_GRAPH), (self.interaction.priority if self.priority_override is None else self.priority_override),
              run_priority=(self.interaction.run_priority if self.priority_override is None else self.priority_override),
              insert_strategy=(QueueInsertStrategy.FIRST),
              must_run_next=True,
              group_id=(self.interaction.group_id))
        else:
            source_interaction_context = InteractionContext((self.sim), (InteractionContext.SOURCE_POSTURE_GRAPH), priority=(Priority.High),
              insert_strategy=(QueueInsertStrategy.FIRST),
              must_run_next=False)
        result = new_source_aop.interaction_factory(source_interaction_context)
        if not result:
            return result
        source_interaction = result.interaction
        new_posture.source_interaction = source_interaction
        owning_interaction = None
        if self.create_owning_si_fn is not None:
            aop, owning_interaction_context = self.create_owning_si_fn()
            if aop is not None:
                if owning_interaction_context is not None:
                    if aop.test(owning_interaction_context):
                        result = aop.interaction_factory(owning_interaction_context)
                        if result:
                            owning_interaction = result.interaction
        if owning_interaction is None and self.interaction is not None:
            self.interaction.acquire_posture_ownership(new_posture)
            yield from source_interaction.run_direct_gen(timeline)
        else:
            if owning_interaction is not None:
                owning_interaction.acquire_posture_ownership(new_posture)
                aop.execute_interaction(owning_interaction)
                new_source_aop.execute_interaction(source_interaction)
            return result
        if False:
            yield None

    def build_enter_carry_immediately_element(self, parenting_joint=None):
        self.owning_interaction_context = InteractionContext((self.sim), (InteractionContext.SOURCE_SCRIPT), (Priority.High), insert_strategy=(QueueInsertStrategy.FIRST))
        if not self.owning_affordance.test(target=(self.carry_target), context=(self.owning_interaction_context)):
            return
        self.create_owning_si_fn = self._get_default_create_owning_si_fn

        def set_up_transition_gen(timeline):
            new_posture_state, new_posture, new_source_aop, var_map = _create_enter_carry_posture(self.sim, self.sim.posture_state, self.carry_target, self.carry_track)
            if self.carry_target.is_sim:
                target_posture_state = new_posture.set_target_linked_posture_data()
            else:
                target_posture_state = None
            old_carry_posture = self.sim.posture_state.get_aspect(self.carry_track)
            self._do_enter_carry(old_carry_posture, new_posture_state, new_posture, var_map)
            if parenting_joint is not None:
                self.carry_target.set_parent((self.sim), (sims4.math.Transform.IDENTITY()), joint_name_or_hash=parenting_joint)

            def maybe_do_transition_gen(timeline):

                def push_si_gen(timeline):
                    result = yield from self._do_push_si_gen(timeline, new_source_aop, new_posture)
                    if target_posture_state is not None:
                        yield from new_posture.kickstart_linked_carried_posture_gen(timeline)
                    return result
                    if False:
                        yield None

                def call_callback(_):
                    if self.callback is not None:
                        self.callback(new_posture, new_posture.source_interaction)

                def appearance_modifier_call_callback(_):
                    evet_handler_appearance_modifier_entry = new_posture.get_appearance_modifier_entry_event()
                    if evet_handler_appearance_modifier_entry is not None:
                        evet_handler_appearance_modifier_entry()

                if target_posture_state is not None:
                    self.carry_target.posture_state = target_posture_state
                result = yield from element_utils.run_child(timeline, must_run([
                 PostureTransition(new_posture, new_posture_state, self.owning_interaction_context, var_map), push_si_gen,
                 call_callback, appearance_modifier_call_callback]))
                return result
                if False:
                    yield None

            yield from element_utils.run_child(timeline, must_run(build_critical_section(flush_all_animations, maybe_do_transition_gen)))
            if False:
                yield None

        return build_element((self.sequence, set_up_transition_gen))

    def enter_carry_while_holding(self):
        self.owning_interaction_context = self.interaction.context.clone_for_sim((self.sim), insert_strategy=(QueueInsertStrategy.NEXT))
        if self.owning_interaction_context.source == InteractionContext.SOURCE_CARRY_CANCEL_AOP:
            self.owning_interaction_context.source = InteractionContext.SOURCE_POSTURE_GRAPH
        if self.priority_override is not None:
            self.owning_interaction_context.priority = self.priority_override
        if self.carry_track is None:
            raise RuntimeError("[rmccord] enter_carry_while_holding: Interaction {} does not have a carry_track, which means its animation tuning doesn't have a carry target or create target specified in object editor or the posture manifest from the swing graph does not require a specific object. {}".format(self.interaction, StackVar(('process',
                                                                                                                                                                                                                                                                                                                                                  '_auto_constraints'))))
        if self.create_owning_si_fn is DEFAULT:
            if self.owning_affordance is None:
                self.create_owning_si_fn = None
        if self.create_owning_si_fn is DEFAULT:
            if self.owning_affordance is DEFAULT:
                raise AssertionError("[rmccord] No create_owning_si_fn was provided and we don't know how to make one.")
            self.create_owning_si_fn = self._get_default_create_owning_si_fn

        def set_up_transition_gen(timeline):
            new_posture_state, new_posture, new_source_aop, var_map = _create_enter_carry_posture(self.sim, self.sim.posture_state, self.carry_target, self.carry_track)
            if self.carry_target.is_sim:
                target_posture_state = new_posture.set_target_linked_posture_data()
            else:
                target_posture_state = None

            def event_handler_enter_carry(event_data):
                old_carry_posture = self.sim.posture_state.get_aspect(self.carry_track)
                self._do_enter_carry(old_carry_posture, new_posture_state, new_posture, var_map, event_data=event_data)

            if self.asm_context is not None:
                self.asm_context.register_event_handler(event_handler_enter_carry, handler_type=(ClipEventType.Script), handler_id=SCRIPT_EVENT_ID_START_CARRY, tag='enter_carry')
            else:
                self.interaction.store_event_handler(event_handler_enter_carry, handler_id=SCRIPT_EVENT_ID_START_CARRY)

            def maybe_do_transition_gen(timeline):

                def push_si_gen(timeline):
                    result = yield from self._do_push_si_gen(timeline, new_source_aop, new_posture)
                    if target_posture_state is not None:
                        yield from new_posture.kickstart_linked_carried_posture_gen(timeline)
                    return result
                    if False:
                        yield None

                def call_callback(_):
                    if self.callback is not None:
                        self.callback(new_posture, new_posture.source_interaction)

                if self.anim_was_played:
                    if target_posture_state is not None:
                        self.carry_target.posture_state = target_posture_state
                    result = yield from element_utils.run_child(timeline, must_run([
                     PostureTransition(new_posture, new_posture_state, self.owning_interaction_context, var_map), push_si_gen, call_callback]))
                    return result
                return True
                if False:
                    yield None

            self.sequence = disable_asm_auto_exit(self.sim, self.sequence)
            with self.interaction.cancel_deferred((self.interaction,)):
                yield from element_utils.run_child(timeline, must_run(build_critical_section(build_critical_section(self.sequence, flush_all_animations), maybe_do_transition_gen)))
            if False:
                yield None

        return build_element(set_up_transition_gen)

    def exit_carry_while_holding(self, use_posture_animations=False, arb=None):

        def set_up_transition_gen(timeline):
            old_carry_posture, new_posture, _, transition, var_map = _create_exit_carry_posture(self.sim, self.carry_target, self.interaction, use_posture_animations)
            if transition is None:
                yield from element_utils.run_child(timeline, self.sequence)
                return
            elif arb is None:
                register_event = functools.partial((self.interaction.store_event_handler), handler_id=SCRIPT_EVENT_ID_STOP_CARRY)
            else:
                register_event = functools.partial((arb.register_event_handler), handler_id=SCRIPT_EVENT_ID_STOP_CARRY)
            exited_carry = False
            if not use_posture_animations:

                def event_handler_exit_carry(event_data):
                    nonlocal exited_carry
                    exited_carry = True
                    self._do_exit_carry(old_carry_posture, new_posture, var_map)

                register_event(event_handler_exit_carry)
            if self.callback is not None:
                register_event(self.callback)

            def maybe_do_transition(timeline):
                nonlocal transition
                _, _, _, new_transition, _ = _create_exit_carry_posture((self.sim), (self.carry_target), (self.interaction), use_posture_animations, preserve_posture=new_posture)
                if new_transition is not None:
                    transition = new_transition
                if not use_posture_animations:
                    if not exited_carry:
                        event_handler_exit_carry(None)
                        if self.callback is not None:
                            self.callback()
                if use_posture_animations or exited_carry:
                    interaction_target_was_target = False
                    si_target_was_target = False
                    if old_carry_posture.target_is_transient:
                        if self.interaction.target == self.carry_target:
                            interaction_target_was_target = True
                            self.interaction.set_target(None)
                        if self.si.target == self.carry_target:
                            si_target_was_target = True
                            self.si.set_target(None)
                    if self.carry_system_target is not None:
                        old_carry_posture.carry_system_target = self.carry_system_target

                    def do_transition(timeline):
                        result = yield from element_utils.run_child(timeline, transition)
                        if result:
                            if self.carry_target.is_sim:
                                body_posture_type = self.sim.posture_state.spec.body.posture_type
                                if not body_posture_type.multi_sim:
                                    post_transition_spec = self.sim.posture_state.spec.clone(body=(PostureAspectBody(body_posture_type, None)),
                                      surface=(PostureAspectSurface(None, None, None)))
                                    post_posture_state = PostureState(self.sim, self.sim.posture_state, post_transition_spec, var_map)
                                    post_posture_state.body.source_interaction = self.sim.posture.source_interaction
                                    post_transition = PostureTransition(post_posture_state.body, post_posture_state, self.sim.posture.posture_context, var_map)
                                    post_transition.must_run = True
                                    yield from element_utils.run_child(timeline, post_transition)
                            interaction_target_was_target = False
                            si_target_was_target = False
                            new_posture.source_interaction = None
                            return True
                        return False
                        if False:
                            yield None

                    def post_transition(_):
                        if interaction_target_was_target:
                            self.interaction.set_target(self.carry_target)
                        if si_target_was_target:
                            self.si.set_target(self.carry_target)
                        if self.carry_system_target is not None:
                            old_carry_posture.carry_system_target = None

                    yield from element_utils.run_child(timeline, must_run(build_critical_section_with_finally(do_transition, post_transition)))
                if False:
                    yield None

            self.sequence = disable_asm_auto_exit(self.sim, self.sequence)
            yield from element_utils.run_child(timeline, build_critical_section(build_critical_section(self.sequence, flush_all_animations), maybe_do_transition))
            if False:
                yield None

        return build_element(set_up_transition_gen)

    def swap_carry_while_holding(self, new_carry_target):

        def set_up_transition(timeline):
            original_carry_posture, carry_nothing_posture, carry_nothing_posture_state, transition_to_carry_nothing, carry_nothing_var_map = _create_exit_carry_posture(self.sim, self.carry_target, self.interaction, False)
            if transition_to_carry_nothing is None:
                return False
            final_posture_state, final_posture, final_source_aop, final_var_map = _create_enter_carry_posture(self.sim, carry_nothing_posture_state, new_carry_target, original_carry_posture.track)

            def event_handler_swap_carry(event_data):
                self._do_exit_carry(original_carry_posture, carry_nothing_posture, carry_nothing_var_map)
                original_carry_posture.target.transient = True
                original_carry_posture.target.clear_parent(self.sim.transform, self.sim.routing_surface)
                original_carry_posture.target.remove_from_client()
                self._do_enter_carry(carry_nothing_posture, final_posture_state, final_posture, final_var_map, event_data)

            self.interaction.store_event_handler(event_handler_swap_carry, handler_id=SCRIPT_EVENT_ID_START_CARRY)
            if self.callback is not None:
                self.interaction.store_event_handler((self.callback), handler_id=SCRIPT_EVENT_ID_START_CARRY)

            def maybe_do_transition(timeline):

                def push_si(_):
                    source_interaction_context = InteractionContext((self.sim), (InteractionContext.SOURCE_POSTURE_GRAPH),
                      (self.si.priority),
                      run_priority=(self.si.run_priority),
                      insert_strategy=(QueueInsertStrategy.NEXT),
                      must_run_next=True,
                      group_id=(self.si.group_id))
                    result = final_source_aop.interaction_factory(source_interaction_context)
                    if not result:
                        return result
                    final_source_interaction = result.interaction
                    self.si.acquire_posture_ownership(final_posture)
                    yield from final_source_interaction.run_direct_gen(timeline)
                    final_posture.source_interaction = final_source_interaction
                    return result
                    if False:
                        yield None

                if not self.anim_was_played:
                    event_handler_swap_carry(None)
                    if self.callback is not None:
                        self.callback()
                if self.anim_was_played:
                    if original_carry_posture.target_is_transient:
                        if self.interaction.target == self.carry_target:
                            interaction_target_was_target = True
                            self.interaction.set_target(None)
                        else:
                            interaction_target_was_target = False
                        if self.si.target == self.carry_target:
                            si_target_was_target = True
                            self.si.set_target(None)
                        else:
                            si_target_was_target = False
                    else:
                        interaction_target_was_target = False
                        si_target_was_target = False
                    if self.carry_system_target is not None:
                        original_carry_posture.carry_system_target = self.carry_system_target

                    def do_transition(timeline):
                        nonlocal interaction_target_was_target
                        nonlocal si_target_was_target
                        result = yield from element_utils.run_child(timeline, transition_to_carry_nothing)
                        if not result:
                            return False
                        interaction_target_was_target = False
                        si_target_was_target = False
                        carry_nothing_posture.source_interaction = None
                        return True
                        if False:
                            yield None

                    def post_transition(_):
                        if interaction_target_was_target:
                            self.interaction.set_target(self.carry_target)
                        if si_target_was_target:
                            self.si.set_target(self.carry_target)
                        if self.carry_system_target is not None:
                            original_carry_posture.carry_system_target = None

                    exit_carry_result = yield from element_utils.run_child(timeline, must_run(build_critical_section_with_finally(do_transition, post_transition)))
                    if not exit_carry_result:
                        raise RuntimeError('[maxr] Failed to exit carry: {}'.format(original_carry_posture))
                if self.anim_was_played:
                    self.owning_interaction_context = self.si.context.clone_for_sim(self.sim)
                    yield from element_utils.run_child(timeline, (
                     PostureTransition(final_posture, final_posture_state, self.owning_interaction_context, final_var_map), push_si))
                if False:
                    yield None

            self.sequence = disable_asm_auto_exit(self.sim, self.sequence)
            yield from element_utils.run_child(timeline, build_critical_section(build_critical_section(self.sequence, flush_all_animations), maybe_do_transition))
            if False:
                yield None

        return (
         set_up_transition,)

    def change_carry_while_holding(self):
        self.owning_interaction_context = self.interaction.context.clone_for_sim((self.sim), insert_strategy=(QueueInsertStrategy.NEXT))
        if self.priority_override is not None:
            self.owning_interaction_context.priority = self.priority_override
        if self.carry_track is None:
            raise RuntimeError("[yozhang] change_carry_while_holding: Interaction {} does not have a carry_track, which means its animation tuning doesn't have a carry target or create target specified in object editor or the posture manifest from the swing graph does not require a specific object. {}".format(self.interaction, StackVar(('process',
                                                                                                                                                                                                                                                                                                                                                   '_auto_constraints'))))
        if self.create_owning_si_fn is DEFAULT:
            if self.owning_affordance is None:
                self.create_owning_si_fn = None
        if self.create_owning_si_fn is DEFAULT:
            if self.owning_affordance is DEFAULT:
                raise AssertionError("[yozhang] No create_owning_si_fn was provided and we don't know how to make one.")
            self.create_owning_si_fn = self._get_default_create_owning_si_fn

        def set_up_transition_gen(timeline):
            original_carry_posture, carry_nothing_posture, carry_nothing_posture_state, transition_to_carry_nothing, carry_nothing_var_map = _create_exit_carry_posture(self.sim, self.si_target, self.interaction, False)
            if transition_to_carry_nothing is None:
                return False
                new_posture_state, new_posture, new_source_aop, var_map = _create_enter_carry_posture(self.sim, carry_nothing_posture_state, self.carry_target, self.carry_track)
                if self.carry_target.is_sim:
                    target_posture_state = new_posture.bind_target_linked_posture_data()
                else:
                    target_posture_state = None
                new_posture._carried_linked_posture._entry_anim_complete = False
                new_posture._carried_linked_posture._exit_anim_complete = False

                def event_handler_exit_carry(event_data):
                    self._do_exit_carry(original_carry_posture, carry_nothing_posture, carry_nothing_var_map)

                def event_handler_enter_carry(event_data):
                    self._do_enter_carry(carry_nothing_posture, new_posture_state, new_posture, var_map, event_data=event_data)

                evet_handler_appearance_modifier_entry = new_posture.get_appearance_modifier_entry_event()
                evet_handler_appearance_modifier_exit = original_carry_posture.get_appearance_modifier_exit_event()
                if self.asm_context is not None:
                    self.asm_context.register_event_handler(event_handler_exit_carry, handler_type=(ClipEventType.Script), handler_id=SCRIPT_EVENT_ID_STOP_CARRY,
                      tag='exit_carry')
                    self.asm_context.register_event_handler(event_handler_enter_carry, handler_type=(ClipEventType.Script), handler_id=SCRIPT_EVENT_ID_START_CARRY,
                      tag='enter_carry')
                    if evet_handler_appearance_modifier_entry is not None:
                        self.asm_context.register_event_handler(evet_handler_appearance_modifier_entry, handler_type=(ClipEventType.Script), handler_id=(new_posture.appearance_modifier.entry_xevt))
                    if evet_handler_appearance_modifier_exit is not None:
                        self.asm_context.register_event_handler(evet_handler_appearance_modifier_exit, handler_type=(ClipEventType.Script),
                          handler_id=(original_carry_posture.appearance_modifier.exit_xevt))
            else:
                self.interaction.store_event_handler(event_handler_exit_carry, handler_id=SCRIPT_EVENT_ID_STOP_CARRY)
                self.interaction.store_event_handler(event_handler_enter_carry, handler_id=SCRIPT_EVENT_ID_START_CARRY)
                if evet_handler_appearance_modifier_entry is not None:
                    self.interaction.store_event_handler(evet_handler_appearance_modifier_entry, handler_id=(new_posture.appearance_modifier.entry_xevt))
            if evet_handler_appearance_modifier_exit is not None:
                self.interaction.store_event_handler(evet_handler_appearance_modifier_exit, handler_id=(original_carry_posture.appearance_modifier.exit_xevt))

            def maybe_do_transition_gen(timeline):

                def push_si_gen(timeline):
                    result = yield from self._do_push_si_gen(timeline, new_source_aop, new_posture)
                    return result
                    if False:
                        yield None

                def call_callback(_):
                    if self.callback is not None:
                        self.callback(new_posture, new_posture.source_interaction)

                if self.anim_was_played:

                    def do_exit_transition(timeline):
                        result = yield from element_utils.run_child(timeline, transition_to_carry_nothing)
                        if not result:
                            return False
                        carry_nothing_posture.source_interaction = None
                        return True
                        if False:
                            yield None

                    exit_carry_result = yield from element_utils.run_child(timeline, must_run(do_exit_transition))
                    if not exit_carry_result:
                        raise RuntimeError('[yozhang] Failed to exit carry: {}'.format(original_carry_posture))
                    if target_posture_state is not None:
                        self.carry_target.posture_state = target_posture_state
                    result = yield from element_utils.run_child(timeline, must_run([
                     PostureTransition(new_posture, new_posture_state, self.owning_interaction_context, var_map),
                     push_si_gen, call_callback]))
                    return result
                return True
                if False:
                    yield None

            self.sequence = disable_asm_auto_exit(self.sim, self.sequence)
            with self.interaction.cancel_deferred((self.interaction,)):
                yield from element_utils.run_child(timeline, must_run(build_critical_section(build_critical_section(self.sequence, flush_all_animations), maybe_do_transition_gen)))
            if False:
                yield None

        return build_element(set_up_transition_gen)


class ChangeCarryWhileHolding(elements.ParentElement, HasTunableFactory, AutoFactoryInit):
    NONE = 1
    OBJECT_TO_BE_CARRIED = 2
    PARTICIPANT_TYPE = 3
    FACTORY_TUNABLES = {'carry_obj_participant_type':TunableEnumEntry(description='\n            The object that will be re-carried.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.CarriedObject), 
     'sim_participant_type':TunableEnumEntry(description='\n            The Sim that will get a new carry.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'target':TunableVariant(description='\n            Specify what to use as the target of\n            the owning affordance.\n            ',
       object_to_be_carried=TunableTuple(description='\n                Target is the object that WILL be carried.\n                ',
       locked_args={'target_type': OBJECT_TO_BE_CARRIED}),
       none=TunableTuple(description='\n                Target is None\n                ',
       locked_args={'target_type': NONE}),
       participant_type=TunableTuple(description='\n                Target is the specified participant of THIS interaction.\n                \n                This is necessary if we need to target another participant\n                when we push the owning affordance\n                ',
       participant=TunableEnumEntry(tunable_type=ParticipantType,
       default=(ParticipantType.CarriedObject)),
       locked_args={'target_type': PARTICIPANT_TYPE}),
       default='object_to_be_carried'), 
     'owning_affordance':TunablePackSafeReference(description='\n            The interaction that will be pushed that will own the carry\n            state.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION),
       allow_none=True), 
     'carry_track_override':OptionalTunable(description='\n            If enabled, specify which hand the Sim must use to carry the object,\n            instead of using the carry of the SI\n            ',
       tunable=TunableEnumEntry(description='\n                Which hand to carry the object.\n                ',
       tunable_type=PostureTrack,
       default=(PostureTrack.RIGHT)))}

    def __init__(self, interaction, *args, sequence=(), **kwargs):
        (super().__init__)(*args, **kwargs)
        self.interaction = interaction
        self.sequence = sequence

    def _run(self, timeline):
        target = self.target
        if target.target_type == EnterCarryWhileHolding.NONE:
            target_participant_type = None
        else:
            if target.target_type == EnterCarryWhileHolding.OBJECT_TO_BE_CARRIED:
                target_participant_type = self.carry_obj_participant_type
            else:
                if target.target_type == EnterCarryWhileHolding.PARTICIPANT_TYPE:
                    target_participant_type = target.participant
        carry_element_helper = CarryElementHelper(interaction=(self.interaction), sequence=(self.sequence),
          carry_target_participant_type=(self.carry_obj_participant_type),
          sim_participant_type=(self.sim_participant_type),
          si_target_participant_type=target_participant_type,
          owning_affordance=(self.owning_affordance),
          carry_track=(self.carry_track_override))
        carry_element = carry_element_helper.change_carry_while_holding()
        return timeline.run_child(carry_element)


class EnterCarryWhileHolding(elements.ParentElement, HasTunableFactory, AutoFactoryInit):

    class TrackOverrideExplicit(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'carry_track': TunableEnumEntry(description='\n                Which hand to carry the object in.\n                ',
                          tunable_type=PostureTrack,
                          default=(PostureTrack.RIGHT),
                          invalid_enums=(
                         PostureTrack.BODY,))}

        def get_override(self, *args, **kwargs):
            return self.carry_track

    class TrackOverrideHandedness(HasTunableSingletonFactory, AutoFactoryInit):

        def get_override(self, interaction, sim_participant, *args, **kwargs):
            carry_participant = interaction.get_participant(sim_participant)
            if carry_participant is None:
                return
            hand = carry_participant.get_preferred_hand()
            return hand_to_track(hand)

    NONE = 1
    OBJECT_TO_BE_CARRIED = 2
    PARTICIPANT_TYPE = 3
    FACTORY_TUNABLES = {'carry_obj_participant_type':TunableEnumEntry(description='\n            The object that will be carried.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.CarriedObject), 
     'sim_participant_type':TunableEnumEntry(description='\n            The Sim that will get a new carry.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'target':TunableVariant(description='\n            Specify what to use as the target of\n            the owning affordance.\n            ',
       object_to_be_carried=TunableTuple(description='\n                Target is the object that WILL be carried.\n                ',
       locked_args={'target_type': OBJECT_TO_BE_CARRIED}),
       none=TunableTuple(description='\n                Target is None\n                ',
       locked_args={'target_type': NONE}),
       participant_type=TunableTuple(description='\n                Target is the specified participant of THIS interaction.\n                \n                This is necessary if we need to target another participant\n                when we push the owning affordance\n                ',
       participant=TunableEnumEntry(tunable_type=ParticipantType,
       default=(ParticipantType.CarriedObject)),
       locked_args={'target_type': PARTICIPANT_TYPE}),
       default='object_to_be_carried'), 
     'owning_affordance':TunablePackSafeReference(description='\n            The interaction that will be pushed that will own the carry\n            state (e.g. a put down).\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION),
       allow_none=True), 
     'carry_track_override':TunableVariant(description='\n            Specify the carry track, instead of using the carry of the SI.\n            ',
       explicit=TrackOverrideExplicit.TunableFactory(),
       handedness=TrackOverrideHandedness.TunableFactory(),
       default='disabled',
       locked_args={'disabled': None}), 
     'enter_carry_immediately':OptionalTunable(description='\n            If enabled, we are gonna run this element immediately without waiting for the 700 XEvt.\n            ',
       tunable=TunableTuple(description='\n                The joint of the carrier sim to parent the carryable sim to.\n                ',
       parenting_joint=(TunableStringHash32())))}

    def __init__(self, interaction, *args, sequence=(), **kwargs):
        (super().__init__)(*args, **kwargs)
        self.interaction = interaction
        self.sequence = sequence

    def _run(self, timeline):
        carry_track_override = self.carry_track_override.get_override(self.interaction, self.sim_participant_type) if self.carry_track_override is not None else None
        target = self.target
        if target.target_type == EnterCarryWhileHolding.NONE:
            target_participant_type = None
        else:
            if target.target_type == EnterCarryWhileHolding.OBJECT_TO_BE_CARRIED:
                target_participant_type = self.carry_obj_participant_type
            else:
                if target.target_type == EnterCarryWhileHolding.PARTICIPANT_TYPE:
                    target_participant_type = target.participant
                else:
                    carry_element_helper = CarryElementHelper(interaction=(self.interaction), sequence=(self.sequence),
                      carry_target_participant_type=(self.carry_obj_participant_type),
                      sim_participant_type=(self.sim_participant_type),
                      si_target_participant_type=target_participant_type,
                      owning_affordance=(self.owning_affordance),
                      carry_track=carry_track_override)
                    if self.enter_carry_immediately is not None:
                        carry_element = carry_element_helper.build_enter_carry_immediately_element(self.enter_carry_immediately.parenting_joint)
                        if carry_element is not None:
                            services.time_service().sim_timeline.schedule(carry_element, timeline.now)
                            return True
                        logger.error('Enter Carry Immediately element failed: {}', self)
                        return False
                    else:
                        carry_element = carry_element_helper.enter_carry_while_holding()
                        return timeline.run_child(carry_element)


class ExitCarryWhileHolding(elements.ParentElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'sim_participant_type': TunableEnumEntry(description='\n            The Sim that will exit a carry.\n            ',
                               tunable_type=ParticipantTypeSingleSim,
                               default=(ParticipantTypeSingleSim.Actor))}

    def __init__(self, interaction, *args, sequence=(), **kwargs):
        (super().__init__)(*args, **kwargs)
        self.interaction = interaction
        self.sequence = sequence

    def _run(self, timeline):
        carry_element_helper = CarryElementHelper(interaction=(self.interaction), sequence=(self.sequence),
          sim_participant_type=(self.sim_participant_type))
        carry_element = carry_element_helper.exit_carry_while_holding()
        return timeline.run_child(carry_element)


class TransferCarryWhileHolding(elements.ParentElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'enter_carry_while_holding':EnterCarryWhileHolding.TunableFactory(), 
     'exit_carry_while_holding':ExitCarryWhileHolding.TunableFactory()}

    def __init__(self, interaction, *args, sequence=(), **kwargs):
        (super().__init__)(*args, **kwargs)
        self.interaction = interaction
        self.sequence = sequence

    def _run(self, timeline):
        obj = self.interaction.get_participant(self.enter_carry_while_holding.carry_obj_participant_type)
        source_sim = self.interaction.get_participant(self.exit_carry_while_holding.sim_participant_type)
        target_sim = self.interaction.get_participant(self.enter_carry_while_holding.sim_participant_type)

        def _add_reservation_clobberer(_):
            obj.add_reservation_clobberer(source_sim, target_sim)

        def _remove_reservation_clobberer(_):
            obj.remove_reservation_clobberer(source_sim, target_sim)

        sequence = self.enter_carry_while_holding((self.interaction), sequence=(self.sequence))
        sequence = self.exit_carry_while_holding((self.interaction), sequence=sequence)
        sequence = element_utils.build_critical_section_with_finally(_add_reservation_clobberer, sequence, _remove_reservation_clobberer)
        return timeline.run_child(sequence)