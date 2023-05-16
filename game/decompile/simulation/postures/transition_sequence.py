# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\transition_sequence.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 337270 bytes
import itertools
from _collections import defaultdict
from animation.animation_utils import flush_all_animations
from animation.posture_manifest import Hand, PostureManifest, AnimationParticipant, SlotManifest, MATCH_ANY, _NOT_SPECIFIC_ACTOR, FrozenPostureManifest
from buffs.buff import BuffHandler
from carry.carry_elements import CarryElementHelper
from carry.carry_tuning import CarryTuning
from carry.carry_utils import create_carry_constraint, get_carried_objects_gen
from carry.pick_up_sim_liability import PickUpSimLiability
from contextlib import contextmanager
from element_utils import build_critical_section_with_finally, build_critical_section, soft_sleep_forever
from element_utils import build_element, do_all, must_run
from event_testing.resolver import SingleActorAndObjectResolver
from interactions import ParticipantType, PipelineProgress, TargetType
from interactions.aop import AffordanceObjectPair
from interactions.base.super_interaction import SuperInteraction
from interactions.constraints import Constraint, ANYWHERE, create_constraint_set, _ConstraintSet
from interactions.context import InteractionContext, QueueInsertStrategy, InteractionSource
from interactions.interaction_finisher import FinishingType
from interactions.priority import Priority
from interactions.utils.animation_reference import TunableAnimationReference
from interactions.utils.interaction_liabilities import STAND_SLOT_LIABILITY, CANCEL_AOP_LIABILITY, PRIVACY_LIABILITY, PrivacyLiability
from interactions.utils.route_fail import handle_transition_failure
from interactions.utils.routing_constants import TransitionFailureReasons
from objects.components.types import CARRYABLE_COMPONENT
from objects.object_enums import ResetReason
from objects.pools import pool_utils
from objects.terrain import TerrainPoint
from postures import DerailReason, MOVING_DERAILS, FAILURE_DERAILS
from postures.base_postures import create_puppet_postures
from postures.context import PostureContext
from postures.posture import POSTURE_FAMILY_MAP
from postures.posture_graph import TransitionSequenceStage, EMPTY_PATH_SPEC, PathType, SIM_DEFAULT_POSTURE_TYPE
from postures.posture_specs import PostureSpecVariable, PostureAspectBody, PostureAspectSurface
from postures.posture_state import PostureState
from postures.posture_state_spec import PostureStateSpec
from postures.posture_tuning import PostureTuning
from postures.stand import StandSuperInteraction
from postures.transition import PostureStateTransition
from routing import SurfaceType
from routing.formation.formation_liability import RoutingFormationLiability
from routing.walkstyle.walkstyle_behavior import WalksStyleBehavior
from server.pick_info import PickType, PickInfo
from services.reset_and_delete_service import ResetRecord
from sims.outfits.outfit_enums import OutfitChangeReason
from sims.sim_info_types import Age
from sims4 import callback_utils
from sims4.callback_utils import CallableList
from sims4.collections import frozendict
from sims4.math import Vector3, Location, Quaternion, Transform
from sims4.math import transform_almost_equal
from sims4.profiler_utils import create_custom_named_profiler_function
from sims4.sim_irq_service import yield_to_irq
from sims4.tuning.tunable import TunableSimMinute, TunableRealSecond
from singletons import DEFAULT
from teleport.teleport_helper import TeleportHelper
from teleport.teleport_type_liability import TeleportStyleInjectionLiability
from terrain import get_water_depth
from vehicles.vehicle_constants import VehicleTransitionState
from weakref import WeakValueDictionary
from world.ocean_tuning import OceanTuning
import build_buy, caches, clock, collections, date_and_time, element_utils, elements, functools, gsi_handlers, interactions.constraints, interactions.utils, macros, postures.posture_graph, postures.posture_scoring, routing, services, sims4.collections, sims4.log
logger = sims4.log.Logger('TransitionSequence')
with sims4.reload.protected(globals()):
    global_plan_lock = None
    inject_interaction_name_in_callstack = False

def path_plan_allowed():
    global global_plan_lock
    if global_plan_lock is None:
        return True
    sim_with_lock = global_plan_lock()
    return sim_with_lock is None


def final_destinations_gen():
    for transition_controller in services.current_zone().all_transition_controllers:
        if transition_controller.is_transition_active():
            for final_dest in transition_controller.final_destinations_gen():
                yield final_dest


postures.posture_scoring.set_final_destinations_gen(final_destinations_gen)

class PosturePreferencesData:

    def __init__(self, apply_posture_costs, prefer_surface, require_current_constraint, posture_cost_overrides):
        self.apply_posture_costs = apply_posture_costs
        self.prefer_surface = prefer_surface
        self.require_current_constraint = require_current_constraint
        self.posture_cost_overrides = posture_cost_overrides.copy()


class TransitionSequenceData:

    def __init__(self):
        self.intended_location = None
        self.constraint = (None, None)
        self.templates = (None, None, None)
        self.valid_dest_nodes = set()
        self.segmented_paths = None
        self.connectivity = (None, None, None, None)
        self.path_spec = None
        self.final_destination = None
        self.final_included_sis = None
        self.progress = TransitionSequenceStage.EMPTY
        self.progress_max = TransitionSequenceStage.COMPLETE


class TransitionSequenceController:
    PRIVACY_ENGAGE = 0
    PRIVACY_SHOO = 1
    PRIVACY_BLOCK = 2
    MINIMUM_AREA_FOR_NO_STAND_RESERVATION = 2
    SIM_MINUTES_TO_WAIT_FOR_VIOLATORS = TunableSimMinute(description='\n        How many Sim minutes a Sim will wait for violating Sims to route away\n        before giving up on the interaction he was trying to run.  Used\n        currently for privacy and for slot reservations.\n        ',
      default=15,
      minimum=0)
    SLEEP_TIME_FOR_IDLE_WAITING = TunableRealSecond(1, description='\n        Time in real seconds idle behavior will sleep for before trying to find\n        next work again.\n        ')
    SHOO_ANIMATION = TunableAnimationReference(description='\n        The animation to play when Sims need to shoo privacy violators.\n        ')
    CALL_OVER_ANIMATION = TunableAnimationReference(description='\n        The animation to play when Sims require another Sim to continue their\n        transition, e.g. a toddler requiring to be picked up.\n        ')

    def __init__(self, interaction, ignore_all_other_sis=False):
        self._interaction = interaction
        self._target_interaction = None
        self._expected_sim_count = 0
        self._success = False
        self._canceled = False
        self._running_transition_interactions = set()
        self._transition_canceled = False
        self._current_transitions = {}
        self._derailed = {}
        self._has_tried_bring_group_along = False
        self._original_interaction_target = None
        self._original_interaction_target_changed = False
        self._shortest_path_success = collections.defaultdict(lambda: True)
        self._failure_target_and_reason = {}
        self._blocked_sis = []
        self._sim_jobs = []
        self._sim_idles = set()
        self._worker_all_element = None
        self._exited_due_to_exception = False
        self._sim_data = {}
        self._tried_destinations = collections.defaultdict(set)
        self._failure_path_spec = None
        self._running = False
        self._privacy_initiation_time = None
        self._processed_on_route_change = False
        self.outdoor_streetwear_change = {}
        self.deferred_si_cancels = {}
        self._relevant_objects = set()
        self._location_changed_targets = set()
        self.ignore_all_other_sis = ignore_all_other_sis
        self._pushed_mobile_posture_exit = False
        self._has_deferred_putdown = False
        self._force_carry_path = False
        self._vehicle_transition_states = defaultdict((lambda: VehicleTransitionState.NO_STATE))
        self._deployed_vehicles = WeakValueDictionary()
        self._pushed_posture_object_retrieval_affordance = False

    @property
    def force_carry_path(self):
        return self._force_carry_path

    @force_carry_path.setter
    def force_carry_path(self, value):
        self._force_carry_path = value

    @property
    def has_deferred_putdown(self):
        return self._has_deferred_putdown

    @has_deferred_putdown.setter
    def has_deferred_putdown(self, value):
        self._has_deferred_putdown = value

    def __str__(self):
        if self.interaction.sim is not None:
            return 'TransitionSequence for {} {} on {}'.format(self.interaction.affordance.__name__, self.interaction.id, self.interaction.sim.full_name)
        return 'TransitionSequence for {} {} on Sim who is None'.format(self.interaction.affordance.__name__, self.interaction.id)

    @property
    def running(self):
        return self._running

    def with_current_transition(self, sim, posture_transition, sequence=()):

        def set_current_transition(_):
            if sim in self._current_transitions:
                if self._current_transitions[sim] is not None:
                    raise RuntimeError('{} attempting to do two posture transitions at the same time. \n   1: Dest State: {}, Source: {}\n   2: Dest State: {}, Source: {}'.format(sim, self._current_transitions[sim]._dest_state, self._current_transitions[sim]._source_interaction, posture_transition._dest_state, posture_transition._source_interaction))
            self._current_transitions[sim] = posture_transition

        def clear_current_transition(_):
            if self._current_transitions[sim] == posture_transition:
                self._current_transitions[sim] = None
            self._deployed_vehicles.pop(sim, None)
            self._vehicle_transition_states.pop(sim, None)

        return build_critical_section_with_finally(set_current_transition, sequence, clear_current_transition)

    @property
    def succeeded(self):
        return self._success

    @property
    def canceled(self):
        return self._canceled

    @property
    def interaction(self):
        return self._interaction

    @property
    def sim(self):
        return self.interaction.sim

    @staticmethod
    @caches.cached
    def _get_intended_location_from_spec(sim, path_spec):
        final_transition_spec = path_spec._path[-1]
        final_posture_spec = final_transition_spec.posture_spec
        posture_type = final_posture_spec.body.posture_type
        if not posture_type.mobile:
            if not posture_type.unconstrained:
                if posture_type.has_mobile_entry_transition():
                    final_posture_target = final_posture_spec.body.target
                    posture = posture_type(sim, final_posture_target, (postures.PostureTrack.BODY), is_throwaway=True)
                    slot_constraint = posture.slot_constraint_simple
                    if slot_constraint is not None:
                        for sub_slot_constraint in slot_constraint:
                            final_transform = sub_slot_constraint.containment_transform
                            routing_surface = sub_slot_constraint.routing_surface
                            location = routing.Location(final_transform.translation, final_transform.orientation, routing_surface)
                            return location

        for transition_spec in reversed(path_spec._path):
            if transition_spec.path is not None:
                return transition_spec.path.final_location

    def intended_location(self, sim):
        if self.running:
            if not self.canceled:
                if not self.interaction.is_finishing:
                    if not self.is_derailed(sim):
                        path_spec = self._get_path_spec(sim)
                        if path_spec is not None:
                            if path_spec._path is not None:
                                intended_location = self._get_intended_location_from_spec(sim, path_spec)
                                if intended_location is not None:
                                    return intended_location
        return sim.location

    def _clear_target_interaction(self):
        if self._target_interaction is not None:
            self._target_interaction.transition = None
            self._target_interaction.on_removed_from_queue()
            self._target_interaction = None

    def on_reset(self):
        self.end_transition()
        self.shutdown()

    def on_reset_early_detachment(self, obj, reset_reason):
        if reset_reason != ResetReason.BEING_DESTROYED:
            if self.sim is not None:
                self.derail(DerailReason.NAVMESH_UPDATED, self.sim)

    def on_reset_add_interdependent_reset_records(self, obj, reset_reason, reset_records):
        if not self.interaction.should_reset_based_on_pipeline_progress:
            return
        if reset_reason == ResetReason.BEING_DESTROYED:
            if obj.is_aging_up_baby:
                return
            for sim in self._sim_data:
                reset_records.append(ResetRecord(sim, ResetReason.RESET_EXPECTED, self, 'Relevant object for Transition.'))

    def derail(self, reason: DerailReason, sim, test_result=None):
        if self._success:
            return
        else:
            if self.interaction is sim.posture.source_interaction:
                return
            if gsi_handlers.posture_graph_handlers.archiver.enabled:
                gsi_handlers.posture_graph_handlers.archive_derailed_transition(sim, self.interaction, reason, test_result)
            self._derailed[sim] = reason
            if sim in self._current_transitions and self._current_transitions[sim] is not None:
                self._current_transitions[sim].trigger_soft_stop()

    def release_stand_slot_reservations(self, sims):
        for sim in sims:
            interaction = self.get_interaction_for_sim(sim)
            if interaction is not None:
                interaction.release_liabilities(liabilities_to_release=(STAND_SLOT_LIABILITY,))

    def sim_is_traversing_invalid_portal(self, sim):
        if sim not in self._sim_data:
            return False
        else:
            path_spec = self._sim_data[sim].path_spec
            return path_spec is None or path_spec.path or False
        specs_to_check = [
         path_spec.transition_specs[path_spec.path_progress]]
        if path_spec.path_progress > 0:
            specs_to_check.append(path_spec.transition_specs[path_spec.path_progress - 1])
        for spec in specs_to_check:
            if spec.portal_id is not None and spec.portal_obj is None:
                return True

        return False

    def get_interaction_for_sim(self, sim):
        participant_type = self.interaction.get_participant_type(sim)
        if participant_type == ParticipantType.Actor:
            return self.interaction
        if participant_type in (ParticipantType.TargetSim, ParticipantType.CarriedObject):
            return self.interaction.get_target_si()[0]
        return

    @contextmanager
    def deferred_derailment(self):
        derail = self.derail
        derailed = dict(self._derailed)

        def deferred_derail(reason, sim, test_result=None):
            derailed[sim] = reason

        self.derail = deferred_derail
        try:
            yield
        finally:
            self.derail = derail
            self._derailed = derailed

    @macros.macro
    def _get_path_spec(self, sim):
        if sim in self._sim_data:
            return self._sim_data[sim].path_spec

    def is_multi_sim_path_spec(self, sim):
        path_spec = self._get_path_spec(sim)
        if path_spec is not None:
            dest_spec = path_spec.path[-1]
            if dest_spec is not None:
                if dest_spec.body is not None:
                    return dest_spec.body.posture_type.multi_sim
        return False

    def get_transition_specs(self, sim):
        path_spec = self._get_path_spec(sim)
        if path_spec is not None:
            return path_spec.transition_specs
        return path_spec

    def get_transitions_gen(self):
        for sim, sim_data in self._sim_data.items():
            if sim_data.progress >= TransitionSequenceStage.ROUTES:
                yield (
                 sim, sim_data.path_spec.remaining_path)

    def get_transitioning_sims(self):
        if self._sim_data is None:
            return ()
        sims = set(self._sim_data.keys())
        sims.update(self.interaction.required_sims(for_threading=True))
        return sims

    def get_remaining_transitions(self, sim):
        path_spec = self._get_path_spec(sim)
        if path_spec is None:
            return []
        return path_spec.remaining_path

    def get_previous_spec(self, sim):
        path_spec = self._get_path_spec(sim)
        if path_spec is None:
            return []
        return path_spec.previous_posture_spec

    def advance_path(self, sim, prime_path=False):
        path_spec = self._get_path_spec(sim)
        if path_spec is postures.posture_graph.EMPTY_PATH_SPEC:
            return
        if path_spec is not None:
            if not prime_path or path_spec.path_progress == 0:
                path_spec.advance_path()

    def get_transition_spec(self, sim):
        path_spec = self._get_path_spec(sim)
        if path_spec is not None:
            return path_spec.get_transition_spec()

    def get_next_transition_spec(self, sim):
        path_spec = self._get_path_spec(sim)
        if path_spec is None:
            return
        transition_spec = path_spec.get_transition_spec()
        if transition_spec is None:
            return
        return path_spec.get_next_transition_spec(transition_spec)

    def get_transition_should_reserve(self, sim):
        path_spec = self._get_path_spec(sim)
        if path_spec is not None:
            return path_spec.get_transition_should_reserve()
        return False

    def get_destination_constraint(self, sim):
        path_spec = self._get_path_spec(sim)
        if path_spec is not None:
            return path_spec.final_constraint

    def get_var_map(self, sim):
        path_spec = self._get_path_spec(sim)
        if path_spec is None:
            return
        return path_spec.var_map

    def is_derailed(self, sim):
        if sim in self._derailed:
            return self._derailed[sim] != DerailReason.NOT_DERAILED
        return False

    @property
    def any_derailed(self):
        return any((v != DerailReason.NOT_DERAILED for v in self._derailed.values()))

    @property
    def any_failure_derails(self):
        return any((v in FAILURE_DERAILS for v in self._derailed.values()))

    def is_transition_active(self):
        if not self._success:
            if not self.canceled:
                return True
        return False

    def get_failure_reason_and_target(self, sim):
        failure_reason, failure_object_id = (None, None)
        path_spec = self._get_path_spec(sim)
        if path_spec is not None:
            failure_reason, failure_object_id = path_spec.get_failure_reason_and_object_id()
            if failure_reason is not None:
                if failure_reason == routing.FAIL_PATH_TYPE_OBJECT_BLOCKING:
                    failure_reason = TransitionFailureReasons.BLOCKING_OBJECT
                else:
                    if failure_reason == routing.FAIL_PATH_TYPE_BUILD_BLOCKING or failure_reason == routing.FAIL_PATH_TYPE_UNKNOWN or failure_reason == routing.FAIL_PATH_TYPE_UNKNOWN_BLOCKING:
                        failure_reason = TransitionFailureReasons.BUILD_BUY
        if failure_reason is None:
            if sim in self._failure_target_and_reason:
                failure_reason, failure_object_id = self._failure_target_and_reason[sim]
        return (
         failure_reason, failure_object_id)

    def set_failure_target(self, sim, reason, target_id=None):
        if sim in self._failure_target_and_reason:
            return
        self._failure_target_and_reason[sim] = (
         reason, target_id)

    def add_stand_slot_reservation(self, sim, interaction, position, routing_surface):
        sim.routing_component.add_stand_slot_reservation(interaction, position, routing_surface, self.get_transitioning_sims())

    def _do(self, timeline, sim, *args):
        element = build_element(args)
        if element is None:
            return
        result = yield from element_utils.run_child(timeline, element)
        return result
        if False:
            yield None

    def _do_must(self, timeline, sim, *args):
        element = build_element(args)
        if element is None:
            return
        element = must_run(element)
        result = yield from element_utils.run_child(timeline, element)
        return result
        if False:
            yield None

    def on_owned_interaction_canceled(self, interaction):
        if interaction.is_social:
            if self.interaction.is_social:
                if interaction.social_group is self.interaction.social_group:
                    return
        self.derail(DerailReason.PREEMPTED, interaction.sim)

    def cancel(self, finishing_type=None, cancel_reason_msg=None, test_result=None, si_to_cancel=None):
        if finishing_type is not None:
            if finishing_type == FinishingType.NATURAL:
                return True
            if finishing_type == FinishingType.USER_CANCEL:
                self.interaction.route_fail_on_transition_fail = False
        else:
            self._transition_canceled = True
            main_group = self.sim.get_main_group()
            if main_group is not None:
                main_group.remove_non_adjustable_sim(self.sim)
            defer_cancel = False
            for transition in self._current_transitions.values():
                if transition is None:
                    continue
                if transition.is_routing:
                    transition.trigger_soft_stop()
                else:
                    defer_cancel = True

            if self.interaction.is_cancel_aop and self.interaction.running:
                defer_cancel = True
        if not defer_cancel:
            self.cancel_sequence(finishing_type=finishing_type, test_result=test_result)
        else:
            if si_to_cancel is not None:
                if si_to_cancel not in self.deferred_si_cancels:
                    self.deferred_si_cancels[si_to_cancel] = (
                     finishing_type, cancel_reason_msg)
        return self.canceled

    def cancel_sequence(self, finishing_type=None, test_result=None):
        if not self.canceled:
            if gsi_handlers.posture_graph_handlers.archiver.enabled:
                gsi_handlers.posture_graph_handlers.archive_canceled_transition(self.interaction.sim, self.interaction, finishing_type, test_result)
            self._canceled = True
            transition_finishing_type = finishing_type or FinishingType.TRANSITION_FAILURE
            for interaction in list(self._running_transition_interactions):
                if interaction.sim.posture.source_interaction is interaction:
                    continue
                interaction.cancel(transition_finishing_type, cancel_reason_msg='Transition Sequence Failed. Cancel all running transition interactions.')

            if not self.interaction.is_finishing:
                self.interaction.cancel(transition_finishing_type, cancel_reason_msg='Transition Sequence Failed. Cancel transition interaction.')
            for si, cancel_info in self.deferred_si_cancels.items():
                finishing_type, cancel_reason_msg = cancel_info
                si.cancel(finishing_type, cancel_reason_msg=cancel_reason_msg)

            self.deferred_si_cancels.clear()

    def final_destinations_gen(self):
        for sim_data in self._sim_data.values():
            if sim_data.final_destination is not None:
                yield sim_data.final_destination

    def get_final_constraint(self, sim):
        sim_data = self._sim_data.get(sim)
        if sim_data is None:
            return ANYWHERE
        if sim_data.path_spec is not None and sim_data.path_spec.final_constraint is not None:
            final_constraint = sim_data.path_spec.final_constraint
        else:
            final_constraint = sim_data.constraint[0]
        if final_constraint is None:
            return ANYWHERE
        return final_constraint

    @staticmethod
    def _is_set_valid(source_dest_sets):
        valid = False
        for source_dest_set in source_dest_sets.values():
            if source_dest_set[0] and source_dest_set[1]:
                valid = True
                break

        return valid

    def _is_putdown_interaction(self, target=None, interaction=None):
        interaction = interaction or self.interaction
        if not interaction.is_putdown:
            return False
        if target is not None:
            carry_target = interaction.carry_target or interaction.target
            if carry_target is not target:
                return False
        return True

    def get_sims_with_invalid_paths(self):
        permanent_failure = True
        invalid_sims = set()
        for sim, sim_data in self._sim_data.items():
            if not any(sim_data.connectivity):
                invalid_sims.add(sim)
                if not sim_data.constraint:
                    continue
                if self._tried_destinations[sim]:
                    continue
                must_include_sis = list(sim.si_state.all_guaranteed_si_gen(self.interaction.priority, self.interaction.group_id))
                if must_include_sis:
                    permanent_failure = False
                    continue
                best_complete_path, source_destination_sets, source_middle_sets, middle_destination_sets = sim_data.connectivity
                if best_complete_path:
                    continue
                if source_destination_sets:
                    if self._is_set_valid(source_destination_sets):
                        continue
                if source_middle_sets:
                    if middle_destination_sets:
                        if self._is_set_valid(source_middle_sets):
                            continue
                invalid_sims.add(sim)

        if invalid_sims:
            if permanent_failure:
                return set()
        if invalid_sims:
            self.cancel_incompatible_sis_given_final_posture_states()
        return invalid_sims

    def estimate_distance_for_current_progress(self):
        yield_to_irq()
        sim = self.interaction.sim
        sim_data = self._sim_data[sim]
        included_sis = sim_data.constraint[1] or set()
        if self.interaction.teleporting:
            return (0, True, included_sis)
        if sim_data.progress < TransitionSequenceStage.CONNECTIVITY:
            return (None, False, set())
        if sim_data.progress == TransitionSequenceStage.CONNECTIVITY:
            if len(self.interaction.object_reservation_tests):
                for valid_destination in sim_data.valid_dest_nodes:
                    if valid_destination.body_target.may_reserve(sim):
                        break
                else:
                    return (
                     None, False, set())

            distance, posture_change = self._estimate_distance_for_connectivity(sim)
            return (distance, posture_change, included_sis)
        if sim_data.progress > TransitionSequenceStage.CONNECTIVITY:
            path_spec = sim_data.path_spec
            if path_spec is EMPTY_PATH_SPEC or path_spec.is_failure_path:
                return (
                 None, False, set())
            if path_spec.completed_path:
                return (
                 0, False, included_sis)
            return (path_spec.total_cost, True, included_sis)
        return (None, False, set())

    def _estimate_distance_for_connectivity(self, sim):
        connectivity = self._sim_data[sim].connectivity
        best_complete_path, source_destination_sets, source_middle_sets, _ = connectivity
        if best_complete_path:
            return (0, False)
        if not source_destination_sets:
            if not source_middle_sets:
                return (None, False)
        min_distance = sims4.math.MAX_FLOAT
        if source_destination_sets and source_middle_sets:
            routing_sets = source_destination_sets if any((source_handles and destination_handles for source_handles, destination_handles, _, _, _, _ in source_destination_sets.values())) else source_middle_sets
        else:
            routing_sets = source_destination_sets or source_middle_sets
        for source_handles, destination_handles, _, _, _, _ in routing_sets.values():
            left_handles = set(source_handles.keys())
            right_handles = set(destination_handles.keys())
            if left_handles:
                if not right_handles:
                    continue
                yield_to_irq()
                if DEFAULT in right_handles:
                    min_distance = 0.0
                    continue
                distances = routing.estimate_path_batch(left_handles, right_handles, routing_context=(sim.routing_context))
                if not distances:
                    continue
                for left_handle, right_handle, distance in distances:
                    if distance is not None and distance < min_distance:
                        min_distance = distance + left_handle.path.cost + right_handle.path.cost

        if min_distance == sims4.math.MAX_FLOAT:
            return (None, False)
        return (min_distance, True)

    def get_included_sis(self):
        included_sis = set()
        for sim_data in self._sim_data.values():
            included_sis_sim = sim_data.constraint[1]
            if included_sis_sim:
                for included_si_sim in included_sis_sim:
                    if included_si_sim is self.interaction:
                        continue
                    included_sis.add(included_si_sim)

        return included_sis

    def add_blocked_si(self, blocked_si):
        self._blocked_sis.append(blocked_si)

    def _wait_for_violators(self, timeline, blocked_sims):
        cancel_functions = CallableList()

        def wait_for_violators(timeline):
            then = services.time_service().sim_now
            while 1:
                if self._blocked_sis:
                    for blocked_si in self._blocked_sis[:]:
                        handler = blocked_si.get_interaction_reservation_handler(sim=(self.sim))
                        if handler is None:
                            continue
                        if handler.may_reserve():
                            self._blocked_sis.remove(blocked_si)

                if not self._blocked_sis:
                    if not any((blocked_sim.routing_component.get_stand_slot_reservation_violators() for blocked_sim in blocked_sims)):
                        cancel_functions()
                        return
                now = services.time_service().sim_now
                timeout = self.SIM_MINUTES_TO_WAIT_FOR_VIOLATORS
                if not self.canceled:
                    if now - then > clock.interval_in_sim_minutes(timeout):
                        for blocked_sim in blocked_sims:
                            self.derail(DerailReason.TRANSITION_FAILED, blocked_sim)

                        del self._blocked_sis[:]
                        cancel_functions()
                        return
                    yield timeline.run_child(elements.SleepElement(date_and_time.create_time_span(minutes=1)))

        idle_work = [
         elements.GeneratorElement(wait_for_violators)]
        for blocked_sim in blocked_sims:
            idle, cancel_fn = blocked_sim.get_idle_element()
            cancel_functions.append(cancel_fn)
            idle_work.append(idle)

        yield from self._do(timeline, self.sim, elements.AllElement(idle_work))
        if False:
            yield None

    def reset_derailed_transitions--- This code section failed: ---

 L.1252         0  BUILD_LIST_0          0 
                2  STORE_FAST               'sims_to_reset'

 L.1253         4  LOAD_CONST               False
                6  STORE_FAST               'moved_social_group'

 L.1254      8_10  SETUP_LOOP          366  'to 366'
               12  LOAD_FAST                'self'
               14  LOAD_ATTR                _derailed
               16  LOAD_METHOD              items
               18  CALL_METHOD_0         0  '0 positional arguments'
               20  GET_ITER         
             22_0  COME_FROM           342  '342'
             22_1  COME_FROM           320  '320'
             22_2  COME_FROM            38  '38'
            22_24  FOR_ITER            364  'to 364'
               26  UNPACK_SEQUENCE_2     2 
               28  STORE_FAST               'sim'
               30  STORE_FAST               'derailed_reason'

 L.1255        32  LOAD_FAST                'derailed_reason'
               34  LOAD_CONST               None
               36  COMPARE_OP               is
               38  POP_JUMP_IF_TRUE     22  'to 22'
               40  LOAD_FAST                'derailed_reason'
               42  LOAD_GLOBAL              DerailReason
               44  LOAD_ATTR                NOT_DERAILED
               46  COMPARE_OP               ==
               48  POP_JUMP_IF_FALSE    52  'to 52'

 L.1256        50  CONTINUE             22  'to 22'
             52_0  COME_FROM            48  '48'

 L.1258        52  LOAD_FAST                'self'
               54  LOAD_ATTR                _derailed
               56  LOAD_FAST                'sim'
               58  BINARY_SUBSCR    
               60  LOAD_GLOBAL              DerailReason
               62  LOAD_ATTR                TRANSITION_FAILED
               64  COMPARE_OP               !=
               66  POP_JUMP_IF_FALSE   100  'to 100'

 L.1265        68  SETUP_LOOP          164  'to 164'
               70  LOAD_FAST                'self'
               72  LOAD_ATTR                _tried_destinations
               74  GET_ITER         
               76  FOR_ITER             96  'to 96'
               78  STORE_FAST               'tried_destinations_sim'

 L.1266        80  LOAD_FAST                'self'
               82  LOAD_ATTR                _tried_destinations
               84  LOAD_FAST                'tried_destinations_sim'
               86  BINARY_SUBSCR    
               88  LOAD_METHOD              clear
               90  CALL_METHOD_0         0  '0 positional arguments'
               92  POP_TOP          
               94  JUMP_BACK            76  'to 76'
               96  POP_BLOCK        
               98  JUMP_FORWARD        164  'to 164'
            100_0  COME_FROM            66  '66'

 L.1268       100  LOAD_FAST                'self'
              102  LOAD_ATTR                _sim_data
              104  LOAD_FAST                'sim'
              106  BINARY_SUBSCR    
              108  LOAD_ATTR                final_destination
              110  STORE_DEREF              'final_destination'

 L.1269       112  LOAD_DEREF               'final_destination'
              114  LOAD_CONST               None
              116  COMPARE_OP               is-not
              118  POP_JUMP_IF_FALSE   164  'to 164'

 L.1275       120  LOAD_CLOSURE             'final_destination'
              122  BUILD_TUPLE_1         1 
              124  LOAD_SETCOMP             '<code_object <setcomp>>'
              126  LOAD_STR                 'TransitionSequenceController.reset_derailed_transitions.<locals>.<setcomp>'
              128  MAKE_FUNCTION_8          'closure'
              130  LOAD_FAST                'self'
              132  LOAD_ATTR                _sim_data
              134  LOAD_FAST                'sim'
              136  BINARY_SUBSCR    
              138  LOAD_ATTR                valid_dest_nodes
              140  GET_ITER         
              142  CALL_FUNCTION_1       1  '1 positional argument'
              144  STORE_FAST               'tried_dests'

 L.1277       146  LOAD_FAST                'self'
              148  LOAD_ATTR                _tried_destinations
              150  LOAD_FAST                'sim'
              152  DUP_TOP_TWO      
              154  BINARY_SUBSCR    
              156  LOAD_FAST                'tried_dests'
              158  INPLACE_OR       
              160  ROT_THREE        
              162  STORE_SUBSCR     
            164_0  COME_FROM           118  '118'
            164_1  COME_FROM            98  '98'
            164_2  COME_FROM_LOOP       68  '68'

 L.1279       164  LOAD_FAST                'derailed_reason'
              166  LOAD_GLOBAL              DerailReason
              168  LOAD_ATTR                PRIVACY_ENGAGED
              170  COMPARE_OP               !=
              172  POP_JUMP_IF_FALSE   244  'to 244'

 L.1280       174  LOAD_FAST                'sims_to_reset'
              176  LOAD_METHOD              append
              178  LOAD_FAST                'sim'
              180  CALL_METHOD_1         1  '1 positional argument'
              182  POP_TOP          

 L.1281       184  LOAD_FAST                'self'
              186  LOAD_ATTR                _derailed
              188  LOAD_FAST                'sim'
              190  BINARY_SUBSCR    
              192  LOAD_GLOBAL              DerailReason
              194  LOAD_ATTR                TRANSITION_FAILED
              196  COMPARE_OP               ==
              198  POP_JUMP_IF_FALSE   244  'to 244'

 L.1282       200  LOAD_FAST                'sim'
              202  LOAD_FAST                'self'
              204  LOAD_ATTR                interaction
              206  LOAD_ATTR                sim
              208  COMPARE_OP               is
              210  POP_JUMP_IF_FALSE   244  'to 244'
              212  LOAD_FAST                'self'
              214  LOAD_ATTR                _original_interaction_target_changed
              216  POP_JUMP_IF_FALSE   244  'to 244'

 L.1283       218  LOAD_FAST                'self'
              220  LOAD_ATTR                interaction
              222  LOAD_METHOD              set_target
              224  LOAD_FAST                'self'
              226  LOAD_ATTR                _original_interaction_target
              228  CALL_METHOD_1         1  '1 positional argument'
              230  POP_TOP          

 L.1284       232  LOAD_CONST               None
              234  LOAD_FAST                'self'
              236  STORE_ATTR               _original_interaction_target

 L.1285       238  LOAD_CONST               False
              240  LOAD_FAST                'self'
              242  STORE_ATTR               _original_interaction_target_changed
            244_0  COME_FROM           216  '216'
            244_1  COME_FROM           210  '210'
            244_2  COME_FROM           198  '198'
            244_3  COME_FROM           172  '172'

 L.1287       244  LOAD_FAST                'moved_social_group'
          246_248  POP_JUMP_IF_TRUE    300  'to 300'
              250  LOAD_FAST                'derailed_reason'
              252  LOAD_GLOBAL              MOVING_DERAILS
              254  COMPARE_OP               in
          256_258  POP_JUMP_IF_FALSE   300  'to 300'

 L.1290       260  LOAD_FAST                'self'
              262  LOAD_ATTR                interaction
              264  LOAD_ATTR                is_social
          266_268  POP_JUMP_IF_FALSE   300  'to 300'
              270  LOAD_FAST                'self'
              272  LOAD_ATTR                interaction
              274  LOAD_ATTR                social_group
              276  LOAD_CONST               None
              278  COMPARE_OP               is-not
          280_282  POP_JUMP_IF_FALSE   300  'to 300'

 L.1291       284  LOAD_FAST                'self'
              286  LOAD_ATTR                interaction
              288  LOAD_ATTR                social_group
              290  LOAD_METHOD              refresh_social_geometry
              292  CALL_METHOD_0         0  '0 positional arguments'
              294  POP_TOP          

 L.1292       296  LOAD_CONST               True
              298  STORE_FAST               'moved_social_group'
            300_0  COME_FROM           280  '280'
            300_1  COME_FROM           266  '266'
            300_2  COME_FROM           256  '256'
            300_3  COME_FROM           246  '246'

 L.1294       300  LOAD_GLOBAL              DerailReason
              302  LOAD_ATTR                NOT_DERAILED
              304  LOAD_FAST                'self'
              306  LOAD_ATTR                _derailed
              308  LOAD_FAST                'sim'
              310  STORE_SUBSCR     

 L.1297       312  LOAD_FAST                'derailed_reason'
              314  LOAD_GLOBAL              DerailReason
              316  LOAD_ATTR                NAVMESH_UPDATED_BY_BUILD
              318  COMPARE_OP               ==
              320  POP_JUMP_IF_FALSE    22  'to 22'

 L.1298       322  LOAD_FAST                'sim'
              324  LOAD_METHOD              get_location_on_nearest_surface_below
              326  CALL_METHOD_0         0  '0 positional arguments'
              328  UNPACK_SEQUENCE_2     2 
              330  STORE_FAST               'location'
              332  STORE_FAST               '_'

 L.1299       334  LOAD_FAST                'sim'
              336  LOAD_METHOD              validate_location
              338  LOAD_FAST                'location'
              340  CALL_METHOD_1         1  '1 positional argument'
              342  POP_JUMP_IF_TRUE     22  'to 22'

 L.1300       344  LOAD_FAST                'sim'
              346  LOAD_ATTR                schedule_reset_asap
              348  LOAD_GLOBAL              ResetReason
              350  LOAD_ATTR                RESET_EXPECTED

 L.1301       352  LOAD_FAST                'self'
              354  LOAD_STR                 'Sim is in invalid location during transition.'
              356  LOAD_CONST               ('reset_reason', 'source', 'cause')
              358  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              360  POP_TOP          
              362  JUMP_BACK            22  'to 22'
              364  POP_BLOCK        
            366_0  COME_FROM_LOOP        8  '8'

 L.1303       366  SETUP_LOOP          396  'to 396'
              368  LOAD_FAST                'sims_to_reset'
              370  GET_ITER         
              372  FOR_ITER            394  'to 394'
              374  STORE_FAST               'sim'

 L.1304       376  LOAD_FAST                'self'
              378  LOAD_METHOD              set_sim_progress
              380  LOAD_FAST                'sim'
              382  LOAD_GLOBAL              TransitionSequenceStage
              384  LOAD_ATTR                EMPTY
              386  CALL_METHOD_2         2  '2 positional arguments'
              388  POP_TOP          
          390_392  JUMP_BACK           372  'to 372'
              394  POP_BLOCK        
            396_0  COME_FROM_LOOP      366  '366'

 L.1306       396  LOAD_FAST                'sims_to_reset'
          398_400  POP_JUMP_IF_FALSE   422  'to 422'

 L.1307       402  LOAD_FAST                'self'
              404  LOAD_ATTR                interaction
              406  LOAD_METHOD              refresh_constraints
              408  CALL_METHOD_0         0  '0 positional arguments'
              410  POP_TOP          

 L.1308       412  LOAD_FAST                'self'
              414  LOAD_METHOD              release_stand_slot_reservations
              416  LOAD_FAST                'sims_to_reset'
              418  CALL_METHOD_1         1  '1 positional argument'
              420  POP_TOP          
            422_0  COME_FROM           398  '398'

 L.1310       422  LOAD_CONST               False
              424  LOAD_FAST                'self'
              426  STORE_ATTR               _has_tried_bring_group_along

Parse error at or near `LOAD_SETCOMP' instruction at offset 124

    def _validate_transitions(self):
        for sim_data in self._sim_data.values():
            if sim_data.path_spec is None or sim_data.path_spec is postures.posture_graph.EMPTY_PATH_SPEC:
                self.cancel()

    def end_transition(self):
        if self._sim_data is not None:
            for sim_data in self._sim_data.values():
                included_sis = sim_data.constraint[1]
                if included_sis is None:
                    continue
                for included_si in included_sis:
                    included_si.transition = None
                    included_si.owning_transition_sequences.discard(self)

        self._clear_target_interaction()
        if self._sim_data is not None:
            for sim, sim_data in self._sim_data.items():
                if sim_data.path_spec is not None:
                    sim_data.path_spec.cleanup_path_spec(sim)

    def shutdown(self):
        self._clear_relevant_objects()
        self._clear_target_location_changed_callbacks()
        if self._sim_data is not None:
            for sim in self._sim_data:
                self._clear_owned_transition(sim)
                social_group = sim.get_main_group()
                if social_group is not None:
                    sims4.math.transform_almost_equal((sim.intended_transform), (sim.transform), epsilon=(sims4.geometry.ANIMATION_SLOT_EPSILON)) or social_group.refresh_social_geometry(sim=sim)

        if self._success or self.canceled:
            self.reset_all_progress()
            self.cancel_incompatible_sis_given_final_posture_states()
        services.current_zone().all_transition_controllers.discard(self)

    def cancel_incompatible_sis_given_final_posture_states(self):
        interaction = self.interaction
        return interaction is None or interaction.cancel_incompatible_with_posture_on_transition_shutdown or None
        cancel_reason_msg = "Incompatible with Sim's final transform."
        for sim in self.get_transitioning_sims():
            sim.evaluate_si_state_and_cancel_incompatible(FinishingType.INTERACTION_INCOMPATIBILITY, cancel_reason_msg)

    def _clear_cancel_by_posture_change(self):
        for sim_data in self._sim_data.values():
            if sim_data.final_included_sis:
                for si in sim_data.final_included_sis:
                    si.disable_cancel_by_posture_change = False

    def _clear_owned_transition(self, sim):
        sim_data = self._sim_data.get(sim)
        if sim_data.final_included_sis:
            for included_si in sim_data.final_included_sis:
                included_si.owning_transition_sequences.discard(self)

        included_sis = sim_data.constraint[1]
        if included_sis:
            for included_si in included_sis:
                included_si.owning_transition_sequences.discard(self)

    def _get_carry_transference_work(self):
        carry_transference_work_begin = collections.defaultdict(list)
        for sim in self._sim_data:
            for si in sim.si_state:
                if si._carry_transfer_animation is None:
                    continue
                end_carry_transfer = si.get_carry_transfer_end_element()
                carry_transference_work_begin[si.sim].append(build_critical_section(end_carry_transfer, flush_all_animations))

        carry_transference_sis = set()
        for sim_data in self._sim_data.values():
            additional_templates = sim_data.templates[1]
            if additional_templates:
                carry_transference_sis.update(additional_templates.keys())
            carry_si = sim_data.templates[2]
            if carry_si is not None:
                carry_transference_sis.add(carry_si)

        carry_transference_sis.discard(self.interaction)
        carry_transference_work_end = collections.defaultdict(list)
        for si in carry_transference_sis:
            if si._carry_transfer_animation is None:
                continue
            begin_carry_transfer = si.get_carry_transfer_begin_element()
            carry_transference_work_end[si.sim].append(build_critical_section(begin_carry_transfer, flush_all_animations))

        return (carry_transference_work_begin, carry_transference_work_end)

    def _get_animation_work(self, animation):
        return (
         animation((self._interaction), sequence=()), flush_all_animations)

    def get_final_included_sis_for_sim(self, sim):
        if sim not in self._sim_data:
            return
        return self._sim_data[sim].final_included_sis

    def get_tried_dest_nodes_for_sim(self, sim):
        return self._tried_destinations[sim]

    def get_sims_in_sim_data(self):
        return self._sim_data

    def compute_transition_connectivity(self):
        gen = self.run_transitions(None, progress_max=(TransitionSequenceStage.CONNECTIVITY))
        try:
            next(gen)
            logger.error('run_transitions yielded when computing connectivity.')
        except StopIteration as exc:
            try:
                return exc.value
            finally:
                exc = None
                del exc

    def run_transitions(self, timeline, progress_max=TransitionSequenceStage.COMPLETE):
        logger.debug('{}: Running.', self)
        callback_utils.invoke_callbacks(callback_utils.CallbackEvent.TRANSITION_SEQUENCE_ENTER)
        try:
            try:
                self._running = True
                self._progress_max = progress_max
                self.reset_derailed_transitions()
                self._add_interaction_target_location_changed_callback()
                for required_sim in self.get_transitioning_sims():
                    sim_data = self._sim_data.get(required_sim)
                    if sim_data is None or sim_data.progress < progress_max:
                        break
                else:
                    return True

                sim = self.interaction.get_participant(ParticipantType.Actor)
                services.current_zone().all_transition_controllers.add(self)
                if not (progress_max < TransitionSequenceStage.COMPLETE or self.interaction.disable_transitions):
                    yield from self._build_transitions(timeline)
                if self.any_derailed:
                    return False
                if progress_max < TransitionSequenceStage.COMPLETE:
                    services.current_zone().all_transition_controllers.discard(self)
                    return True
                if self.interaction.disable_transitions:
                    result = yield from self.run_super_interaction(timeline, self.interaction)
                    return result
                self._validate_transitions()
                target_si, test_result = self.interaction.get_target_si()
                if not test_result:
                    self.cancel((FinishingType.FAILED_TESTS), test_result=test_result)
                if self.canceled:
                    failure_reason, failure_target = self.get_failure_reason_and_target(sim)
                    if failure_reason is not None or failure_target is not None:
                        yield from self._do(timeline, sim, handle_transition_failure(sim, (self.interaction.target), (self.interaction), failure_reason=failure_reason,
                          failure_object_id=failure_target))
                    return False
                if target_si is not None:
                    if target_si.set_as_added_to_queue():
                        target_si.transition = self
                        self._target_interaction = target_si
                for sim_data in self._sim_data.values():
                    if sim_data.final_included_sis:
                        for si in sim_data.final_included_sis:
                            si.disable_cancel_by_posture_change = True

                carry_transference_work_begin, carry_transference_work_end = self._get_carry_transference_work()
                if carry_transference_work_begin:
                    yield from self._do_must(timeline, self.sim, do_all(thread_element_map=carry_transference_work_begin))
                self._worker_all_element = elements.AllElement([build_element(self._create_next_elements)])
                result = yield from self._do(timeline, None, self._worker_all_element)
                if carry_transference_work_end:
                    yield from self._do_must(timeline, self.sim, do_all(thread_element_map=carry_transference_work_end))
                if progress_max == TransitionSequenceStage.COMPLETE:
                    blocked_sims = set()
                    for blocked_sim, reason in self._derailed.items():
                        if reason == DerailReason.WAIT_FOR_BLOCKING_SIMS:
                            blocked_sims.add(blocked_sim)

                    if blocked_sims:
                        yield from self._wait_for_violators(timeline, blocked_sims)
                if not self._success:
                    if self._transition_canceled:
                        self.cancel()
                    if self.canceled or self.is_derailed(self._interaction.sim):
                        result = False
                if result:
                    for _, transition in self.get_transitions_gen():
                        if transition:
                            result = False
                            break

                if not self._shortest_path_success[sim]:
                    derail_reason = self._derailed.get(sim)
                    if derail_reason != DerailReason.WAIT_TO_BE_PUT_DOWN:
                        self.cancel()
                    return False
                if result:
                    self._success = True
                    if not self.interaction.active:
                        if not self.interaction.is_finishing:
                            should_replace_posture_source = SuperInteraction.should_replace_posture_source_interaction(self.interaction)
                            would_replace_nonfinishing = should_replace_posture_source and not self.sim.posture.source_interaction.is_finishing
                            if would_replace_nonfinishing:
                                self.interaction.is_cancel_aop or self.sim.posture.source_interaction.merge(self.interaction)
                                self.interaction.cancel(FinishingType.TRANSITION_FAILURE, 'Transition Sequence. Replace posture source non-finishing.')
                            else:
                                if len(sim_data.path_spec.transition_specs) == 1:
                                    sim_data.path_spec.transition_specs[0].do_reservation(self.sim) or self.sim.posture.source_interaction.merge(self.interaction)
                                    self.interaction.cancel(FinishingType.TRANSITION_FAILURE, 'Transition Sequence. Reservation failed.')
                                else:
                                    self.interaction.apply_posture_state(self.interaction.sim.posture_state)
                                    result = yield from self.run_super_interaction(timeline, self.interaction)
            except:
                logger.debug('{} RAISED EXCEPTION.', self)
                self._exited_due_to_exception = True
                for sim in self._sim_jobs:
                    logger.warn('Terminating transition for Sim {}', sim)

                for sim in self._sim_idles:
                    logger.warn('Terminating transition idle for Sim {}', sim)

                self._sim_jobs.clear()
                self._sim_idles.clear()
                raise

        finally:
            if self._transition_canceled:
                self.cancel()
            logger.debug('{} DONE.', self)
            self._clear_cancel_by_posture_change()
            if progress_max == TransitionSequenceStage.COMPLETE:
                sims_to_update_intended_location = set()
                for sim in self.get_transitioning_sims():
                    if not sims4.math.transform_almost_equal((sim.intended_transform), (sim.transform), epsilon=(sims4.geometry.ANIMATION_SLOT_EPSILON)):
                        sims_to_update_intended_location.add(sim)
                        for _, _, carry_object in get_carried_objects_gen(sim):
                            if carry_object.is_sim:
                                sims_to_update_intended_location.add(carry_object)

                self.shutdown()
                if not (hasattr(self.interaction, 'suppress_transition_ops_after_death') and self.interaction.suppress_transition_ops_after_death):
                    for sim in sims_to_update_intended_location:
                        sim.routing_component.on_intended_location_changed(sim.intended_location)

                if not self.any_derailed:
                    self.cancel_incompatible_sis_given_final_posture_states()
                callback_utils.invoke_callbacks(callback_utils.CallbackEvent.TRANSITION_SEQUENCE_EXIT)
                if not self._success:
                    if self._interaction.must_run:
                        for sim in self.get_transitioning_sims():
                            if self.is_derailed(sim):
                                break
                        else:
                            logger.warn('Failed to plan a must run interaction {}', (self.interaction), owner='tastle')
                            for sim in self.get_transitioning_sims():
                                self.sim.reset(ResetReason.RESET_EXPECTED, self, 'Failed to plan must run.')

            self._worker_all_element = None
            self._running = False

        if self._sim_jobs:
            raise AssertionError('Transition Sequence: Attempted to exit when there were still existing jobs. [tastle]')
        return self._success
        if False:
            yield None

    @staticmethod
    def choose_hand_and_filter_specs(sim, posture_specs_and_vars, carry_target, used_hand_and_target=None):
        new_specs_and_vars = []
        already_matched = set()
        used_hand = None
        used_hand_target = None
        left_carry_target = sim.posture_state.left.target
        right_carry_target = sim.posture_state.right.target
        back_carry_target = sim.posture_state.back.target
        chosen_hand = None
        if left_carry_target == carry_target:
            if carry_target is not None:
                chosen_hand = Hand.LEFT
            else:
                if right_carry_target == carry_target and carry_target is not None:
                    chosen_hand = Hand.RIGHT
                else:
                    if back_carry_target == carry_target and carry_target is not None:
                        chosen_hand = Hand.BACK
                    else:
                        if left_carry_target is None and right_carry_target is not None:
                            chosen_hand = Hand.LEFT
                        else:
                            if right_carry_target is None and left_carry_target is not None:
                                chosen_hand = Hand.RIGHT
                            else:
                                if used_hand_and_target is not None:
                                    used_hand, used_hand_target = used_hand_and_target
                                    if carry_target is used_hand_target:
                                        chosen_hand = used_hand
                                else:
                                    chosen_hand = Hand.LEFT if used_hand != Hand.LEFT else Hand.RIGHT
        else:
            if carry_target is not None:
                allowed_hands = carry_target.get_allowed_hands(sim)
                if len(allowed_hands) == 1:
                    chosen_hand = allowed_hands[0]
                if chosen_hand is None:
                    allowed_hands = set()
                    for _, posture_spec_vars, _ in posture_specs_and_vars:
                        required_hand = posture_spec_vars.get(PostureSpecVariable.HAND)
                        if required_hand is not None:
                            allowed_hands.add(required_hand)

                    if used_hand is not None:
                        allowed_hands.discard(used_hand)
                    preferred_hand = sim.get_preferred_hand()
                    if not allowed_hands or preferred_hand in allowed_hands:
                        chosen_hand = preferred_hand
            else:
                chosen_hand = allowed_hands.pop()
            if chosen_hand is None:
                logger.error('Failed to find a valid hand for {}', carry_target)
            else:
                if carry_target is not None:
                    allowed_hands = carry_target.get_allowed_hands(sim)
                    if not allowed_hands:
                        logger.error('Sim {} failed to find a hand to carry object {}', sim, carry_target, owner='camilogarcia')
                        return (new_specs_and_vars, chosen_hand)
                    if chosen_hand not in allowed_hands:
                        if len(allowed_hands) == 1:
                            chosen_hand = allowed_hands[0]
                        else:
                            for _, posture_spec_vars, _ in posture_specs_and_vars:
                                required_hand = posture_spec_vars.get(PostureSpecVariable.HAND)
                                if required_hand is not None and required_hand in allowed_hands:
                                    chosen_hand = required_hand

                if chosen_hand == used_hand:
                    if carry_target is not used_hand_target:
                        return (
                         new_specs_and_vars, chosen_hand)
                hand_map = {PostureSpecVariable.HAND: chosen_hand}
                for index_a, (posture_spec_template_a, posture_spec_vars_a, constraint_a) in enumerate(posture_specs_and_vars):
                    if index_a in already_matched:
                        continue
                    found_match = False
                    if index_a + 1 < len(posture_specs_and_vars):
                        if PostureSpecVariable.HAND in posture_spec_vars_a:
                            for index_b, (posture_spec_template_b, posture_spec_vars_b, constraint_b) in enumerate(posture_specs_and_vars[index_a + 1:]):
                                real_index_b = index_b + index_a + 1
                                if posture_spec_template_a != posture_spec_template_b:
                                    continue
                                if carry_target is not None:
                                    is_sim = getattr(carry_target, 'is_sim', False)
                                    if is_sim:
                                        hand_a = posture_spec_vars_a.get(PostureSpecVariable.HAND)
                                        hand_b = posture_spec_vars_b.get(PostureSpecVariable.HAND)
                                        if hand_a == hand_b:
                                            if constraint_a.geometry != constraint_b.geometry:
                                                continue
                                    vars_match = True
                                    for key_a, var_a in posture_spec_vars_a.items():
                                        if key_a == PostureSpecVariable.HAND:
                                            continue
                                        if not key_a not in posture_spec_vars_b:
                                            if posture_spec_vars_b[key_a] != var_a:
                                                pass
                                            vars_match = False
                                            break

                                    if not vars_match:
                                        continue
                                    found_match = True
                                    already_matched.add(real_index_b)
                                    cur_posture_vars = frozendict(posture_spec_vars_a, hand_map)
                                    hand_constraint = create_carry_constraint(carry_target, hand=chosen_hand)
                                    constraint_new = constraint_a.intersect(hand_constraint)
                                    if not constraint_new.valid:
                                        constraint_new = constraint_b.intersect(hand_constraint)
                                    if constraint_new.valid:
                                        new_specs_and_vars.append((posture_spec_template_a, cur_posture_vars, constraint_new))

                        cur_posture_vars = found_match or frozendict(posture_spec_vars_a, hand_map)
                        new_specs_and_vars.append((posture_spec_template_a, cur_posture_vars, constraint_a))

                return (
                 new_specs_and_vars, chosen_hand)

    @staticmethod
    def resolve_constraint_for_hands(sim, interaction, interaction_constraint, context=None):
        if not interaction_constraint.valid:
            return interaction_constraint
        else:
            if context is not None:
                carry_target = context.carry_target
            else:
                carry_target = interaction.carry_target
            hand_is_immutable = dict(zip((Hand.LEFT, Hand.RIGHT, Hand.BACK), (o is not None and o is not carry_target for o in sim.posture_state.carry_targets)))
            return any(hand_is_immutable.values()) or interaction_constraint
        new_constraints = []
        for constraint in interaction_constraint:
            if not constraint._posture_state_spec is None:
                if not constraint._posture_state_spec.posture_manifest:
                    new_constraints.append(constraint)
                    continue
                valid_manifest_entries = PostureManifest()
                for entry in constraint._posture_state_spec.posture_manifest:
                    hand, entry_carry_target = entry.carry_hand_and_target
                    if not hand_is_immutable.get(hand, False) or entry_carry_target != AnimationParticipant.CREATE_TARGET:
                        valid_manifest_entries.add(entry)

                if not valid_manifest_entries:
                    continue
                valid_manifest_constraint = Constraint(posture_state_spec=(PostureStateSpec(valid_manifest_entries, SlotManifest().intern(), None)))
                test_constraint = constraint.intersect(valid_manifest_constraint)
                if not test_constraint.valid:
                    continue
                new_constraints.append(test_constraint)

        new_constraint = create_constraint_set(new_constraints)
        return new_constraint

    @staticmethod
    def _get_specs_for_constraints(sim, interaction, interaction_constraint, pick=None, carry_target=None, used_hand_and_target=None):
        target = interaction.target
        create_target = interaction.create_target
        if any(sim.posture_state.carry_targets):

            def remove_references_to_unrelated_carried_objects(obj, default):
                if obj != None:
                    if obj != carry_target:
                        if obj in sim.posture_state.carry_targets:
                            return MATCH_ANY
                return default

        else:
            remove_references_to_unrelated_carried_objects = None
        posture_specs_and_vars = interaction_constraint.get_posture_specs(remove_references_to_unrelated_carried_objects,
          interaction=interaction)
        posture_specs_and_vars, used_hand = TransitionSequenceController.choose_hand_and_filter_specs(sim, posture_specs_and_vars,
          carry_target,
          used_hand_and_target=used_hand_and_target)
        if interaction is not None:
            interaction.add_preferred_body_target_participants()
            interaction.add_preferred_carrying_sim()
        posture_preferences = interaction.posture_preferences if interaction is not None else None
        templates = collections.defaultdict(list)
        posture_spec_templates = []
        for posture_spec_template, posture_spec_vars, constraint in posture_specs_and_vars:
            if any((isinstance(v, PostureSpecVariable) for v in posture_spec_vars.values())):
                logger.error('posture_spec_vars contains a variable as a value: {}', posture_spec_vars)
                continue
            else:
                posture_spec_templates.append(posture_spec_template)
                posture_spec_vars_updates = {}
                if PostureSpecVariable.INTERACTION_TARGET not in posture_spec_vars:
                    if interaction.target_type == TargetType.FILTERED_TARGET:
                        posture_spec_vars_updates[PostureSpecVariable.INTERACTION_TARGET] = PostureSpecVariable.BODY_TARGET_FILTERED
                    else:
                        posture_spec_vars_updates[PostureSpecVariable.INTERACTION_TARGET] = target
            if PostureSpecVariable.CARRY_TARGET not in posture_spec_vars:
                posture_spec_vars_updates[PostureSpecVariable.CARRY_TARGET] = carry_target
            if posture_spec_vars.get(PostureSpecVariable.SLOT_TEST_DEFINITION) == AnimationParticipant.CREATE_TARGET:
                posture_spec_vars_updates[PostureSpecVariable.SLOT_TEST_DEFINITION] = create_target
            if posture_spec_vars_updates:
                posture_spec_vars += posture_spec_vars_updates
            if posture_preferences is not None and not posture_preferences.prefer_specific_clicked_part:
                if posture_preferences.prefer_clicked_parts and pick is not None:
                    if pick.target is not None:
                        best_parts = pick.target.get_closest_parts_to_position((pick.location), posture_specs=(posture_spec_template,))
                        interaction.add_preferred_objects(best_parts)
            templates[constraint].append((posture_spec_template, posture_spec_vars))

        if posture_preferences is not None:
            if posture_preferences.prefer_specific_clicked_part:
                if pick is not None:
                    if pick.target is not None:
                        best_parts = pick.target.get_closest_parts_to_position((pick.location), posture_specs=posture_spec_templates)
                        interaction.add_preferred_objects(best_parts)
        return (
         templates, used_hand)

    @staticmethod
    def get_templates_including_carry_transference(sim, interaction, interaction_constraint, included_sis, participant_type):
        potential_carry_sis = set()
        for si in included_sis:
            if not si.has_active_cancel_replacement:
                potential_carry_sis.add(si)

        carried_object_transfers = []
        for carry_posture in sim.posture_state.carry_aspects:
            if carry_posture.target is None:
                continue
            elif carry_posture.owning_interactions:
                carry_interactions = carry_posture.owning_interactions
            else:
                carry_interactions = [
                 carry_posture.source_interaction]
            for carry_interaction in carry_interactions:
                if carry_interaction is not None:
                    if carry_posture is not None:
                        valid_targets = {
                         carry_interaction.target}
                        if carry_interaction.staging:
                            valid_targets.add(carry_interaction.carry_target)
                    if carry_posture.target in valid_targets and carry_interaction in potential_carry_sis:
                        carried_object_transfers.append(carry_interaction)
                        for owning_interaction in carry_posture.owning_interactions:
                            potential_carry_sis.discard(owning_interaction)

                        potential_carry_sis.discard(carry_posture.source_interaction)

        for si in potential_carry_sis:
            if not si.is_finishing:
                if si.has_active_cancel_replacement:
                    continue
                for constraint in si.constraint_intersection(posture_state=None):
                    if constraint.posture_state_spec is not None and constraint.posture_state_spec.slot_manifest:
                        potential_carry_target = si.carry_target
                        if potential_carry_target is not None and potential_carry_target is si.target:
                            carried_object_transfers.append(si)
                            break

        carry_target = interaction.carry_target
        if interaction.should_carry_create_target() and interaction.create_target is not None and not carry_target is None:
            if carry_target.definition != interaction.create_target.definition:
                carry_target = interaction.create_target
            if interaction.disable_transitions:
                carry_target = None
            if carry_target is not None:
                carry_target_si = interaction
                carry_target_constraint = interaction_constraint
            else:
                carry_target_si = None
                carry_target_constraint = None
            TSC = TransitionSequenceController
            constraint_resolver = interaction.get_constraint_resolver(None, participant_type=participant_type)
            additional_constraint_list = {}
            if carried_object_transfers:
                for carry_si in reversed(carried_object_transfers):
                    cancel_aop_liability = carry_si.get_liability(CANCEL_AOP_LIABILITY)
                    if cancel_aop_liability is not None:
                        if cancel_aop_liability.interaction_to_cancel is interaction:
                            continue
                        carry_constraint = carry_si.constraint_intersection(posture_state=None)
                        carry_constraint_resolved = TSC.resolve_constraint_for_hands(sim, carry_si, carry_constraint)
                        carry_constraint_resolved = carry_constraint_resolved.apply_posture_state(None, constraint_resolver)
                        additional_constraint_list[carry_si] = carry_constraint_resolved
                        carry_target_additional = carry_si.carry_target
                        if carry_target_additional is not None and not carry_target is None:
                            if sim.posture_state.get_carry_track(carry_target_additional) is None:
                                if sim.posture_state.get_carry_track(carry_target) is not None and carry_target is not interaction.carry_target and carry_target is not interaction.target:
                                    pass
                                carry_target = carry_target_additional
                                carry_target_si = carry_si
                                carry_target_constraint = carry_constraint_resolved

        if carry_target_si is not None and carry_target_si is not interaction:
            template_constraint = interaction_constraint.intersect(carry_target_constraint)
            del additional_constraint_list[carry_target_si]
        else:
            template_constraint = interaction_constraint
        templates, used_hand = TSC._get_specs_for_constraints(sim, interaction, template_constraint,
          pick=(interaction.context.pick),
          carry_target=carry_target)
        additional_template_list = {}
        for carry_si, carry_constraint_resolved in additional_constraint_list.items():
            carry_constraint_templates, _ = TSC._get_specs_for_constraints(sim, carry_si, carry_constraint_resolved,
              pick=(interaction.context.pick),
              carry_target=(carry_si.carry_target),
              used_hand_and_target=(
             used_hand, carry_target))
            additional_template_list[carry_si] = carry_constraint_templates

        return (templates, additional_template_list, carry_target_si)

    def _get_constraint_for_interaction(self, sim, interaction, participant_type, ignore_inertial, ignore_combinables):
        interaction_raw_constraint = interaction.constraint_intersection(sim=sim, participant_type=participant_type,
          posture_state=None)
        if gsi_handlers.posture_graph_handlers.archiver.enabled:
            gsi_handlers.posture_graph_handlers.add_possible_constraints(sim, interaction_raw_constraint, 'Interaction')
        else:
            interaction_constraint = interaction.transition_constraint_intersection(sim, participant_type, interaction_raw_constraint)
            if gsi_handlers.posture_graph_handlers.archiver.enabled:
                gsi_handlers.posture_graph_handlers.add_possible_constraints(sim, interaction_constraint, 'Interaction Transition')
            return interaction_constraint.valid or (
             interaction_constraint, ())
        interaction_constraint_resolved = self.resolve_constraint_for_hands(sim, self.interaction, interaction_constraint)
        if not interaction_constraint_resolved.valid:
            included_sis = [carry_si for carry_si in sim.si_state if sim.posture_state.is_carry_source_or_owning_interaction(carry_si)]
            return (interaction_constraint_resolved, included_sis)
        if self.ignore_all_other_sis:
            return (
             interaction_constraint, ())
        additional_included_sis = set()
        final_valid_combinables = ignore_combinables or interaction.get_combinable_interactions_with_safe_carryables()
        if interaction.is_super:
            if final_valid_combinables:
                if interaction.sim is sim:
                    test_intersection = interaction_constraint_resolved
                    interaction_constraint_no_holster = interaction.constraint_intersection(sim=sim, participant_type=participant_type, posture_state=None,
                      allow_holster=False)
                    interaction_constraint_no_holster = interaction.transition_constraint_intersection(sim, participant_type, interaction_constraint_no_holster)
                    for combinable in final_valid_combinables:
                        if combinable is interaction:
                            continue
                        combinable_constraint = combinable.constraint_intersection(sim=sim, posture_state=None)
                        if not combinable_constraint.valid:
                            break
                        test_intersection = test_intersection.intersect(combinable_constraint)
                        if not test_intersection.valid:
                            break
                        interaction_constraint_resolved = test_intersection
                        if combinable.targeted_carryable is not None:
                            test_intersection_no_holster = interaction_constraint_no_holster.intersect(combinable_constraint)
                            if test_intersection_no_holster.valid:
                                additional_included_sis.add(combinable)
                        else:
                            additional_included_sis.add(combinable)

        if gsi_handlers.posture_graph_handlers.archiver.enabled:
            gsi_handlers.posture_graph_handlers.add_possible_constraints(sim, interaction_constraint_resolved, 'Interaction Resolved')
        force_inertial_sis = self.interaction.posture_preferences.require_current_constraint or self.interaction.is_adjustment_interaction()
        if force_inertial_sis:
            ignore_inertial = False
        si_constraint, included_sis = sim.si_state.get_best_constraint_and_sources(interaction_constraint_resolved, (self.interaction),
          force_inertial_sis,
          ignore_inertial=ignore_inertial,
          participant_type=participant_type)
        if additional_included_sis:
            included_sis.update(additional_included_sis)
        if not si_constraint.valid:
            if interaction.is_cancel_aop:
                return (interaction_constraint_resolved, [])
            if gsi_handlers.posture_graph_handlers.archiver.enabled:
                gsi_handlers.posture_graph_handlers.add_possible_constraints(sim, si_constraint, 'SI Constraint')
            if not si_constraint.valid:
                if self._progress_max == TransitionSequenceStage.COMPLETE and interaction.context.can_derail_if_constraint_invalid:
                    self.derail(DerailReason.CONSTRAINTS_CHANGED, sim)
        else:
            return (
             si_constraint, included_sis)
        si_constraint_geometry_only = si_constraint.generate_geometry_only_constraint()
        if gsi_handlers.posture_graph_handlers.archiver.enabled:
            gsi_handlers.posture_graph_handlers.add_possible_constraints(sim, si_constraint_geometry_only, 'Geometry Only')
        combined_constraint = interaction_constraint_resolved.intersect(si_constraint_geometry_only)
        if gsi_handlers.posture_graph_handlers.archiver.enabled:
            gsi_handlers.posture_graph_handlers.add_possible_constraints(sim, combined_constraint, 'Int Resolved + Geometry')
        si_constraint_body_posture_only = si_constraint.generate_body_posture_only_constraint()
        final_constraint = combined_constraint.intersect(si_constraint_body_posture_only)
        body_aspect = sim.posture_state.body
        if body_aspect.mobile and body_aspect.posture_type is not SIM_DEFAULT_POSTURE_TYPE and not any((sub_constraint.geometry is not None for sub_constraint in final_constraint)) or interaction.is_cancel_aop or self.involves_specific_surface_or_body_target(final_constraint) or final_constraint.supports_mobile_posture(body_aspect.posture_type):
            posture_graph_service = services.current_zone().posture_graph_service
            posture_object = posture_graph_service.get_compatible_mobile_posture_target(sim)
            if posture_object is not None:
                self._pushed_mobile_posture_exit = True
                edge_constraint = posture_object.get_edge_constraint(sim=sim)
                final_constraint = final_constraint.generate_constraint_with_new_geometry((edge_constraint.geometry), routing_surface=(edge_constraint.routing_surface))
            if gsi_handlers.posture_graph_handlers.archiver.enabled:
                gsi_handlers.posture_graph_handlers.add_possible_constraints(sim, final_constraint, 'Pre Revised Constraint')
        return (
         final_constraint, included_sis)

    def has_geometry_outside_pool(self, constraint, sim):
        ray_projection_distance = 0.5
        pool = pool_utils.get_pool_by_block_id(sim.block_id)
        pool_center = pool.center_point
        for sub_constraint in constraint:
            sub_routing_surfaces = sub_constraint.get_all_valid_routing_surfaces()
            if not sub_routing_surfaces:
                continue
            for sub_surface in sub_routing_surfaces:
                if not sub_surface is None:
                    if sub_surface.type == routing.SurfaceType.SURFACETYPE_POOL or sub_constraint.geometry is None:
                        continue
                    for polygon in sub_constraint.geometry.polygon:
                        for polygon_corner in polygon:
                            if build_buy.is_location_pool(polygon_corner, sub_surface.secondary_id):
                                continue
                            polygon_corner_2d = sims4.math.Vector2(polygon_corner.x, polygon_corner.z)
                            v = pool_center - polygon_corner_2d
                            u = sims4.math.vector_normalize(v)
                            new_point = polygon_corner_2d + ray_projection_distance * u
                            new_position = sims4.math.Vector3(new_point.x, 0, new_point.y)
                            new_routing_location = build_buy.is_location_pool(new_position, sub_surface.secondary_id) or routing.Location(new_position, sims4.math.Quaternion.ZERO(), sub_surface)
                            if routing.test_connectivity_pt_pt(sim.routing_location, new_routing_location, sim.routing_context):
                                return True

        return False

    def involves_specific_surface_or_body_target(self, constraint):
        for sub_constraint in constraint:
            posture_state_spec = sub_constraint.posture_state_spec
            if posture_state_spec is not None:
                if not any((manifest_entry.surface in _NOT_SPECIFIC_ACTOR for manifest_entry in list(posture_state_spec.posture_manifest))) or posture_state_spec.body_target is None or isinstance(posture_state_spec.body_target, PostureSpecVariable):
                    return False

        return True

    def get_graph_test_functions(self, sim, target_sim, target_path_spec):
        sim_data = self._sim_data[sim]
        target_transitions = None
        if target_path_spec is not None:
            target_transitions = target_path_spec.path
        else:
            if target_transitions:
                previous_transition = None
                for target_transition in reversed(target_transitions):
                    target_posture_target = target_transition.body.target
                    if target_transition.body.posture_type.multi_sim:
                        break
                    if self.interaction.require_shared_body_target:
                        if previous_transition is not None:
                            if target_transition.body.posture_type.mobile:
                                target_posture_target = previous_transition.body.target
                                break
                    previous_transition = target_transition
                else:
                    target_posture_target = target_transitions[-1].body.target

            else:
                target_posture_target = None

            def valid_destination_test(destination_spec, var_map):

                def is_valid_destination():
                    dest_body = destination_spec.body
                    dest_body_target = dest_body.target
                    dest_body_posture_type = dest_body.posture_type
                    if dest_body_target is not None:
                        if sim in self._tried_destinations:
                            for tried_destination_spec in self._tried_destinations[sim]:
                                if dest_body_target == tried_destination_spec.body.target:
                                    return False

                    if sim in self._tried_destinations:
                        if destination_spec in self._tried_destinations[sim]:
                            return False
                    if destination_spec in sim_data.valid_dest_nodes:
                        return True
                    if target_sim is None:
                        if dest_body_posture_type.multi_sim:
                            if sim.posture.posture_type is not dest_body_posture_type:
                                return False
                    for additional_destination_validity_test in self.interaction.additional_destination_validity_tests:
                        if not additional_destination_validity_test(dest_body_target):
                            return False

                    if dest_body_target is None:
                        return True
                    if dest_body_target is not target_sim:
                        if not dest_body_posture_type.is_valid_destination_target(sim, dest_body_target, adjacent_sim=target_sim,
                          adjacent_target=target_posture_target):
                            return False
                    if dest_body_target.is_part:
                        if not dest_body_target.supports_posture_spec(destination_spec, (self.interaction), sim=sim):
                            return False
                    return True

                result = is_valid_destination()
                if result:
                    sim_data.valid_dest_nodes.add(destination_spec)
                return result

            valid_edge_test = None
            if target_transitions is not None:
                for transition_index, target_transition in enumerate(target_transitions):
                    target_transition_posture_type = target_transition.body.posture_type
                    if target_transition_posture_type.multi_sim and target_transition_posture_type.require_parallel_entry_transition:
                        previous_target_transition = target_transitions[transition_index - 1]
                        previous_target_transition_posture_type = previous_target_transition.body.posture_type

                        def valid_edge_test(node_a, node_b):
                            posture_type_a = node_a.body.posture_type
                            posture_type_b = node_b.body.posture_type
                            if posture_type_b is target_transition_posture_type:
                                return posture_type_a is previous_target_transition_posture_type or posture_type_a is PostureTuning.SIM_CARRIED_POSTURE
                            if posture_type_a.multi_sim or posture_type_b.multi_sim:
                                return target_path_spec.edge_exists(posture_type_a, posture_type_b)
                            return True

                        break

                if valid_edge_test is None and len(target_transitions) > 1:

                    def valid_edge_test(node_a, node_b):
                        if self._interaction.carry_target is sim:
                            node_b_body_target = node_b.body.target
                            if node_b_body_target is not None:
                                if node_b_body_target.is_sim:
                                    if node_b_body_target is not self._interaction.sim:
                                        return False
                        posture_type_a = node_a.body.posture_type
                        posture_type_b = node_b.body.posture_type
                        b_requires_parallel_entry = posture_type_b.multi_sim and posture_type_b.require_parallel_entry_transition
                        if b_requires_parallel_entry:
                            return target_path_spec.edge_exists(posture_type_a, posture_type_b)
                        return True

            elif target_sim is None:

                def valid_edge_test(node_a, node_b):
                    if node_b.body.posture_type.multi_sim:
                        if node_a.body.posture_type.multi_sim:
                            return True
                        return False
                    return True

        preferred_carrying_sim = self._interaction.context.preferred_carrying_sim
        if self._interaction._prefer_participants_as_carrying_sim is None:
            if preferred_carrying_sim in (self._interaction.sim, self._interaction.target, self._interaction.carry_target):
                preferred_carrying_sim = None
        if preferred_carrying_sim is not None:
            _valid_edge_test = valid_edge_test

            def valid_edge_test(node_a, node_b):
                if _valid_edge_test is not None:
                    result = _valid_edge_test(node_a, node_b)
                    if not result:
                        return result
                if node_b.body.target is not None:
                    if node_b.body.target.is_sim:
                        if node_b.body.target is not preferred_carrying_sim:
                            return False
                return True

        if target_transitions:
            if self._is_putdown_interaction(target=sim):
                put_down_body_target = target_transitions[-1].body.target
                _valid_edge_test2 = valid_edge_test

                def valid_edge_test(node_a, node_b):
                    if _valid_edge_test2 is not None:
                        result = _valid_edge_test2(node_a, node_b)
                        if not result:
                            return result
                    node_a_target = node_a.body.target
                    if node_a_target is not None:
                        if node_a_target.is_sim:
                            node_b_target = node_b.body.target
                            if node_b_target is not node_a_target:
                                if node_b_target is not put_down_body_target:
                                    return False
                    return True

        return (
         valid_destination_test, valid_edge_test)

    def _combine_preferences(self, sim, interaction, included_sis):
        preferences = interaction.combined_posture_preferences
        posture_preferences = PosturePreferencesData(preferences.apply_posture_costs, preferences.prefer_surface, preferences.require_current_constraint, preferences.posture_cost_overrides)
        combined_preferences = sims4.collections.AttributeDict(vars(posture_preferences))
        for si in included_sis:
            if si.has_active_cancel_replacement:
                continue
            si_preferences = si.combined_posture_preferences
            combined_preferences.apply_posture_costs = si_preferences.apply_posture_costs or combined_preferences.apply_posture_costs
            combined_preferences.prefer_surface = si_preferences.prefer_surface or combined_preferences.prefer_surface
            combined_preferences.require_current_constraint = si_preferences.require_current_constraint or combined_preferences.require_current_constraint
            for entry, value in si_preferences.posture_cost_overrides.items():
                if combined_preferences.posture_cost_overrides.get(entry):
                    combined_preferences.posture_cost_overrides[entry] += value
                    continue
                combined_preferences.posture_cost_overrides[entry] = value

        for posture, score in sim.Buffs.get_additional_posture_costs().items():
            if combined_preferences.posture_cost_overrides.get(posture):
                combined_preferences.posture_cost_overrides[posture] += score
                continue
            combined_preferences.posture_cost_overrides[posture] = score

        return sims4.collections.FrozenAttributeDict(combined_preferences)

    @property
    def relevant_objects(self):
        return self._relevant_objects

    def add_relevant_object(self, obj):
        if obj is None or isinstance(obj, PostureSpecVariable) or obj.is_sim:
            return
        relevant_object = obj.part_owner if obj.is_part else obj
        if relevant_object not in self._relevant_objects:
            relevant_object.register_transition_controller(self)
            self._relevant_objects.add(relevant_object)

    def _add_interaction_target_location_changed_callback(self):
        target = self.interaction.target
        if target is None:
            return
        if target.is_sim:
            return
        routing_component = target.routing_component
        if routing_component is None:
            return
        self.add_on_target_location_changed_callback(target)

    def add_on_target_location_changed_callback(self, target):
        target = target.part_owner if target.is_part else target
        if target not in self._location_changed_targets:
            target.register_on_location_changed(self._target_location_changed)
            self._location_changed_targets.add(target)

    def _target_location_changed(self, obj, *args, **kwargs):
        carry_target = self.interaction.carry_target
        if carry_target is not None:
            carry_target = carry_target.part_owner if carry_target.is_part else carry_target
        interaction_target = self.interaction.target
        if interaction_target is not None:
            interaction_target = interaction_target.part_owner if interaction_target.is_part else interaction_target
        elif carry_target is obj or interaction_target is obj:
            if self.interaction.sim is None:
                logger.error('Trying to derail a transition for interaction {} with a None Sim', (self.interaction), owner='camilogarcia')
            else:
                self.derail(DerailReason.CONSTRAINTS_CHANGED, self.interaction.sim)
        else:
            obj.unregister_on_location_changed(self._target_location_changed)
            self._location_changed_targets.remove(obj)

    def _clear_target_location_changed_callbacks(self):
        for target in self._location_changed_targets:
            target.unregister_on_location_changed(self._target_location_changed)

        self._location_changed_targets.clear()

    def _clear_relevant_objects(self):
        for obj in self._relevant_objects:
            if obj is not None:
                obj.is_sim or obj.unregister_transition_controller(self)

        self._relevant_objects.clear()

    def remove_relevant_object(self, obj):
        if obj is None or obj.is_sim:
            return
        relevant_obj = obj.part_owner if obj.is_part else obj
        if relevant_obj not in self._relevant_objects:
            return
        relevant_obj.unregister_transition_controller(self)
        self._relevant_objects.remove(relevant_obj)

    def will_derail_if_given_object_is_reset(self, obj):
        if not self.succeeded:
            if obj in self._relevant_objects:
                return True
        return False

    def get_transitions_for_sim(self, *args, **kwargs):
        if not inject_interaction_name_in_callstack:
            result = yield from (self._get_transitions_for_sim)(*args, **kwargs)
            return result
        name = self.interaction.__class__.__name__.replace('-', '_')
        name_f = create_custom_named_profiler_function(name, use_generator=True)
        result = yield from name_f((lambda: (self._get_transitions_for_sim)(*args, **kwargs)))
        return result
        if False:
            yield None

    def _get_transitions_for_sim(self, timeline, sim, target_sim=None, target_path_spec=None, ignore_inertial=False, ignore_combinables=False):
        global global_plan_lock
        if sim is None:
            return postures.posture_graph.EMPTY_PATH_SPEC
            participant_type = self.interaction.get_participant_type(sim)
            interaction = self.interaction
            is_putdown = self._is_putdown_interaction(target=sim)
            sim_data = self._sim_data[sim]
            sim_data.progress_max = self._progress_max
            final_constraint, included_sis = sim_data.constraint
            if final_constraint is None:
                if is_putdown:
                    constraint_interaction, _ = interaction.get_target_si()
                    constraint_interaction_participant_type = ParticipantType.Actor
                else:
                    constraint_interaction = interaction
                    constraint_interaction_participant_type = participant_type
                final_constraint, included_sis = self._get_constraint_for_interaction(sim, constraint_interaction, constraint_interaction_participant_type, ignore_inertial, ignore_combinables)
                if self.is_derailed(sim):
                    return postures.posture_graph.EMPTY_PATH_SPEC
                final_constraint = self._revise_final_constraint(sim, final_constraint, interaction)
                if not final_constraint.valid:
                    included_sis = list(sim.si_state.all_guaranteed_si_gen(priority=(self.interaction.priority), group_id=(self.interaction.group_id)))
                sim_data.constraint = (
                 final_constraint, included_sis)
                for si in included_sis:
                    si.owning_transition_sequences.add(self)

                if gsi_handlers.interaction_archive_handlers.is_archive_enabled(self._interaction):
                    if sim is interaction.sim:
                        gsi_handlers.interaction_archive_handlers.add_constraint(interaction, sim, final_constraint)
            if final_constraint is ANYWHERE:
                reservation_handler = self.interaction.get_interaction_reservation_handler(sim=sim)
                if reservation_handler:
                    reservation_result = reservation_handler.may_reserve()
                    if not reservation_result:
                        self._shortest_path_success[sim] = False
                        self.set_failure_target(sim, (TransitionFailureReasons.RESERVATION), target_id=(reservation_result.result_obj.id))
                        return postures.posture_graph.EMPTY_PATH_SPEC
                if gsi_handlers.posture_graph_handlers.archiver.enabled:
                    gsi_handlers.posture_graph_handlers.archive_current_spec_valid(sim, self.interaction)
                if self.interaction.outfit_change is not None and self.interaction.outfit_change.on_route_change is not None:
                    path_nodes = [
                     sim.posture_state.spec, sim.posture_state.spec]
                else:
                    path_nodes = [sim.posture_state.spec]
                path = postures.posture_graph.PathSpec(path_nodes, 0, {}, sim.posture_state.spec, final_constraint, final_constraint)
                if sim_data.progress_max >= TransitionSequenceStage.CONNECTIVITY:
                    sim_data.connectivity = postures.posture_graph.Connectivity(path, None, None, None)
                    sim_data.progress = TransitionSequenceStage.CONNECTIVITY
                if sim_data.progress_max >= TransitionSequenceStage.ROUTES:
                    sim_data.progress = TransitionSequenceStage.ROUTES
                    sim_data.path_spec = path
                return path
            if not final_constraint.valid:
                self.set_failure_target(sim, TransitionFailureReasons.NO_VALID_INTERSECTION, None)
                self._shortest_path_success[sim] = False
                path = postures.posture_graph.EMPTY_PATH_SPEC
                if sim_data.progress_max >= TransitionSequenceStage.ROUTES:
                    sim_data.progress = TransitionSequenceStage.ROUTES
                    sim_data.path_spec = path
                return path
            if sim_data.progress >= TransitionSequenceStage.TEMPLATES:
                templates, additional_template_list, carry_target_si = sim_data.templates
            else:
                templates, additional_template_list, carry_target_si = self.get_templates_including_carry_transference(sim, interaction, final_constraint, included_sis, participant_type)
                if gsi_handlers.posture_graph_handlers.archiver.enabled:
                    gsi_handlers.posture_graph_handlers.add_possible_constraints(sim, final_constraint, 'Final Constraint')
                sim_data.templates = (templates, additional_template_list, carry_target_si)
                sim_data.progress = TransitionSequenceStage.TEMPLATES
            valid_destination_test, valid_edge_test = self.get_graph_test_functions(sim, target_sim, target_path_spec)
            posture_graph = services.current_zone().posture_graph_service
            if sim_data.progress >= TransitionSequenceStage.PATHS:
                segmented_paths = sim_data.segmented_paths
            else:
                preferences = self._combine_preferences(sim, interaction, included_sis)
                segmented_paths = posture_graph.get_segmented_paths(sim, templates, additional_template_list, interaction, participant_type, valid_destination_test, valid_edge_test, preferences, final_constraint, included_sis)
                sim_data.progress = TransitionSequenceStage.PATHS
                sim_data.segmented_paths = segmented_paths
                sim_data.intended_location = sim.get_intended_location_excluding_transition(self)
            if not segmented_paths:
                self._shortest_path_success[sim] = False
                return postures.posture_graph.EMPTY_PATH_SPEC
            all_destinations = (set().union)(*(sp.destinations for sp in segmented_paths))
            if sim_data.progress_max < TransitionSequenceStage.CONNECTIVITY:
                return postures.posture_graph.EMPTY_PATH_SPEC
            if sim_data.progress >= TransitionSequenceStage.CONNECTIVITY:
                connectivity = sim_data.connectivity
        else:
            postures.posture_graph.set_transition_destinations(self.sim, {}, {})
            resolve_animation_participant = self.interaction.get_constraint_resolver(None)
            connectivity = posture_graph.generate_connectivity_handles(sim, segmented_paths, interaction, participant_type, resolve_animation_participant, self._force_carry_path)
            sim_data.connectivity = connectivity
            sim_data.progress = TransitionSequenceStage.CONNECTIVITY
        if interaction.teleporting:
            path = posture_graph.handle_teleporting_path(segmented_paths)
            if sim_data.progress_max >= TransitionSequenceStage.ROUTES:
                sim_data.path_spec = path
                sim_data.progress = TransitionSequenceStage.ROUTES
            _, source_dest_sets, _, _ = connectivity
            for _, destination_handles, _, _, _, _ in source_dest_sets.values():
                for dest_data in destination_handles.values():
                    _, _, _, _, dest_goals, _, _ = dest_data
                    if interaction.dest_goals is not None:
                        interaction.dest_goals.extend(dest_goals)

            return path
        if interaction.disable_transitions:
            return
        if self._progress_max < TransitionSequenceStage.ROUTES:
            return
        success = False
        path_spec = postures.posture_graph.EMPTY_PATH_SPEC
        while global_plan_lock:
            yield from element_utils.run_child(timeline, elements.BusyWaitElement(soft_sleep_forever(), path_plan_allowed))

        global_plan_lock = sim.ref()
        try:
            success, path_spec = yield from posture_graph.find_best_path_pair(self.interaction, sim, connectivity, timeline)
            if gsi_handlers.posture_graph_handlers.archiver.enabled:
                gsi_handlers.posture_graph_handlers.log_possible_segmented_paths(sim, segmented_paths)
            elif not success:
                if path_spec.failed_path_type != PathType.MIDDLE_LEFT:
                    if path_spec.failed_path_type != PathType.MIDDLE_RIGHT:
                        if all_destinations - self._tried_destinations[sim]:
                            if path_spec.destination_spec is not None:
                                if self._failure_path_spec is None:
                                    self._failure_path_spec = path_spec
                                sim_data.final_destination = path_spec.destination_spec
                                self.derail(DerailReason.TRANSITION_FAILED, sim)
                                return postures.posture_graph.EMPTY_PATH_SPEC
                path_spec.finalize(sim)
                additional_sis = posture_graph.handle_additional_pickups_and_putdowns(path_spec, additional_template_list, sim)
                defer_carry = any((node.body.posture_type.mobile for node in path_spec.path))
                should_derail = defer_carry or not self._interaction.cancel_incompatible_carry_interactions(can_defer_putdown=False, derail_actors=True)
                if should_derail:
                    self.derail(DerailReason.WAIT_FOR_CARRY_TARGET, sim)
                current_path = path_spec.remaining_original_transition_specs()
                if current_path:
                    sim_data.path_spec = path_spec
                    destination_node = current_path[-1]
                    sim_data.final_destination = destination_node.posture_spec
                    all_included_sis = set(included_sis)
                    if carry_target_si is not None:
                        if carry_target_si is not self.interaction:
                            all_included_sis.add(carry_target_si)
                    all_included_sis.update(additional_sis)
                    sim_data.final_included_sis = all_included_sis
                    for si in all_included_sis:
                        si.owning_transition_sequences.add(self)

                    if sim is self.interaction.sim:
                        if destination_node.var_map:
                            self._original_interaction_target = self.interaction.target
                            self._original_interaction_target_changed = True
                            self.interaction.apply_var_map(sim, destination_node.var_map)
                    if destination_node.locked_params and not destination_node.mobile:
                        if self.interaction.apply_transition_dest_params:
                            self.interaction.locked_params += destination_node.locked_params
                        if not transform_almost_equal((sim.intended_location.transform), (sim.location.transform), epsilon=(sims4.geometry.ANIMATION_SLOT_EPSILON)):
                            sim.routing_component.on_intended_location_changed(sim.intended_location)
                            for _, _, carry_object in get_carried_objects_gen(sim):
                                if carry_object.is_sim:
                                    carry_object.routing_component.on_intended_location_changed(sim.intended_location)

                        if final_constraint.create_jig_fn is not None:
                            final_constraint.create_jig_fn(sim, intended_location=(sim.intended_location))
            else:
                path_spec = postures.posture_graph.EMPTY_PATH_SPEC
                sim_data.path_spec = path_spec
            sim_data.progress = TransitionSequenceStage.ROUTES
            self._shortest_path_success[sim] = success
            if self.interaction.on_path_planned_callbacks is not None:
                self.interaction.on_path_planned_callbacks(interaction=(self.interaction), success=success)
            return path_spec
        finally:
            global_plan_lock = None

        if False:
            yield None

    @staticmethod
    def _revise_final_constraint(sim, final_constraint, interaction):
        if not final_constraint.valid:
            return final_constraint
        else:
            new_constraints = []
            for constraint in final_constraint:
                posture_state_spec = constraint._posture_state_spec
                if posture_state_spec is None:
                    new_constraints.append(constraint)
                    continue
                new_posture_manifest = set()
                for posture_manifest_entry in posture_state_spec.posture_manifest:
                    specific_posture = posture_manifest_entry.posture_type_specific
                    if specific_posture is not None:
                        new_posture_manifest.add(posture_manifest_entry)
                        continue
                    family = posture_manifest_entry.family
                    posture_family = POSTURE_FAMILY_MAP.get(family)
                    if not posture_family:
                        if family == '*' or family == '':
                            return final_constraint
                        logger.error("No postures in the '{}' family. Interaction {}.", family,
                          interaction, owner='manus')
                        continue
                    for specific in posture_family:
                        if specific.consider_posture_for_family_constraints or sim.posture.posture_type is specific:
                            new_entry = posture_manifest_entry.clone(family=None, specific=(specific._posture_name))
                            new_posture_manifest.add(new_entry)

                if not new_posture_manifest:
                    logger.error('While evaluating interaction {}, could not find any substitutions for {}', interaction,
                      final_constraint, owner='manus')
                    return final_constraint
                    body_target_in_spec = posture_state_spec.body_target
                    if body_target_in_spec is None or body_target_in_spec == PostureSpecVariable.ANYTHING:
                        if posture_state_spec.is_vehicle_only_spec():
                            parented_vehicle = sim.parented_vehicle
                            if parented_vehicle is not None:
                                body_target_in_spec = parented_vehicle
                    new_posture_state_spec = PostureStateSpec(FrozenPostureManifest(new_posture_manifest), posture_state_spec.slot_manifest, body_target_in_spec)
                    new_constraint = constraint.generate_constraint_with_posture_spec(new_posture_state_spec)
                    new_constraints.append(new_constraint)

            new_final_constraint = create_constraint_set(new_constraints)
            new_final_constraint.valid or logger.error('While evaluating interaction {}, _revise_final_constraint created an invalid constraint {}.', interaction,
              new_final_constraint, owner='manus')
            return final_constraint
        return new_final_constraint

    def set_sim_progress(self, sim, progress: TransitionSequenceStage):
        if sim not in self._sim_data:
            return
        sim_data = self._sim_data[sim]
        if progress > sim_data.progress:
            raise RuntimeError('Attempt to set progress for a Sim forwards: {} > {}'.format(progress, sim_data.progress))
        if progress < TransitionSequenceStage.ACTOR_TARGET_SYNC:
            sim_data.progress = TransitionSequenceStage.ROUTES
        if progress < TransitionSequenceStage.ROUTES:
            self._shortest_path_success[sim] = True
            if sim_data.path_spec is not None:
                sim_data.path_spec.cleanup_path_spec(sim)
                sim_data.path_spec = None
            del self._blocked_sis[:]
        if progress < TransitionSequenceStage.PATHS:
            sim_data.valid_dest_nodes = set()
            sim_data.final_destination = None
            sim_data.segmented_paths = None
        if progress < TransitionSequenceStage.CONNECTIVITY:
            sim_data.connectivity = (None, None, None, None)
        if progress < TransitionSequenceStage.TEMPLATES:
            self._clear_owned_transition(sim)
            if sim_data.final_included_sis is not None:
                for si in sim_data.final_included_sis:
                    si.disable_cancel_by_posture_change = False

                sim_data.final_included_sis = None
            sim_data.intended_location = None
            sim_data.constraint = (None, None)
            sim_data.templates = (None, None, None)
        sim_data.progress = progress

    def reset_sim_progress(self, sim):
        sim_data = self._sim_data.get(sim)
        if sim_data is not None:
            self.set_sim_progress(sim, TransitionSequenceStage.EMPTY)
            sim.queue.clear_head_cache()

    def reset_all_progress(self):
        if self._sim_data is not None:
            for sim in self._sim_data:
                self.reset_sim_progress(sim)

    def _build_and_log_transitions_for_sim(self, timeline, sim, required=True, **kwargs):
        path_spec = yield from (self._build_transitions_for_sim)(timeline, sim, required=required, **kwargs)
        if gsi_handlers.posture_graph_handlers.archiver.enabled:
            try:
                gsi_handlers.posture_graph_handlers.archive_path(sim, path_spec, self._shortest_path_success[sim], self._progress_max)
            except:
                logger.exception('GSI Transition Archive Failed.')

        return path_spec
        if False:
            yield None

    def _build_transitions_for_sim(self, timeline, sim, required=True, **kwargs):
        sim_data = self._sim_data.get(sim)
        if sim_data is None:
            sim_data = TransitionSequenceData()
            self._sim_data[sim] = sim_data
        else:
            needs_reset = False
            if sim_data.path_spec is not None:
                if sim_data.path_spec is not EMPTY_PATH_SPEC:
                    current_state = sim.posture_state.get_posture_spec(sim_data.path_spec.var_map)
                    current_path = sim_data.path_spec.path
                    if not current_path[0].same_spec_except_slot(current_state):
                        if not current_path[0].same_spec_ignoring_surface_if_mobile(current_state):
                            needs_reset = True
            intended_location_built = sim_data.intended_location
            if not needs_reset:
                if intended_location_built is not None:
                    intended_location_current = sim.get_intended_location_excluding_transition(self)
                    if not sims4.math.transform_almost_equal_2d((intended_location_built.transform), (intended_location_current.transform), epsilon=(sims4.geometry.ANIMATION_SLOT_EPSILON)) or intended_location_built.routing_surface != intended_location_current.routing_surface:
                        needs_reset = True
            if not needs_reset:
                _, included_sis = sim_data.constraint
                if included_sis:
                    needs_reset = any((si.is_finishing for si in included_sis))
            if not needs_reset:
                if sim_data.progress >= TransitionSequenceStage.PATHS:
                    segmented_paths = sim_data.segmented_paths
                    needs_reset = segmented_paths and not all((segmented_path.check_validity(sim) for segmented_path in segmented_paths))
            if not needs_reset:
                if sim_data.progress >= TransitionSequenceStage.ROUTES:
                    needs_reset = not sim_data.path_spec.check_validity(sim)
            if needs_reset:
                self.reset_sim_progress(sim)
            if sim_data.path_spec is not None:
                if sim_data.progress < TransitionSequenceStage.ROUTES:
                    raise RuntimeError('Sim has path specs but progress < ROUTES')
                return sim_data.path_spec
            if gsi_handlers.posture_graph_handlers.archiver.enabled:
                gsi_handlers.posture_graph_handlers.set_current_posture_interaction(sim, self.interaction)
            path_spec = yield from (self.get_transitions_for_sim)(timeline, sim, **kwargs)
            if self.is_derailed(sim):
                return path_spec
            if path_spec is EMPTY_PATH_SPEC:
                if self.interaction.combinable_interactions:
                    self.set_sim_progress(sim, TransitionSequenceStage.EMPTY)
                    path_spec = yield from (self.get_transitions_for_sim)(timeline, sim, ignore_combinables=True, **kwargs)
                    if self.is_derailed(sim):
                        return path_spec
                if path_spec is EMPTY_PATH_SPEC:
                    must_include_sis = list(sim.si_state.all_guaranteed_si_gen(self.interaction.priority, self.interaction.group_id))
                    if not must_include_sis:
                        self.set_sim_progress(sim, TransitionSequenceStage.EMPTY)
                        path_spec = yield from (self.get_transitions_for_sim)(timeline, sim, ignore_inertial=True, ignore_combinables=True, **kwargs)
                        if self.is_derailed(sim):
                            return path_spec
            if self._progress_max < TransitionSequenceStage.COMPLETE or self.interaction.disable_transitions:
                return path_spec
            if self._failure_path_spec is not None:
                if path_spec is EMPTY_PATH_SPEC:
                    self._sim_data[sim].path_spec = self._failure_path_spec
                    self._failure_path_spec.generate_transition_interactions(sim, (self.interaction), transition_success=(self._shortest_path_success[sim]))
                    return self._failure_path_spec
            current_path = path_spec.remaining_path
            current_state = current_path or None
            if sim is not None and required and self.sim is sim:
                logger.info('{} could not find transitions for {}.', self, sim)
                self.cancel(test_result='No path found for sim.')
            else:
                current_state = sim.posture_state.get_posture_spec(path_spec.var_map)
                path_spec.flag_slot_reservations()
                if self._is_putdown_interaction(target=sim):
                    transition_interaction, _ = self.interaction.get_target_si()
                else:
                    transition_interaction = self.interaction
                result = path_spec.generate_transition_interactions(sim, transition_interaction, transition_success=(self._shortest_path_success[sim]))
                if not result:
                    logger.info('{} failed to generate transitions for {}.', self, sim)
                    self.cancel(test_result='Failed to generate transition interactions for sequence.')
                if len(current_path) == 1:
                    if current_state == current_path[0]:
                        if not current_path[0].body.posture_type.unconstrained:
                            path_spec.completed_path = True
                return path_spec
        if False:
            yield None

    @staticmethod
    def do_paths_incompatibly_share_body_target(path_spec_a, path_spec_b, exception_fn=None):
        if path_spec_a is not None:
            if path_spec_b is not None:
                for node_a in path_spec_a.path:
                    if node_a.body_target is not None:
                        for node_b in path_spec_b.path:
                            if node_a.body_target is node_b.body_target:
                                if node_a.body_posture.targets_same_part:
                                    if node_b.body_posture.targets_same_part:
                                        continue
                                if exception_fn is not None:
                                    if exception_fn(node_a, node_b):
                                        continue
                                return True

        return False

    def _build_transitions(self, timeline):
        if gsi_handlers.posture_graph_handlers.archiver.enabled:
            gsi_handlers.posture_graph_handlers.increment_build_pass(self.sim, self.interaction)
            gsi_handlers.posture_graph_handlers.add_tried_destinations(self.sim, self.interaction, self._tried_destinations)
        else:
            actor = self.interaction.get_participant(ParticipantType.Actor)
            if self.interaction.carry_target is not None and self.interaction.carry_target.is_sim:
                target = self.interaction.carry_target
            else:
                target = self.interaction.get_participant(ParticipantType.TargetSim)
            services.current_zone().posture_graph_service.update_generic_sim_carry_node(actor)
            if (target not in self.interaction.required_sims(for_threading=True) or self.interaction).is_social:
                if self.interaction.is_target_sim_location_and_posture_valid():
                    if target in self._sim_data:
                        self.set_sim_progress(target, TransitionSequenceStage.EMPTY)
                        del self._sim_data[target]
                    target = None
            actor_path_spec = yield from self._build_and_log_transitions_for_sim(timeline, actor, target_sim=target)
            if not self._shortest_path_success[actor]:
                return
            if not self._has_tried_bring_group_along:
                if self._progress_max == TransitionSequenceStage.COMPLETE:
                    main_group = self.sim.get_main_group()
                    if main_group is not None and main_group.has_social_geometry(self.sim) and self.interaction.context.source == InteractionSource.PIE_MENU:
                        if not self.interaction.is_social:
                            main_group.add_non_adjustable_sim(self.sim)
                        self._has_tried_bring_group_along = True
                        if self.interaction.should_rally:
                            self._interaction.maybe_bring_group_along()
                            if self.sim in self.interaction.preferred_carrying_sims:
                                self.cancel(finishing_type=(FinishingType.DISPLACED), cancel_reason_msg='Displaced by rally carry interaction.')
                                context = InteractionContext(actor, (InteractionSource.POSTURE_GRAPH), (Priority.Low), insert_strategy=(QueueInsertStrategy.FIRST),
                                  must_run_next=True)
                                aop = AffordanceObjectPair(CarryTuning.RALLY_INTERACTION_CARRY_RULES.wait_to_carry_affordance, self.interaction.target, CarryTuning.RALLY_INTERACTION_CARRY_RULES.wait_to_carry_affordance, None)
                                aop.test_and_execute(context)
                                return
                    elif self.interaction.relocate_main_group:
                        if main_group is not None:
                            main_group.try_relocate_around_focus(self.sim)
            if target is not None and actor_path_spec is not None:
                with create_puppet_postures(target):
                    target_path_spec = yield from self._build_and_log_transitions_for_sim(timeline, target, target_sim=actor, target_path_spec=actor_path_spec)
                    if not self._shortest_path_success[target]:
                        if self._shortest_path_success[actor]:
                            self.derail(DerailReason.TRANSITION_FAILED, actor)
                            self.derail(DerailReason.TRANSITION_FAILED, target)
                        return
                    if not self._is_putdown_interaction():
                        carry_target = self._interaction.carry_target
                        if carry_target is not None and carry_target.is_sim:

                            def exception_fn(actor_node, target_node):
                                if actor_node.body.posture_type is postures.posture_graph.SIM_DEFAULT_POSTURE_TYPE:
                                    return True
                                return False

                        else:
                            if actor.posture.target is not None and actor.posture.target is target.posture.target:

                                def exception_fn(actor_node, target_node):
                                    if actor_node == actor_path_spec.path[0]:
                                        return True
                                    return False

                            else:
                                exception_fn = None
                        if TransitionSequenceController.do_paths_incompatibly_share_body_target(actor_path_spec, target_path_spec, exception_fn=exception_fn):
                            self.derail(DerailReason.TRANSITION_FAILED, actor)
                            self.derail(DerailReason.TRANSITION_FAILED, target)
                            return
            else:
                target_path_spec = None
            for sim in self.get_transitioning_sims():
                if sim is not actor and sim is not target and sim in self.interaction.get_participants(ParticipantType.AllSims):
                    yield from self._build_and_log_transitions_for_sim(timeline, sim, required=False)

            if self._progress_max < TransitionSequenceStage.ROUTES or self.interaction.disable_transitions or self.any_derailed:
                return
            actor_data = self._sim_data[actor]
            if target is not None:
                target_data = self._sim_data[target]
            if actor_data.progress < TransitionSequenceStage.ACTOR_TARGET_SYNC:
                if actor_path_spec.path:
                    if target_path_spec and target_path_spec.path:
                        for transition in actor_path_spec.path:
                            if not transition is not None or transition.body.posture_type.multi_sim or self.interaction.require_shared_body_target:
                                if actor_path_spec.cost <= target_path_spec.cost:
                                    self.set_sim_progress(target, TransitionSequenceStage.TEMPLATES)
                                    with create_puppet_postures(target):
                                        target_path_spec = yield from self._build_and_log_transitions_for_sim(timeline, target, target_sim=actor, target_path_spec=actor_path_spec)
                                        if self.is_derailed(target):
                                            return
                                else:
                                    self.set_sim_progress(actor, TransitionSequenceStage.TEMPLATES)
                                    actor_path_spec = yield from self._build_and_log_transitions_for_sim(timeline, actor, target_sim=target, target_path_spec=target_path_spec)
                                    if self.is_derailed(actor):
                                        return
                                    break

        actor_data.progress = TransitionSequenceStage.ACTOR_TARGET_SYNC
        if target is not None:
            target_data.progress = TransitionSequenceStage.ACTOR_TARGET_SYNC
        if not self.interaction.disable_transitions:
            for sim in self.get_transitioning_sims():
                if sim in self._sim_data:
                    path_spec = self._get_path_spec(sim)
                    if path_spec is not None:
                        path_spec.unlock_portals(sim)
                        if len(path_spec.path) > 1 and path_spec.path[-1].body.posture_type.mobile:
                            if not path_spec.path[-2].body.posture_type.mobile:
                                continue
                    final_constraint = path_spec.final_constraint
                    if final_constraint is not None:
                        interaction = path_spec.is_failure_path or self.get_interaction_for_sim(sim)
                        if interaction is None:
                            interaction = self.interaction
                        else:
                            single_point, routing_surface = final_constraint.single_point()
                            constraint_areas = {constraint.area() for constraint in final_constraint}
                            constraint_areas.discard(None)
                            if single_point is not None or constraint_areas and min(constraint_areas) < self.MINIMUM_AREA_FOR_NO_STAND_RESERVATION:
                                final_location = path_spec.final_routing_location
                                if final_location is not None:
                                    single_point = final_location.transform.translation
                                    routing_surface = final_location.routing_surface
                                if single_point is not None:
                                    self.add_stand_slot_reservation(sim, interaction, single_point, routing_surface)
                                else:
                                    sim.routing_component.remove_stand_slot_reservation(interaction)
                        sim.routing_component.remove_stand_slot_reservation(interaction)

        for sim in self._sim_data:
            self.advance_path(sim, prime_path=True)

        if False:
            yield None

    def _assign_source_interaction_to_posture_state(self, sim, si, posture_state):
        source_interaction = None
        potential_source_sis = [source_si for source_si in sim.si_state if si is None else itertools.chain((si,), sim.si_state) if source_si.provided_posture_type is not None]
        for aspect in posture_state.aspects:
            for potential_source_si in potential_source_sis:
                if aspect.posture_type is potential_source_si.provided_posture_type:
                    if aspect.source_interaction is None:
                        aspect.source_interaction = potential_source_si
                    if aspect.source_interaction is None or potential_source_si is si:
                        source_interaction = potential_source_si
                        break

        return source_interaction

    def _get_transition_path_clothing_change(self, path_nodes, sim_info):

        def get_node_water_height(path_node):
            return get_water_depth(path_node.position[0], path_node.position[2], path_node.routing_surface_id.secondary_id)

        if services.terrain_service.ocean_object() is None:
            return
        swimwear_water_depth, swimwear_outfit_change_reason = OceanTuning.get_actor_swimwear_change_info(sim_info)
        if swimwear_water_depth is None:
            return
        if swimwear_outfit_change_reason is None:
            return
        should_change_into_swimwear = False
        prev_node_in_water = get_node_water_height(path_nodes[0]) > swimwear_water_depth
        for node in path_nodes[1:]:
            position = node.position
            if bool(build_buy.get_pond_id(sims4.math.Vector3(position[0], position[1], position[2]))):
                continue
            current_node_in_water = get_node_water_height(node) > swimwear_water_depth
            if current_node_in_water:
                if not prev_node_in_water:
                    should_change_into_swimwear = True
                    break
            prev_node_in_water = current_node_in_water

        if should_change_into_swimwear:
            outfit = sim_info.get_outfit_for_clothing_change(self.interaction, swimwear_outfit_change_reason)
            if outfit is not None:
                return build_critical_section(sim_info.get_change_outfit_element_and_archive_change_reason(outfit,
                  do_spin=True, interaction=(self.interaction), change_reason=(self._get_transition_path_clothing_change.__name__)), flush_all_animations)

    def create_transition(self, create_posture_state_func, si, current_transition, var_map, participant_type, sim, *additional_sims):
        posture_state = create_posture_state_func(var_map)
        if posture_state is None:
            self.cancel()
            return (lambda _: False)
        source_interaction = self._assign_source_interaction_to_posture_state(sim, si, posture_state)
        if not posture_state.constraint_intersection.valid:
            logger.error('create_transition ended up with a constraint that is invalid: {} for interaction: {}', posture_state, self.interaction)
            return (lambda _: False)
        last_nonmobile_posture_with_entry_change = None
        remaining_transitions = self.get_remaining_transitions(sim)
        if sim.posture_state.body.supports_outfit_change:
            if not any((remaining_transition.body_posture.supports_outfit_change for remaining_transition in remaining_transitions)):
                for remaining_transition in reversed(remaining_transitions):
                    if remaining_transition.body_posture.outfit_change and remaining_transition.body_posture.posture_type is not posture_state.body.posture_type and remaining_transition.body_posture.multi_sim == posture_state.body.multi_sim:
                        last_nonmobile_posture_with_entry_change = remaining_transition.body_posture
                        break

        elif last_nonmobile_posture_with_entry_change:
            entry_change = last_nonmobile_posture_with_entry_change.post_route_clothing_change((self.interaction), do_spin=True, sim_info=(sim.sim_info))
        else:
            if posture_state.body.outfit_change:
                entry_change = posture_state.body.post_route_clothing_change((self.interaction), do_spin=True, sim_info=(sim.sim_info))
            else:
                entry_change = None
        if posture_state.body.outfit_change:
            if entry_change is not None:
                if posture_state.body.has_exit_change((self.interaction), sim_info=(sim.sim_info)):
                    sim.sim_info.set_previous_outfit(None)
            posture_state.body.prepare_exit_clothing_change((self.interaction), sim_info=(sim.sim_info))
        on_route_change = None
        if not self._processed_on_route_change:
            if entry_change is None and not self.sim.posture_state.body.supports_outfit_change:
                if posture_state.body.supports_outfit_change:
                    on_route_change = self.interaction.pre_route_clothing_change(do_spin=(not sim.should_route_instantly()))
                    self._processed_on_route_change = True
        else:
            exit_change = sim.posture_state.body.exit_clothing_change((self.interaction), sim_info=(sim.sim_info), do_spin=True)
            if entry_change is not None:
                clothing_change = entry_change
            else:
                if on_route_change is not None:
                    clothing_change = on_route_change
                else:
                    if exit_change is not None:
                        clothing_change = exit_change
                    else:
                        clothing_change = None
        outdoor_streetwear_change = self.outdoor_streetwear_change.get(sim.id, None)
        if clothing_change is None and outdoor_streetwear_change is not None and not sim.posture_state.body.supports_outfit_change:
            if posture_state.body.supports_outfit_change:
                clothing_change = build_critical_section(sim.sim_info.get_change_outfit_element_and_archive_change_reason(outdoor_streetwear_change,
                  do_spin=True, interaction=(self.interaction), change_reason=(OutfitChangeReason.WeatherBased)), flush_all_animations)
                del self.outdoor_streetwear_change[sim.id]
            context = PostureContext(self.interaction.context.source, self.interaction.priority, self.interaction.context.pick)
            owning_interaction = None
            if not source_interaction is None:
                if source_interaction.visible or source_interaction is not None:
                    final_valid_combinables = self.interaction.get_combinable_interactions_with_safe_carryables()
                    posture_target = source_interaction.target
                    if posture_target is not None and posture_target.has_component(CARRYABLE_COMPONENT):
                        interactions_set = {
                         self.interaction}
                        interactions_set.update(posture_state.sim.si_state)
                        if final_valid_combinables is not None:
                            interactions_set.update(final_valid_combinables)
                        for si in interactions_set:
                            if si.carry_target is posture_target:
                                owning_interaction = si
                                break

            elif posture_target is not None:
                if final_valid_combinables:
                    if posture_target.is_part:
                        posture_target_part_owner = posture_target.part_owner
                    else:
                        posture_target_part_owner = posture_target
                    for combinable in final_valid_combinables:
                        if combinable != self.interaction and combinable.target is posture_target_part_owner:
                            owning_interaction = combinable
                            break

            if owning_interaction is None:
                owning_interaction = self.interaction
            else:
                transition_spec = self.get_transition_spec(sim)
                portal_obj = transition_spec.portal_obj
                if portal_obj is not None:
                    portal_id = transition_spec.portal_id
                    portal_entry_clothing_change = portal_obj.get_entry_clothing_change(owning_interaction,
                      portal_id, sim_info=(sim.sim_info))
                    portal_exit_clothing_change = portal_obj.get_exit_clothing_change(owning_interaction,
                      portal_id, sim_info=(sim.sim_info))
                else:
                    portal_entry_clothing_change = None
                    portal_exit_clothing_change = None
                if transition_spec.path is not None:
                    final_node = transition_spec.path[-1]
                    final_transform = sims4.math.Transform((sims4.math.Vector3)(*final_node.position), (sims4.math.Quaternion)(*final_node.orientation))
                    final_transform_constraint = interactions.constraints.Transform(final_transform, routing_surface=(final_node.routing_surface_id))
                    posture_state.add_constraint(final_node, final_transform_constraint)
                    path_nodes = list(transition_spec.path.nodes)
                    path_clothing_change = self._get_transition_path_clothing_change(path_nodes, sim.sim_info)
                    if path_clothing_change is not None:
                        clothing_change = path_clothing_change
                else:
                    final_node = None
            sim.si_state.pre_resolve_posture_change(posture_state)
            if final_node is not None:
                posture_state.remove_constraint(final_node)
            elif transition_spec.path is not None:
                posture_state.remove_constraint(final_node)
            else:
                transition = PostureStateTransition(posture_state, source_interaction, context, var_map, transition_spec, self.interaction, owning_interaction, self.get_transition_should_reserve(sim), transition_spec.final_constraint)
                if clothing_change is not None:
                    if sim.posture_state.body.supports_outfit_change:
                        if posture_state.body.saved_exit_clothing_change is not None:
                            sequence = build_critical_section_with_finally(clothing_change, transition, (lambda _: posture_state.body.ensure_exit_clothing_change_application()))
                        else:
                            sequence = (
                             clothing_change, transition)
                    else:
                        if posture_state.body.supports_outfit_change:
                            if sim.posture_state.body.saved_exit_clothing_change is not None:
                                body_posture = sim.posture_state.body
                                sequence = build_critical_section_with_finally(transition, clothing_change, (lambda _: body_posture.ensure_exit_clothing_change_application()))
                            else:
                                sequence = (
                                 transition, clothing_change)
                        else:
                            if exit_change is not None:
                                posture_state.body.transfer_exit_clothing_change(sim.posture_state.body)
                                sequence = (transition,)
                            else:
                                sequence = (
                                 transition,)
                else:
                    if portal_entry_clothing_change is not None:
                        sequence = (
                         portal_entry_clothing_change, transition)
                    else:
                        if portal_exit_clothing_change is not None:
                            sequence = (
                             transition, portal_exit_clothing_change)
                        else:
                            sequence = (
                             transition,)
            if self.interaction.pre_route_buff is not None:
                pre_route_buff = self.interaction.pre_route_buff
                buff_handler = BuffHandler(sim, (pre_route_buff.buff_type), buff_reason=(pre_route_buff.buff_reason))
                sequence = build_critical_section_with_finally(buff_handler.begin, sequence, buff_handler.end)
        sequence = sim.without_social_focus(sequence)
        process_si_states = tuple((sim.si_state.process_gen for sim in itertools.chain((sim,), additional_sims)))
        process_si_states_again = tuple((sim.si_state.process_gen for sim in itertools.chain((sim,), additional_sims)))
        sequence = build_critical_section(process_si_states, sequence, process_si_states_again)
        sequence = self.with_current_transition(sim, transition, sequence)
        transition_spec.created_posture_state = posture_state
        return sequence

    def run_super_interaction(self, timeline, si, pre_run_behavior=None, linked_sim=None):
        if not self._is_putdown_interaction():
            target_si, test_result = si.get_target_si()
            if target_si is not None:
                if not test_result:
                    self.cancel((FinishingType.FAILED_TESTS), test_result=test_result)
                    return False
                else:
                    target_si = None
            else:
                sim = si.sim
                should_wait_for_others = sim is self.sim and si is self.interaction
                start_time = services.time_service().sim_now
                maximum_wait_time = si.maximum_time_to_wait_for_other_sims
                while should_wait_for_others:
                    if not self._transition_canceled:
                        should_wait_for_others = False
                        if self.any_derailed:
                            return False
                        if sim is self.sim:
                            for other_sim in self._sim_data:
                                if sim.posture.multi_sim:
                                    if sim.posture.linked_posture == other_sim.posture:
                                        continue
                                if other_sim is sim or other_sim is linked_sim:
                                    continue
                                if self._is_putdown_interaction(target=other_sim, interaction=si):
                                    continue
                                remaining_transitions_other = self.get_remaining_transitions(other_sim)
                                if remaining_transitions_other:
                                    should_wait_for_others = True
                                    break

                        if should_wait_for_others:
                            now = services.time_service().sim_now
                            if now - start_time > clock.interval_in_sim_minutes(maximum_wait_time):
                                self.cancel()
                                break
                    else:
                        yield from self._do(timeline, sim, (sim.posture.get_idle_behavior(),
                         flush_all_animations,
                         elements.SoftSleepElement(clock.interval_in_real_seconds(self.SLEEP_TIME_FOR_IDLE_WAITING))))

                if self.canceled:
                    return False
                if (si.staging or target_si) is not None and target_si.staging:
                    if not si.is_putdown:
                        si, target_si = target_si, si
                    if si.sim in self._sim_data:
                        included_sis_actor = self._sim_data[si.sim].final_included_sis
                else:
                    included_sis_actor = None
            result = yield from si.run_direct_gen(timeline, source_interaction=(self.interaction), pre_run_behavior=pre_run_behavior, included_sis=included_sis_actor)
            if result:
                if target_si is not None:
                    if target_si.sim in self._sim_data:
                        included_sis_target = self._sim_data[target_si.sim].final_included_sis
                    else:
                        included_sis_target = None
                    result = yield from target_si.run_direct_gen(timeline, source_interaction=(self.interaction), included_sis=included_sis_target)
        else:
            if si is self.interaction or target_si is self.interaction:
                self._success = True
                if self.interaction.is_social:
                    if self.interaction.additional_social_to_run_on_both is not None:
                        result = yield from self.interaction.run_additional_social_affordance_gen(timeline)
                        if not result:
                            logger.warn('Failed to run additional social affordances for {}', (self.interaction), owner='maxr')
                            return False
        if self._is_putdown_interaction(interaction=si):
            self.reset_all_progress()
        return result
        if False:
            yield None

    def _create_transition_interaction(self, timeline, sim, destination_spec, create_posture_state_func, target, participant_type, target_si=None, linked_sim=None):
        if self.is_derailed(sim):
            return True
        else:
            result = True
            transition_spec = self.get_transition_spec(sim)
            current_spec = None
            return transition_spec is None or transition_spec.test_transition_interactions(sim, self.interaction) or False
            executed_path = False
            for si, var_map in transition_spec.transition_interactions(sim):
                current_spec = sim.posture_state.get_posture_spec(var_map)
                yield_to_irq()
                has_pre_route_change = si is not None and si.outfit_change is not None and si.outfit_change.on_route_change is not None
                if executed_path:
                    run_transition_gen = None
                else:
                    if current_spec == destination_spec and transition_spec.path is None and not has_pre_route_change:
                        if not transition_spec.portal_obj:
                            run_transition_gen = None
                        else:

                            def run_transition_gen(timeline):
                                nonlocal executed_path
                                self.interaction.add_default_outfit_priority()
                                if target is not None:
                                    sequence = self.create_transition(create_posture_state_func, si, destination_spec, var_map, participant_type, sim, target)
                                else:
                                    sequence = self.create_transition(create_posture_state_func, si, destination_spec, var_map, participant_type, sim)
                                if si is not None:
                                    if not si.route_fail_on_transition_fail:
                                        sequence = sim.without_route_failure(sequence)
                                executed_path = True
                                result_transition = yield from element_utils.run_child(timeline, sequence)
                                if not result_transition:
                                    if not self.is_derailed(sim) or self._derailed[sim] == DerailReason.TRANSITION_FAILED:
                                        if not self.canceled:
                                            if not self._shortest_path_success[sim]:
                                                self.cancel(test_result=result_transition)
                                return result_transition
                                if False:
                                    yield None

                    elif si is None:
                        if run_transition_gen is not None:
                            result = yield from run_transition_gen(timeline)
                        else:
                            result = True
                    else:
                        try:
                            self._running_transition_interactions.add(si)
                            if self.interaction == si and self._transition_canceled:
                                result = False
                            else:
                                result = yield from self.run_super_interaction(timeline, si, pre_run_behavior=run_transition_gen, linked_sim=linked_sim)
                                if result:
                                    if target_si is not None:
                                        self._running_transition_interactions.add(target_si)
                                        result = yield from self.run_super_interaction(timeline, target_si)
                                        target_si = None
                        finally:
                            self._running_transition_interactions.discard(si)
                            if target_si is not None:
                                self._running_transition_interactions.discard(target_si)

                if not result:
                    break

            path_spec = self._get_path_spec(sim)
            if (result or path_spec) is not None:
                if path_spec.is_failure_path:
                    self.advance_path(sim)
                    if target is not None:
                        self.advance_path(target)
                    if linked_sim is not None:
                        if target is not linked_sim:
                            self.advance_path(linked_sim)
                    return result
            if self.is_derailed(sim):
                return True
            if self.any_derailed:
                self.any_failure_derails or self.derail(DerailReason.WAIT_FOR_BLOCKING_SIMS, sim)
                return True
        return result
        if False:
            yield None

    def _create_posture_state(self, posture_state, spec, var_map):
        posture_state = PostureState(posture_state.sim, posture_state, spec, var_map)
        return posture_state

    def _create_transition_single(self, sim, transition, participant_type=ParticipantType.Actor):

        def do_transition_single(timeline):

            def create_posture_state_func(var_map):
                return self._create_posture_state(sim.posture_state, transition, var_map)

            result = yield from self._create_transition_interaction(timeline, sim, transition, create_posture_state_func, None, participant_type)
            return result
            if False:
                yield None

        return do_transition_single

    def _create_transition_multi_entry(self, sim, sim_node, target, target_node):

        def do_transition_multi_entry(timeline):
            target_transition_spec = self._get_path_spec(target).get_transition_spec()
            target_si = target_transition_spec.get_multi_target_interaction(target)
            if target_si is None:
                logger.error('Target {} does not have target si to run for mulit sim tranistion. {}', target, self.interaction)
                return False
            target_si.context.group_id = self.interaction.group_id
            if not target_si.aop.test(target_si.context):
                logger.debug('Target interaction failed for multi-entry: {}', target_si)
                return False

            def create_multi_sim_posture_state(var_map):
                master_posture_state = self._create_posture_state(sim.posture_state, sim_node, var_map)
                puppet_posture_state = self._create_posture_state(target.posture_state, target_node, var_map)
                if master_posture_state is not None:
                    if puppet_posture_state is not None:
                        master_posture_state.linked_posture_state = puppet_posture_state
                        puppet_posture_state.body.source_interaction = target_si
                        puppet_posture_state.body.transfer_exit_clothing_change(target.posture_state.body)
                return master_posture_state

            result = yield from self._create_transition_interaction(timeline, sim, sim_node, create_multi_sim_posture_state, target,
              (ParticipantType.Actor), target_si=target_si)
            return result
            if False:
                yield None

        return do_transition_multi_entry

    def _create_transition_multi_carry_exit(self, sim, sim_node, target, target_node):

        def do_transition_multi_carry_exit(timeline):

            def create_posture_state_func(var_map):
                return self._create_posture_state(sim.posture_state, sim_node, var_map)

            target_transition_spec = self.get_transition_spec(target)
            target_si, target_var_map = target_transition_spec.transition_interactions(target)[0]
            target_posture_state = self._create_posture_state(target.posture_state, target_node, target_var_map)
            source_interaction = self._assign_source_interaction_to_posture_state(sim, target_si, target_posture_state)
            context = PostureContext(self.interaction.context.source, self.interaction.priority, self.interaction.context.pick)
            transition = PostureStateTransition(target_posture_state, source_interaction, context, target_var_map, target_transition_spec, self.interaction, None, False, target_transition_spec.final_constraint)
            for posture in sim.posture_state.aspects:
                if posture.target is target:
                    posture.set_carried_linked_posture_exit_transition(transition, target_posture_state.body)
                    break

            self._target_interaction = None
            result = yield from self._create_transition_interaction(timeline, sim, sim_node, create_posture_state_func, None, ParticipantType.Actor)
            if not result:
                return result
            transition_element = must_run(target_posture_state.body.begin(None, target_posture_state, context, target.routing_surface))
            result = yield from self.run_super_interaction(timeline, target_si, pre_run_behavior=transition_element)
            yield from element_utils.run_child(timeline, (target_posture_state.body.get_idle_behavior(), flush_all_animations))
            target_si.transition = None
            return result
            if False:
                yield None

        return do_transition_multi_carry_exit

    def _create_transition_multi_carry_entry(self, sim, sim_node, target):

        def do_transition_multi_carry_entry(timeline):

            def create_posture_state_func(var_map):
                return self._create_posture_state(sim.posture_state, sim_node, var_map)

            result = yield from self._create_transition_interaction(timeline, sim, sim_node, create_posture_state_func, target, ParticipantType.Actor)
            return result
            if False:
                yield None

        return do_transition_multi_carry_entry

    def _create_transition_multi_exit(self, sim, sim_current_state, sim_edge):

        def do_transition_multi_exit(timeline):
            linked_sim = sim.posture.linked_sim
            linked_path_spec = self._get_path_spec(linked_sim)
            linked_destination_target = linked_sim.posture.target
            if linked_path_spec is not None and linked_path_spec.final_constraint is not ANYWHERE:
                linked_transition_spec = sim.posture.should_carry_sim_on_exit or linked_path_spec.get_transition_spec()
                linked_si = linked_transition_spec.get_multi_target_interaction(linked_sim)
                linked_destination_spec = linked_transition_spec.posture_spec
            else:
                source_posture_type = sim_current_state.body_posture
                linked_source_target = None if sim_current_state.body_target is None else linked_sim.posture.target
                valid_exit_posture_types = tuple(sorted((source_posture_type.get_exit_postures_gen(linked_sim, linked_destination_target)), key=(lambda p: p is sim_edge.body_posture),
                  reverse=True))
                posture_graph_service = services.current_zone().posture_graph_service
                for linked_sim_destination_posture_type in valid_exit_posture_types:
                    linked_source_spec = linked_sim.posture_state.spec.clone(body=(PostureAspectBody(source_posture_type, linked_source_target)))
                    if not source_posture_type.mobile:
                        if linked_sim_destination_posture_type.mobile:
                            body_target = None
                        else:
                            body_target = linked_destination_target
                        linked_destination_spec = linked_sim.posture_state.spec.clone(body=(PostureAspectBody(linked_sim_destination_posture_type, body_target)))
                        if body_target is None:
                            linked_destination_spec = linked_destination_spec.clone(surface=(PostureAspectSurface(None, None, None)))
                        edge_info = posture_graph_service.get_edge(linked_source_spec, linked_destination_spec)
                        if edge_info is None:
                            if body_target is not None:
                                if body_target.is_part:
                                    for overlapping_part in body_target.get_overlapping_parts():
                                        linked_destination_spec = linked_sim.posture_state.spec.clone(body=(PostureAspectBody(linked_sim_destination_posture_type, overlapping_part)))
                                        edge_info = posture_graph_service.get_edge(linked_source_spec, linked_destination_spec)
                                        if edge_info is not None:
                                            body_target = overlapping_part
                                            break

                        if edge_info is None:
                            continue
                        for op in edge_info.operations:
                            aop = op.associated_aop(linked_sim, self.get_var_map(linked_sim))
                            if aop is not None:
                                break
                        else:
                            continue

                        break
                else:
                    self.cancel()
                    return False

                linked_context = InteractionContext(linked_sim, (self.interaction.source), (self.interaction.priority), insert_strategy=(QueueInsertStrategy.NEXT),
                  must_run_next=True,
                  group_id=(self.interaction.group_id))
                linked_aop = AffordanceObjectPair(aop.affordance, body_target, aop.affordance, None)
                if not linked_aop.test(linked_context):
                    self.cancel()
                    return False
                    execute_result = linked_aop.interaction_factory(linked_context)
                    linked_si = execute_result.interaction
                else:
                    posture_transition_context = PostureContext(self.interaction.context.source, self.interaction._priority, None)
                    linked_posture_state = PostureState(linked_sim, linked_sim.posture_state, linked_destination_spec, {})
                    linked_target_posture = linked_posture_state.body
                    linked_target_posture.source_interaction = linked_si
                    linked_target_posture.transfer_exit_clothing_change(linked_sim.posture_state.body)
                    if linked_target_posture._primitive is None:
                        transition = must_run(linked_target_posture.begin(None, linked_posture_state, posture_transition_context, linked_sim.routing_surface))
                    else:
                        transition = None
                with self.deferred_derailment():
                    result = yield from self.run_super_interaction(timeline, linked_si, pre_run_behavior=transition)
                    if not result:
                        self.cancel()
                        return False

                    def multi_posture_exit(var_map):
                        master_posture = self._create_posture_state(sim.posture_state, sim_edge, var_map)
                        if master_posture is not None:
                            if linked_target_posture is not None:
                                master_posture.linked_posture_state = linked_posture_state
                        return master_posture

                    result = yield from self._create_transition_interaction(timeline, sim, sim_edge, multi_posture_exit, None,
                      (ParticipantType.Actor), linked_sim=linked_sim)
                    return result
            if False:
                yield None

        return do_transition_multi_exit

    def _run_interaction_privacy_tests(self, privacy_interaction, sim):
        resolver = privacy_interaction.get_resolver(target=sim)
        return privacy_interaction.privacy.tests.run_tests(resolver)

    def _determine_privacy_interaction(self, sim):
        if self.interaction.privacy is not None:
            return self.interaction
        sim_data = self._sim_data.get(sim)
        for transition_spec in reversed(sim_data.path_spec.transition_specs):
            transition_interactions = transition_spec.transition_interactions(sim)
            if not transition_interactions:
                continue
            for interaction, _ in reversed(transition_interactions):
                if interaction is not None and interaction.privacy is not None and interaction.pipeline_progress < PipelineProgress.EXITED:
                    return interaction

    def _get_privacy_status--- This code section failed: ---

 L.4533         0  LOAD_FAST                'self'
                2  LOAD_METHOD              _determine_privacy_interaction
                4  LOAD_FAST                'sim'
                6  CALL_METHOD_1         1  '1 positional argument'
                8  STORE_FAST               'privacy_interaction'

 L.4534        10  LOAD_FAST                'privacy_interaction'
               12  POP_JUMP_IF_TRUE     18  'to 18'

 L.4535        14  LOAD_CONST               (None, None)
               16  RETURN_VALUE     
             18_0  COME_FROM            12  '12'

 L.4537        18  LOAD_FAST                'privacy_interaction'
               20  LOAD_METHOD              get_participant_type
               22  LOAD_FAST                'sim'
               24  CALL_METHOD_1         1  '1 positional argument'
               26  STORE_FAST               'participant_type'

 L.4538        28  LOAD_FAST                'participant_type'
               30  LOAD_GLOBAL              ParticipantType
               32  LOAD_ATTR                Actor
               34  COMPARE_OP               ==
            36_38  POP_JUMP_IF_FALSE   330  'to 330'
               40  LOAD_FAST                'privacy_interaction'
               42  LOAD_ATTR                privacy
            44_46  POP_JUMP_IF_FALSE   330  'to 330'

 L.4539        48  LOAD_FAST                'privacy_interaction'
               50  LOAD_ATTR                privacy_test_cache
               52  LOAD_CONST               None
               54  COMPARE_OP               is
               56  POP_JUMP_IF_FALSE    72  'to 72'

 L.4540        58  LOAD_FAST                'self'
               60  LOAD_METHOD              _run_interaction_privacy_tests
               62  LOAD_FAST                'privacy_interaction'
               64  LOAD_FAST                'sim'
               66  CALL_METHOD_2         2  '2 positional arguments'
               68  LOAD_FAST                'privacy_interaction'
               70  STORE_ATTR               privacy_test_cache
             72_0  COME_FROM            56  '56'

 L.4542        72  LOAD_FAST                'privacy_interaction'
               74  LOAD_ATTR                privacy_test_cache
               76  POP_JUMP_IF_TRUE     82  'to 82'

 L.4545        78  LOAD_CONST               (None, None)
               80  RETURN_VALUE     
             82_0  COME_FROM            76  '76'

 L.4547        82  LOAD_FAST                'privacy_interaction'
               84  LOAD_METHOD              get_liability
               86  LOAD_GLOBAL              PRIVACY_LIABILITY
               88  CALL_METHOD_1         1  '1 positional argument'
            90_92  POP_JUMP_IF_TRUE    276  'to 276'

 L.4548        94  LOAD_FAST                'self'
               96  LOAD_METHOD              get_remaining_transitions
               98  LOAD_FAST                'sim'
              100  CALL_METHOD_1         1  '1 positional argument'
              102  STORE_FAST               'remaining_transitions'

 L.4550       104  LOAD_CODE                <code_object is_transition_between_parts>
              106  LOAD_STR                 'TransitionSequenceController._get_privacy_status.<locals>.is_transition_between_parts'
              108  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              110  STORE_FAST               'is_transition_between_parts'

 L.4557       112  SETUP_LOOP          330  'to 330'
              114  LOAD_GLOBAL              zip
              116  LOAD_FAST                'remaining_transitions'
              118  LOAD_FAST                'remaining_transitions'
              120  LOAD_CONST               1
              122  LOAD_CONST               None
              124  BUILD_SLICE_2         2 
              126  BINARY_SUBSCR    
              128  CALL_FUNCTION_2       2  '2 positional arguments'
              130  GET_ITER         
            132_0  COME_FROM           176  '176'
              132  FOR_ITER            182  'to 182'
              134  UNPACK_SEQUENCE_2     2 
              136  STORE_FAST               'transition'
              138  STORE_FAST               'next_transition'

 L.4563       140  LOAD_FAST                'transition'
              142  LOAD_ATTR                body_posture
              144  LOAD_ATTR                mobile
              146  POP_JUMP_IF_FALSE   156  'to 156'
              148  LOAD_FAST                'next_transition'
              150  LOAD_ATTR                body_posture
              152  LOAD_ATTR                mobile
              154  POP_JUMP_IF_FALSE   178  'to 178'
            156_0  COME_FROM           146  '146'

 L.4564       156  LOAD_FAST                'is_transition_between_parts'
              158  LOAD_FAST                'transition'
              160  LOAD_ATTR                body_posture
              162  LOAD_FAST                'transition'
              164  LOAD_ATTR                body_target

 L.4565       166  LOAD_FAST                'next_transition'
              168  LOAD_ATTR                body_posture
              170  LOAD_FAST                'next_transition'
              172  LOAD_ATTR                body_target
              174  CALL_FUNCTION_4       4  '4 positional arguments'
              176  POP_JUMP_IF_FALSE   132  'to 132'
            178_0  COME_FROM           154  '154'

 L.4566       178  BREAK_LOOP       
              180  JUMP_BACK           132  'to 132'
              182  POP_BLOCK        

 L.4578       184  LOAD_FAST                'sim'
              186  LOAD_ATTR                posture
              188  LOAD_ATTR                posture_type
              190  STORE_FAST               'body_posture'

 L.4579       192  LOAD_FAST                'remaining_transitions'
              194  LOAD_CONST               0
              196  BINARY_SUBSCR    
              198  LOAD_ATTR                body_posture
              200  STORE_FAST               'next_body_posture'

 L.4580       202  LOAD_GLOBAL              len
              204  LOAD_FAST                'remaining_transitions'
              206  CALL_FUNCTION_1       1  '1 positional argument'
              208  LOAD_CONST               1
              210  COMPARE_OP               ==
          212_214  POP_JUMP_IF_TRUE    264  'to 264'

 L.4581       216  LOAD_FAST                'body_posture'
              218  LOAD_ATTR                mobile
              220  POP_JUMP_IF_FALSE   230  'to 230'
              222  LOAD_FAST                'next_body_posture'
              224  LOAD_ATTR                mobile
          226_228  POP_JUMP_IF_FALSE   264  'to 264'
            230_0  COME_FROM           220  '220'

 L.4582       230  LOAD_FAST                'next_body_posture'
              232  LOAD_ATTR                mobile
          234_236  POP_JUMP_IF_TRUE    330  'to 330'
              238  LOAD_FAST                'is_transition_between_parts'
              240  LOAD_FAST                'body_posture'
              242  LOAD_FAST                'sim'
              244  LOAD_ATTR                posture_state
              246  LOAD_ATTR                body_target

 L.4583       248  LOAD_FAST                'next_body_posture'
              250  LOAD_FAST                'remaining_transitions'
              252  LOAD_CONST               0
              254  BINARY_SUBSCR    
              256  LOAD_ATTR                body_target
              258  CALL_FUNCTION_4       4  '4 positional arguments'
          260_262  POP_JUMP_IF_TRUE    330  'to 330'
            264_0  COME_FROM           226  '226'
            264_1  COME_FROM           212  '212'

 L.4586       264  LOAD_FAST                'self'
              266  LOAD_ATTR                PRIVACY_ENGAGE
              268  LOAD_FAST                'privacy_interaction'
              270  BUILD_TUPLE_2         2 
              272  RETURN_VALUE     
              274  JUMP_FORWARD        330  'to 330'
            276_0  COME_FROM            90  '90'

 L.4589       276  LOAD_FAST                'privacy_interaction'
              278  LOAD_METHOD              get_liability
              280  LOAD_GLOBAL              PRIVACY_LIABILITY
              282  CALL_METHOD_1         1  '1 positional argument'
              284  LOAD_ATTR                privacy
              286  LOAD_ATTR                has_shooed
          288_290  POP_JUMP_IF_TRUE    302  'to 302'

 L.4591       292  LOAD_FAST                'self'
              294  LOAD_ATTR                PRIVACY_SHOO
              296  LOAD_FAST                'privacy_interaction'
              298  BUILD_TUPLE_2         2 
              300  RETURN_VALUE     
            302_0  COME_FROM           288  '288'

 L.4592       302  LOAD_FAST                'privacy_interaction'
              304  LOAD_METHOD              get_liability
              306  LOAD_GLOBAL              PRIVACY_LIABILITY
              308  CALL_METHOD_1         1  '1 positional argument'
              310  LOAD_ATTR                privacy
              312  LOAD_METHOD              find_violating_sims
              314  CALL_METHOD_0         0  '0 positional arguments'
          316_318  POP_JUMP_IF_FALSE   330  'to 330'

 L.4593       320  LOAD_FAST                'self'
              322  LOAD_ATTR                PRIVACY_BLOCK
              324  LOAD_FAST                'privacy_interaction'
              326  BUILD_TUPLE_2         2 
              328  RETURN_VALUE     
            330_0  COME_FROM           316  '316'
            330_1  COME_FROM           274  '274'
            330_2  COME_FROM           260  '260'
            330_3  COME_FROM           234  '234'
            330_4  COME_FROM_LOOP      112  '112'
            330_5  COME_FROM            44  '44'
            330_6  COME_FROM            36  '36'

 L.4594       330  LOAD_CONST               (None, None)
              332  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `JUMP_FORWARD' instruction at offset 274

    def _get_putdown_transition_info(self, sim, actor_transitions, current_state, next_state, putdown_at_destination):
        if self._interaction.is_waiting_pickup_putdown:
            self.derail(DerailReason.WAIT_TO_BE_PUT_DOWN, sim)
            return (None, None, None, None, None)
            if self._is_putdown_interaction(target=sim):
                return
            if not actor_transitions:
                return
                current_body_posture_target = current_state.body.target
                next_body_posture_target = next_state.body.target
                if not current_body_posture_target is None:
                    if current_body_posture_target.is_sim or next_body_posture_target is not None and next_body_posture_target.is_sim:
                        if len(actor_transitions) == 1:
                            return
                        carrying_sim = next_state.body.target
                        preferred_carrying_sim = self._interaction.context.preferred_carrying_sim
                        if preferred_carrying_sim is not carrying_sim:
                            animation_work = self._get_animation_work(self.CALL_OVER_ANIMATION)
                else:
                    animation_work = None
            elif current_body_posture_target is not None and current_body_posture_target.is_sim:
                carrying_sim = next_body_posture_target is None or next_body_posture_target.is_sim or current_body_posture_target
                animation_work = None
            else:
                return
            put_down_position, put_down_routing_surface = (None, None)
            if putdown_at_destination:
                transition_spec = self.get_transition_spec(sim)
                if transition_spec is not None:
                    final_si = transition_spec.final_si
                    if final_si is not None:
                        target = final_si.target
                        if target is not None:
                            put_down_position = target.position
                            put_down_routing_surface = target.routing_surface
                else:
                    if put_down_position is None or put_down_routing_surface is None:
                        path_spec = self._get_path_spec(sim)
                        if path_spec is not None:
                            final_constraint = path_spec.final_constraint
                            if final_constraint is not None:
                                if not isinstance(final_constraint, _ConstraintSet):
                                    put_down_position = final_constraint.average_position
                                    put_down_routing_surface = final_constraint.get_world_routing_surface()
        else:
            if not put_down_position is None:
                if put_down_routing_surface is None:
                    social_group = self._interaction.social_group
                    if social_group is not None and sim in social_group:
                        if carrying_sim in social_group:
                            put_down_position = social_group.position
                            put_down_routing_surface = social_group.routing_surface
                if put_down_position is None or put_down_routing_surface is None:
                    put_down_position, put_down_routing_surface = sim.get_initial_put_down_position()
                context = InteractionContext(carrying_sim, (InteractionSource.POSTURE_GRAPH), (Priority.High), carry_target=sim, insert_strategy=(QueueInsertStrategy.FIRST),
                  must_run_next=True)
                interaction_parameters = {'put_down_position':put_down_position, 
                 'put_down_routing_surface':put_down_routing_surface}
                post_carry_aspect = actor_transitions[0].body if len(actor_transitions) < 2 else actor_transitions[1].body
                if post_carry_aspect.posture_type.multi_sim:
                    return
                max_putdown_derailment = CarryTuning.MAXIMUM_PUTDOWN_DERAILMENT
                if self.interaction.affordance in CarryTuning.PUTDOWN_DERAILMENT_INTERACTION_MAP.keys():
                    max_putdown_derailment = CarryTuning.PUTDOWN_DERAILMENT_INTERACTION_MAP[self.interaction.affordance]
                if self.interaction.putdown_derailment_counter >= max_putdown_derailment:
                    logger.error('Put down derailment requests exceeded maximum. Transition Failed. Interaction: {}', (self.interaction),
                      owner='yozhang')
                    self.derail(DerailReason.TRANSITION_FAILED, sim)
                    return (None, None, None, None, None)
                if post_carry_aspect.target is not None:
                    for aop in (sim.get_provided_aops_gen)((post_carry_aspect.target), context, **interaction_parameters):
                        affordance = aop.affordance
                        if not affordance.is_putdown:
                            continue
                        if affordance.get_provided_posture() is not post_carry_aspect.posture_type:
                            continue
                        if not aop.test(context):
                            continue
                        break
                    else:
                        self.derail(DerailReason.TRANSITION_FAILED, sim)
                        return (None, None, None, None, None)
            else:
                aop = AffordanceObjectPair((SuperInteraction.CARRY_POSTURE_REPLACEMENT_AFFORDANCE), sim, 
                 (SuperInteraction.CARRY_POSTURE_REPLACEMENT_AFFORDANCE), None, **interaction_parameters)

            def _on_finish(pickup_interaction):
                if not pickup_interaction.is_finishing_naturally:
                    if self._interaction.is_cancel_aop:
                        self.derail(DerailReason.WAIT_TO_BE_PUT_DOWN, sim)
                    else:
                        self._interaction.cancel((pickup_interaction.finishing_type), cancel_reason_msg='Unable to complete pick up')
                        self.derail(DerailReason.TRANSITION_FAILED, sim)

            pick_up_liability = PickUpSimLiability(self._interaction, _on_finish)
            result = aop.test_and_execute(context)
            result or self.derail(DerailReason.TRANSITION_FAILED, sim)
        pick_up_interaction = result.interaction
        for si in sim.si_state.all_guaranteed_si_gen(pick_up_interaction.priority, pick_up_interaction.group_id):
            si.cancel((FinishingType.INTERACTION_INCOMPATIBILITY), cancel_reason_msg='Canceling in order to be picked up.')

        self._interaction.set_saved_participant(0, carrying_sim)
        pick_up_interaction.add_liability(PickUpSimLiability.LIABILITY_TOKEN, pick_up_liability)
        self.derail(DerailReason.WAIT_TO_BE_PUT_DOWN, sim)
        if sim is not self.sim:
            self.derail(DerailReason.CONSTRAINTS_CHANGED, self.sim)
        self.interaction.putdown_derailment_counter += 1
        return (None, None, None, None, animation_work)

    def _get_pickup_transition_info(self, sim, actor_transitions, current_state, next_state):
        if self._interaction.is_waiting_pickup_putdown:
            self.derail(DerailReason.DISPLACE, sim)
            return (None, None, None, None, None)
            if len(actor_transitions) != 1:
                return
                current_body_posture_target = current_state.body.target
                next_body_posture_target = next_state.body.target
                if not current_body_posture_target is None:
                    if current_body_posture_target.is_sim or next_body_posture_target is not None and next_body_posture_target.is_sim:
                        carrying_sim = next_body_posture_target
                        if carrying_sim in self.get_transitioning_sims():
                            return
                        preferred_carrying_sim = self._interaction.context.preferred_carrying_sim
                        if preferred_carrying_sim is not carrying_sim:
                            animation_work = self._get_animation_work(self.CALL_OVER_ANIMATION)
            else:
                animation_work = None
        else:
            return
        context = InteractionContext(carrying_sim, (InteractionSource.POSTURE_GRAPH), (Priority.High), carry_target=sim, insert_strategy=(QueueInsertStrategy.FIRST),
          must_run_next=True)
        aop = AffordanceObjectPair(SuperInteraction.CARRIED_POSTURE_PICKUP_AFFORDANCE, sim, SuperInteraction.CARRIED_POSTURE_PICKUP_AFFORDANCE, None)

        def _on_finish(_):
            self.cancel(finishing_type=(FinishingType.DISPLACED), cancel_reason_msg='Displaced by pick up interaction.')

        result = aop.test_and_execute(context)
        if not result:
            self.derail(DerailReason.TRANSITION_FAILED, sim)
        pick_up_interaction = result.interaction
        for si in sim.si_state.all_guaranteed_si_gen(pick_up_interaction.priority, pick_up_interaction.group_id):
            si.cancel((FinishingType.INTERACTION_INCOMPATIBILITY), cancel_reason_msg='Canceling in order to be picked up.')

        pick_up_liability = PickUpSimLiability(self._interaction, _on_finish)
        pick_up_interaction.add_liability(PickUpSimLiability.LIABILITY_TOKEN, pick_up_liability)
        self.derail(DerailReason.DISPLACE, sim)
        return (None, None, None, None, animation_work)

    def _handle_distance_based_transition_info(self, sim, actor_transitions, current_state, next_state):
        if sim.age is not Age.INFANT:
            return False
            was_pickup_requested = self._force_carry_path
            self._force_carry_path = False
            is_being_carried = current_state is not None and current_state.body_target is not None and current_state.body_target.is_sim or next_state is not None and next_state.body_target is not None and next_state.body_target.is_sim
            if was_pickup_requested:
                if not is_being_carried:
                    self.derail(DerailReason.TRANSITION_FAILED, sim)
                return was_pickup_requested
            if current_state and current_state.carry_target is sim or next_state:
                if next_state.carry_target is sim:
                    return False
            path_spec = self._get_path_spec(sim)
            remaining_transition_specs = path_spec.remaining_original_transition_specs()
            if not remaining_transition_specs:
                return False
        else:

            def _is_carry_path_needed_for_distance(sim, distance):
                if self._is_walkstyle_distance_restricted(sim, distance):
                    return True
                if self._is_carry_needed_for_rally(distance):
                    return True
                if self._does_constraint_require_carry_path(sim, distance):
                    return True
                return False

            if is_being_carried and not sim.is_mobile:
                return True
                transition_spec = path_spec.get_transition_spec()
                if transition_spec is not None:
                    final_si = transition_spec.final_si
                    if final_si is not None:
                        target = final_si.target
                        if target is not None:
                            return _is_carry_path_needed_for_distance(sim, (target.position - sim.position).magnitude())
                return False
                next_spec = remaining_transition_specs[0]
                if next_spec.path is None:
                    return False
                if not _is_carry_path_needed_for_distance(sim, next_spec.path.length()):
                    return False
                derail_reason = self._derailed.get(sim)
                if derail_reason is not None and derail_reason != DerailReason.NOT_DERAILED:
                    return False
        self._force_carry_path = True
        self.derail(DerailReason.CARRY_NEEDED, sim)
        return False

    def _is_carry_needed_for_rally(self, distance):
        if self.interaction.is_rally_interaction:
            if self.interaction.context.preferred_carrying_sim is not None:
                return distance > CarryTuning.RALLY_INTERACTION_CARRY_RULES.min_carry_distance
        return False

    def _is_walkstyle_distance_restricted(self, sim, distance):
        if sim is None:
            return False
        limit = self._get_walkstyle_distance_limit(sim)
        if limit is not None:
            return distance > limit
        return False

    def _does_constraint_require_carry_path(self, sim, distance):
        final_constraint = self.get_final_constraint(sim)
        if final_constraint is not None:
            if final_constraint.get_require_carried():
                return distance > CarryTuning.CARRY_PATH_CONSTRAINT_RULES.min_carry_distance
        return False

    def _get_walkstyle_distance_limit(self, sim):
        walkstyle = sim.routing_component.get_walkstyle()
        if walkstyle not in WalksStyleBehavior.WALKSTYLE_DISTANCE_LIMITS:
            return
        return WalksStyleBehavior.WALKSTYLE_DISTANCE_LIMITS[walkstyle]

    def _handle_teleport_style_interaction_transition_info(self, sim, actor_transitions, current_state, next_state):
        teleport_style_aop = None
        if TeleportHelper.can_teleport_style_be_injected_before_interaction(sim, self.interaction):
            remaining_transition_specs = self._get_path_spec(sim).remaining_original_transition_specs()
            final_routing_location = None
            for spec in remaining_transition_specs:
                if spec.portal_obj is not None:
                    portal_inst = spec.portal_obj.get_portal_by_id(spec.portal_id)
                    if portal_inst is not None:
                        portal_template = portal_inst.portal_template
                        if not portal_template.allow_teleport_style_interaction_to_skip_portal:
                            break
                if spec.path is not None:
                    if spec.path.final_location.routing_surface.type != SurfaceType.SURFACETYPE_WORLD:
                        continue
                    final_routing_location = spec.path.final_location

            if final_routing_location is not None:
                pick_type = PickType.PICK_TERRAIN
                location = final_routing_location.transform.translation
                routing_surface = final_routing_location.routing_surface
                lot_id = None
                level = sim.level
                alt = False
                control = False
                shift = False
                ignore_neighborhood_id = False
                override_target = TerrainPoint(final_routing_location)
                if self.interaction.context.pick is not None:
                    parent_pick = self.interaction.context.pick
                    lot_id = parent_pick.lot_id
                    level = parent_pick.level
                    ignore_neighborhood_id = parent_pick.ignore_neighborhood_id
                    alt = parent_pick.modifiers.alt
                    control = parent_pick.modifiers.control
                    shift = parent_pick.modifiers.shift
                else:
                    if self.interaction.target is not None:
                        parent_target = self.interaction.target
                        level = parent_target.level
                override_pick = PickInfo(pick_type=pick_type, target=override_target, location=location, routing_surface=routing_surface,
                  lot_id=lot_id,
                  level=level,
                  alt=alt,
                  control=control,
                  shift=shift,
                  ignore_neighborhood_id=ignore_neighborhood_id)
                teleport_style_aop, interaction_context, _ = sim.get_teleport_style_interaction_aop((self.interaction), override_pick=override_pick, override_target=override_target)
        self.interaction.add_liability(TeleportStyleInjectionLiability.LIABILITY_TOKEN, TeleportStyleInjectionLiability())
        if teleport_style_aop is not None:
            execute_result = teleport_style_aop.execute(interaction_context)
            if execute_result:
                return True
        return False

    def _handle_vehicle_dismount(self, sim, current_state, next_state, vehicle_info):
        vehicle, vehicle_component, current_posture_on_vehicle, next_posture_on_vehicle = vehicle_info
        if current_posture_on_vehicle:
            if self._vehicle_transition_states[sim] != VehicleTransitionState.NO_STATE:
                return False
            remaining_transition_specs = self._get_path_spec(sim).remaining_original_transition_specs()
            path = None
            object_manager = services.object_manager()
            for spec in remaining_transition_specs:
                if spec.path is None:
                    continue
                path = spec.path
                path_nodes = path.nodes
                dismount_node = None
                dismount_dist = 0.0
                redeploy_node = None
                redeploy_dist = 0.0
                if not (len(path_nodes) > 1 and any((node.portal_object_id for node in path_nodes))):
                    if any((node.tracked_terrain_tags for node in path.nodes)):
                        nodes = list(path_nodes)
                        prev_node = path_nodes[0]
                        next_node = None
                        for next_node in nodes[1:]:
                            node_dist = (Vector3(*next_node.position) - Vector3(*prev_node.position)).magnitude()
                            if redeploy_node is not None:
                                redeploy_dist += node_dist
                            portal_obj_id = prev_node.portal_object_id
                            portal_obj = object_manager.get(portal_obj_id) if portal_obj_id else None
                            if prev_node.portal_id:
                                dismount_node = portal_obj and vehicle_component.can_transition_through_portal(portal_obj, prev_node.portal_id) or (prev_node if dismount_node is None else dismount_node)
                                redeploy_node = next_node
                                redeploy_dist = 0.0
                            else:
                                if not vehicle_component.can_transition_over_node(next_node, prev_node):
                                    dismount_node = next_node if dismount_node is None else dismount_node
                                    dismount_dist += node_dist
                                    break
                                else:
                                    if redeploy_node is None:
                                        dismount_dist += node_dist
                                    if redeploy_node:
                                        if redeploy_dist >= vehicle_component.minimum_route_distance:
                                            break
                                    prev_node = next_node

                    if dismount_node is None:
                        dismount_dist = path.length()
                        if not next_posture_on_vehicle:
                            dismount_node = path_nodes[-1]
                    break

            if path is None:
                return False
                defer_position = None
                if dismount_dist < vehicle_component.minimum_route_distance:
                    if not next_posture_on_vehicle:
                        return False
                    if dismount_node is not None:
                        for si in sim.si_state.sis_actor_gen():
                            if si.target is vehicle:
                                if si.affordance is vehicle_component.drive_affordance:
                                    if redeploy_node is not None:
                                        footprint = vehicle.footprint_polygon
                                        if not footprint.contains(path.start_location.position):
                                            location = Location(Transform(Vector3(*redeploy_node.position), Quaternion(*redeploy_node.orientation)), redeploy_node.routing_surface_id)
                                            result = vehicle_component.push_auto_deploy_affordance(sim, location)
                                            if not result:
                                                return False
                                self.derail(DerailReason.MUST_EXIT_MOBILE_POSTURE_OBJECT, sim)
                                si.cancel(FinishingType.DISPLACED, 'Vehicle Dismount for Portal.')
                                return True
                        else:
                            self.derail(DerailReason.MUST_EXIT_MOBILE_POSTURE_OBJECT, sim)
                            return True
            else:
                return False
        else:
            if dismount_node is not None:
                defer_position = Vector3(*dismount_node.position)
                defer_location = Location(Transform(defer_position, Quaternion.IDENTITY()), dismount_node.routing_surface_id)
                execute_result = vehicle_component.push_dismount_affordance(sim, defer_location)
                if execute_result:
                    self.derail(DerailReason.MUST_EXIT_MOBILE_POSTURE_OBJECT, sim)
                    return True
            return False

    def _handle_vehicle_transition_info(self, sim, actor_transitions, current_state, next_state):
        vehicle = current_state.body.target
        vehicle_component = vehicle.vehicle_component if vehicle is not None else None
        current_posture_on_vehicle = vehicle_component is not None
        next_posture_on_vehicle = next_state.is_on_vehicle()
        vehicle_info = (vehicle, vehicle_component, current_posture_on_vehicle, next_posture_on_vehicle)
        deployed_vehicle = self._deployed_vehicles.get(sim, None)
        if self._handle_vehicle_dismount(sim, current_state, next_state, vehicle_info):
            return
        if self._vehicle_transition_states[sim] != VehicleTransitionState.DEPLOYING:
            path_spec = self._get_path_spec(sim)
            previous_posture_spec = path_spec.previous_posture_spec
            if current_state == previous_posture_spec:
                path_progress = path_spec.path_progress
                if path_progress >= 2:
                    previous_posture_spec = path_spec.path[path_progress - 2]
            if current_posture_on_vehicle and not next_posture_on_vehicle:
                if len(path_spec.path) == 2:
                    if previous_posture_spec is not None and previous_posture_spec.body_posture.is_vehicle:
                        self._vehicle_transition_states[sim] = VehicleTransitionState.NO_STATE
                        vehicle = previous_posture_spec.body_target
                        vehicle_component = vehicle.vehicle_component if vehicle is not None else None
                        if vehicle_component is not None and not self._should_skip_vehicle_retrieval(path_spec.remaining_original_transition_specs()):
                            if vehicle_component.retrieve_tuning is not None and sim.routing_surface == vehicle.routing_surface and sim.household_id == vehicle.household_owner_id and vehicle.inventoryitem_component is not None and self.sim.inventory_component.can_add(vehicle):
                                execute_result = vehicle_component.push_retrieve_vehicle_affordance(sim, depend_on_si=(self.interaction))
                                if execute_result:
                                    self.derail(DerailReason.MUST_EXIT_MOBILE_POSTURE_OBJECT, sim)
                                    return
                is_vehicle_posture_change = current_posture_on_vehicle or next_posture_on_vehicle
                if self.interaction.should_disable_vehicles:
                    return
                if sim.get_routing_slave_data():
                    return
                vehicle_transition_state = self._vehicle_transition_states[sim]
                if not is_vehicle_posture_change:
                    if not vehicle_transition_state == VehicleTransitionState.DEPLOYING:
                        if not vehicle_transition_state == VehicleTransitionState.MOUNTING:
                            if len(sim.posture_state.get_free_hands()) == 3:
                                path_spec = self._get_path_spec(sim)
                                remaining_transition_specs = path_spec.remaining_original_transition_specs()
                                if not remaining_transition_specs:
                                    return
                                next_spec = remaining_transition_specs[0]
                                mounted = False
                                final_spec = remaining_transition_specs[-1] if remaining_transition_specs else None
                                final_body_target = final_spec.posture_spec.body.target
                                if next_spec.path is not None:
                                    if final_body_target is not None or sim.routing_surface.type == SurfaceType.SURFACETYPE_WORLD or any((next_spec.portal_obj is not None for next_spec in remaining_transition_specs)):
                                        for vehicle in sim.get_vehicles_for_path(next_spec.path):
                                            execute_result = vehicle.vehicle_component.push_deploy_vehicle_affordance(sim, depend_on_si=(self.interaction))
                                            if execute_result:
                                                self._vehicle_transition_states[sim] = VehicleTransitionState.DEPLOYING
                                                self._deployed_vehicles[sim] = vehicle
                                                self.derail(DerailReason.CONSTRAINTS_CHANGED, sim)
                                                mounted = True
                                                break

                                if not mounted:
                                    previous_spec = path_spec.previous_transition_spec
                                    if previous_spec is not None and previous_spec.portal_obj is not None and next_spec.path is not None:
                                        self._mount_vehicle_post_portal_transition(sim, previous_spec, next_spec)
        elif (is_vehicle_posture_change or self._vehicle_transition_states[sim]) == VehicleTransitionState.DEPLOYING:
            if deployed_vehicle is not None:
                execute_result = deployed_vehicle.vehicle_component.push_drive_affordance(sim, depend_on_si=(self.interaction))
                if execute_result:
                    self._vehicle_transition_states[sim] = VehicleTransitionState.NO_STATE
                    self._deployed_vehicles.pop(sim, None)
                    self.derail(DerailReason.CONSTRAINTS_CHANGED, sim)
                    return

    def _handle_formation_transition_info(self, sim):
        master = sim.routing_master if not sim.get_routing_slave_data() else sim
        if master is None:
            return
        else:
            slave_datas = master.get_routing_slave_data()
            return slave_datas or None
        transitioning_sims = self.get_transitioning_sims()
        if master in transitioning_sims:
            if all((slave_data.slave in transitioning_sims for slave_data in slave_datas)):
                return
        if master is sim:
            derail = False
            transition_spec = self.get_transition_spec(sim)
            if transition_spec.path is None:
                return
            incompatible_sis = set()
            for slave_data in slave_datas:
                if not slave_data.should_slave_for_path(transition_spec.path):
                    continue
                slave = slave_data.slave
                if not slave.is_sim:
                    continue
                for interaction in slave.get_all_running_and_queued_interactions():
                    if interaction.is_super:
                        if interaction.provided_posture_type is None:
                            if interaction not in incompatible_sis:
                                if interaction.get_liability(RoutingFormationLiability.LIABILITY_TOKEN) is not None:
                                    continue
                                incompatible_sis.add(interaction)
                        else:
                            interaction.interruptible or interaction.cancel((FinishingType.ROUTING_FORMATION), 'Routing Formation master started to route.', immediate=True)
                            derail = True

                for si in incompatible_sis:
                    if not si.is_finishing:
                        if si.user_cancelable:
                            si.cancel((FinishingType.ROUTING_FORMATION), 'Routing Formation master started to route.', immediate=True)
                        derail = True

                for interaction in slave.queue:
                    if interaction.provided_posture_type is not None:
                        if interaction.provided_posture_type.mobile:
                            continue
                        if interaction.transition is not None and interaction not in incompatible_sis:
                            interaction.transition.derail(DerailReason.MASTER_SIM_ROUTING, slave)
                            if interaction.transition.running:
                                derail = True

                if slave.posture.mobile:
                    if not slave.transition_controller is not None or sim not in slave.transition_controller.get_transitioning_sims():
                        derail = True

            if derail:
                self.derail(DerailReason.WAIT_FOR_FORMATION_SLAVE, sim)
            return
        slave_data = master.get_formation_data_for_slave(sim)
        if master.is_sim:
            if master.routing_component.current_path is not None:
                if master.routing_component.current_path.length() > slave_data.route_length_minimum:
                    self.derail(DerailReason.MASTER_SIM_ROUTING, sim)
                    return
            if master.transition_controller is not None:
                transition_spec = master.transition_controller.get_transition_spec(master)
                if transition_spec is not None and transition_spec.path is not None and transition_spec.path.length() > slave_data.route_length_minimum:
                    if self.interaction.provided_posture_type is None:
                        self.derail(DerailReason.MASTER_SIM_ROUTING, sim)

    def _handle_deferred_putdown(self, sim, current_state, next_state):
        carry_targets = sim.posture_state.carry_targets
        if current_state.carry_target is None:
            if any(carry_targets):
                derail_actors = next_state.body_posture.mobile and next_state.body_posture is not StandSuperInteraction.STAND_POSTURE_TYPE
                should_derail = not self._interaction.cancel_incompatible_carry_interactions(can_defer_putdown=False, derail_actors=derail_actors)
                if should_derail:
                    self.derail(DerailReason.WAIT_FOR_BLOCKING_SIMS, sim)
                    if self.interaction.is_social:
                        other_sim = self.interaction.target_sim if sim is self.interaction.sim else self.interaction.sim
                        self.interaction.transition.derail(DerailReason.WAIT_FOR_BLOCKING_SIMS, other_sim)
        if self.has_deferred_putdown:
            if current_state._body_target_type != next_state._body_target_type:
                posture_graph = services.current_zone().posture_graph_service
                posture_graph.handle_additional_pickups_and_putdowns((self._get_path_spec(sim)), (self._sim_data.get(sim).templates[1]), sim, can_defer_putdown=False)
                self.has_deferred_putdown = False

    def _handle_posture_object_retrieval_info(self, sim, var_map, next_state):
        current_posture = sim.posture
        retrieve_objects_from_posture = current_posture.retrieve_objects_on_exit
        if retrieve_objects_from_posture is None or retrieve_objects_from_posture.transition_retrieval_affordance is None:
            return True
        placeholders = self.interaction.animation_context.get_placeholder_objects()
        if next_state._validate_surface(var_map, objects_to_ignore=placeholders):
            return True
        if self._pushed_posture_object_retrieval_affordance:
            return False
        affordance = retrieve_objects_from_posture.transition_retrieval_affordance
        aop = AffordanceObjectPair(affordance, current_posture.target, affordance, None)
        context = InteractionContext(sim, (InteractionContext.SOURCE_SCRIPT),
          (Priority.High),
          insert_strategy=(QueueInsertStrategy.FIRST),
          must_run_next=True)
        result = aop.test_and_execute(context)
        self._pushed_posture_object_retrieval_affordance = True
        if not result:
            sim.posture.retrieve_objects()
        self.derail(DerailReason.CONSTRAINTS_CHANGED, sim)
        return False

    def _get_next_transition_info(self, sim):
        if self._get_path_spec(sim) is None:
            return (None, None, None, None, None)
            actor_transitions = self.get_remaining_transitions(sim)
            if not actor_transitions:
                return (None, None, None, None, None)
                participant_type = self.interaction.get_participant_type(sim)
                var_map = self.get_var_map(sim)
                current_state = sim.posture_state.get_posture_spec(var_map)
                next_state = actor_transitions[0]
                work = None
                if sim.waiting_multi_sim_posture:
                    self.derail(DerailReason.WAIT_FOR_MULTI_SIM_POSTURE, sim)
                    return (None, None, None, None, None)
                was_teleport_style_interaction_executed = self._handle_teleport_style_interaction_transition_info(sim, actor_transitions, current_state, next_state)
                if was_teleport_style_interaction_executed:
                    self.derail(DerailReason.CONSTRAINTS_CHANGED, sim)
                    return (None, None, None, None, None)
                if not self._handle_posture_object_retrieval_info(sim, var_map, next_state):
                    return (None, None, None, None, None)
                self._handle_vehicle_transition_info(sim, actor_transitions, current_state, next_state)
                putdown_at_destination = self._handle_distance_based_transition_info(sim, actor_transitions, current_state, next_state)
                self._handle_formation_transition_info(sim)
                self._handle_deferred_putdown(sim, current_state, next_state)
                privacy_status, privacy_interaction = self._get_privacy_status(sim)
                if privacy_status == self.PRIVACY_ENGAGE:
                    target = next_state.body.target
                    privacy_interaction.add_liability(PRIVACY_LIABILITY, PrivacyLiability(privacy_interaction, target))
                    sim.queue.on_required_sims_changed(privacy_interaction)
                    if privacy_interaction.get_liability(PRIVACY_LIABILITY).privacy.find_violating_sims(consider_exempt=False):
                        if not privacy_interaction.privacy.animate_shoo:
                            return (None, None, None, None, None)
                        work = self._get_animation_work(self.SHOO_ANIMATION)
            elif privacy_status == self.PRIVACY_SHOO:
                privacy_interaction.priority = Priority.Critical
                services.get_master_controller().reset_timestamp_for_sim(self.sim)
                self.derail(DerailReason.PRIVACY_ENGAGED, sim)
                privacy_interaction.get_liability(PRIVACY_LIABILITY).privacy.has_shooed = True
                self._privacy_initiation_time = services.time_service().sim_now
                return (None, None, None, None, None)
            if privacy_status == self.PRIVACY_BLOCK:
                return (None, None, None, None, None)
            else:
                transition_info = self._get_putdown_transition_info(sim, actor_transitions, current_state, next_state, putdown_at_destination)
                if transition_info is not None:
                    return transition_info
                else:
                    pickup_transition_info = self._get_pickup_transition_info(sim, actor_transitions, current_state, next_state)
                    if pickup_transition_info is not None:
                        return pickup_transition_info
                        current_body_posture_target = current_state.body.target
                        next_body_posture_target = next_state.body.target
                        next_carry_target = next_state.carry_target
                        next_carry_target = var_map.get(next_carry_target, next_carry_target)
                        if current_state.carry_target is None and next_carry_target is not None and next_carry_target.is_sim:
                            if sim.routing_surface != next_carry_target.routing_surface:
                                constraint = next_carry_target.get_carry_transition_constraint(sim, sim.position, sim.routing_surface)
                                constraint = constraint._copy(_multi_surface=False)
                                affordance = interactions.utils.satisfy_constraint_interaction.SatisfyConstraintSuperInteraction
                                aop = AffordanceObjectPair(affordance, None, affordance, None, constraint_to_satisfy=constraint, route_fail_on_transition_fail=False,
                                  name_override='TransitionSequence[CarryTargetMove]',
                                  allow_posture_changes=True,
                                  depended_on_si=(self.interaction))
                                context = InteractionContext(next_carry_target, (InteractionContext.SOURCE_SCRIPT), (Priority.High), insert_strategy=(QueueInsertStrategy.FIRST),
                                  must_run_next=True,
                                  group_id=(self.interaction.group_id))
                                execute_result = aop.test_and_execute(context)
                                if execute_result:
                                    self.derail(DerailReason.WAIT_FOR_CARRY_TARGET, sim)
                    else:
                        self.derail(DerailReason.TRANSITION_FAILED, sim)
                return (None, None, None, None, None)
            if next_carry_target.parent is not None:
                self.derail(DerailReason.WAIT_FOR_CARRY_TARGET, sim)
                return (None, None, None, None, None)
            carry_target_transitions = self.get_remaining_transitions(next_carry_target)
            if carry_target_transitions:
                carry_target_next_body_target = carry_target_transitions[0].body.target
                if carry_target_next_body_target is not sim:
                    return (None, None, None, None, None)
            if next_body_posture_target is not None:
                if next_body_posture_target.is_sim:
                    if next_body_posture_target is not current_body_posture_target:
                        return (None, None, None, None, None)
        elif current_body_posture_target is not None:
            if current_body_posture_target.is_sim:
                if next_body_posture_target is not current_body_posture_target:
                    return (None, None, None, None, None)
                if next_body_posture_target is not None and next_body_posture_target.is_sim:
                    next_body_posture_target_carry_target = next_body_posture_target.posture_state.get_posture_spec(self.get_var_map(next_body_posture_target)).carry_target
                    if next_body_posture_target_carry_target != PostureSpecVariable.CARRY_TARGET:
                        if next_body_posture_target_carry_target is not sim:
                            logger.error('{} is transitioning to the same state: {} -> {} with next_body_posture_target: {} and next_body_posture_target_carry_target: {}', sim, current_state, next_state, next_body_posture_target, next_body_posture_target_carry_target)
                            return (None, None, None, None, None)
        return (
         participant_type, current_state, next_state, actor_transitions, work)

    def is_multi_sim_entry(self, current_state, next_state):
        if current_state is None or next_state is None:
            return False
        return not current_state.body.posture_type.multi_sim and next_state.body.posture_type.multi_sim

    def is_multi_sim_exit(self, current_state, next_state):
        if current_state is None or next_state is None:
            return False
        return current_state.body.posture_type.multi_sim and not next_state.body.posture_type.multi_sim

    def is_multi_to_multi(self, current_state, next_state):
        if current_state is None or next_state is None:
            return False
        return current_state.body.posture_type.multi_sim and next_state.body.posture_type.multi_sim

    def _create_next_elements(self, timeline):
        no_work_sims = []
        executed_work = False
        any_participant_has_work = False
        for sim in self.get_transitioning_sims():
            participant_has_work = False
            if sim in self._sim_jobs:
                executed_work = True
                if sim not in self._sim_idles:
                    participant_has_work = True
                else:
                    if self._get_path_spec(sim) is not None:
                        transitions_sim = self.get_remaining_transitions(sim)
                        if transitions_sim:
                            if sim.posture.multi_sim:
                                if self.is_multi_to_multi(self.get_previous_spec(sim), transitions_sim[0]) and self.interaction.get_participant_type(sim) != ParticipantType.Actor:
                                    continue
                            elif sim.posture.linked_sim in self._sim_jobs:
                                if self.is_multi_sim_exit(self.get_previous_spec(sim), transitions_sim[0]):
                                    continue
                            else:
                                privacy_status, _ = self._get_privacy_status(sim)
                                if privacy_status != self.PRIVACY_BLOCK:
                                    participant_has_work = True
                                else:
                                    now = services.time_service().sim_now
                                    timeout = self.SIM_MINUTES_TO_WAIT_FOR_VIOLATORS
                                    delta = now - self._privacy_initiation_time
                                    if delta > clock.interval_in_sim_minutes(timeout):
                                        self.cancel(FinishingType.TRANSITION_FAILURE)
                                    else:
                                        self._execute_work_as_element(timeline, sim, elements.SoftSleepElement(clock.interval_in_sim_minutes(1)))
                    any_participant_has_work = any_participant_has_work or participant_has_work
                    if not participant_has_work:
                        no_work_sims.append(sim)
                    if participant_has_work:
                        if sim in self._sim_jobs:
                            continue
                        executed_work = True
                        self._sim_idles.discard(sim)
                        self._execute_work_as_element(timeline, sim, functools.partial(self._execute_next_transition, sim))

        if any_participant_has_work:
            for sim in no_work_sims:
                if sim not in self._sim_idles:
                    self._execute_work_as_element(timeline, sim, functools.partial((self._execute_next_transition), sim, no_work=True))

        if any_participant_has_work and not executed_work:
            raise RuntimeError('Deadlock in the transition sequence.\n Interaction: {},\n Participants: {},\n Full path_specs: {} \n[tastle]'.format(self.interaction, self.get_transitioning_sims(), [sim_data.path_spec for sim_data in self._sim_data.values()]))

    def _execute_work_as_element(self, timeline, sim, work):
        self._sim_jobs.append(sim)
        child = build_element([
         build_critical_section_with_finally(work, (lambda _: self._sim_jobs.remove(sim))),
         self._create_next_elements])
        self._worker_all_element.add_work(timeline, child)

    def _execute_next_transition(self, sim, timeline, no_work=False):
        if any(self._derailed.values()):
            return False
        if self._transition_canceled:
            self.cancel()
            return False
        selected_work = None
        participant_type, sim_current_state, sim_next_state, actor_transitions, work = no_work or self._get_next_transition_info(sim)
        if work is not None:
            single_sim_transition = build_element(work)
            selected_work = single_sim_transition
        else:
            multi_sim_exit_sim = self.is_multi_sim_exit(sim_current_state, sim_next_state)
            if multi_sim_exit_sim:
                multi_sim_posture = sim.posture
                target = multi_sim_posture.linked_sim
                sim_multi_exit = self._create_transition_multi_exit(sim, sim_current_state, sim_next_state)

                def _lock_sim_transitions(_):
                    sim.waiting_multi_sim_posture = True
                    if target is not None:
                        target.waiting_multi_sim_posture = True

                def _unlock_sim_transitions(_):
                    sim.waiting_multi_sim_posture = False
                    if target is not None:
                        target.waiting_multi_sim_posture = False

                sim_multi_exit = build_critical_section_with_finally(_lock_sim_transitions, sim_multi_exit, _unlock_sim_transitions)
                if multi_sim_posture.should_carry_sim_on_exit:
                    carrying_sim, carried_sim = sim, target
                    if multi_sim_posture.is_puppet:
                        carrying_sim, carried_sim = carried_sim, carrying_sim
                    carry_linked_sim_data = multi_sim_posture.carry_actor_b_on_exit_transition[carried_sim.age]

                    def _derail_pending_interactions_for_carried_sim(_, __):
                        for interaction in carried_sim.queue:
                            if interaction.transition is not None:
                                interaction.transition.derail(DerailReason.PREEMPTED, carried_sim)

                    carry_element_helper = CarryElementHelper(sim=carrying_sim, carry_target=carried_sim,
                      owning_affordance=(carry_linked_sim_data.carry_affordance),
                      carry_track=(carry_linked_sim_data.carry_track),
                      callback=_derail_pending_interactions_for_carried_sim)
                    multi_exit_carry_element = carry_element_helper.build_enter_carry_immediately_element()
                    sim_multi_exit = build_critical_section_with_finally(_lock_sim_transitions, sim_multi_exit, multi_exit_carry_element, _unlock_sim_transitions)
                else:
                    sim_multi_exit = build_critical_section_with_finally(_lock_sim_transitions, sim_multi_exit, _unlock_sim_transitions)
                selected_work = sim_multi_exit
            if (multi_sim_exit_sim or self._interaction).is_putdown:
                if actor_transitions is not None:
                    next_transition_spec = self.get_next_transition_spec(sim)
                    target = next_transition_spec is None or next_transition_spec.is_carry or self.interaction.carry_target or self.interaction.target
                    if target is not None and target.is_sim and target.parent is sim:
                        target_transitions = self.get_remaining_transitions(target)
                        if target_transitions:
                            next_state_target = target_transitions[0]
                            if sim_next_state is None or next_state_target.body.target is sim_next_state.body.target:
                                selected_work = build_element(self._create_transition_multi_carry_exit(sim, sim_next_state or sim_current_state, target, next_state_target))
                                multi_sim_exit_sim = True
                        elif target.posture_state.body.target is sim:
                            self.derail(DerailReason.WAIT_TO_BE_PUT_DOWN, sim)
            multi_sim_entry_sim = self.is_multi_sim_entry(sim_current_state, sim_next_state) or self.is_multi_to_multi(sim_current_state, sim_next_state)
            if not multi_sim_exit_sim:
                if participant_type is ParticipantType.Actor:
                    target = self.interaction.get_participant(ParticipantType.TargetSim)
                    if target is not None:
                        var_map_target = self.get_var_map(target)
                        if var_map_target is not None:
                            current_state_target = sim.posture_state.get_posture_spec(var_map_target)
                            next_transitions_target = self.get_remaining_transitions(target)
                            next_state_target = next_transitions_target[0] if next_transitions_target else None
                            multi_sim_entry_target = self.is_multi_sim_entry(current_state_target, next_state_target) or self.is_multi_to_multi(current_state_target, next_state_target)
                            multi_sim_entry = multi_sim_entry_sim and multi_sim_entry_target
                            if multi_sim_entry:
                                multi_sim_entry = self._create_transition_multi_entry(sim, sim_next_state, target, next_state_target)
                                multi_sim_entry = build_element(multi_sim_entry)
                                if selected_work is not None:
                                    raise RuntimeError('Multiple work units planned in _execute_next_transition')
                                selected_work = multi_sim_entry
            if sim_next_state is not None and not multi_sim_entry_sim:
                if not multi_sim_exit_sim:
                    single_sim_transition = None
                    next_carry_target = sim_next_state.carry_target
                    if sim_current_state.carry_target is None:
                        if next_carry_target is not None:
                            var_map = self.get_var_map(sim)
                            if var_map is not None:
                                next_carry_target = var_map.get(next_carry_target, next_carry_target)
                                if next_carry_target.is_sim:
                                    single_sim_transition = self._create_transition_multi_carry_entry(sim, sim_next_state, next_carry_target)
                    if single_sim_transition is None:
                        single_sim_transition = self._create_transition_single(sim, sim_next_state, participant_type)
                    single_sim_transition = build_element(single_sim_transition)
                    if selected_work is not None:
                        raise RuntimeError('Multiple work units planned in _execute_next_transition')
                    selected_work = single_sim_transition
                if selected_work is None:
                    if sim not in self._sim_idles:

                        def _do_idle_behavior(timeline):
                            if sim.posture.multi_sim and sim.posture.source_interaction is not None and sim.posture.source_interaction.is_finishing:
                                result = yield from element_utils.run_child(timeline, elements.SoftSleepElement(clock.interval_in_real_seconds(self.SLEEP_TIME_FOR_IDLE_WAITING)))
                            else:
                                result = yield from element_utils.run_child(timeline, (sim.posture.get_idle_behavior(),
                                 flush_all_animations,
                                 elements.SoftSleepElement(clock.interval_in_real_seconds(self.SLEEP_TIME_FOR_IDLE_WAITING))))
                            return result
                            if False:
                                yield None

                        selected_work = _do_idle_behavior
                        self._sim_idles.add(sim)
            if selected_work is not None:
                result = yield from self._do(timeline, sim, selected_work)
                if not result:
                    if self._shortest_path_success[sim]:
                        self.derail((DerailReason.TRANSITION_FAILED), sim, test_result=result)
                    else:
                        self.cancel(test_result=result)
                    return False
            return True
        if False:
            yield None

    def _should_skip_vehicle_retrieval(self, remaining_transition_specs):
        for spec in remaining_transition_specs:
            if spec.portal_obj is None:
                continue
            portal_inst = spec.portal_obj.get_portal_by_id(spec.portal_id)
            if portal_inst is None:
                continue
            portal_template = portal_inst.portal_template
            if portal_template.use_vehicle_after_traversal:
                return True
            break

        return False

    def _mount_vehicle_post_portal_transition(self, sim, previous_spec, next_spec):
        portal_object = previous_spec.portal_obj
        portal_id = previous_spec.portal_id
        vehicles = portal_object.portal_component.get_vehicles_nearby_portal_id(portal_id)
        vehicles.sort(key=(lambda vehicle: vehicle.household_owner_id == sim.household_id), reverse=True)
        for vehicle in vehicles:
            if vehicle.household_owner_id is not None:
                if vehicle.household_owner_id != 0:
                    if vehicle.household_owner_id != sim.household_id:
                        continue
            vehicle_component = vehicle.vehicle_component
            if next_spec.path.length() > vehicle_component.minimum_route_distance:
                execute_result = vehicle.vehicle_component.push_drive_affordance(sim, depend_on_si=(self.interaction))
                if execute_result:
                    self._vehicle_transition_states[sim] = VehicleTransitionState.MOUNTING
                    self.derail(DerailReason.CONSTRAINTS_CHANGED, sim)
                    return True

        return False