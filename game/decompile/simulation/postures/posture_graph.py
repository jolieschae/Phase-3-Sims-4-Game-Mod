# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\posture_graph.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 423452 bytes
from collections import OrderedDict, namedtuple, defaultdict
from contextlib import contextmanager
import collections, functools, itertools, operator, time, weakref, xml.etree
from caches import BarebonesCache
from event_testing.resolver import SingleActorAndObjectResolver, SingleSimResolver
from event_testing.tests import TunableTestSet
from objects.pools.pond_utils import PondUtils
from routing.path_planner.height_clearance_helper import get_required_height_clearance
from sims4 import reload
from sims4.callback_utils import CallableTestList
from sims4.collections import frozendict, enumdict
from sims4.geometry import test_point_in_compound_polygon, QtCircle
from sims4.log import Logger, StackVar
from sims4.repr_utils import standard_angle_repr, suppress_quotes
from sims4.service_manager import Service
from sims4.sim_irq_service import yield_to_irq
from sims4.tuning.geometric import TunableVector2
from sims4.tuning.tunable import Tunable, TunableReference, TunableList, TunableMapping, TunableEnumEntry, TunableTuple
from sims4.utils import enumerate_reversed
from singletons import DEFAULT
import algos, caches, enum, sims4.geometry, sims4.math, sims4.reload
from animation.posture_manifest import SlotManifestEntry, AnimationParticipant
from animation.posture_manifest_constants import SWIM_AT_NONE_CONSTRAINT, STAND_AT_NONE_CONSTRAINT
from autonomy.autonomy_preference import AutonomyPreferenceType
from balloon.passive_balloons import PassiveBalloons
from element_utils import build_element, maybe
from event_testing.results import TestResult
from indexed_manager import CallbackTypes
from interactions import ParticipantType, constraints
from interactions.aop import AffordanceObjectPair
from interactions.constraints import create_transform_geometry, Anywhere, ANYWHERE, RequiredSlotSingle, create_constraint_set, Constraint, Nowhere
from interactions.context import InteractionContext, QueueInsertStrategy, InteractionSource
from interactions.interaction_finisher import FinishingType
from interactions.priority import Priority
from interactions.utils import routing_constants
from interactions.utils.interaction_liabilities import RESERVATION_LIABILITY, ReservationLiability
from interactions.utils.routing import FollowPath, get_route_element_for_path, SlotGoal
from interactions.utils.routing_constants import TransitionFailureReasons
from objects import ALL_HIDDEN_REASONS
from objects.definition import Definition
from objects.helpers.user_footprint_helper import push_route_away
from objects.object_enums import ResetReason
from objects.pools import pool_utils
from objects.proxy import ProxyObject
from postures import DerailReason
from postures.base_postures import create_puppet_postures
from postures.generic_posture_node import SimPostureNode
from postures.posture import Posture
from postures.posture_errors import PostureGraphError, PostureGraphMiddlePathError
from postures.posture_scoring import PostureScoring, may_reserve_posture_target
from postures.posture_specs import PostureSpecVariable, PostureSpec, PostureOperation, get_origin_spec, get_origin_spec_carry, with_caches, get_pick_up_spec_sequence, get_put_down_spec_sequence, destination_test, PostureAspectBody, PostureAspectSurface, _object_addition, PostureAspectBody_create
from postures.posture_state_spec import create_body_posture_state_spec
from postures.posture_tuning import PostureTuning
from relationships.global_relationship_tuning import RelationshipGlobalTuning
from reservation.reservation_handler_multi import ReservationHandlerMulti
from routing import SurfaceType, GoalFailureType
from routing.formation.formation_tuning import FormationTuning
from routing.formation.formation_type_base import FormationRoutingType
from sims.sim_info_types import Species, Age
from world.ocean_tuning import OceanTuning
import build_buy, cython, debugvis, element_utils, elements, event_testing.test_utils, gsi_handlers.posture_graph_handlers, indexed_manager, interactions.utils.routing, postures, primitives.routing_utils, routing, services, terrain
if not cython.compiled:
    from postures.posture_specs import get_origin_spec, get_origin_spec_carry, PostureSpec, PostureAspectBody
    import cython_utils as cu
else:
    MAX_RIGHT_PATHS = 30
    NON_OPTIMAL_PATH_DESTINATION = 1000
    logger = Logger('PostureGraph')
    cython_log = Logger('CythonConfig')
    if cython.compiled:
        cython_log.always('CYTHON posture_graph is imported!', color=(sims4.log.LEVEL_WARN))
    else:
        cython_log.always('Pure Python posture_graph is imported!', color=(sims4.log.LEVEL_WARN))
with sims4.reload.protected(globals()):
    SIM_DEFAULT_POSTURE_TYPE = None
    SIM_DEFAULT_AOPS = None
    SIM_DEFAULT_OPERATION = None
    SIM_INFANT_OVERRIDE_DEFAULT_OPERATION = None
    SIM_DEFAULT_POSTURE_TYPE = None
    SIM_TESTED_AOPS = None
    STAND_AT_NONE = None
    STAND_AT_NONE_CARRY = None
    STAND_AT_NONE_NODES = None
    SIM_SWIM_POSTURE_TYPE = None
    SIM_SWIM_AOPS = None
    SIM_SWIM_OPERATION = None
    SWIM_AT_NONE = None
    SWIM_AT_NONE_CARRY = None
    SWIM_AT_NONE_NODES = None
    _MOBILE_NODES_AT_NONE = None
    _MOBILE_NODES_AT_NONE_CARRY = None
    _DEFAULT_MOBILE_NODES = None
    enable_debug_goals_visualization = False
    on_transition_destinations_changed = sims4.callback_utils.CallableList()
InsertionIndexAndSpec = namedtuple('InsertionIndexAndSpec', ['index', 'spec'])

@cython.cfunc
@cython.exceptval(check=False)
def get_subset_keys(node_or_spec: PostureSpec) -> set:
    keys = set()
    posture_type = node_or_spec.get_body_posture()
    if posture_type is not None:
        keys.add(('posture_type', posture_type))
    carry_target = node_or_spec.get_carry_target()
    keys.add(('carry_target', carry_target))
    body_target = node_or_spec.body_target
    body_target = getattr(body_target, 'part_owner', None) or body_target
    if node_or_spec.surface is not None:
        original_surface_target = node_or_spec.get_surface_target()
        surface_target = getattr(original_surface_target, 'part_owner', None) or original_surface_target
        keys.add(('slot_target', node_or_spec.get_slot_target()))
        slot_type = node_or_spec.get_slot_type()
        if slot_type is not None:
            if slot_type != PostureSpecVariable.SLOT:
                keys.add(('slot_type', slot_type))
        if surface_target == PostureSpecVariable.CONTAINER_TARGET:
            surface_target = node_or_spec.get_body_target()
        if surface_target is None:
            if body_target is not None and not isinstance(body_target, PostureSpecVariable):
                if body_target.is_surface():
                    keys.add(('surface_target', body_target))
                    keys.add(('has_a_surface', True))
        else:
            keys.add(('has_a_surface', False))
    else:
        if surface_target not in (PostureSpecVariable.ANYTHING, PostureSpecVariable.SURFACE_TARGET):
            keys.add(('surface_target', surface_target))
            keys.add(('has_a_surface', True))
        else:
            if surface_target == PostureSpecVariable.SURFACE_TARGET:
                keys.add(('has_a_surface', True))
            else:
                if slot_type == PostureSpecVariable.SLOT:
                    if not isinstance(original_surface_target, PostureSpecVariable):
                        for slot_type in original_surface_target.get_provided_slot_types():
                            keys.add(('slot_type', slot_type))

                    else:
                        surface_target = None
                if posture_type is not None:
                    if body_target != PostureSpecVariable.ANYTHING:
                        keys.add(('body_target', body_target))
                        if body_target != PostureSpecVariable.BODY_TARGET_FILTERED:
                            keys.add(('body_target', PostureSpecVariable.BODY_TARGET_FILTERED))
                    elif surface_target is None:
                        if posture_type.mobile:
                            keys.add(('body_target', None))
                if ('body_target', None) in keys and ('slot_target', None) in keys:
                    keys.add(('body_target and slot_target', None))
            return keys


def set_transition_destinations(sim, source_goals, destination_goals, selected_source=None, selected_destination=None, preserve=False, draw_both_sets=False):
    if False:
        if on_transition_destinations_changed:
            transition_destinations = []
            transition_sources = []
            max_dest_cost = 0
            for slot_goal in source_goals:
                slot_transform = sims4.math.Transform(slot_goal.location.position, slot_goal.location.orientation)
                slot_constraint = interactions.constraints.Transform(slot_transform,
                  routing_surface=(slot_goal.routing_surface_id))
                if slot_goal is selected_source:
                    slot_constraint.was_selected = True
                else:
                    slot_constraint.was_selected = False
                transition_sources.append(slot_constraint)

            for slot_goal in destination_goals:
                if slot_goal.cost > max_dest_cost:
                    max_dest_cost = slot_goal.cost
                else:
                    slot_transform = sims4.math.Transform(slot_goal.location.position, slot_goal.location.orientation)
                    slot_constraint = interactions.constraints.Transform(slot_transform,
                      routing_surface=(slot_goal.routing_surface_id))
                    if slot_goal is selected_destination:
                        slot_constraint.was_selected = True
                    else:
                        slot_constraint.was_selected = False
                transition_destinations.append((slot_goal.path_id,
                 slot_constraint,
                 slot_goal.cost))

            on_transition_destinations_changed(sim, transition_destinations,
              transition_sources,
              max_dest_cost,
              preserve=preserve)


def _is_sim_carry(interaction, sim):
    if sim.parent is not None:
        return True
        if interaction.carry_target is sim:
            return True
        if interaction.is_putdown:
            if interaction.target is sim:
                return True
        if interaction.is_pickup_requester:
            return True
    elif interaction.is_social:
        if interaction.target is sim and interaction.sim is sim.parent:
            return True
    return False


class DistanceEstimator:

    def __init__(self, posture_service, sim, interaction, constraint):
        self.posture_service = posture_service
        self.sim = sim
        self.interaction = interaction
        preferred_objects = interaction.preferred_objects
        self.preferred_objects = preferred_objects
        self.constraint = constraint
        routing_context = sim.get_routing_context()

        @caches.BarebonesCache
        def estimate_connectivity_distance(locations):
            source_location, dest_location = locations
            source_locations = ((source_location.transform.translation, source_location.routing_surface),)
            dest_locations = ((dest_location.transform.translation, dest_location.routing_surface),)
            try:
                distance = primitives.routing_utils.estimate_distance_between_multiple_points(source_locations, dest_locations, routing_context)
            except Exception as e:
                try:
                    logger.warn('{}', e, owner='camilogarcia', trigger_breakpoint=True)
                    distance = None
                finally:
                    e = None
                    del e

            distance = cu.MAX_FLOAT if distance is None else distance
            return distance

        self.estimate_distance = estimate_distance = estimate_connectivity_distance

        @caches.BarebonesCache
        def get_preferred_object_cost(obj):
            return postures.posture_scoring.PostureScoring.get_preferred_object_cost((obj,), preferred_objects)

        self.get_preferred_object_cost = get_preferred_object_cost

        @caches.BarebonesCache
        def get_inventory_distance(sim_location_inv_node_location_and_mobile):
            cython.declare(node_body_posture_is_mobile=(cython.bint))
            sim_location, inv, node_location, node_body_posture_is_mobile = sim_location_inv_node_location_and_mobile
            min_dist = cu.MAX_FLOAT
            include_node_location = not node_body_posture_is_mobile or sim_location != node_location
            for owner in inv.owning_objects_gen():
                routing_position, _ = Constraint.get_validated_routing_position(owner)
                routing_location = routing.Location(routing_position, orientation=(owner.orientation),
                  routing_surface=(owner.routing_surface))
                distance = cython.cast(cython.double, estimate_distance((sim_location, routing_location)))
                if distance >= min_dist:
                    continue
                distance += cython.cast(cython.double, get_preferred_object_cost(owner))
                if distance >= min_dist:
                    continue
                if include_node_location:
                    distance += cython.cast(cython.double, estimate_distance((routing_location, node_location)))
                if distance < min_dist:
                    min_dist = distance

            return min_dist

        self.get_inventory_distance = get_inventory_distance

        @caches.BarebonesCache
        def estimate_location_distance(sim_location_and_target_location_and_mobile):
            sim_location, target_location, node_body_posture_is_mobile = sim_location_and_target_location_and_mobile
            if interaction.target is None:
                return estimate_distance((sim_location, target_location))
            carry_target = interaction.carry_target
            if carry_target is None:
                return estimate_distance((sim_location, target_location))
            inv = interaction.target.get_inventory()
            if inv is None:
                interaction_target_routing_location = interaction.target.routing_location
                if interaction_target_routing_location == target_location:
                    return estimate_distance((sim_location, target_location))
                elif interaction_target_routing_location.routing_surface.type == SurfaceType.SURFACETYPE_OBJECT:
                    interaction_target_world_routing_location = interaction_target_routing_location.get_world_surface_location()
                else:
                    interaction_target_world_routing_location = None
                if interaction.is_put_in_inventory:
                    if node_body_posture_is_mobile:
                        if sim_location == target_location:
                            distance = estimate_distance((sim_location, interaction_target_routing_location))
                            if interaction_target_world_routing_location is not None:
                                world_distance = estimate_distance((sim_location, interaction_target_world_routing_location))
                                distance = min(distance, world_distance)
                            return distance
                distance = estimate_distance((sim_location, interaction_target_routing_location)) + estimate_distance((interaction_target_routing_location, target_location))
                if interaction_target_world_routing_location is not None:
                    world_distance = estimate_distance((sim_location, interaction_target_world_routing_location)) + estimate_distance((interaction_target_world_routing_location, target_location))
                    distance = min(distance, world_distance)
                return distance
            if inv.owner.is_sim:
                if inv.owner is not sim:
                    return NON_OPTIMAL_PATH_DESTINATION
                return estimate_distance((sim_location, target_location))
            return get_inventory_distance((sim_location, inv, target_location, node_body_posture_is_mobile))

        self.estimate_location_distance = estimate_location_distance


class PathType(enum.Int, export=False):
    LEFT = 0
    MIDDLE_LEFT = 1
    MIDDLE_RIGHT = 2
    RIGHT = 3


class SegmentedPath:

    def __init__--- This code section failed: ---

 L. 489         0  LOAD_FAST                'posture_graph'
                2  LOAD_FAST                'self'
                4  STORE_ATTR               posture_graph

 L. 490         6  LOAD_FAST                'sim'
                8  LOAD_FAST                'self'
               10  STORE_ATTR               sim

 L. 491        12  LOAD_FAST                'interaction'
               14  LOAD_FAST                'self'
               16  STORE_ATTR               interaction

 L. 492        18  LOAD_FAST                'source'
               20  LOAD_FAST                'self'
               22  STORE_ATTR               source

 L. 493        24  LOAD_FAST                'valid_edge_test'
               26  LOAD_FAST                'self'
               28  STORE_ATTR               valid_edge_test

 L. 495        30  LOAD_FAST                'var_map'
               32  LOAD_FAST                'self'
               34  STORE_ATTR               var_map

 L. 496        36  LOAD_CONST               None
               38  LOAD_FAST                'self'
               40  STORE_ATTR               _var_map_resolved

 L. 498        42  LOAD_FAST                'constraint'
               44  LOAD_FAST                'self'
               46  STORE_ATTR               constraint

 L. 499        48  LOAD_FAST                'is_complete'
               50  LOAD_FAST                'self'
               52  STORE_ATTR               is_complete

 L. 500        54  LOAD_FAST                'is_complete'
               56  POP_JUMP_IF_FALSE   150  'to 150'

 L. 501        58  LOAD_GLOBAL              _is_sim_carry
               60  LOAD_FAST                'interaction'
               62  LOAD_FAST                'sim'
               64  CALL_FUNCTION_2       2  '2 positional arguments'
               66  STORE_FAST               'is_sim_carry'

 L. 504        68  LOAD_FAST                'source'
               70  LOAD_ATTR                body_target
               72  STORE_DEREF              'source_body_target'

 L. 505        74  LOAD_FAST                'is_sim_carry'
               76  POP_JUMP_IF_FALSE    88  'to 88'

 L. 506        78  LOAD_GLOBAL              dict
               80  LOAD_FAST                'destination_specs'
               82  CALL_FUNCTION_1       1  '1 positional argument'
               84  STORE_FAST               'destination_specs'
               86  JUMP_FORWARD        150  'to 150'
             88_0  COME_FROM            76  '76'

 L. 507        88  LOAD_DEREF               'source_body_target'
               90  LOAD_CONST               None
               92  COMPARE_OP               is
               94  POP_JUMP_IF_FALSE   116  'to 116'

 L. 508        96  LOAD_DICTCOMP            '<code_object <dictcomp>>'
               98  LOAD_STR                 'SegmentedPath.__init__.<locals>.<dictcomp>'
              100  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              102  LOAD_FAST                'destination_specs'
              104  LOAD_METHOD              items
              106  CALL_METHOD_0         0  '0 positional arguments'
              108  GET_ITER         
              110  CALL_FUNCTION_1       1  '1 positional argument'
              112  STORE_FAST               'destination_specs'
              114  JUMP_FORWARD        150  'to 150'
            116_0  COME_FROM            94  '94'

 L. 511       116  LOAD_DEREF               'source_body_target'
              118  LOAD_ATTR                is_part
              120  POP_JUMP_IF_FALSE   128  'to 128'

 L. 512       122  LOAD_DEREF               'source_body_target'
              124  LOAD_ATTR                part_owner
              126  STORE_DEREF              'source_body_target'
            128_0  COME_FROM           120  '120'

 L. 513       128  LOAD_CLOSURE             'source_body_target'
              130  BUILD_TUPLE_1         1 
              132  LOAD_DICTCOMP            '<code_object <dictcomp>>'
              134  LOAD_STR                 'SegmentedPath.__init__.<locals>.<dictcomp>'
              136  MAKE_FUNCTION_8          'closure'
              138  LOAD_FAST                'destination_specs'
              140  LOAD_METHOD              items
              142  CALL_METHOD_0         0  '0 positional arguments'
              144  GET_ITER         
              146  CALL_FUNCTION_1       1  '1 positional argument'
              148  STORE_FAST               'destination_specs'
            150_0  COME_FROM           114  '114'
            150_1  COME_FROM            86  '86'
            150_2  COME_FROM            56  '56'

 L. 515       150  LOAD_FAST                'destination_specs'
              152  POP_JUMP_IF_TRUE    162  'to 162'

 L. 516       154  LOAD_GLOBAL              ValueError
              156  LOAD_STR                 'Segmented paths need destinations.'
              158  CALL_FUNCTION_1       1  '1 positional argument'
              160  RAISE_VARARGS_1       1  'exception instance'
            162_0  COME_FROM           152  '152'

 L. 517       162  LOAD_FAST                'destination_specs'
              164  LOAD_FAST                'self'
              166  STORE_ATTR               destination_specs

 L. 518       168  LOAD_FAST                'destination_specs'
              170  LOAD_METHOD              keys
              172  CALL_METHOD_0         0  '0 positional arguments'
              174  LOAD_FAST                'self'
              176  STORE_ATTR               destinations

 L. 520       178  LOAD_FAST                'distance_estimator'
              180  LOAD_CONST               None
              182  COMPARE_OP               is
              184  POP_JUMP_IF_FALSE   206  'to 206'

 L. 521       186  LOAD_GLOBAL              DistanceEstimator
              188  LOAD_FAST                'self'
              190  LOAD_ATTR                posture_graph
              192  LOAD_FAST                'self'
              194  LOAD_ATTR                sim

 L. 522       196  LOAD_FAST                'self'
              198  LOAD_ATTR                interaction
              200  LOAD_FAST                'constraint'
              202  CALL_FUNCTION_4       4  '4 positional arguments'
              204  STORE_FAST               'distance_estimator'
            206_0  COME_FROM           184  '184'

 L. 523       206  LOAD_FAST                'distance_estimator'
              208  LOAD_FAST                'self'
              210  STORE_ATTR               _distance_estimator

Parse error at or near `LOAD_DICTCOMP' instruction at offset 132

    def teardown(self):
        pass

    @property
    def var_map_resolved(self):
        if self._var_map_resolved is None:
            return self.var_map
        return self._var_map_resolved

    @var_map_resolved.setter
    def var_map_resolved(self, value):
        self._var_map_resolved = value

    def check_validity(self, sim):
        source_spec = sim.posture_state.get_posture_spec(self.var_map)
        return source_spec == self.source

    def generate_left_paths(self, force_carry_path=False):
        left_path_gen = self.posture_graph._left_path_gen(self.sim, self.source, self.destinations, self.interaction, self.constraint, self.var_map, self.valid_edge_test, self.is_complete, force_carry_path)
        for path_left in left_path_gen:
            path_left.segmented_path = self
            yield path_left

    def generate_right_paths(self, sim, path_left):
        global STAND_AT_NONE_CARRY
        global STAND_AT_NONE_NODES
        if path_left[-1] in self.destinations:
            if len(self.destinations) == 1:
                cost = self.posture_graph._get_goal_cost(self.sim, self.interaction, self.constraint, self.var_map, path_left[-1])
                path_right = algos.Path([path_left[-1]], cost)
                path_right.segmented_path = self
                yield path_right
                return
        allow_carried = False
        ensemble = None
        if self.is_complete:
            left_destinations = (path_left[-1],)
        else:
            carry = self.var_map.get(PostureSpecVariable.CARRY_TARGET)
            if carry is sim:
                left_destinations = (
                 path_left[-1],)
                allow_carried = True
                ensemble = services.ensemble_service().get_most_important_ensemble_for_sim(sim)
            else:
                if carry is not None:
                    if path_left[-1].carry_target is None:
                        for constraint in self.constraint:
                            if constraint.posture_state_spec is not None and carry is not self.sim and constraint.posture_state_spec.references_object(carry):
                                break
                        else:
                            carry = None

                if carry is None or isinstance(carry, Definition):
                    left_destinations = services.posture_graph_service().all_mobile_nodes_at_none_no_carry
                else:
                    if (carry.is_in_inventory() or carry.parent) not in (None, self.sim):
                        left_destinations = STAND_AT_NONE_NODES
                    else:
                        left_destinations = (
                         STAND_AT_NONE_CARRY,)
        self.left_destinations = left_destinations
        paths_right = self.posture_graph._right_path_gen((self.sim),
          (self.interaction), (self._distance_estimator), left_destinations, (self.destinations),
          (self.var_map), (self.constraint), (self.valid_edge_test), path_left,
          allow_carried=allow_carried, ensemble=ensemble)
        for path_right in paths_right:
            path_right.segmented_path = self
            yield path_right

    def generate_middle_paths(self, path_left, path_right):
        if self.is_complete:
            yield
            return
        middle_paths = self.posture_graph._middle_path_gen(path_left, path_right, self.sim, self.interaction, self._distance_estimator, self.var_map)
        for path_middle in middle_paths:
            if path_middle is not None:
                path_middle.segmented_path = self
            yield path_middle

    @property
    def _path(self):
        return algos.Path(list(getattr(self, '_path_left', ['...?'])) + list(getattr(self, '_path_middle', ['...', '...?']) or [])[1:] + list(getattr(self, '_path_right', ['...', '...?']))[1:])

    def __repr__(self):
        if self.is_complete:
            return 'CompleteSegmentedPath(...)'
        return 'SegmentedPath(...)'


class Connectivity:

    def __init__(self, best_complete_path, source_destination_sets, source_middle_sets, middle_destination_sets):
        self.best_complete_path = best_complete_path
        self.source_destination_sets = source_destination_sets
        self.source_middle_sets = source_middle_sets
        self.middle_destination_sets = middle_destination_sets

    def __repr__(self):
        return 'Connectivity%r' % (tuple(self),)

    def __bool__(self):
        return any(self)

    def __iter__(self):
        return iter((self.best_complete_path, self.source_destination_sets,
         self.source_middle_sets, self.middle_destination_sets))

    def __getitem__(self, i):
        return (
         self.best_complete_path, self.source_destination_sets,
         self.source_middle_sets, self.middle_destination_sets)[i]


class TransitionSequenceStage(enum.Int, export=False):
    EMPTY = ...
    TEMPLATES = ...
    PATHS = ...
    CONNECTIVITY = ...
    ROUTES = ...
    ACTOR_TARGET_SYNC = ...
    COMPLETE = ...


class SequenceId(enum.Int, export=False):
    DEFAULT = 0
    PICKUP = 1
    PUTDOWN = 2


_MobileNode = namedtuple('_MobileNode', ('graph_node', 'prev'))
COST_DELIMITER_STR = '----------------------------------'

def _shortest_path_gen(sim, sources, destinations, force_carry_path, *args, **kwargs):
    if gsi_handlers.posture_graph_handlers.archiver.enabled:
        gsi_handlers.posture_graph_handlers.log_path_cost(sim, COST_DELIMITER_STR, COST_DELIMITER_STR, (COST_DELIMITER_STR,))
        gsi_handlers.posture_graph_handlers.add_heuristic_fn_score(sim, '', COST_DELIMITER_STR, COST_DELIMITER_STR, '')

    def is_destination(node):
        prev = None
        if isinstance(node, _MobileNode):
            prev = node.prev
            node = node.graph_node
        if force_carry_path:
            if prev:
                if prev.body_target:
                    if prev.body_target.is_sim:
                        return node in destinations
            return False
        return node in destinations

    fake_paths = (algos.shortest_path_gen)(sources, is_destination, *args, **kwargs)
    for fake_path in fake_paths:
        path = algos.Path([node.graph_node if isinstance(node, _MobileNode) else node for node in fake_path], fake_path.cost)
        yield path


def set_transition_failure_reason(sim, reason, target_id=None, transition_controller=None):
    if transition_controller is None:
        transition_controller = sim.transition_controller
    if transition_controller is not None:
        transition_controller.set_failure_target(sim, reason, target_id=target_id)


def _cache_global_sim_default_values():
    global SIM_DEFAULT_AOPS
    global SIM_DEFAULT_OPERATION
    global SIM_DEFAULT_POSTURE_TYPE
    global SIM_INFANT_OVERRIDE_DEFAULT_OPERATION
    global SIM_SWIM_AOPS
    global SIM_SWIM_OPERATION
    global SIM_SWIM_POSTURE_TYPE
    global SIM_TESTED_AOPS
    global STAND_AT_NONE
    global STAND_AT_NONE_CARRY
    global STAND_AT_NONE_NODES
    global SWIM_AT_NONE
    global SWIM_AT_NONE_CARRY
    global SWIM_AT_NONE_NODES
    global _DEFAULT_MOBILE_NODES
    global _MOBILE_NODES_AT_NONE
    global _MOBILE_NODES_AT_NONE_CARRY
    SIM_DEFAULT_POSTURE_TYPE = PostureGraphService.get_default_affordance(Species.HUMAN).provided_posture_type
    SIM_INFANT_OVERRIDE_DEFAULT_POSTURE_TYPE = PostureGraphService.get_infant_default_affordance_override_posture_type()
    STAND_AT_NONE = get_origin_spec(SIM_DEFAULT_POSTURE_TYPE)
    STAND_AT_NONE_CARRY = get_origin_spec_carry(SIM_DEFAULT_POSTURE_TYPE)
    STAND_AT_NONE_NODES = (STAND_AT_NONE, STAND_AT_NONE_CARRY)
    SIM_DEFAULT_AOPS = enumdict(Species, {species: AffordanceObjectPair(affordance, None, affordance, None, force_inertial=True) for species, affordance in PostureGraphService.SIM_DEFAULT_AFFORDANCES.items()})
    SIM_INFANT_OVERRIDE_DEFAULT_AOPS = enumdict(Species, {data.species: AffordanceObjectPair((data.affordance), None, (data.affordance), None, force_inertial=True) for data in PostureGraphService.SIM_DEFAULT_AFFORDANCES_OVERRIDES if data.age == Age.INFANT})
    SIM_TESTED_AOPS = {}
    for data in PostureGraphService.SIM_DEFAULT_AFFORDANCES_OVERRIDES:
        aop = AffordanceObjectPair((data.affordance), None, (data.affordance), None, force_inertial=True)
        if (data.species, data.age) not in SIM_TESTED_AOPS:
            SIM_TESTED_AOPS[(data.species, data.age)] = []
        SIM_TESTED_AOPS[(data.species, data.age)].append({'tests':data.tests,  'aop':aop})

    SIM_DEFAULT_OPERATION = PostureOperation.BodyTransition(SIM_DEFAULT_POSTURE_TYPE, SIM_DEFAULT_AOPS)
    SIM_INFANT_OVERRIDE_DEFAULT_OPERATION = PostureOperation.BodyTransition(SIM_INFANT_OVERRIDE_DEFAULT_POSTURE_TYPE, SIM_INFANT_OVERRIDE_DEFAULT_AOPS) if SIM_INFANT_OVERRIDE_DEFAULT_POSTURE_TYPE is not None else None
    SIM_SWIM_POSTURE_TYPE = PostureGraphService.get_default_swim_affordance(Species.HUMAN).provided_posture_type
    SWIM_AT_NONE = get_origin_spec(SIM_SWIM_POSTURE_TYPE)
    SWIM_AT_NONE_CARRY = get_origin_spec_carry(SIM_SWIM_POSTURE_TYPE)
    SWIM_AT_NONE_NODES = (SWIM_AT_NONE, SWIM_AT_NONE_CARRY)
    SIM_SWIM_AOPS = enumdict(Species, {species: AffordanceObjectPair(affordance, None, affordance, None, force_inertial=True) for species, affordance in PostureGraphService.SWIM_DEFAULT_AFFORDANCES.items()})
    SIM_SWIM_OPERATION = PostureOperation.BodyTransition(SIM_SWIM_POSTURE_TYPE, SIM_SWIM_AOPS)
    _MOBILE_NODES_AT_NONE = {
     STAND_AT_NONE}
    _MOBILE_NODES_AT_NONE_CARRY = {STAND_AT_NONE_CARRY}
    _DEFAULT_MOBILE_NODES = {STAND_AT_NONE, STAND_AT_NONE_CARRY}
    for affordance in PostureGraphService.POSTURE_PROVIDING_AFFORDANCES:
        if affordance.provided_posture_type is not None and affordance.provided_posture_type.mobile:
            posture_type = affordance.provided_posture_type.skip_route or affordance.provided_posture_type
            mobile_node_at_none = get_origin_spec(posture_type)
            _MOBILE_NODES_AT_NONE.add(mobile_node_at_none)
            _DEFAULT_MOBILE_NODES.add(mobile_node_at_none)
            if posture_type._supports_carry:
                mobile_node_at_none_carry = get_origin_spec_carry(posture_type)
                _MOBILE_NODES_AT_NONE_CARRY.add(mobile_node_at_none_carry)
                _DEFAULT_MOBILE_NODES.add(mobile_node_at_none_carry)


def get_mobile_posture_constraint(posture=None, target=None):
    posture_manifests = []
    body_target = target
    if posture is not None:
        if posture is SIM_DEFAULT_POSTURE_TYPE:
            return STAND_AT_NONE_CONSTRAINT
        else:
            if posture is SIM_SWIM_POSTURE_TYPE:
                return SWIM_AT_NONE_CONSTRAINT
            posture.mobile or logger.error('Cannot create mobile posture constraint from non-mobile posture {}', posture)
            return Nowhere('Mobile posture override {} is not actually mobile.', posture)
        posture_manifests = [posture.get_provided_postures()]
    if (posture_manifests or target) is not None:
        for mobile_posture in target.provided_mobile_posture_types:
            posture_manifests.append(mobile_posture.get_provided_postures())
            if mobile_posture.unconstrained:
                body_target = None
            break

    else:
        if posture_manifests:
            if target is not None and target.routing_component is None:
                body_target = PostureSpecVariable.ANYTHING
    constraints = []
    for manifest in posture_manifests:
        posture_state_spec = create_body_posture_state_spec(manifest, body_target=body_target)
        constraint = Constraint(debug_name='MobilePosture@None', posture_state_spec=posture_state_spec)
        constraints.append(constraint)

    if constraints:
        return create_constraint_set(constraints, debug_name='MobilePostureConstraints')
    return STAND_AT_NONE_CONSTRAINT


def is_object_mobile_posture_compatible(obj):
    return any((posture_type.posture_objects is not None for posture_type in obj.provided_mobile_posture_types))


@contextmanager
def supress_posture_graph_build(rebuild=True):
    posture_graph_service = services.current_zone().posture_graph_service
    posture_graph_service.disable_graph_building()
    try:
        yield
    finally:
        posture_graph_service.enable_graph_building()
        if rebuild:
            posture_graph_service.rebuild()


def can_remove_blocking_sims(sim, interaction, required_targets):
    need_to_cancel = []
    blocking_sims = set()
    for obj in required_targets:
        obj_users = obj.get_users()
        if not obj_users:
            if obj.is_part:
                obj = obj.part_owner
                obj_users = obj.get_users()
        for blocking_sim in obj_users:
            if blocking_sim is sim:
                continue
            if not blocking_sim.is_sim:
                return (
                 False, need_to_cancel, blocking_sims)
                for blocking_si in blocking_sim.si_state:
                    if not obj.is_same_object_or_part(blocking_si.target):
                        continue
                    if not blocking_si.can_shoo or blocking_si.priority >= interaction.priority:
                        return (
                         False, need_to_cancel, blocking_sims)
                    need_to_cancel.append(blocking_si)
                    blocking_sims.add(blocking_sim)

    return (
     True, need_to_cancel, blocking_sims)


class TransitionSpec:
    DISTANCE_TO_FADE_SIM_OUT = Tunable(description='\n        Distance at which a Sim will start fading out if tuned as such.\n        ',
      tunable_type=float,
      default=5.0)


@cython.cfunc
@cython.exceptval(check=False)
def TransitionSpecCython_create(path_spec, posture_spec: PostureSpec, var_map, sequence_id=SequenceId.DEFAULT, portal_obj=None, portal_id=None) -> 'TransitionSpecCython':
    self = cython.declare(TransitionSpecCython, TransitionSpecCython.__new__(TransitionSpecCython))
    self.posture_spec = posture_spec
    self._path_spec = path_spec
    self.var_map = var_map
    self.path = None
    self.final_constraint = None
    self._transition_interactions = {}
    self.sequence_id = sequence_id
    self.locked_params = frozendict()
    self._additional_reservation_handlers = []
    self.handle_slot_reservations = False
    self._portal_ref = portal_obj.ref() if portal_obj is not None else None
    self.portal_id = portal_id
    self.created_posture_state = None
    return self


@cython.cclass
class TransitionSpecCython:
    posture_spec = cython.declare(PostureSpec, visibility='readonly')
    _path_spec = cython.declare(object, visibility='public')
    var_map = cython.declare(object, visibility='public')
    path = cython.declare(object, visibility='public')
    final_constraint = cython.declare(object, visibility='readonly')
    _transition_interactions = cython.declare(dict, visibility='readonly')
    sequence_id = cython.declare(object, visibility='readonly')
    locked_params = cython.declare(object, visibility='public')
    _additional_reservation_handlers: list
    handle_slot_reservations = cython.declare((cython.bint), visibility='public')
    _portal_ref: object
    portal_id = cython.declare(object, visibility='public')
    created_posture_state = cython.declare(object, visibility='public')

    @property
    def mobile(self):
        return self.posture_spec.body.posture_type.mobile

    @property
    def is_failure_path(self):
        return self._path_spec.is_failure_path

    @property
    def final_si(self):
        return self._path_spec._final_si

    @property
    def is_carry(self):
        return self.posture_spec.carry.target is not None

    @property
    def targets_empty_slot(self):
        surface_spec = self.posture_spec.surface
        if surface_spec.slot_type is not None:
            if surface_spec.slot_target is None:
                return True
        return False

    @property
    def portal_obj(self):
        if self._portal_ref is not None:
            return self._portal_ref()

    @portal_obj.setter
    def portal_obj(self, value):
        if value is None:
            self._portal_ref = None
        else:
            if issubclass(value.__class__, ProxyObject):
                self._portal_ref = value.ref()
            else:
                self._portal_ref = weakref.ref(value)

    def transition_interactions(self, sim):
        if sim in self._transition_interactions:
            return self._transition_interactions[sim]
        return []

    def test_transition_interactions(self, sim, interaction):
        if sim in self._transition_interactions:
            for si, _ in self._transition_interactions[sim]:
                if si is interaction:
                    continue
                if si is not None:
                    return si.aop.test(si.context) or False

        return True

    def get_multi_target_interaction(self, sim):
        final_si = self._path_spec._final_si
        if sim in self._transition_interactions:
            for si, _ in self._transition_interactions[sim]:
                if si is not final_si:
                    return si

    @cython.ccall
    @cython.exceptval(check=False)
    def set_path(self, path, final_constraint) -> cython.void:
        self.path = path
        if final_constraint is not None and final_constraint.tentative:
            logger.warn("TransitionSpec's final constraint is tentative, this will not work correctly so the constraint will be ignored. This may interfere with slot reservation.", owner='jpollak')
        else:
            self.final_constraint = final_constraint

    def transfer_route_to(self, other_spec):
        other_spec.path = self.path
        self.path = None

    def add_transition_interaction(self, sim, interaction, var_map):
        if interaction is not None:
            if not interaction.get_participant_type(sim) == ParticipantType.Actor:
                return
        if sim not in self._transition_interactions:
            self._transition_interactions[sim] = []
        self._transition_interactions[sim].append((interaction, var_map))

    def set_locked_params(self, locked_params):
        self.locked_params = locked_params

    def __repr__(self):
        args = [
         self.posture_spec]
        kwargs = {}
        if self.path is not None:
            args.append(suppress_quotes('has_route'))
        if self.locked_params:
            kwargs['locked_params'] = self.locked_params
        if self.final_constraint is not None:
            kwargs['final_constraint'] = self.final_constraint
        return standard_angle_repr(self, *args, **kwargs)

    def release_additional_reservation_handlers(self):
        for handler in self._additional_reservation_handlers:
            handler.end_reservation()

        self._additional_reservation_handlers.clear()

    def remove_props_created_to_reserve_slots(self, sim):
        if self._transition_interactions is not None:
            for reservation_si, _ in self._transition_interactions.get(sim, ()):
                if reservation_si is not None:
                    reservation_si.animation_context.clear_reserved_slots()

    def do_reservation--- This code section failed: ---

 L.1218         0  LOAD_CLOSURE             'reserve_object_handlers'
                2  BUILD_TUPLE_1         1 
                4  LOAD_CODE                <code_object cancel_reservations>
                6  LOAD_STR                 'TransitionSpecCython.do_reservation.<locals>.cancel_reservations'
                8  MAKE_FUNCTION_8          'closure'
               10  STORE_DEREF              'cancel_reservations'

 L.1222        12  LOAD_CONST               (False,)
               14  LOAD_CLOSURE             'cancel_reservations'
               16  LOAD_CLOSURE             'reserve_object_handlers'
               18  LOAD_CLOSURE             'sim'
               20  BUILD_TUPLE_3         3 
               22  LOAD_CODE                <code_object add_reservation>
               24  LOAD_STR                 'TransitionSpecCython.do_reservation.<locals>.add_reservation'
               26  MAKE_FUNCTION_9          'default, closure'
               28  STORE_FAST               'add_reservation'

 L.1238     30_32  SETUP_EXCEPT       1132  'to 1132'

 L.1241        34  LOAD_GLOBAL              set
               36  CALL_FUNCTION_0       0  '0 positional arguments'
               38  STORE_DEREF              'reserve_object_handlers'

 L.1243        40  BUILD_LIST_0          0 
               42  STORE_FAST               'reservations_sis'

 L.1244        44  LOAD_FAST                'self'
               46  STORE_FAST               'reservation_spec'

 L.1245        48  SETUP_LOOP          120  'to 120'
             50_0  COME_FROM           112  '112'
             50_1  COME_FROM           102  '102'
               50  LOAD_FAST                'reservation_spec'
               52  LOAD_CONST               None
               54  COMPARE_OP               is-not
               56  POP_JUMP_IF_FALSE   118  'to 118'

 L.1246        58  LOAD_DEREF               'sim'
               60  LOAD_FAST                'reservation_spec'
               62  LOAD_ATTR                _transition_interactions
               64  COMPARE_OP               in
               66  POP_JUMP_IF_FALSE    84  'to 84'

 L.1247        68  LOAD_FAST                'reservations_sis'
               70  LOAD_METHOD              extend
               72  LOAD_FAST                'reservation_spec'
               74  LOAD_ATTR                _transition_interactions
               76  LOAD_DEREF               'sim'
               78  BINARY_SUBSCR    
               80  CALL_METHOD_1         1  '1 positional argument'
               82  POP_TOP          
             84_0  COME_FROM            66  '66'

 L.1248        84  LOAD_FAST                'self'
               86  LOAD_ATTR                _path_spec
               88  LOAD_METHOD              get_next_transition_spec
               90  LOAD_FAST                'reservation_spec'
               92  CALL_METHOD_1         1  '1 positional argument'
               94  STORE_FAST               'reservation_spec'

 L.1251        96  LOAD_FAST                'reservation_spec'
               98  LOAD_CONST               None
              100  COMPARE_OP               is-not
              102  POP_JUMP_IF_FALSE    50  'to 50'
              104  LOAD_FAST                'reservation_spec'
              106  LOAD_ATTR                path
              108  LOAD_CONST               None
              110  COMPARE_OP               is-not
              112  POP_JUMP_IF_FALSE    50  'to 50'

 L.1252       114  BREAK_LOOP       
              116  JUMP_BACK            50  'to 50'
            118_0  COME_FROM            56  '56'
              118  POP_BLOCK        
            120_0  COME_FROM_LOOP       48  '48'

 L.1254       120  LOAD_FAST                'is_failure_path'
              122  POP_JUMP_IF_FALSE   132  'to 132'
              124  LOAD_FAST                'reservations_sis'
              126  POP_JUMP_IF_TRUE    132  'to 132'

 L.1255       128  LOAD_CONST               False
              130  RETURN_VALUE     
            132_0  COME_FROM           126  '126'
            132_1  COME_FROM           122  '122'

 L.1257   132_134  SETUP_LOOP          666  'to 666'
              136  LOAD_FAST                'reservations_sis'
              138  GET_ITER         
            140_0  COME_FROM           534  '534'
          140_142  FOR_ITER            664  'to 664'
              144  UNPACK_SEQUENCE_2     2 
              146  STORE_FAST               'si'
              148  STORE_FAST               '_'

 L.1258       150  LOAD_FAST                'si'
              152  LOAD_CONST               None
              154  COMPARE_OP               is
              156  POP_JUMP_IF_FALSE   160  'to 160'

 L.1259       158  CONTINUE            140  'to 140'
            160_0  COME_FROM           156  '156'

 L.1260       160  LOAD_FAST                'si'
              162  LOAD_ATTR                is_putdown
              164  POP_JUMP_IF_FALSE   196  'to 196'

 L.1261       166  LOAD_FAST                'si'
              168  LOAD_METHOD              get_target_si
              170  CALL_METHOD_0         0  '0 positional arguments'
              172  UNPACK_SEQUENCE_2     2 
              174  STORE_FAST               'target_si'
              176  STORE_FAST               '_'

 L.1262       178  LOAD_FAST                'target_si'
              180  LOAD_CONST               None
              182  COMPARE_OP               is-not
              184  POP_JUMP_IF_FALSE   196  'to 196'

 L.1263       186  LOAD_FAST                'target_si'
              188  STORE_FAST               'si'

 L.1264       190  LOAD_FAST                'si'
              192  LOAD_ATTR                sim
              194  STORE_DEREF              'sim'
            196_0  COME_FROM           184  '184'
            196_1  COME_FROM           164  '164'

 L.1265       196  LOAD_FAST                'si'
              198  LOAD_METHOD              get_liability
              200  LOAD_GLOBAL              RESERVATION_LIABILITY
              202  CALL_METHOD_1         1  '1 positional argument'
              204  LOAD_CONST               None
              206  COMPARE_OP               is-not
              208  POP_JUMP_IF_FALSE   212  'to 212'

 L.1267       210  CONTINUE            140  'to 140'
            212_0  COME_FROM           208  '208'

 L.1269       212  LOAD_FAST                'si'
              214  LOAD_ATTR                get_interaction_reservation_handler
              216  LOAD_DEREF               'sim'
              218  LOAD_CONST               ('sim',)
              220  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              222  STORE_FAST               'handler'

 L.1270       224  LOAD_FAST                'is_failure_path'
              226  POP_JUMP_IF_FALSE   238  'to 238'
              228  LOAD_FAST                'handler'
              230  LOAD_CONST               None
              232  COMPARE_OP               is
              234  POP_JUMP_IF_FALSE   238  'to 238'

 L.1271       236  CONTINUE            140  'to 140'
            238_0  COME_FROM           234  '234'
            238_1  COME_FROM           226  '226'

 L.1273       238  LOAD_FAST                'handler'
              240  LOAD_CONST               None
              242  COMPARE_OP               is-not
          244_246  POP_JUMP_IF_FALSE   516  'to 516'

 L.1274       248  BUILD_LIST_0          0 
              250  STORE_FAST               'handlers'

 L.1275       252  LOAD_FAST                'is_failure_path'
          254_256  POP_JUMP_IF_FALSE   272  'to 272'

 L.1279       258  LOAD_FAST                'add_reservation'
              260  LOAD_FAST                'handler'
              262  LOAD_CONST               True
              264  LOAD_CONST               ('test_only',)
              266  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              268  STORE_FAST               'reserve_result'
              270  JUMP_FORWARD        280  'to 280'
            272_0  COME_FROM           254  '254'

 L.1281       272  LOAD_FAST                'add_reservation'
              274  LOAD_FAST                'handler'
              276  CALL_FUNCTION_1       1  '1 positional argument'
              278  STORE_FAST               'reserve_result'
            280_0  COME_FROM           270  '270'

 L.1282       280  LOAD_FAST                'reserve_result'
          282_284  POP_JUMP_IF_TRUE    476  'to 476'

 L.1283       286  LOAD_FAST                'si'
              288  LOAD_ATTR                source
              290  LOAD_GLOBAL              InteractionSource
              292  LOAD_ATTR                BODY_CANCEL_AOP
              294  COMPARE_OP               ==
          296_298  POP_JUMP_IF_TRUE    314  'to 314'

 L.1284       300  LOAD_FAST                'si'
              302  LOAD_ATTR                source
              304  LOAD_GLOBAL              InteractionSource
              306  LOAD_ATTR                CARRY_CANCEL_AOP
              308  COMPARE_OP               ==
          310_312  POP_JUMP_IF_FALSE   334  'to 334'
            314_0  COME_FROM           296  '296'

 L.1289       314  LOAD_GLOBAL              logger
              316  LOAD_ATTR                warn
              318  LOAD_STR                 '{} failed to pass reservation tests as a cancel AOP. Result: {}'
              320  LOAD_FAST                'si'
              322  LOAD_FAST                'reserve_result'
              324  LOAD_STR                 'cgast'
              326  LOAD_CONST               ('owner',)
              328  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
              330  POP_TOP          

 L.1290       332  CONTINUE            140  'to 140'
            334_0  COME_FROM           310  '310'

 L.1292       334  LOAD_FAST                'si'
              336  LOAD_ATTR                priority
              338  LOAD_GLOBAL              Priority
              340  LOAD_ATTR                Low
              342  COMPARE_OP               ==
          344_346  POP_JUMP_IF_FALSE   352  'to 352'

 L.1296       348  LOAD_CONST               False
              350  RETURN_VALUE     
            352_0  COME_FROM           344  '344'

 L.1301       352  LOAD_GLOBAL              can_remove_blocking_sims
              354  LOAD_DEREF               'sim'
              356  LOAD_FAST                'si'
              358  LOAD_FAST                'handler'
              360  LOAD_METHOD              get_targets
              362  CALL_METHOD_0         0  '0 positional arguments'
              364  CALL_FUNCTION_3       3  '3 positional arguments'
              366  UNPACK_SEQUENCE_3     3 
              368  STORE_FAST               'able_to_cancel_blockers'
              370  STORE_FAST               'need_to_cancel'
              372  STORE_FAST               'blocking_sims'

 L.1302       374  LOAD_FAST                'able_to_cancel_blockers'
          376_378  POP_JUMP_IF_TRUE    384  'to 384'

 L.1303       380  LOAD_CONST               False
              382  RETURN_VALUE     
            384_0  COME_FROM           376  '376'

 L.1305       384  LOAD_FAST                'need_to_cancel'
          386_388  POP_JUMP_IF_FALSE   472  'to 472'

 L.1306       390  SETUP_LOOP          416  'to 416'
              392  LOAD_FAST                'need_to_cancel'
              394  GET_ITER         
              396  FOR_ITER            414  'to 414'
              398  STORE_FAST               'blocking_si'

 L.1307       400  LOAD_FAST                'blocking_si'
              402  LOAD_METHOD              cancel_user
              404  LOAD_STR                 'Sim was kicked out by another Sim with a higher priority interaction.'
              406  CALL_METHOD_1         1  '1 positional argument'
              408  POP_TOP          
          410_412  JUMP_BACK           396  'to 396'
              414  POP_BLOCK        
            416_0  COME_FROM_LOOP      390  '390'

 L.1309       416  SETUP_LOOP          440  'to 440'
              418  LOAD_FAST                'blocking_sims'
              420  GET_ITER         
              422  FOR_ITER            438  'to 438'
              424  STORE_FAST               'blocking_sim'

 L.1310       426  LOAD_GLOBAL              push_route_away
              428  LOAD_FAST                'blocking_sim'
              430  CALL_FUNCTION_1       1  '1 positional argument'
              432  POP_TOP          
          434_436  JUMP_BACK           422  'to 422'
              438  POP_BLOCK        
            440_0  COME_FROM_LOOP      416  '416'

 L.1312       440  LOAD_DEREF               'sim'
              442  LOAD_ATTR                queue
              444  LOAD_ATTR                transition_controller
              446  LOAD_METHOD              add_blocked_si
              448  LOAD_FAST                'si'
              450  CALL_METHOD_1         1  '1 positional argument'
              452  POP_TOP          

 L.1313       454  LOAD_DEREF               'sim'
              456  LOAD_ATTR                queue
              458  LOAD_ATTR                transition_controller
              460  LOAD_METHOD              derail

 L.1314       462  LOAD_GLOBAL              DerailReason
              464  LOAD_ATTR                WAIT_FOR_BLOCKING_SIMS
              466  LOAD_DEREF               'sim'
              468  CALL_METHOD_2         2  '2 positional arguments'
              470  POP_TOP          
            472_0  COME_FROM           386  '386'

 L.1316       472  LOAD_CONST               False
              474  RETURN_VALUE     
            476_0  COME_FROM           282  '282'

 L.1318       476  LOAD_FAST                'is_failure_path'
          478_480  POP_JUMP_IF_FALSE   486  'to 486'

 L.1319       482  LOAD_CONST               False
              484  RETURN_VALUE     
            486_0  COME_FROM           478  '478'

 L.1321       486  LOAD_FAST                'handlers'
              488  LOAD_METHOD              append
              490  LOAD_FAST                'handler'
              492  CALL_METHOD_1         1  '1 positional argument'
              494  POP_TOP          

 L.1323       496  LOAD_GLOBAL              ReservationLiability
              498  LOAD_FAST                'handlers'
              500  CALL_FUNCTION_1       1  '1 positional argument'
              502  STORE_FAST               'liability'

 L.1324       504  LOAD_FAST                'si'
              506  LOAD_METHOD              add_liability
              508  LOAD_GLOBAL              RESERVATION_LIABILITY
              510  LOAD_FAST                'liability'
              512  CALL_METHOD_2         2  '2 positional arguments'
              514  POP_TOP          
            516_0  COME_FROM           244  '244'

 L.1328       516  LOAD_FAST                'self'
              518  LOAD_ATTR                _path_spec
              520  LOAD_METHOD              get_next_transition_spec
              522  LOAD_FAST                'self'
              524  CALL_METHOD_1         1  '1 positional argument'
              526  STORE_FAST               'next_spec'

 L.1329       528  LOAD_FAST                'next_spec'
              530  LOAD_CONST               None
              532  COMPARE_OP               is-not
              534  POP_JUMP_IF_FALSE   140  'to 140'

 L.1330       536  LOAD_GLOBAL              set
              538  CALL_FUNCTION_0       0  '0 positional arguments'
              540  STORE_FAST               'target_set'

 L.1331       542  LOAD_FAST                'target_set'
              544  LOAD_METHOD              add
              546  LOAD_FAST                'next_spec'
              548  LOAD_ATTR                posture_spec
              550  LOAD_ATTR                body_target
              552  CALL_METHOD_1         1  '1 positional argument'
              554  POP_TOP          

 L.1332       556  LOAD_FAST                'target_set'
              558  LOAD_METHOD              add
              560  LOAD_FAST                'next_spec'
              562  LOAD_ATTR                posture_spec
              564  LOAD_ATTR                surface_target
              566  CALL_METHOD_1         1  '1 positional argument'
              568  POP_TOP          

 L.1333       570  SETUP_LOOP          662  'to 662'
              572  LOAD_FAST                'target_set'
              574  GET_ITER         
            576_0  COME_FROM           640  '640'
            576_1  COME_FROM           586  '586'
              576  FOR_ITER            660  'to 660'
              578  STORE_FAST               'target'

 L.1334       580  LOAD_FAST                'target'
              582  LOAD_CONST               None
              584  COMPARE_OP               is
          586_588  POP_JUMP_IF_TRUE    576  'to 576'
              590  LOAD_FAST                'handler'
              592  LOAD_CONST               None
              594  COMPARE_OP               is-not
          596_598  POP_JUMP_IF_FALSE   618  'to 618'
              600  LOAD_FAST                'target'
              602  LOAD_FAST                'handler'
              604  LOAD_METHOD              get_targets
              606  CALL_METHOD_0         0  '0 positional arguments'
              608  COMPARE_OP               in
          610_612  POP_JUMP_IF_FALSE   618  'to 618'

 L.1335   614_616  CONTINUE            576  'to 576'
            618_0  COME_FROM           610  '610'
            618_1  COME_FROM           596  '596'

 L.1336       618  LOAD_GLOBAL              ReservationHandlerMulti
              620  LOAD_DEREF               'sim'
              622  LOAD_FAST                'target'
              624  LOAD_FAST                'si'
              626  LOAD_CONST               None
              628  LOAD_CONST               ('reservation_interaction', 'reservation_limit')
              630  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
              632  STORE_FAST               'target_handler'

 L.1337       634  LOAD_FAST                'add_reservation'
              636  LOAD_FAST                'target_handler'
              638  CALL_FUNCTION_1       1  '1 positional argument'
          640_642  POP_JUMP_IF_FALSE   576  'to 576'

 L.1338       644  LOAD_FAST                'self'
              646  LOAD_ATTR                _additional_reservation_handlers
              648  LOAD_METHOD              append
              650  LOAD_FAST                'target_handler'
              652  CALL_METHOD_1         1  '1 positional argument'
              654  POP_TOP          
          656_658  JUMP_BACK           576  'to 576'
              660  POP_BLOCK        
            662_0  COME_FROM_LOOP      570  '570'
              662  JUMP_BACK           140  'to 140'
              664  POP_BLOCK        
            666_0  COME_FROM_LOOP      132  '132'

 L.1340       666  LOAD_FAST                'is_failure_path'
          668_670  POP_JUMP_IF_FALSE   676  'to 676'

 L.1341       672  LOAD_CONST               False
              674  RETURN_VALUE     
            676_0  COME_FROM           668  '668'

 L.1343       676  LOAD_DEREF               'sim'
              678  LOAD_ATTR                posture
              680  LOAD_ATTR                retrieve_objects_on_exit
              682  STORE_FAST               'retrieve_posture_objects'

 L.1344       684  LOAD_FAST                'retrieve_posture_objects'
              686  LOAD_CONST               None
              688  COMPARE_OP               is-not
          690_692  POP_JUMP_IF_FALSE   748  'to 748'

 L.1345       694  LOAD_FAST                'retrieve_posture_objects'
              696  LOAD_ATTR                transition_retrieval_affordance
              698  LOAD_CONST               None
              700  COMPARE_OP               is-not
          702_704  POP_JUMP_IF_FALSE   748  'to 748'

 L.1350       706  LOAD_GLOBAL              SingleActorAndObjectResolver
              708  LOAD_DEREF               'sim'

 L.1351       710  LOAD_DEREF               'sim'
              712  LOAD_ATTR                posture
              714  LOAD_ATTR                target

 L.1352       716  LOAD_STR                 'PostureScoring'
              718  LOAD_CONST               ('source',)
              720  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              722  STORE_FAST               'resolver'

 L.1353       724  LOAD_FAST                'retrieve_posture_objects'
              726  LOAD_ATTR                objects_to_retrieve
              728  LOAD_METHOD              get_objects
              730  LOAD_FAST                'resolver'
              732  CALL_METHOD_1         1  '1 positional argument'
              734  STORE_FAST               'objects_to_retrieve'

 L.1354       736  LOAD_FAST                'objects_to_retrieve'
          738_740  POP_JUMP_IF_FALSE   748  'to 748'

 L.1355       742  LOAD_CONST               False
              744  LOAD_FAST                'self'
              746  STORE_ATTR               handle_slot_reservations
            748_0  COME_FROM           738  '738'
            748_1  COME_FROM           702  '702'
            748_2  COME_FROM           690  '690'

 L.1358       748  LOAD_FAST                'self'
              750  LOAD_ATTR                handle_slot_reservations
          752_754  POP_JUMP_IF_FALSE  1126  'to 1126'

 L.1361       756  BUILD_LIST_0          0 
              758  STORE_FAST               'object_to_ignore'

 L.1362       760  SETUP_LOOP          866  'to 866'
              762  LOAD_FAST                'self'
              764  LOAD_ATTR                _transition_interactions
              766  LOAD_DEREF               'sim'
              768  BINARY_SUBSCR    
              770  GET_ITER         
            772_0  COME_FROM           842  '842'
            772_1  COME_FROM           800  '800'
            772_2  COME_FROM           788  '788'
              772  FOR_ITER            864  'to 864'
              774  UNPACK_SEQUENCE_2     2 
              776  STORE_FAST               'transition_si'
              778  STORE_FAST               '_'

 L.1363       780  LOAD_GLOBAL              hasattr
              782  LOAD_FAST                'transition_si'
              784  LOAD_STR                 'process'
              786  CALL_FUNCTION_2       2  '2 positional arguments'
          788_790  POP_JUMP_IF_FALSE   772  'to 772'

 L.1364       792  LOAD_FAST                'transition_si'
              794  LOAD_ATTR                process
              796  LOAD_CONST               None
              798  COMPARE_OP               is-not
          800_802  POP_JUMP_IF_FALSE   772  'to 772'

 L.1365       804  LOAD_FAST                'transition_si'
              806  LOAD_ATTR                process
              808  LOAD_ATTR                previous_ico
              810  LOAD_CONST               None
              812  COMPARE_OP               is-not
          814_816  POP_JUMP_IF_FALSE   832  'to 832'

 L.1366       818  LOAD_FAST                'object_to_ignore'
              820  LOAD_METHOD              append
              822  LOAD_FAST                'transition_si'
              824  LOAD_ATTR                process
              826  LOAD_ATTR                previous_ico
              828  CALL_METHOD_1         1  '1 positional argument'
              830  POP_TOP          
            832_0  COME_FROM           814  '814'

 L.1367       832  LOAD_FAST                'transition_si'
              834  LOAD_ATTR                process
              836  LOAD_ATTR                current_ico
              838  LOAD_CONST               None
              840  COMPARE_OP               is-not
          842_844  POP_JUMP_IF_FALSE   772  'to 772'

 L.1368       846  LOAD_FAST                'object_to_ignore'
              848  LOAD_METHOD              append
              850  LOAD_FAST                'transition_si'
              852  LOAD_ATTR                process
              854  LOAD_ATTR                current_ico
              856  CALL_METHOD_1         1  '1 positional argument'
              858  POP_TOP          
          860_862  JUMP_BACK           772  'to 772'
              864  POP_BLOCK        
            866_0  COME_FROM_LOOP      760  '760'

 L.1373       866  LOAD_FAST                'self'
              868  STORE_FAST               'cur_spec'

 L.1374       870  BUILD_LIST_0          0 
              872  STORE_FAST               'slot_manifest_entries'

 L.1375       874  SETUP_LOOP         1014  'to 1014'
              876  LOAD_FAST                'cur_spec'
              878  LOAD_CONST               None
              880  COMPARE_OP               is-not
          882_884  POP_JUMP_IF_FALSE  1012  'to 1012'

 L.1376       886  LOAD_FAST                'cur_spec'
              888  LOAD_FAST                'self'
              890  COMPARE_OP               is-not
          892_894  POP_JUMP_IF_FALSE   910  'to 910'
              896  LOAD_FAST                'cur_spec'
              898  LOAD_ATTR                path
              900  LOAD_CONST               None
              902  COMPARE_OP               is-not
          904_906  POP_JUMP_IF_FALSE   910  'to 910'

 L.1379       908  BREAK_LOOP       
            910_0  COME_FROM           904  '904'
            910_1  COME_FROM           892  '892'

 L.1381       910  LOAD_FAST                'cur_spec'
              912  LOAD_ATTR                handle_slot_reservations
          914_916  POP_JUMP_IF_FALSE   996  'to 996'

 L.1384       918  LOAD_GLOBAL              PostureSpecVariable
              920  LOAD_ATTR                SLOT
              922  LOAD_FAST                'cur_spec'
              924  LOAD_ATTR                var_map
              926  COMPARE_OP               in
          928_930  POP_JUMP_IF_FALSE   972  'to 972'

 L.1385       932  LOAD_FAST                'cur_spec'
              934  LOAD_ATTR                var_map
              936  LOAD_GLOBAL              PostureSpecVariable
              938  LOAD_ATTR                SLOT
              940  BINARY_SUBSCR    
              942  STORE_FAST               'slot_entry'

 L.1386       944  LOAD_FAST                'slot_entry'
              946  LOAD_CONST               None
              948  COMPARE_OP               is-not
          950_952  POP_JUMP_IF_FALSE   996  'to 996'

 L.1387       954  LOAD_FAST                'slot_manifest_entries'
              956  LOAD_METHOD              append
              958  LOAD_FAST                'slot_entry'
              960  CALL_METHOD_1         1  '1 positional argument'
              962  POP_TOP          

 L.1388       964  LOAD_CONST               False
              966  LOAD_FAST                'cur_spec'
              968  STORE_ATTR               handle_slot_reservations
              970  JUMP_FORWARD        996  'to 996'
            972_0  COME_FROM           928  '928'

 L.1390       972  LOAD_GLOBAL              logger
              974  LOAD_METHOD              error
              976  LOAD_STR                 'Trying to reserve a surface with no PostureSpecVariable.SLOT in the var_map.\n    Sim: {}\n    Spec: {}\n    Var_map: {}\n    Transition: {}'

 L.1391       978  LOAD_DEREF               'sim'
              980  LOAD_FAST                'cur_spec'
              982  LOAD_FAST                'cur_spec'
              984  LOAD_ATTR                var_map
              986  LOAD_FAST                'cur_spec'
              988  LOAD_ATTR                _path_spec
              990  LOAD_ATTR                path
              992  CALL_METHOD_5         5  '5 positional arguments'
              994  POP_TOP          
            996_0  COME_FROM           970  '970'
            996_1  COME_FROM           950  '950'
            996_2  COME_FROM           914  '914'

 L.1392       996  LOAD_FAST                'self'
              998  LOAD_ATTR                _path_spec
             1000  LOAD_METHOD              get_next_transition_spec
             1002  LOAD_FAST                'cur_spec'
             1004  CALL_METHOD_1         1  '1 positional argument'
             1006  STORE_FAST               'cur_spec'
         1008_1010  JUMP_BACK           876  'to 876'
           1012_0  COME_FROM           882  '882'
             1012  POP_BLOCK        
           1014_0  COME_FROM_LOOP      874  '874'

 L.1394      1014  LOAD_FAST                'slot_manifest_entries'
         1016_1018  POP_JUMP_IF_FALSE  1126  'to 1126'

 L.1395      1020  LOAD_FAST                'self'
             1022  LOAD_ATTR                final_si
             1024  LOAD_ATTR                animation_context
             1026  STORE_FAST               'final_animation_context'

 L.1396      1028  SETUP_LOOP         1126  'to 1126'
             1030  LOAD_FAST                'slot_manifest_entries'
             1032  GET_ITER         
           1034_0  COME_FROM          1056  '1056'
             1034  FOR_ITER           1124  'to 1124'
             1036  STORE_FAST               'slot_manifest_entry'

 L.1397      1038  LOAD_FAST                'final_animation_context'
             1040  LOAD_ATTR                update_reserved_slots
             1042  LOAD_FAST                'slot_manifest_entry'
             1044  LOAD_DEREF               'sim'

 L.1398      1046  LOAD_FAST                'object_to_ignore'
             1048  LOAD_CONST               ('objects_to_ignore',)
             1050  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
             1052  STORE_FAST               'slot_result'

 L.1399      1054  LOAD_FAST                'slot_result'
         1056_1058  POP_JUMP_IF_TRUE   1034  'to 1034'

 L.1400      1060  LOAD_GLOBAL              set_transition_failure_reason
             1062  LOAD_DEREF               'sim'
             1064  LOAD_GLOBAL              TransitionFailureReasons
             1066  LOAD_ATTR                RESERVATION

 L.1401      1068  LOAD_FAST                'slot_manifest_entry'
             1070  LOAD_ATTR                target
             1072  LOAD_CONST               None
             1074  COMPARE_OP               is-not
         1076_1078  POP_JUMP_IF_FALSE  1088  'to 1088'
             1080  LOAD_FAST                'slot_manifest_entry'
             1082  LOAD_ATTR                target
             1084  LOAD_ATTR                id
             1086  JUMP_FORWARD       1090  'to 1090'
           1088_0  COME_FROM          1076  '1076'
             1088  LOAD_CONST               None
           1090_0  COME_FROM          1086  '1086'
             1090  LOAD_CONST               ('target_id',)
             1092  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
             1094  POP_TOP          

 L.1402      1096  LOAD_DEREF               'cancel_reservations'
             1098  CALL_FUNCTION_0       0  '0 positional arguments'
             1100  POP_TOP          

 L.1403      1102  LOAD_GLOBAL              TestResult
             1104  LOAD_CONST               False
             1106  LOAD_STR                 'Slot Reservation Failed for {}'
             1108  LOAD_METHOD              format
             1110  LOAD_FAST                'self'
             1112  LOAD_ATTR                final_si
             1114  CALL_METHOD_1         1  '1 positional argument'
             1116  CALL_FUNCTION_2       2  '2 positional arguments'
             1118  RETURN_VALUE     
         1120_1122  JUMP_BACK          1034  'to 1034'
             1124  POP_BLOCK        
           1126_0  COME_FROM_LOOP     1028  '1028'
           1126_1  COME_FROM          1016  '1016'
           1126_2  COME_FROM           752  '752'

 L.1405      1126  LOAD_GLOBAL              TestResult
             1128  LOAD_ATTR                TRUE
             1130  RETURN_VALUE     
           1132_0  COME_FROM_EXCEPT     30  '30'

 L.1406      1132  POP_TOP          
             1134  POP_TOP          
             1136  POP_TOP          

 L.1407      1138  LOAD_DEREF               'cancel_reservations'
             1140  CALL_FUNCTION_0       0  '0 positional arguments'
             1142  POP_TOP          

 L.1408      1144  LOAD_GLOBAL              logger
             1146  LOAD_METHOD              exception
             1148  LOAD_STR                 'Exception reserving for transition: {}'
             1150  LOAD_FAST                'self'
             1152  CALL_METHOD_2         2  '2 positional arguments'
             1154  POP_TOP          

 L.1409      1156  RAISE_VARARGS_0       0  'reraise'
             1158  POP_EXCEPT       
             1160  JUMP_FORWARD       1164  'to 1164'
             1162  END_FINALLY      
           1164_0  COME_FROM          1160  '1160'

Parse error at or near `COME_FROM_EXCEPT' instruction at offset 1132_0

    def get_approaching_portal(self):
        next_transition_spec = self._path_spec.get_next_transition_spec(self)
        if next_transition_spec is not None:
            if next_transition_spec.portal_obj is not None:
                return (
                 next_transition_spec.portal_obj, next_transition_spec.portal_id)
        return (None, None)

    def get_transition_route(self, sim, fade_out, lock_out_socials, dest_posture):
        if self.path is None:
            return
        fade_sim_out = fade_out or sim.is_hidden()
        reserve = True
        fire_service = services.get_fire_service()

        def route_callback(distance_left):
            nonlocal fade_sim_out
            nonlocal reserve
            if not self.is_failure_path:
                if distance_left < FollowPath.DISTANCE_TO_RECHECK_STAND_RESERVATION:
                    if sim.routing_component.on_slot is not None:
                        transition_controller = sim.queue.transition_controller
                        excluded_sims = transition_controller.get_transitioning_sims() if transition_controller is not None else ()
                        violators = tuple((violator for violator in sim.routing_component.get_stand_slot_reservation_violators(excluded_sims=excluded_sims) if violator.parent not in excluded_sims))
                        if violators:
                            if transition_controller is not None:
                                transition_controller.derail(DerailReason.WAIT_FOR_BLOCKING_SIMS, sim)
                            return FollowPath.Action.CANCEL
                elif reserve and distance_left < FollowPath.DISTANCE_TO_RECHECK_INUSE:
                    reserve = False
                    portal_obj, portal_id = self.get_approaching_portal()
                    if portal_obj is not None:
                        portal_cost_override = portal_obj.get_portal_cost_override(portal_id)
                        if portal_cost_override == routing.PORTAL_USE_LOCK:
                            transition_controller = sim.queue.transition_controller
                            if transition_controller is not None:
                                transition_controller.derail(DerailReason.WAIT_FOR_BLOCKING_SIMS, sim)
                            return FollowPath.Action.CANCEL
                        if portal_obj.lock_portal_on_use(portal_id):
                            portal_obj.set_portal_cost_override(portal_id, (routing.PORTAL_USE_LOCK), sim=sim)
                    if not self.do_reservation(sim, is_failure_path=(self.is_failure_path)):
                        return FollowPath.Action.CANCEL
            elif not self.is_failure_path:
                if distance_left < TransitionSpec.DISTANCE_TO_FADE_SIM_OUT:
                    if fade_sim_out:
                        fade_sim_out = False
                        dest_posture.sim.fade_out()
                    if lock_out_socials:
                        sim.socials_locked = True
            time_now = services.time_service().sim_now
            if time_now > sim.next_passive_balloon_unlock_time:
                PassiveBalloons.request_passive_balloon(sim, time_now)
            if fire_service.check_for_catching_on_fire(sim):
                if sim.queue.running is not None:
                    sim.queue.running.route_fail_on_transition_fail = False
                return FollowPath.Action.CANCEL
            return FollowPath.Action.CONTINUE

        def should_fade_in():
            if not fade_sim_out:
                return self.path.length() > 0
            return False

        return build_element((maybe(should_fade_in, build_element((lambda _: dest_posture.sim.fade_in()))),
         get_route_element_for_path(sim, (self.path), interaction=(sim.queue.transition_controller.interaction), callback_fn=route_callback,
           handle_failure=True)))


class PathSpec:

    def __init__--- This code section failed: ---

 L.1513         0  LOAD_FAST                'path'
                2  LOAD_CONST               None
                4  COMPARE_OP               is-not
                6  POP_JUMP_IF_FALSE    54  'to 54'
                8  LOAD_FAST                'path_as_posture_specs'
               10  POP_JUMP_IF_FALSE    54  'to 54'

 L.1514        12  BUILD_LIST_0          0 
               14  LOAD_FAST                'self'
               16  STORE_ATTR               _path

 L.1515        18  SETUP_LOOP           92  'to 92'
               20  LOAD_FAST                'path'
               22  GET_ITER         
               24  FOR_ITER             50  'to 50'
               26  STORE_FAST               'posture_spec'

 L.1516        28  LOAD_FAST                'self'
               30  LOAD_ATTR                _path
               32  LOAD_METHOD              append
               34  LOAD_GLOBAL              TransitionSpecCython_create
               36  LOAD_FAST                'self'
               38  LOAD_FAST                'posture_spec'
               40  LOAD_FAST                'var_map'
               42  CALL_FUNCTION_3       3  '3 positional arguments'
               44  CALL_METHOD_1         1  '1 positional argument'
               46  POP_TOP          
               48  JUMP_BACK            24  'to 24'
               50  POP_BLOCK        
               52  JUMP_FORWARD         92  'to 92'
             54_0  COME_FROM            10  '10'
             54_1  COME_FROM             6  '6'

 L.1518        54  LOAD_FAST                'path'
               56  LOAD_FAST                'self'
               58  STORE_ATTR               _path

 L.1519        60  LOAD_FAST                'self'
               62  LOAD_ATTR                _path
               64  LOAD_CONST               None
               66  COMPARE_OP               is-not
               68  POP_JUMP_IF_FALSE    92  'to 92'

 L.1520        70  SETUP_LOOP           92  'to 92'
               72  LOAD_FAST                'self'
               74  LOAD_ATTR                _path
               76  GET_ITER         
               78  FOR_ITER             90  'to 90'
               80  STORE_FAST               'transition_spec'

 L.1521        82  LOAD_FAST                'self'
               84  LOAD_FAST                'transition_spec'
               86  STORE_ATTR               _path_spec
               88  JUMP_BACK            78  'to 78'
               90  POP_BLOCK        
             92_0  COME_FROM_LOOP       70  '70'
             92_1  COME_FROM            68  '68'
             92_2  COME_FROM            52  '52'
             92_3  COME_FROM_LOOP       18  '18'

 L.1523        92  LOAD_FAST                'path_cost'
               94  LOAD_FAST                'self'
               96  STORE_ATTR               cost

 L.1525        98  LOAD_FAST                'destination_spec'
              100  LOAD_FAST                'self'
              102  STORE_ATTR               destination_spec

 L.1529       104  LOAD_CONST               False
              106  LOAD_FAST                'self'
              108  STORE_ATTR               completed_path

 L.1532       110  LOAD_CONST               0
              112  LOAD_FAST                'self'
              114  STORE_ATTR               _path_progress

 L.1535       116  LOAD_FAST                'is_failure_path'
              118  LOAD_FAST                'self'
              120  STORE_ATTR               _is_failure_path

 L.1537       122  LOAD_FAST                'failed_path_type'
              124  LOAD_FAST                'self'
              126  STORE_ATTR               _failed_path_type

 L.1542       128  LOAD_FAST                'allow_tentative'
              130  POP_JUMP_IF_TRUE    168  'to 168'
              132  LOAD_FAST                'final_constraint'
              134  LOAD_CONST               None
              136  COMPARE_OP               is-not
              138  POP_JUMP_IF_FALSE   168  'to 168'
              140  LOAD_FAST                'final_constraint'
              142  LOAD_ATTR                tentative
              144  POP_JUMP_IF_FALSE   168  'to 168'

 L.1543       146  LOAD_GLOBAL              logger
              148  LOAD_ATTR                warn
              150  LOAD_STR                 "PathSpec's final constraint is tentative, this will not work correctly so the constraint will be ignored. This may interfere with slot reservation."

 L.1545       152  LOAD_STR                 'jpollak'
              154  LOAD_CONST               ('owner',)
              156  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              158  POP_TOP          

 L.1546       160  LOAD_CONST               None
              162  LOAD_FAST                'self'
              164  STORE_ATTR               _final_constraint
              166  JUMP_FORWARD        174  'to 174'
            168_0  COME_FROM           144  '144'
            168_1  COME_FROM           138  '138'
            168_2  COME_FROM           130  '130'

 L.1548       168  LOAD_FAST                'final_constraint'
              170  LOAD_FAST                'self'
              172  STORE_ATTR               _final_constraint
            174_0  COME_FROM           166  '166'

 L.1550       174  LOAD_FAST                'spec_constraint'
              176  LOAD_FAST                'self'
              178  STORE_ATTR               _spec_constraint

 L.1552       180  LOAD_CONST               None
              182  LOAD_FAST                'self'
              184  STORE_ATTR               _final_si

Parse error at or near `COME_FROM_LOOP' instruction at offset 92_3

    def __repr__(self):
        if self._path:
            posture_specs = ['({}{}{})'.format(transition_spec.posture_spec, '(R)' if transition_spec.path is not None else '', '(P)' if transition_spec.portal_obj is not None else '') for transition_spec in self._path]
            if self.is_failure_path:
                return 'FAILURE PATH: PathSpec[{}]'.format('->'.join(posture_specs))
            return 'PathSpec[{}]'.format('->'.join(posture_specs))
        return 'PathSpec[Empty]'

    def __bool__(self):
        return bool(self._path)

    @property
    def path(self):
        if self._path is not None:
            return [transition_spec.posture_spec for transition_spec in self._path]
        return []

    @property
    def transition_specs(self):
        return self._path

    @property
    def path_progress(self):
        return self._path_progress

    @property
    def total_cost(self):
        return self.cost + self.routing_cost

    @property
    def routing_cost(self):
        routing_cost = 0
        if self._path is not None:
            for trans_spec in self._path:
                if trans_spec.path is not None:
                    routing_cost += trans_spec.path.length()

        return routing_cost

    @property
    def var_map(self):
        if self._path is not None:
            return self._path[self._path_progress].var_map
        return [{}]

    @property
    def remaining_path(self):
        if self._path is not None:
            if not self.completed_path:
                return [transition_spec.posture_spec for transition_spec in self._path[self._path_progress:]]
        return []

    @property
    def is_failure_path(self):
        return self._is_failure_path

    @property
    def failed_path_type(self):
        return self._failed_path_type

    def remaining_original_transition_specs(self):
        original_transition_specs = []
        if self._path is not None:
            if not self.completed_path:
                for spec in self._path[self._path_progress:]:
                    if spec.sequence_id == SequenceId.DEFAULT:
                        original_transition_specs.append(spec)

        return original_transition_specs

    def remaining_transition_specs(self):
        transition_specs = []
        if self._path is not None:
            if not self.completed_path:
                for spec in self._path[self._path_progress:]:
                    transition_specs.append(spec)

        return transition_specs

    @property
    def previous_posture_spec(self):
        previous_progress = self._path_progress - 1
        if previous_progress < 0 or previous_progress >= len(self._path):
            return
        return self._path[previous_progress].posture_spec

    @property
    def previous_transition_spec(self):
        previous_progress = self._path_progress - 1
        if previous_progress < 0 or previous_progress >= len(self._path):
            return
        return self._path[previous_progress]

    @property
    def final_constraint(self):
        if self._final_constraint is not None:
            return self._final_constraint
        if self._path is None:
            return
        for transition_spec in reversed(self._path):
            if transition_spec.final_constraint is not None:
                return transition_spec.final_constraint

    @property
    def final_routing_location(self):
        for transition_spec in reversed(self._path):
            if transition_spec.path is not None:
                return transition_spec.path.final_location

    @property
    def spec_constraint(self):
        return self._spec_constraint

    def advance_path(self):
        new_progress = self._path_progress + 1
        if new_progress < len(self._path):
            self._path_progress = new_progress
        else:
            self.completed_path = True

    def get_spec(self):
        return self._path[self._path_progress].posture_spec

    def get_transition_spec(self):
        return self._path[self._path_progress]

    def get_transition_should_reserve(self):
        for i, transition_spec in enumerate_reversed(self._path):
            if transition_spec.path is not None:
                return self._path_progress >= i

        return True

    def get_next_transition_spec(self, transition_spec):
        if self._path is None:
            return
        for index, cur_transition_spec in enumerate(self._path):
            if cur_transition_spec is transition_spec:
                next_index = index + 1
                if next_index < len(self._path):
                    return self._path[next_index]

    def check_validity(self, sim):
        transition_specs = self.transition_specs
        if transition_specs is None:
            return True
        for transition_spec in self.remaining_transition_specs():
            for interaction, _ in transition_spec.transition_interactions(sim):
                if interaction is not None and interaction.is_finishing:
                    return False

        return True

    def cleanup_path_spec(self, sim):
        transition_specs = self.transition_specs
        if transition_specs is None:
            return
        cleanup_portal_costs = not services.current_zone().is_zone_shutting_down
        for transition_spec in transition_specs:
            if transition_spec.created_posture_state is not None:
                for aspect in transition_spec.created_posture_state.aspects:
                    if aspect not in sim.posture_state.aspects:
                        aspect.reset()

                transition_spec.created_posture_state = None
            else:
                if transition_spec.path is not None:
                    transition_spec.path.remove_intended_location_from_quadtree()
                portal_obj = transition_spec.portal_obj
                if cleanup_portal_costs:
                    if portal_obj is not None and sim not in portal_obj.get_users():
                        portal_obj.clear_portal_cost_override((transition_spec.portal_id), sim=sim)
            for interaction, _ in transition_spec.transition_interactions(sim):
                if interaction is not None and interaction not in sim.queue and interaction not in sim.si_state:
                    interaction.release_liabilities()

    def insert_transition_specs_at_index(self, i, new_specs):
        self._path[i:i] = new_specs

    def combine(self, *path_specs):
        full_path = self._path
        cost = self.cost
        final_constraint = self.final_constraint
        spec_constraint = self.spec_constraint
        is_failure_path = False
        for path_spec in path_specs:
            if not path_spec._path:
                raise AssertionError('Trying to combine two paths when one of them is None!')
            else:
                if full_path[-1].posture_spec != path_spec._path[0].posture_spec:
                    raise AssertionError("Trying to combine two paths that don't have a common node on the ends {} != {}.\nThis may be caused by handles being generated for complete paths.".format(self.path[-1], path_spec.path[0]))
                if full_path[-1].mobile and path_spec._path[0].path is not None:
                    full_path = list(itertools.chain(full_path, path_spec._path))
                else:
                    if full_path[-1].locked_params:
                        path_spec._path[0].locked_params = full_path[-1].locked_params
                    if full_path[-1].portal_obj:
                        path_spec._path[0].portal_obj = full_path[-1].portal_obj
                        path_spec._path[0].portal_id = full_path[-1].portal_id
                    if full_path[-1].path is not None:
                        path_spec._path[0].path = full_path[-1].path
                full_path = list(itertools.chain(full_path[:-1], path_spec._path))
            cost = cost + path_spec.cost
            final_constraint = path_spec.final_constraint
            spec_constraint = path_spec.spec_constraint
            is_failure_path = is_failure_path or path_spec.is_failure_path

        return PathSpec(full_path, cost, None, (path_spec.destination_spec), final_constraint,
          spec_constraint, path_as_posture_specs=False, is_failure_path=is_failure_path)

    def get_carry_sim_merged_path_spec(self):
        if not any((n.body.target is not None and n.body.target.is_sim for n in self.path)):
            return self
        other_index = None
        for index, node in enumerate(self.path):
            node_target = node.body.target
            if node_target is None:
                continue
            for _other_index, other_node in enumerate(self.path[index + 1:]):
                if node == other_node:
                    other_index = _other_index + index + 1
                    break

            if other_index:
                break

        if other_index:
            full_path = self._path[:index] + self._path[other_index:]
            return PathSpec(full_path, (self.cost), (self.var_map), (self.destination_spec), (self.final_constraint), (self.spec_constraint),
              path_as_posture_specs=False, is_failure_path=(self._is_failure_path), failed_path_type=(self._failed_path_type))
        return self

    def get_stand_to_carry_sim_direct_path_spec(self):
        if self is EMPTY_PATH_SPEC or self.path[0].body.posture_type is not SIM_DEFAULT_POSTURE_TYPE:
            return self
        sim_stand_posture_index = 0
        sim_carried_posture_index = 0
        sim_carried_posture_type = PostureTuning.SIM_CARRIED_POSTURE
        for index, node in enumerate(self.path):
            node_posture_type = node.body.posture_type
            if node_posture_type is SIM_DEFAULT_POSTURE_TYPE:
                sim_stand_posture_index = index
            elif node_posture_type is sim_carried_posture_type:
                sim_carried_posture_index = index
                break

        if sim_carried_posture_index - sim_stand_posture_index > 1:
            full_path = self._path[:1] + self._path[sim_carried_posture_index:]
            return PathSpec(full_path, (self.cost), (self.var_map), (self.destination_spec), (self.final_constraint), (self.spec_constraint),
              path_as_posture_specs=False, is_failure_path=(self._is_failure_path), failed_path_type=(self._failed_path_type))
        return self

    def edge_exists(self, spec_a_type, spec_b_type):
        for cur_spec, next_spec in zip(self.path, self.path[1:]):
            cur_spec_type = cur_spec.body.posture_type
            next_spec_type = next_spec.body.posture_type
            if cur_spec_type == spec_a_type and next_spec_type == spec_b_type:
                return True

        return False

    def get_failure_reason_and_object_id(self):
        if self._path is not None:
            for trans_spec in self._path:
                if trans_spec.path is not None and trans_spec.path.is_route_fail():
                    return (
                     trans_spec.path.nodes.plan_failure_path_type,
                     trans_spec.path.nodes.plan_failure_object_id)

        return (None, None)

    def create_route_nodes(self, path, portal_obj=None, portal_id=None):
        final_node = self._path[-1]
        if not final_node.mobile:
            raise ValueError('PathSpec: Trying to turn a non-mobile node into a route: {}'.format(self._path))
        else:
            if portal_obj is None:
                posture_specs = (
                 final_node.posture_spec,)
            else:
                posture_spec_enter, posture_spec_exit = portal_obj.get_posture_change(portal_id, final_node.posture_spec)
                if posture_spec_enter is posture_spec_exit:
                    posture_specs = (posture_spec_enter,)
                else:
                    posture_specs = (
                     posture_spec_enter, posture_spec_exit)
            if len(posture_specs) == 1:
                new_transition_spec = TransitionSpecCython_create(self, posture_specs[0], final_node.var_map, SequenceId.DEFAULT, portal_obj, portal_id)
            else:
                new_transition_spec = TransitionSpecCython_create(self, posture_specs[0], final_node.var_map)
            new_transition_spec.set_path(path, None)
            prev_posture_type = cython.cast(TransitionSpecCython, self._path[-1]).posture_spec.body.posture_type
            next_posture_type = new_transition_spec.posture_spec.body.posture_type
            return prev_posture_type.is_available_transition(next_posture_type) or False
        self._path.append(new_transition_spec)
        for posture_spec in posture_specs[1:]:
            new_transition_spec = TransitionSpecCython_create(self, posture_spec, final_node.var_map, SequenceId.DEFAULT, portal_obj, portal_id)
            self._path.append(new_transition_spec)

        return True

    def attach_route_and_params(self, path, locked_params, final_constraint, reverse=False):
        if reverse:
            sequence = reversed(self._path)
        else:
            sequence = self._path
        previous_spec = None
        route_spec = None
        locked_param_spec = None
        carry_spec = None
        for transition_spec in sequence:
            if not transition_spec.posture_spec.body.posture_type.unconstrained:
                if route_spec is None:
                    route_spec = previous_spec if previous_spec is not None else transition_spec
                else:
                    if reverse:
                        if previous_spec is not None:
                            locked_param_spec = previous_spec
                        else:
                            locked_param_spec = transition_spec
                        break
                    elif carry_spec is None and transition_spec.is_carry:
                        carry_spec = transition_spec
                    if route_spec is None and not reverse:
                        if transition_spec.posture_spec.body.target is not None:
                            route_spec = previous_spec if previous_spec is not None else transition_spec
                        else:
                            if previous_spec is not None:
                                if (previous_spec.posture_spec.carry.target is not None) != (transition_spec.posture_spec.carry.target is not None):
                                    route_spec = previous_spec
                previous_spec = transition_spec

        if locked_param_spec is None:
            locked_param_spec = transition_spec
        if route_spec is None:
            route_spec = transition_spec
        route_spec.set_path(path, final_constraint)
        locked_param_spec.set_locked_params(locked_params)
        if carry_spec is not None:
            carry_spec.set_locked_params(locked_params)

    def adjust_route_for_sim_inventory(self):
        spec_to_destination = None
        spec_for_pick_up_route = None
        for transition_spec in reversed(self._path):
            if transition_spec.path is not None:
                if transition_spec.path.portal_obj is not None:
                    return
                    if spec_to_destination is None:
                        spec_to_destination = transition_spec
                else:
                    spec_for_pick_up_route = transition_spec
                    break

        if spec_to_destination is not None:
            if spec_for_pick_up_route is not None:
                if spec_to_destination.path.length_squared() > 0:
                    spec_to_destination.transfer_route_to(spec_for_pick_up_route)

    def unlock_portals(self, sim):
        if self._path is not None:
            for transition_spec in self._path:
                portal_obj = transition_spec.portal_obj
                if portal_obj is not None:
                    portal_obj.clear_portal_cost_override((transition_spec.portal_id), sim=sim)

    def finalize(self, sim):
        if self.path is not None:
            if len(self.path) > 0:
                final_destination = self.path[-1]
                final_var_map = self._path[-1].var_map
                interaction_target = final_var_map[PostureSpecVariable.INTERACTION_TARGET]
                if interaction_target is not None:
                    for path_node in self._path:
                        if PostureSpecVariable.INTERACTION_TARGET not in path_node.var_map:
                            continue
                        for obj in final_destination.get_core_objects():
                            if obj.id != interaction_target.id:
                                continue
                            new_interaction_target = interaction_target.resolve_retarget(obj)
                            path_node.var_map += {PostureSpecVariable.INTERACTION_TARGET: new_interaction_target}

                carry_target = final_var_map[PostureSpecVariable.CARRY_TARGET]
                if carry_target is not None:
                    if carry_target.is_in_sim_inventory(sim=sim):
                        self.adjust_route_for_sim_inventory()
                body_posture_target = sim.posture.target
                if body_posture_target is not None and sim.posture.mobile:
                    if self.path[0].body.target != body_posture_target:
                        start_spec = sim.posture_state.get_posture_spec(self.var_map)
                        self._path.insert(0, TransitionSpecCython_create(self, start_spec, self.var_map))

    def process_transitions(self, start_spec, get_new_sequence_fn):
        new_transitions = []
        transitions_len = len(self._path)
        prev_transition = None
        for i, transition in enumerate(self._path):
            k = i + 1
            next_transition = None
            if k < transitions_len:
                next_transition = self._path[k]
            new_sequence = get_new_sequence_fn(i, prev_transition, transition, next_transition)
            if self.validate_new_sequence(prev_transition, new_sequence, next_transition, get_new_sequence_fn, start_spec):
                if new_sequence:
                    new_transitions.extend(new_sequence)
                else:
                    new_transitions.append(transition)
                if len(new_transitions) >= 1:
                    prev_transition = new_transitions[-1]

        self._path = new_transitions

    def validate_new_sequence(self, prev_transition, new_sequence, next_transition, get_new_sequence_fn, start_spec):
        validate = services.current_zone().posture_graph_service._can_transition_between_nodes
        if new_sequence:
            if prev_transition is None:
                if not validate(start_spec, new_sequence[0].posture_spec):
                    self.handle_validate_error_msg(start_spec, new_sequence[0].posture_spec, get_new_sequence_fn, start_spec)
                    return False
        elif not validate(prev_transition.posture_spec, new_sequence[0].posture_spec):
            self.handle_validate_error_msg(prev_transition.posture_spec, new_sequence[0].posture_spec, get_new_sequence_fn, start_spec)
            return False
        if len(new_sequence) > 1:
            for curr_trans, next_trans in zip(new_sequence[0:], new_sequence[1:]):
                if not validate(curr_trans.posture_spec, next_trans.posture_spec):
                    self.handle_validate_error_msg(curr_trans.posture_spec, next_trans.posture_spec, get_new_sequence_fn, start_spec)
                    return False

        if next_transition:
            validate(new_sequence[-1].posture_spec, next_transition.posture_spec) or self.handle_validate_error_msg(new_sequence[-1].posture_spec or prev_transition.posture_spec, next_transition.posture_spec, get_new_sequence_fn, start_spec)
            return False
        else:
            if prev_transition is None:
                if next_transition:
                    if not validate(start_spec, next_transition.posture_spec):
                        self.handle_validate_error_msg(start_spec, next_transition.posture_spec, get_new_sequence_fn, start_spec)
                        return False
            if prev_transition:
                if next_transition:
                    if not validate(prev_transition.posture_spec, next_transition.posture_spec):
                        self.handle_validate_error_msg(prev_transition.posture_spec, next_transition.posture_spec, get_new_sequence_fn, start_spec)
                        return False
            return True

    def handle_validate_error_msg(self, posture_spec_a, posture_spec_b, mod_function, start_spec):
        logger.error('--- FAIL: validate_new_sequence({}) ---', mod_function.__name__)
        logger.error('Start Spec: {}', start_spec)
        logger.error('Full Path:')
        for index, posture_spec in enumerate(self.path):
            logger.error('    {}: {}', index, posture_spec)

        logger.error('Failure:', posture_spec_a, posture_spec_b)
        logger.error('    posture_spec_a: {}', posture_spec_a)
        logger.error('    posture_spec_b: {}', posture_spec_b)

    @staticmethod
    def remove_non_surface_to_surface_transitions(i, prev_transition_spec, transition_spec, next_transition_spec):
        prev_transition = prev_transition_spec.posture_spec if prev_transition_spec is not None else None
        transition = transition_spec.posture_spec
        next_transition = next_transition_spec.posture_spec if next_transition_spec is not None else None
        if next_transition is not None:
            if prev_transition is None or prev_transition.body.posture_type.mobile:
                if transition.surface.target is None:
                    if next_transition.body.posture_type.mobile:
                        if next_transition.surface.target is not None:
                            if prev_transition is None or prev_transition.carry == next_transition.carry or next_transition is None:
                                return ()
        return (
         transition_spec,)

    @staticmethod
    def remove_extra_mobile_transitions(i, prev_transition_spec, transition_spec, next_transition_spec):
        prev_transition = prev_transition_spec.posture_spec if prev_transition_spec is not None else None
        transition = transition_spec.posture_spec
        next_transition = next_transition_spec.posture_spec if next_transition_spec is not None else None
        if prev_transition is None or next_transition is None:
            return (
             transition_spec,)
        if prev_transition.carry == next_transition.carry:
            if prev_transition.surface == next_transition.surface:
                if prev_transition.body.target == next_transition.body.target:
                    if transition.body.posture_type == next_transition.body.posture_type:
                        return ()
        if prev_transition.surface.target != transition.surface.target or transition.surface.target != next_transition.surface.target:
            return (transition_spec,)
        if prev_transition.carry.target != transition.carry.target or transition.carry.target != next_transition.carry.target:
            return (transition_spec,)
        if not prev_transition.body.posture_type.mobile:
            if next_transition_spec.path is not None:
                return (
                 transition_spec,)
        if prev_transition.body.posture_type.mobile:
            if transition.body.posture_type.mobile:
                if next_transition.body.posture_type.mobile:
                    if services.current_zone().posture_graph_service._can_transition_between_nodes(prev_transition, next_transition):
                        return ()
        return (
         transition_spec,)

    def flag_slot_reservations(self):
        for prev_transition_spec, cur_transition_spec in zip(self._path, self._path[1:]):
            if prev_transition_spec.sequence_id != cur_transition_spec.sequence_id:
                continue
            else:
                if not cur_transition_spec.posture_spec.surface.target:
                    continue
                if prev_transition_spec.is_carry:
                    if not cur_transition_spec.is_carry:
                        prev_transition_spec.handle_slot_reservations = True
            if prev_transition_spec.targets_empty_slot or cur_transition_spec.targets_empty_slot:
                prev_transition_spec.handle_slot_reservations = True

    def generate_transition_interactions(self, sim, final_si, transition_success):
        if self._path is None:
            return True
            self._final_si = final_si
            transition_aops = OrderedDict()
            context = InteractionContext(sim, (InteractionContext.SOURCE_POSTURE_GRAPH),
              (final_si.priority),
              run_priority=(final_si.run_priority),
              insert_strategy=(QueueInsertStrategy.NEXT),
              must_run_next=True)
            preload_outfit_set = set()
            exit_change = sim.posture_state.body.saved_exit_clothing_change
            if exit_change is not None:
                preload_outfit_set.add(exit_change)
            posture_graph_service = services.posture_graph_service()
            for i, cur_transition_spec in enumerate((self._path[1:]), start=1):
                cur_posture_spec = cur_transition_spec.posture_spec
                outfit_change = cur_transition_spec.posture_spec.body.posture_type.outfit_change
                if outfit_change:
                    entry_change = outfit_change.get_on_entry_outfit(final_si, sim_info=(sim.sim_info))
                    if entry_change is not None:
                        preload_outfit_set.add(entry_change)
                portal_obj = cur_transition_spec.portal_obj
                if portal_obj is not None:
                    portal_id = cur_transition_spec.portal_id
                    portal_entry_outfit = portal_obj.get_on_entry_outfit(final_si, portal_id, sim_info=(sim.sim_info))
                    if portal_entry_outfit is not None:
                        preload_outfit_set.add(portal_entry_outfit)
                    portal_exit_outfit = portal_obj.get_on_exit_outfit(final_si, portal_id, sim_info=(sim.sim_info))
                    if portal_exit_outfit is not None:
                        preload_outfit_set.add(portal_exit_outfit)
                for prev_transition_spec in reversed(self._path[:i]):
                    if prev_transition_spec.sequence_id == cur_transition_spec.sequence_id:
                        prev_posture_spec = prev_transition_spec.posture_spec
                        break
                else:
                    prev_posture_spec = None

                aop_list = []
                var_map = cur_transition_spec.var_map
                edge_info = posture_graph_service.get_edge(prev_posture_spec, cur_posture_spec,
                  return_none_on_failure=True)
                aop = None
                if edge_info is not None:
                    for operation in edge_info.operations:
                        op_aop = operation.associated_aop(sim, var_map)
                        if op_aop is not None:
                            aop = op_aop

                if aop is not None:
                    aop_list.append((aop, var_map))
                transition_aops[i] = aop_list

            added_final_si = False
            for i, aops in reversed(list(transition_aops.items())):
                for aop, var_map in aops:
                    final_valid_combinables = final_si.get_combinable_interactions_with_safe_carryables()
                    existing_si_set = {final_si} if not final_valid_combinables else set(itertools.chain((final_si,), final_valid_combinables))
                    for existing_si in existing_si_set:
                        if added_final_si or aop.is_equivalent_to_interaction(existing_si):
                            si = existing_si
                            if existing_si is final_si:
                                added_final_si = True
                            break
                    else:
                        execute_result = aop.interaction_factory(context)
                        if not execute_result:
                            return False
                        si = execute_result.interaction

                    self._path[i].add_transition_interaction(sim, si, var_map)
                    si.add_preload_outfit_changes(preload_outfit_set)

                if not aops:
                    self._path[i].add_transition_interaction(sim, None, self._path[i].var_map)

            if not added_final_si:
                if transition_success:
                    self._path[-1].add_transition_interaction(sim, final_si, self._path[-1].var_map)
                    final_si.add_preload_outfit_changes(preload_outfit_set)
        else:
            current_position_on_active_lot = preload_outfit_set or services.active_lot().is_position_on_lot(sim.position)
            if current_position_on_active_lot:
                if not sim.is_outside:
                    level = sim.intended_location.routing_surface.secondary_id
                    if not sim.intended_position_on_active_lot or build_buy.is_location_outside(sim.intended_position, level):
                        sim.preload_outdoor_streetwear_change(final_si, preload_outfit_set)
        sim.set_preload_outfits(preload_outfit_set)
        return True


with reload.protected(globals()):
    EMPTY_PATH_SPEC = PathSpec(None, 0, {}, None, None, None)
    NO_CONNECTIVITY = Connectivity(EMPTY_PATH_SPEC, None, None, None)

@cython.cclass
class NodeData:
    __slots__ = ('canonical_node', 'predecessors', 'successors')

    def __init__(self, canonical_node, predecessors=(), successors=()):
        self.canonical_node = canonical_node
        self.predecessors = set(predecessors)
        self.successors = set(successors)


@cython.cfunc
@cython.exceptval(check=False)
def NodeData_create(canonical_node: PostureSpec) -> NodeData:
    res = cython.declare(NodeData, NodeData.__new__(NodeData))
    res.canonical_node = canonical_node
    res.predecessors = set()
    res.successors = set()
    return res


@cython.cclass
class PostureGraph:
    _nodes = cython.declare(dict, visibility='readonly')
    _subsets = cython.declare(object, visibility='readonly')
    _quadtrees = cython.declare(object, visibility='readonly')
    proxy_sim = cython.declare(object, visibility='public')
    cached_sim_nodes = cython.declare(object, visibility='readonly')
    cached_vehicle_nodes = cython.declare(set, visibility='readonly')
    cached_postures_to_object_ids = cython.declare(object, visibility='readonly')
    _mobile_nodes_at_none = cython.declare(set, visibility='readonly')
    _mobile_nodes_at_none_no_carry = cython.declare(set, visibility='readonly')
    _mobile_nodes_at_none_carry = cython.declare(set, visibility='readonly')

    def __init__(self):
        self._nodes = {}
        self._subsets = defaultdict(set)
        self._quadtrees = defaultdict(sims4.geometry.QuadTree)
        self.proxy_sim = None
        self.cached_sim_nodes = weakref.WeakKeyDictionary()
        self.cached_vehicle_nodes = set()
        self.cached_postures_to_object_ids = defaultdict(set)
        self._mobile_nodes_at_none = set()
        self._mobile_nodes_at_none_no_carry = set()
        self._mobile_nodes_at_none_carry = set()

    def __len__(self):
        return len(self._nodes)

    def __iter__(self):
        return iter(self._nodes)

    def __bool__(self):
        return bool(self._nodes)

    def __contains__(self, key):
        logger.warn('Please call contains({0}) instead of [{0}] for optimal performance.', key, owner='jdimailig')
        return self.contains(key)

    def items(self):
        return self._nodes.items()

    @cython.cfunc
    @cython.inline
    @cython.exceptval(check=False)
    def get_node(self, key: PostureSpec) -> NodeData:
        key = self._get_transform_key(key)
        return self._nodes[key]

    @cython.cfunc
    @cython.inline
    def set_node(self, key: PostureSpec, value: NodeData):
        self._nodes[key] = value

    @cython.cfunc
    @cython.inline
    def contains(self, key: PostureSpec) -> cython.bint:
        key = self._get_transform_key(key)
        return key in self._nodes

    @cython.cfunc
    @cython.exceptval(check=False)
    def get(self, key: PostureSpec, default=None) -> NodeData:
        key = self._get_transform_key(key)
        if key in self._nodes:
            return self._nodes[key]
        return default

    @cython.cfunc
    @cython.exceptval(check=False)
    def _get_transform_key(self, key: PostureSpec) -> PostureSpec:
        body = key.body
        if body is not None:
            body_target = body.target
            if body_target is not None:
                if body_target.is_sim:
                    posture_type = body.posture_type
                    key = key.clone(body=(PostureAspectBody_create(posture_type, self.proxy_sim)))
        return key

    @property
    def nodes(self):
        return self._nodes.keys()

    @property
    def vehicle_nodes(self):
        return self.cached_vehicle_nodes

    def cache_global_mobile_nodes(self):
        self._mobile_nodes_at_none.update(_DEFAULT_MOBILE_NODES)
        self._mobile_nodes_at_none_no_carry.update(_MOBILE_NODES_AT_NONE)
        self._mobile_nodes_at_none_carry.update(_MOBILE_NODES_AT_NONE_CARRY)

    def setup_provided_mobile_nodes(self):
        object_manager = services.object_manager()
        for obj in object_manager.get_posture_providing_objects():
            self.add_mobile_posture_provider_nodes(obj)

    @property
    def all_mobile_nodes_at_none(self):
        return self._mobile_nodes_at_none

    @property
    def all_mobile_nodes_at_none_no_carry(self):
        return self._mobile_nodes_at_none_no_carry

    @property
    def all_mobile_nodes_at_none_carry(self):
        return self._mobile_nodes_at_none_carry

    @property
    def mobile_posture_providing_affordances(self):
        object_manager = services.object_manager()
        affordances = set()
        for obj in object_manager.get_posture_providing_objects():
            affordances.update(obj.provided_mobile_posture_affordances)

        return affordances

    @cython.cfunc
    @cython.exceptval(check=False)
    def get_canonical_node(self, node: PostureSpec) -> PostureSpec:
        node_data = self.get(node)
        if node_data is None:
            return node
        return node_data.canonical_node

    @cython.cfunc
    @cython.locals(successor=PostureSpec, predecessor=PostureSpec)
    def remove_node(self, node: PostureSpec):
        target = node.get_body_target() or node.get_surface_target()
        if target is not None:
            if target != PostureSpecVariable.ANYTHING:
                self.remove_from_quadtree(target, node)
                body_type = node.body.posture_type
                if body_type.is_vehicle:
                    self.cached_vehicle_nodes.remove(node)
        for key in get_subset_keys(node):
            if key in self._subsets:
                self._subsets[key].remove(node)
                if not self._subsets[key]:
                    del self._subsets[key]

        node_data = self.get_node(node)
        for successor in node_data.successors:
            self.get_node(successor).predecessors.remove(node)

        for predecessor in node_data.predecessors:
            self.get_node(predecessor).successors.remove(node)

        del self._nodes[node]

    def remove_from_quadtree(self, obj, node: PostureSpec):
        level = obj.level
        if level is None:
            return
        quadtree = self._quadtrees[level]
        quadtree.remove(node)

    @cython.cfunc
    def add_to_quadtree(self, obj, node: PostureSpec):
        level = obj.level
        if level is None:
            return
        bounding_box = obj.get_bounding_box()
        quadtree = self._quadtrees[level]
        quadtree.insert(node, bounding_box)

    @cython.cfunc
    def add_successor(self, node: PostureSpec, successor: PostureSpec):
        node = self.get_canonical_node(node)
        successor = self.get_canonical_node(successor)
        self._add_node(node)
        self.get_node(node).successors.add(successor)
        self._add_node(successor)
        self.get_node(successor).predecessors.add(node)

    @cython.cfunc
    def _add_node(self, node: PostureSpec):
        if self.contains(node):
            return
            self.set_node(node, NodeData_create(node))
            target = None
            body = node.body
            if body is not None:
                target = body.target
            if target is None:
                surface = node.surface
                if surface is not None:
                    target = surface.target
        elif target is not None:
            if target != PostureSpecVariable.ANYTHING:
                if not target.is_sim:
                    self.add_to_quadtree(target, node)
                    body_type = node.body.posture_type
                    if body_type.is_vehicle:
                        self.cached_vehicle_nodes.add(node)
        for key in get_subset_keys(node):
            self._subsets[key].add(node)

    @cython.ccall
    def get_successors(self, node: PostureSpec, default=DEFAULT):
        node_data = self.get(node)
        if node_data is not None:
            return node_data.successors
        if default is DEFAULT:
            raise KeyError('Node {} not in posture graph.'.format(node))
        return default

    @cython.ccall
    def get_predecessors(self, node: PostureSpec, default=DEFAULT):
        node_data = self.get(node)
        if node_data is not None:
            return node_data.predecessors
        if default is DEFAULT:
            raise KeyError('Node {} not in posture graph.'.format(node))
        return default

    @caches.cached(key=(lambda _, constraint: constraint))
    def nodes_matching_constraint_geometry(self, constraint):
        if any((sub_constraint.routing_surface is None or sub_constraint.geometry is None for sub_constraint in constraint)):
            return
        nodes = set()
        for sub_constraint in constraint:
            floor = sub_constraint.routing_surface.secondary_id
            quadtree = self._quadtrees[floor]
            for polygon in sub_constraint.geometry.polygon:
                lower_bound, upper_bound = polygon.bounds()
                bounding_box = sims4.geometry.QtRect(sims4.math.Vector2(lower_bound.x, lower_bound.z), sims4.math.Vector2(upper_bound.x, upper_bound.z))
                nodes.update(quadtree.query(bounding_box))

        nodes |= self._subsets[('body_target and slot_target', None)]
        return nodes

    def nodes_for_object_gen(self, obj):
        if obj.is_part:
            owner = obj.part_owner
            nodes = self._subsets.get(('body_target', owner), set()) | self._subsets.get(('surface_target', owner), set())
            for node in nodes:
                if node.body_target is obj or node.surface_target is obj:
                    yield node

        else:
            if obj.is_sim:
                obj = self.proxy_sim
            nodes = self._subsets.get(('body_target', obj), set()) | self._subsets.get(('surface_target', obj), set())
            yield from nodes

    def _get_nodes_internal_gen(self, nodes):
        for node in nodes:
            if node.body_target is not None and node.body_target.is_sim:
                yield from self.sim_carry_nodes_gen(node)
            else:
                yield node

    @cython.locals(spec=PostureSpec)
    def get_matching_nodes_gen--- This code section failed: ---

 L.3008         0  LOAD_GLOBAL              set
                2  CALL_FUNCTION_0       0  '0 positional arguments'
                4  STORE_FAST               'nodes'

 L.3009       6_8  SETUP_LOOP          314  'to 314'
               10  LOAD_FAST                'specs'
               12  GET_ITER         
            14_16  FOR_ITER            312  'to 312'
               18  STORE_FAST               'spec'

 L.3010        20  LOAD_FAST                'slot_types'
               22  POP_JUMP_IF_FALSE   156  'to 156'

 L.3011        24  LOAD_GLOBAL              set
               26  CALL_FUNCTION_0       0  '0 positional arguments'
               28  STORE_FAST               'spec_nodes'

 L.3015        30  SETUP_LOOP          234  'to 234'
               32  LOAD_FAST                'slot_types'
               34  GET_ITER         
               36  FOR_ITER            152  'to 152'
               38  STORE_FAST               'slot_type'

 L.3016        40  LOAD_GLOBAL              PostureAspectSurface
               42  LOAD_FAST                'spec'
               44  LOAD_METHOD              get_surface_target
               46  CALL_METHOD_0         0  '0 positional arguments'
               48  LOAD_FAST                'slot_type'
               50  LOAD_FAST                'spec'
               52  LOAD_METHOD              get_slot_target
               54  CALL_METHOD_0         0  '0 positional arguments'
               56  CALL_FUNCTION_3       3  '3 positional arguments'
               58  STORE_FAST               'surface'

 L.3017        60  LOAD_FAST                'spec'
               62  LOAD_ATTR                clone
               64  LOAD_GLOBAL              DEFAULT
               66  LOAD_GLOBAL              DEFAULT
               68  LOAD_FAST                'surface'
               70  LOAD_CONST               ('body', 'carry', 'surface')
               72  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
               74  STORE_FAST               'slot_type_spec'

 L.3019        76  LOAD_GLOBAL              get_subset_keys
               78  LOAD_FAST                'slot_type_spec'
               80  CALL_FUNCTION_1       1  '1 positional argument'
               82  STORE_FAST               'keys'

 L.3020        84  LOAD_FAST                'keys'
               86  POP_JUMP_IF_TRUE     96  'to 96'

 L.3021        88  LOAD_ASSERT              AssertionError
               90  LOAD_STR                 'No keys returned for a specific slot type!'
               92  CALL_FUNCTION_1       1  '1 positional argument'
               94  RAISE_VARARGS_1       1  'exception instance'
             96_0  COME_FROM            86  '86'

 L.3023        96  LOAD_CLOSURE             'self'
               98  BUILD_TUPLE_1         1 
              100  LOAD_DICTCOMP            '<code_object <dictcomp>>'
              102  LOAD_STR                 'PostureGraph.get_matching_nodes_gen.<locals>.<dictcomp>'
              104  MAKE_FUNCTION_8          'closure'
              106  LOAD_FAST                'keys'
              108  GET_ITER         
              110  CALL_FUNCTION_1       1  '1 positional argument'
              112  STORE_FAST               'subsets'

 L.3024       114  LOAD_GLOBAL              functools
              116  LOAD_METHOD              reduce
              118  LOAD_GLOBAL              operator
              120  LOAD_ATTR                and_
              122  LOAD_GLOBAL              sorted
              124  LOAD_FAST                'subsets'
              126  LOAD_METHOD              values
              128  CALL_METHOD_0         0  '0 positional arguments'
              130  LOAD_GLOBAL              len
              132  LOAD_CONST               ('key',)
              134  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              136  CALL_METHOD_2         2  '2 positional arguments'
              138  STORE_FAST               'intersection'

 L.3025       140  LOAD_FAST                'spec_nodes'
              142  LOAD_METHOD              update
              144  LOAD_FAST                'intersection'
              146  CALL_METHOD_1         1  '1 positional argument'
              148  POP_TOP          
              150  JUMP_BACK            36  'to 36'
              152  POP_BLOCK        
              154  JUMP_FORWARD        234  'to 234'
            156_0  COME_FROM            22  '22'

 L.3027       156  LOAD_GLOBAL              get_subset_keys
              158  LOAD_FAST                'spec'
              160  CALL_FUNCTION_1       1  '1 positional argument'
              162  STORE_FAST               'keys'

 L.3028       164  LOAD_FAST                'keys'
              166  POP_JUMP_IF_TRUE    186  'to 186'

 L.3030       168  LOAD_DEREF               'self'
              170  LOAD_METHOD              _get_nodes_internal_gen
              172  LOAD_DEREF               'self'
              174  LOAD_ATTR                nodes
              176  CALL_METHOD_1         1  '1 positional argument'
              178  GET_YIELD_FROM_ITER
              180  LOAD_CONST               None
              182  YIELD_FROM       
              184  POP_TOP          
            186_0  COME_FROM           166  '166'

 L.3032       186  LOAD_CLOSURE             'self'
              188  BUILD_TUPLE_1         1 
              190  LOAD_DICTCOMP            '<code_object <dictcomp>>'
              192  LOAD_STR                 'PostureGraph.get_matching_nodes_gen.<locals>.<dictcomp>'
              194  MAKE_FUNCTION_8          'closure'
              196  LOAD_FAST                'keys'
              198  GET_ITER         
              200  CALL_FUNCTION_1       1  '1 positional argument'
              202  STORE_FAST               'subsets'

 L.3033       204  LOAD_GLOBAL              set
              206  LOAD_GLOBAL              functools
              208  LOAD_METHOD              reduce
              210  LOAD_GLOBAL              operator
              212  LOAD_ATTR                and_
              214  LOAD_GLOBAL              sorted
              216  LOAD_FAST                'subsets'
              218  LOAD_METHOD              values
              220  CALL_METHOD_0         0  '0 positional arguments'
              222  LOAD_GLOBAL              len
              224  LOAD_CONST               ('key',)
              226  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              228  CALL_METHOD_2         2  '2 positional arguments'
              230  CALL_FUNCTION_1       1  '1 positional argument'
              232  STORE_FAST               'spec_nodes'
            234_0  COME_FROM           154  '154'
            234_1  COME_FROM_LOOP       30  '30'

 L.3036       234  LOAD_FAST                'spec'
              236  LOAD_METHOD              get_body_target
              238  CALL_METHOD_0         0  '0 positional arguments'
              240  JUMP_IF_TRUE_OR_POP   248  'to 248'
              242  LOAD_FAST                'spec'
              244  LOAD_METHOD              get_surface_target
              246  CALL_METHOD_0         0  '0 positional arguments'
            248_0  COME_FROM           240  '240'
              248  STORE_FAST               'target'

 L.3037       250  LOAD_FAST                'target'
              252  LOAD_CONST               None
              254  LOAD_GLOBAL              PostureSpecVariable
              256  LOAD_ATTR                ANYTHING
              258  BUILD_TUPLE_2         2 
              260  COMPARE_OP               in
          262_264  POP_JUMP_IF_FALSE   300  'to 300'
              266  LOAD_FAST                'constraint'
          268_270  POP_JUMP_IF_FALSE   300  'to 300'

 L.3038       272  LOAD_DEREF               'self'
              274  LOAD_METHOD              nodes_matching_constraint_geometry
              276  LOAD_FAST                'constraint'
              278  CALL_METHOD_1         1  '1 positional argument'
              280  STORE_FAST               'quadtree_subset'

 L.3039       282  LOAD_FAST                'quadtree_subset'
              284  LOAD_CONST               None
              286  COMPARE_OP               is-not
          288_290  POP_JUMP_IF_FALSE   300  'to 300'

 L.3041       292  LOAD_FAST                'spec_nodes'
              294  LOAD_FAST                'quadtree_subset'
              296  INPLACE_AND      
              298  STORE_FAST               'spec_nodes'
            300_0  COME_FROM           288  '288'
            300_1  COME_FROM           268  '268'
            300_2  COME_FROM           262  '262'

 L.3043       300  LOAD_FAST                'nodes'
              302  LOAD_METHOD              update
              304  LOAD_FAST                'spec_nodes'
              306  CALL_METHOD_1         1  '1 positional argument'
              308  POP_TOP          
              310  JUMP_BACK            14  'to 14'
              312  POP_BLOCK        
            314_0  COME_FROM_LOOP        6  '6'

 L.3045       314  LOAD_DEREF               'self'
              316  LOAD_METHOD              _get_nodes_internal_gen
              318  LOAD_FAST                'nodes'
              320  CALL_METHOD_1         1  '1 positional argument'
              322  GET_YIELD_FROM_ITER
              324  LOAD_CONST               None
              326  YIELD_FROM       
              328  POP_TOP          

Parse error at or near `LOAD_DICTCOMP' instruction at offset 100

    def sim_carry_nodes_gen(self, carried_node):
        sim_info_manager = services.sim_info_manager()
        for sim in sim_info_manager.instanced_sims_gen():
            sim_node = self.cached_sim_nodes.get(sim)
            if sim_node is None:
                sim_node = carried_node.clone(body=(PostureAspectBody(carried_node.body_posture, sim)))
                self.cached_sim_nodes[sim] = sim_node
            yield sim_node

    def vehicle_nodes_gen(self):
        for node in self.cached_vehicle_nodes:
            yield node

    def add_mobile_posture_provider_nodes(self, new_obj):
        for mobile_posture in new_obj.provided_mobile_posture_types:
            add_nodes = False if self.cached_postures_to_object_ids[mobile_posture] else True
            if new_obj.id not in self.cached_postures_to_object_ids[mobile_posture]:
                self.cached_postures_to_object_ids[mobile_posture].add(new_obj.id)
            if add_nodes:
                mobile_node_at_none = mobile_posture.skip_route or get_origin_spec(mobile_posture)
                self._mobile_nodes_at_none.add(mobile_node_at_none)
                self._mobile_nodes_at_none_no_carry.add(mobile_node_at_none)
                if mobile_posture._supports_carry:
                    mobile_node_at_none_carry = get_origin_spec_carry(mobile_posture)
                    self._mobile_nodes_at_none.add(mobile_node_at_none_carry)
                    self._mobile_nodes_at_none_carry.add(mobile_node_at_none_carry)

    def remove_mobile_posture_provider_nodes(self, old_obj):
        for mobile_posture in old_obj.provided_mobile_posture_types:
            if old_obj.id in self.cached_postures_to_object_ids[mobile_posture]:
                self.cached_postures_to_object_ids[mobile_posture].remove(old_obj.id)
            remove_nodes = False if self.cached_postures_to_object_ids[mobile_posture] else True
            if remove_nodes:
                mobile_node_at_none = mobile_posture.skip_route or get_origin_spec(mobile_posture)
                self._mobile_nodes_at_none.remove(mobile_node_at_none)
                self._mobile_nodes_at_none_no_carry.remove(mobile_node_at_none)
                if mobile_posture._supports_carry:
                    mobile_node_at_none_carry = get_origin_spec_carry(mobile_posture)
                    self._mobile_nodes_at_none.remove(mobile_node_at_none_carry)
                    self._mobile_nodes_at_none_carry.remove(mobile_node_at_none_carry)

    def clear(self):
        self._nodes.clear()
        self._subsets.clear()
        self._quadtrees.clear()
        self.cached_vehicle_nodes.clear()
        self.cached_postures_to_object_ids.clear()
        self._mobile_nodes_at_none.clear()
        self._mobile_nodes_at_none_carry.clear()
        self._mobile_nodes_at_none_no_carry.clear()
        self.proxy_sim = None


class EdgeInfo(namedtuple('_EdgeInfo', ['operations', 'validate', 'species_to_cost_dict'])):
    __slots__ = ()

    def cost(self, species):
        if species in self.species_to_cost_dict:
            return self.species_to_cost_dict[species]
        return self.species_to_cost_dict[PostureOperation.DEFAULT_COST_KEY]


def _get_species_to_aop_tunable_mapping(*, description):
    return TunableMapping(description=description, key_type=TunableEnumEntry(description='\n            The species that this affordance is intended for.\n            ',
      tunable_type=Species,
      default=(Species.HUMAN),
      invalid_enums=(
     Species.INVALID,)),
      value_type=TunableReference(description='\n            The default interaction to push for Sims of this species.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      pack_safe=True))


class PostureGraphService(Service):

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, value):
        for affordance in PostureGraphService.POSTURE_PROVIDING_AFFORDANCES:
            posture_type = affordance.provided_posture_type
            if posture_type.mobile and posture_type.unconstrained and affordance not in PostureGraphService.SIM_DEFAULT_AFFORDANCES:
                logger.error(' Posture Providing Affordance {} provides a\n                mobile, unconstrained, posture but is not tied to an object.\n                You likely want to add this to the Provided Mobile Posture\n                Affordances on the object this posture requires. For example,\n                Oceans and Pools provide swim and float postures.\n                ',
                  affordance, owner='rmccord')

    SIM_DEFAULT_AFFORDANCES = _get_species_to_aop_tunable_mapping(description="\n        The interactions for Sims' default postures. These interactions are used\n        to kickstart Sims; are pushed on them after resets, and are used as the\n        default cancel replacement interaction.\n        ")
    SIM_DEFAULT_AFFORDANCES_OVERRIDES = TunableList(description="\n        Override interactions for Sims' default postures. If applicable, the first interaction whose tests pass will\n        be used instead of the default affordance for the species. \n        ",
      tunable=TunableTuple(species=TunableEnumEntry(description='\n                The species that this affordance is intended for.\n                ',
      tunable_type=Species,
      default=(Species.HUMAN),
      invalid_enums=(
     Species.INVALID,)),
      age=TunableEnumEntry(description='\n                The age that this affordance is intended for.\n                ',
      tunable_type=Age,
      default=(Age.ADULT)),
      tests=(TunableTestSet()),
      affordance=TunableReference(description='\n                The default interaction to push for Sims of this species and age, with the given tests.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      pack_safe=True)))
    SWIM_DEFAULT_AFFORDANCES = _get_species_to_aop_tunable_mapping(description="\n        The interactions for Sims' default swimming postures. These interactions\n        are used as a Sim's default affordance while in a pool.\n        ")
    CARRIED_DEFAULT_AFFORDANCES = _get_species_to_aop_tunable_mapping(description='\n        The interactions for Sims\' default "Be Carried" postures. These\n        interactions are used whenever Sims are transitioning into such\n        postures.\n        ')
    POSTURE_PROVIDING_AFFORDANCES = TunableList(description='\n        Additional posture providing interactions that are not tuned on any\n        object. This allows us to add additional postures for sims to use.\n        Example: Kneel on floor.\n        ',
      tunable=TunableReference(description='\n            Interaction that provides a posture.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      pack_safe=True),
      verify_tunable_callback=_verify_tunable_callback)
    INCREMENTAL_REBUILD_THRESHOLD = Tunable(description='\n        The posture graph will do a full rebuild when exiting build/buy if\n        there have been more than this number of modifications to the posture\n        graph. Otherwise, an incremental rebuild will be done, which is much\n        faster for small numbers of operations, but slower for large numbers.\n        Talk to a gameplay engineer before changing this value.\n        ',
      tunable_type=int,
      default=10)

    def __init__(self):
        self._graph = PostureGraph()
        self._edge_info = {}
        self._goal_costs = {}
        self._zone_loaded = False
        self._disable_graph_update_count = 0
        self._incremental_update_count = None
        self._mobile_posture_objects_quadtree = sims4.geometry.QuadTree()

    @property
    def has_built_for_zone_spin_up(self):
        return self._zone_loaded

    def _clear(self):
        self._graph.clear()
        self._edge_info.clear()

    def rebuild(self):
        if indexed_manager.capture_load_times:
            time_stamp = time.time()
        if self._disable_graph_update_count == 0:
            self._clear()
            self.build()
        if indexed_manager.capture_load_times:
            time_spent_rebuilding = time.time() - time_stamp
            indexed_manager.object_load_times['posture_graph'] = time_spent_rebuilding

    def disable_graph_building(self):
        self._disable_graph_update_count += 1

    def enable_graph_building(self):
        self._disable_graph_update_count -= 1

    @staticmethod
    def get_infant_default_affordance_override_posture_type():
        for data in PostureGraphService.SIM_DEFAULT_AFFORDANCES_OVERRIDES:
            if data.age == Age.INFANT:
                return data.affordance.provided_posture_type

    @staticmethod
    def get_default_affordance(species=Species.HUMAN, sim_info=None):
        if sim_info is not None:
            for data in PostureGraphService.SIM_DEFAULT_AFFORDANCES_OVERRIDES:
                if data.species == species:
                    if not data.age or data.age == sim_info.age:
                        resolver = SingleSimResolver(sim_info)
                        if data.tests.run_tests(resolver):
                            return data.affordance

        if species in PostureGraphService.SIM_DEFAULT_AFFORDANCES:
            return PostureGraphService.SIM_DEFAULT_AFFORDANCES[species]
        logger.warn("Requesting default affordance for {} and it doesn't exist in PostureGraphService.SIM_DEFAULT_AFFORDANCES, using human instead.", species)
        return PostureGraphService.SIM_DEFAULT_AFFORDANCES[Species.HUMAN]

    @staticmethod
    def get_default_posture(species=Species.HUMAN, sim_info=None):
        return PostureGraphService.get_default_affordance(species, sim_info).provided_posture_type

    @staticmethod
    def get_default_aop(species=Species.HUMAN, sim_info=None):
        if SIM_DEFAULT_AOPS is None:
            _cache_global_sim_default_values()
        if sim_info is not None:
            key = (
             species, sim_info.age)
            if key in SIM_TESTED_AOPS:
                for data in SIM_TESTED_AOPS[key]:
                    resolver = SingleSimResolver(sim_info)
                    if data['tests'].run_tests(resolver):
                        return data['aop']

        if species in SIM_DEFAULT_AOPS:
            return SIM_DEFAULT_AOPS[species]
        logger.warn("Requesting default aop for {} and it doesn't exist in PostureGraphService.SIM_DEFAULT_AOPS, using human instead.")
        return SIM_DEFAULT_AOPS[Species.HUMAN]

    @staticmethod
    def get_default_swim_affordance(species):
        if species in PostureGraphService.SWIM_DEFAULT_AFFORDANCES:
            return PostureGraphService.SWIM_DEFAULT_AFFORDANCES[species]
        logger.warn("Requesting default swim affordance for {} and it doesn't exist in PostureGraphService.SWIM_DEFAULT_AFFORDANCES, using human instead.", species)
        return PostureGraphService.SWIM_DEFAULT_AFFORDANCES[Species.HUMAN]

    @staticmethod
    def get_swim_aop(species):
        if SIM_SWIM_AOPS is None:
            _cache_global_sim_default_values()
        if species in SIM_SWIM_AOPS:
            return SIM_SWIM_AOPS[species]
        logger.warn("Requesting default swim aop for {} and it doesn't exist in PostureGraphService.SIM_SWIM_AOPS, using human instead.")
        return SIM_SWIM_AOPS[Species.HUMAN]

    def on_enter_buildbuy(self):
        self._incremental_update_count = 0

    def on_exit_buildbuy(self):
        if self._incremental_update_count is None:
            logger.warn('Posture graph incremental update count is None when exiting build/buy. This can only happen if there is a mismatch between calls to on_enter_buildbuy() and on_exit_buildbuy(). The posture graph will be rebuilt just to be cautious.', owner='bhill')
            self.rebuild()
        else:
            if self._incremental_update_count > self.INCREMENTAL_REBUILD_THRESHOLD:
                logger.info('Exiting build/buy and executing full posture graph rebuild.')
                self.rebuild()
            else:
                logger.info('Exiting build/buy and the incremental posture graph rebuild was good enough. (Only {} changes made)', self._incremental_update_count)
        self._incremental_update_count = None

    def start(self):
        self._clear()
        if SIM_DEFAULT_AOPS is None:
            _cache_global_sim_default_values()
        self.build()

    @contextmanager
    def __reload_context__(oldobj, newobj):
        try:
            yield
        finally:
            if isinstance(oldobj, PostureGraphService):
                _cache_global_sim_default_values()
                newobj._graph.cache_global_mobile_nodes()

    def on_teardown(self):
        self._zone_loaded = False
        object_manager = services.object_manager()
        object_manager.unregister_callback(CallbackTypes.ON_OBJECT_ADD, self._on_object_added)
        object_manager.unregister_callback(CallbackTypes.ON_OBJECT_REMOVE, self._on_object_deleted)

    @cython.profile(True)
    def build_during_zone_spin_up(self):
        skip_cache = caches.skip_cache
        caches.skip_cache = False
        self._zone_loaded = True
        self.rebuild()
        object_manager = services.object_manager()
        object_manager.register_callback(CallbackTypes.ON_OBJECT_ADD, self._on_object_added)
        object_manager.register_callback(CallbackTypes.ON_OBJECT_REMOVE, self._on_object_deleted)
        caches.skip_cache = skip_cache

    def add_node(self, node: PostureSpec, operations):
        nodes = []
        next_node = node
        for operation in operations:
            nodes.append(next_node)
            next_node = operation.apply(next_node)
            if next_node is None:
                return

        if not PostureGraphService._validate_node_for_graph(next_node):
            return
        graph = cython.cast(PostureGraph, self._graph)
        if next_node in graph.get_successors(node, ()):
            return
        species_to_cost_dict = None
        validate = CallableTestList()
        for source_node, operation in zip(nodes, operations):
            if species_to_cost_dict is None:
                species_to_cost_dict = operation.cost(source_node)
            else:
                temp_cost_dict = operation.cost(source_node)
                current_default_cost = species_to_cost_dict[PostureOperation.DEFAULT_COST_KEY]
                new_default_cost = temp_cost_dict[PostureOperation.DEFAULT_COST_KEY]
                for species in species_to_cost_dict:
                    if species in temp_cost_dict:
                        species_to_cost_dict[species] += temp_cost_dict.pop(species)
                    else:
                        species_to_cost_dict[species] += new_default_cost

                for species in temp_cost_dict:
                    species_to_cost_dict[species] = current_default_cost + temp_cost_dict.pop(species)

            validate.append(operation.get_validator(source_node))

        edge_info = EdgeInfo(operations, validate, species_to_cost_dict)
        graph.add_successor(node, next_node)
        self._edge_info[(node, next_node)] = edge_info
        return next_node

    def update_generic_sim_carry_node(self, sim, from_init=False):
        if self._graph.proxy_sim is None:
            if from_init:
                if sim.is_selectable:
                    self._graph.proxy_sim = SimPostureNode(sim)
                    return True
            return False
        return True

    def _obj_triggers_posture_graph_update(self, obj):
        if obj.is_sim:
            return
        else:
            if self._disable_graph_update_count:
                return False
            return obj.is_valid_posture_graph_object or False
        if obj.parts == []:
            return False
        return True

    def on_mobile_posture_object_added_during_zone_spinup(self, new_obj):
        self._on_object_added(new_obj)

    @with_caches
    def _on_object_added(self, new_obj):
        if not new_obj.is_part:
            if not self._obj_triggers_posture_graph_update(new_obj):
                return
            if self._incremental_update_count is not None:
                self._incremental_update_count += 1
                if self._incremental_update_count > self.INCREMENTAL_REBUILD_THRESHOLD:
                    return
            objects = set()

            def add_object_to_build(obj_to_add):
                if obj_to_add.parts:
                    objects.update(obj_to_add.parts)
                else:
                    objects.add(obj_to_add)

            add_object_to_build(new_obj)
            for child in new_obj.children:
                if child.is_valid_posture_graph_object:
                    add_object_to_build(child)

            open_set = set()
            closed_set = set(self._graph.nodes)
            all_ancestors = (set().union)(*(obj.ancestry_gen() for obj in objects))
            for ancestor in all_ancestors:
                if not ancestor.parts:
                    open_set.update(self._graph.nodes_for_object_gen(ancestor))

            closed_set -= open_set
            if new_obj.is_sim:
                if self._graph.proxy_sim is None:
                    for closed_node in tuple(closed_set):
                        body_posture = closed_node.body.posture_type
                        body_target = closed_node.body.target
                        can_transition_to_carry = not body_posture.mobile or body_posture.mobile and body_target is None
                        if can_transition_to_carry and body_posture.is_available_transition(PostureTuning.SIM_CARRIED_POSTURE):
                            closed_set.discard(closed_node)

        else:
            for closed_node in tuple(closed_set):
                if closed_node.body.posture_type is PostureTuning.SIM_CARRIED_POSTURE:
                    closed_set.discard(closed_node)

        provided_posture_aops = []
        mobile_affordances_and_postures = [(affordance, affordance.provided_posture_type) for affordance in new_obj.provided_mobile_posture_affordances]
        for affordance, mobile_posture in mobile_affordances_and_postures:
            if len(self._graph.cached_postures_to_object_ids[mobile_posture]) == 1:
                provided_posture_aops.append(AffordanceObjectPair(affordance, None, affordance, None))

        if provided_posture_aops:
            body_operations_dict = PostureGraphService.get_body_operation_dict(provided_posture_aops)
            for source_posture_type, destination_posture_type in Posture._posture_transitions:
                body_operation = body_operations_dict.get(destination_posture_type)
                if body_operation is None:
                    continue
                if source_posture_type is not SIM_DEFAULT_POSTURE_TYPE:
                    if source_posture_type not in body_operations_dict:
                        continue
                    new_node = self.add_node(get_origin_spec(source_posture_type), (body_operation,))
                    if new_node is not None:
                        open_set.add(new_node)
                    if source_posture_type._supports_carry:
                        new_node = self.add_node(get_origin_spec_carry(source_posture_type), (body_operation,))
                        if new_node is not None:
                            open_set.add(new_node)

        for node, obj in itertools.product(self._graph.all_mobile_nodes_at_none, objects):
            ops = []
            self._expand_and_append_node_object(node, obj, ops)
            for operations in ops:
                new_node = self.add_node(node, operations)
                if new_node is not None and new_node not in closed_set:
                    open_set.add(new_node)

        with _object_addition(new_obj):
            self._build(open_set, closed_set)

    def get_proxied_sim(self):
        if self._graph.proxy_sim is None:
            return
        return self._graph.proxy_sim.sim_proxied

    @with_caches
    def _on_object_deleted(self, obj):
        if not self._obj_triggers_posture_graph_update(obj):
            return
        else:
            if not obj.remove_children_from_posture_graph_on_delete:
                return
            if self._incremental_update_count is not None:
                self._incremental_update_count += 1
                if self._incremental_update_count > self.INCREMENTAL_REBUILD_THRESHOLD:
                    return
        graph = cython.cast(PostureGraph, self._graph)
        for node in graph.nodes_for_object_gen(obj):
            for successor in graph.get_successors(node, ()):
                self._edge_info.pop((node, successor), None)

            for predecessor in graph.get_predecessors(node, ()):
                self._edge_info.pop((predecessor, node), None)

            graph.remove_node(node)

        for mobile_posture in obj.provided_mobile_posture_types:
            if len(graph.cached_postures_to_object_ids[mobile_posture]) == 1:
                mobile_node_at_none = get_origin_spec(mobile_posture)
                graph.remove_node(mobile_node_at_none)
                if mobile_posture._supports_carry:
                    mobile_node_at_none_carry = get_origin_spec_carry(mobile_posture)
                    graph.remove_node(mobile_node_at_none_carry)

    @contextmanager
    @with_caches
    def object_moving(self, obj):
        if not self._zone_loaded or obj.is_sim:
            yield
            return
        if obj.routing_component is not None:
            if obj.routing_component.is_moving:
                sims = obj.get_users(sims_only=True)
                for sim in sims:
                    posture_state = sim.posture_state
                    if posture_state is not None and posture_state.body.target is obj:
                        posture_state.body.invalidate_slot_constraints()

                yield
                return
        if obj.is_valid_posture_graph_object:
            self._on_object_deleted(obj)
        try:
            yield
        finally:
            if obj.is_valid_posture_graph_object:
                self._on_object_added(obj)

    def _expand_node(self, node: PostureSpec):
        ops = []
        for obj in node.get_relevant_objects():
            if not obj.is_valid_posture_graph_object:
                continue
            if obj.is_sim:
                self._expand_and_append_node_sim(node, obj, ops)
            else:
                self._expand_and_append_node_object(node, obj, ops)
            if obj.is_part and obj.routing_surface.type == SurfaceType.SURFACETYPE_OBJECT and obj.part_owner.provided_routing_surface is not None:
                for mobile_posture_operation in obj.part_owner.provided_mobile_posture_operations:
                    ops.append((mobile_posture_operation,))

        ops.append((SIM_DEFAULT_OPERATION,))
        if node.body_posture.supports_swim:
            ops.append((SIM_SWIM_OPERATION,))
        if node.surface is not None:
            ops.append((PostureOperation.FORGET_SURFACE_OP, SIM_DEFAULT_OPERATION))
            if node.body.posture_type.mobile:
                ops.append((PostureOperation.FORGET_SURFACE_OP,))
        if node.body.posture_type._supports_carry:
            ops.append((PostureOperation.STANDARD_PICK_UP_OP,))
        if node.body.posture_type._supports_infant:
            if SIM_INFANT_OVERRIDE_DEFAULT_OPERATION is not None:
                ops.append((SIM_INFANT_OVERRIDE_DEFAULT_OPERATION,))
        return ops

    @staticmethod
    def get_body_operation_dict(posture_aops):
        body_operations_dict = {}
        for aop in posture_aops:
            body_operation = aop.get_provided_posture_change()
            if body_operation is None:
                continue
            body_op_posture_type = body_operation.posture_type
            if body_op_posture_type in body_operations_dict:
                for species, aop in body_operation.all_associated_aops_gen():
                    body_operations_dict[body_op_posture_type].add_associated_aop(species, aop)

            else:
                body_operations_dict[body_operation.posture_type] = body_operation

        return body_operations_dict

    @caches.cached(maxsize=None)
    def _expand_object_surface(self, obj, surface):
        ops = []
        if surface is not None:
            put_down = PostureOperation.PutDownObjectOnSurface(PostureSpecVariable.POSTURE_TYPE_CARRY_NOTHING, surface, PostureSpecVariable.SLOT, PostureSpecVariable.CARRY_TARGET)
            ops.append((put_down,))
            surface_ops = self._expand_surface(surface)
            ops.extend(surface_ops)
        posture_aops = obj.get_posture_aops_gen()
        if obj.is_part:
            posture_aops = filter(obj.supports_affordance, posture_aops)
        body_operations_dict = self.get_body_operation_dict(posture_aops)
        for body_operation in body_operations_dict.values():
            if not obj.parts or body_operation.posture_type.unconstrained:
                ops.append((body_operation,))
                if surface is not None:
                    ops.extend(((body_operation,) + ops for ops in surface_ops))

        if obj.inventory_component is not None:
            at_surface = PostureOperation.TargetAlreadyInSlot(None, obj, None)
            ops.append((at_surface,))
        return ops

    def _expand_and_append_node_object(self, node, obj, out_ops):
        surface = None
        if obj.is_surface():
            surface = obj
        else:
            parent = obj.parent
            if parent is not None:
                if parent.is_surface():
                    surface = parent
            else:
                out_ops.extend(self._expand_object_surface(obj, surface))
                if surface is not obj:
                    return
                if node.body_target not in (None, obj):
                    return
                species_to_affordances = enumdict(Species)
                species_to_disallowed_ages = defaultdict(set)
                for species, affordance in self.SIM_DEFAULT_AFFORDANCES.items():
                    if obj.is_part:
                        if not obj.supports_posture_type(affordance.provided_posture_type):
                            continue
                    species_to_affordances[species] = AffordanceObjectPair(affordance, obj, affordance, None)
                    species_to_disallowed_ages[species] = event_testing.test_utils.get_disallowed_ages(affordance)

                return species_to_affordances or None
            body_operation = PostureOperation.BodyTransition(SIM_DEFAULT_POSTURE_TYPE,
              species_to_affordances,
              target=obj,
              disallowed_ages=species_to_disallowed_ages)
            out_ops.append((body_operation,))

    def _expand_and_append_node_sim(self, node, obj, out_ops):
        logger.assert_log(obj.is_sim, '_expand_and_append_node_sim can only be called with a Sim object')
        species_to_affordances = enumdict(Species)
        species_to_disallowed_ages = defaultdict(set)
        for species, affordance in self.CARRIED_DEFAULT_AFFORDANCES.items():
            if not obj.supports_posture_type(affordance.provided_posture_type):
                continue
            species_to_affordances[species] = AffordanceObjectPair(affordance, obj, affordance, None)
            species_to_disallowed_ages[species] = event_testing.test_utils.get_disallowed_ages(affordance)

        if not species_to_affordances:
            return
        else:
            if obj.age not in species_to_disallowed_ages[obj.species]:
                return
            return self.update_generic_sim_carry_node(obj, from_init=True) or None
        body_operation = PostureOperation.BodyTransition((PostureTuning.SIM_CARRIED_POSTURE), species_to_affordances,
          target=(self._graph.proxy_sim),
          disallowed_ages=species_to_disallowed_ages)
        out_ops.append((body_operation,))

    def _expand_surface(self, surface):
        ops = []
        existing_carryable_slotted_target = PostureOperation.TargetAlreadyInSlot(PostureSpecVariable.CARRY_TARGET, surface, PostureSpecVariable.SLOT)
        ops.append((existing_carryable_slotted_target,))
        existing_noncarryable_slotted_target = PostureOperation.TargetAlreadyInSlot(PostureSpecVariable.SLOT_TARGET, surface, PostureSpecVariable.SLOT)
        ops.append((existing_noncarryable_slotted_target,))
        empty_surface = PostureOperation.TargetAlreadyInSlot(None, surface, PostureSpecVariable.SLOT)
        ops.append((empty_surface,))
        at_surface = PostureOperation.TargetAlreadyInSlot(None, surface, None)
        ops.append((at_surface,))
        forget_surface = PostureOperation.FORGET_SURFACE_OP
        ops.append((forget_surface,))
        return ops

    def _validate_node_for_graph(node):
        target = node.body.target
        if target is not None:
            if not node.body.posture_type.mobile:
                surface = node.surface
                if surface is None or surface.target is None:
                    target_parent = target.parent
                    if target_parent is not None:
                        if not target.is_set_as_head:
                            parent_slot = target.parent_slot
                            if parent_slot:
                                if parent_slot.slot_types:
                                    if target.slot_type_set:
                                        possible_slot_types = parent_slot.slot_types.intersection(target.slot_type_set.slot_types)
                                        if not any((slot_type.implies_slotted_object_has_surface for slot_type in possible_slot_types)):
                                            return True
                            return False
                    if target_parent is None and target.is_surface():
                        return False
                elif surface is not None:
                    target_parent = target.parent
                    if target_parent:
                        if surface.target == target_parent:
                            parent_slot = target.parent_slot
                            if not ((parent_slot is None or parent_slot).slot_types and target.slot_type_set):
                                return False
                            possible_slot_types = parent_slot.slot_types.intersection(target.slot_type_set.slot_types)
                            if not any((slot_type.implies_slotted_object_has_surface for slot_type in possible_slot_types)):
                                return False
        return True

    _validate_node_for_graph = staticmethod(caches.cached(maxsize=4096)(_validate_node_for_graph))

    def _build(self, open_set, closed_set):
        while open_set:
            node = open_set.pop()
            closed_set.add(node)
            for operations in self._expand_node(node):
                new_node = self.add_node(node, operations)
                if new_node is not None and new_node not in closed_set:
                    open_set.add(new_node)

        caches.clear_all_caches()

    @with_caches
    def build(self):
        open_set = set(STAND_AT_NONE_NODES)
        closed_set = set()
        self._graph.cache_global_mobile_nodes()
        self._graph.setup_provided_mobile_nodes()
        self._edge_info[(STAND_AT_NONE, STAND_AT_NONE)] = EdgeInfo((SIM_DEFAULT_OPERATION,), (lambda *_, **__: True), 0)
        provided_posture_aops = [AffordanceObjectPair(affordance, None, affordance, None) for affordance in self.POSTURE_PROVIDING_AFFORDANCES]
        mobile_affordances = self._graph.mobile_posture_providing_affordances
        provided_posture_aops.extend([AffordanceObjectPair(affordance, None, affordance, None) for affordance in mobile_affordances])
        body_operations_dict = PostureGraphService.get_body_operation_dict(provided_posture_aops)
        for source_posture_type, destination_posture_type in Posture._posture_transitions:
            body_operation = body_operations_dict.get(destination_posture_type)
            if body_operation is None:
                continue
            if source_posture_type is not SIM_DEFAULT_POSTURE_TYPE:
                if source_posture_type not in body_operations_dict:
                    continue
            new_node = self.add_node(get_origin_spec(source_posture_type), (body_operation,))
            if new_node is not None:
                open_set.add(new_node)
            if source_posture_type._supports_carry:
                new_node = self.add_node(get_origin_spec_carry(source_posture_type), (body_operation,))
                if new_node is not None:
                    open_set.add(new_node)

        self._build(open_set, closed_set)

    def nodes_matching_constraint_geometry(self, constraint):
        return self._graph.nodes_matching_constraint_geometry(constraint)

    @property
    def all_mobile_nodes_at_none_no_carry(self):
        return self._graph.all_mobile_nodes_at_none_no_carry

    @property
    def all_mobile_nodes_at_none_carry(self):
        return self._graph.all_mobile_nodes_at_none_carry

    @property
    def all_mobile_nodes_at_none(self):
        return self._graph.all_mobile_nodes_at_none

    @property
    def mobile_posture_providing_affordances(self):
        return self._graph.mobile_posture_providing_affordances

    def add_mobile_posture_provider(self, obj):
        self._graph.add_mobile_posture_provider_nodes(obj)

    def remove_mobile_posture_provider(self, obj):
        self._graph.remove_mobile_posture_provider_nodes(obj)

    def distance_fn(self, sim, var_map, interaction, ensemble, curr_node, next_node):
        if isinstance(curr_node, _MobileNode):
            curr_node = curr_node.graph_node
        elif isinstance(next_node, _MobileNode):
            next_node = next_node.graph_node
        else:
            if curr_node == next_node:
                return 0
                cost = 0
                next_body = next_node.body
                next_body_posture = next_node.body_posture
                next_body_target = next_body.target
                if gsi_handlers.posture_graph_handlers.archiver.enabled:
                    cost_str_list = []
                if next_body_target is not None:
                    if next_body_target.is_sim:
                        guaranteed_si_count = sum((1 for _ in next_body_target.si_state.all_guaranteed_si_gen()))
                        if guaranteed_si_count:
                            cost += guaranteed_si_count * PostureScoring.CARRYING_SIM_BUSY_PENALTY
                            if gsi_handlers.posture_graph_handlers.archiver.enabled:
                                cost_str_list.append('CARRYING_SIM_BUSY_PENALTY: {}'.format(PostureScoring.CARRYING_SIM_BUSY_PENALTY))
                        relationship_tracker = next_body_target.relationship_tracker
                        if not relationship_tracker.has_bit(sim.sim_id, RelationshipGlobalTuning.CAREGIVER_RELATIONSHIP_BIT):
                            cost += PostureScoring.CARRYING_SIM_NON_CAREGIVER_PENALTY
                            if gsi_handlers.posture_graph_handlers.archiver.enabled:
                                cost_str_list.append('CARRYING_SIM_NON_CAREGIVER_PENALTY: {}'.format(PostureScoring.CARRYING_SIM_NON_CAREGIVER_PENALTY))
                        relationship_tracker.has_bit(sim.sim_id, RelationshipGlobalTuning.HAS_MET_RELATIONSHIP_BIT) or cost += PostureScoring.CARRYING_SIM_HAS_NOT_MET_PENALTY
                        if gsi_handlers.posture_graph_handlers.archiver.enabled:
                            cost_str_list.append('CARRYING_SIM_HAS_NOT_MET_PENALTY: {}'.format(PostureScoring.CARRYING_SIM_HAS_NOT_MET_PENALTY))
                        if ensemble is not None:
                            ensemble.is_sim_in_ensemble(next_body_target) or cost += PostureScoring.CARRYING_SIM_NOT_IN_ENSEMBLE_PENALTY
                            if gsi_handlers.posture_graph_handlers.archiver.enabled:
                                cost_str_list.append('CARRYING_SIM_NOT_IN_ENSEMBLE_PENALTY: {}'.format(PostureScoring.CARRYING_SIM_NOT_IN_ENSEMBLE_PENALTY))
            else:
                may_reserve_posture_target(sim, next_body_posture, next_body_target) or cost += PostureScoring.OBJECT_RESERVED_PENALTY
            if gsi_handlers.posture_graph_handlers.archiver.enabled:
                cost_str_list.append('OBJECT_RESERVED_PENALTY: {}'.format(PostureScoring.OBJECT_RESERVED_PENALTY))
        edge_info, _ = self._get_edge_info(curr_node, next_node)
        edge_cost = edge_info.cost(sim.species)
        cost += edge_cost
        if gsi_handlers.posture_graph_handlers.archiver.enabled:
            for operation in edge_info.operations:
                cost_str_list.append('OpCost({}): {}'.format(type(operation).__name__, edge_cost))
                operation_cost_str_list = operation.debug_cost_str_list
                if operation_cost_str_list is not None:
                    for operation_cost_str in operation_cost_str_list:
                        cost_str_list.append('\t' + operation_cost_str)

            cost_str_list.insert(0, 'Score: {}'.format(cost))
            logger.debug('Score: {}, curr_node: {}, next_node: {}', cost, curr_node, next_node)
            gsi_handlers.posture_graph_handlers.log_path_cost(sim, curr_node, next_node, cost_str_list)
        return cost

    def _get_edge_info(self, node, successor):
        original_node_body_target = None
        original_successor_body_target = None
        if node.body_target is not None:
            if node.body_target.is_sim:
                original_node_body_target = node.body_target
                node = node.clone(body=(PostureAspectBody(PostureTuning.SIM_CARRIED_POSTURE, self._graph.proxy_sim)))
        if successor.body_target is not None:
            if successor.body_target.is_sim:
                original_successor_body_target = successor.body_target
                successor = successor.clone(body=(PostureAspectBody(PostureTuning.SIM_CARRIED_POSTURE, self._graph.proxy_sim)))
        edge_info = self._edge_info[(node, successor)]
        if original_successor_body_target is not None:
            for operation in edge_info.operations:
                operation.set_target(original_successor_body_target)

        return (
         edge_info, original_node_body_target)

    def _adjacent_nodes_gen--- This code section failed: ---

 L.4277         0  LOAD_GLOBAL              isinstance
                2  LOAD_DEREF               'node'
                4  LOAD_GLOBAL              _MobileNode
                6  CALL_FUNCTION_2       2  '2 positional arguments'
                8  POP_JUMP_IF_FALSE    16  'to 16'

 L.4278        10  LOAD_DEREF               'node'
               12  LOAD_ATTR                graph_node
               14  STORE_DEREF              'node'
             16_0  COME_FROM             8  '8'

 L.4281        16  LOAD_DEREF               'node'
               18  LOAD_ATTR                body_posture
               20  LOAD_ATTR                mobile
               22  JUMP_IF_FALSE_OR_POP    42  'to 42'
               24  LOAD_DEREF               'node'
               26  LOAD_ATTR                body_target
               28  LOAD_CONST               None
               30  COMPARE_OP               is
               32  JUMP_IF_FALSE_OR_POP    42  'to 42'
               34  LOAD_DEREF               'node'
               36  LOAD_ATTR                surface_target
               38  LOAD_CONST               None
               40  COMPARE_OP               is
             42_0  COME_FROM            32  '32'
             42_1  COME_FROM            22  '22'
               42  STORE_FAST               'is_mobile_at_none'

 L.4283        44  LOAD_CONST               False
               46  STORE_FAST               'is_routing_vehicle'

 L.4284        48  LOAD_FAST                'reverse_path'
               50  POP_JUMP_IF_TRUE    158  'to 158'
               52  LOAD_DEREF               'node'
               54  LOAD_ATTR                body_posture
               56  LOAD_ATTR                is_vehicle
               58  POP_JUMP_IF_FALSE   158  'to 158'

 L.4285        60  SETUP_LOOP          158  'to 158'
               62  LOAD_FAST                'constraint'
               64  GET_ITER         
               66  FOR_ITER            156  'to 156'
               68  STORE_FAST               'sub_constraint'

 L.4286        70  LOAD_FAST                'sub_constraint'
               72  LOAD_ATTR                posture_state_spec
               74  LOAD_CONST               None
               76  COMPARE_OP               is
               78  POP_JUMP_IF_FALSE    82  'to 82'

 L.4287        80  CONTINUE             66  'to 66'
             82_0  COME_FROM            78  '78'

 L.4292        82  LOAD_CLOSURE             'node'
               84  BUILD_TUPLE_1         1 
               86  LOAD_LISTCOMP            '<code_object <listcomp>>'
               88  LOAD_STR                 'PostureGraphService._adjacent_nodes_gen.<locals>.<listcomp>'
               90  MAKE_FUNCTION_8          'closure'
               92  LOAD_FAST                'sub_constraint'
               94  LOAD_ATTR                posture_state_spec
               96  LOAD_METHOD              get_posture_specs_gen
               98  CALL_METHOD_0         0  '0 positional arguments'
              100  GET_ITER         
              102  CALL_FUNCTION_1       1  '1 positional argument'
              104  STORE_FAST               'posture_specs'

 L.4293       106  SETUP_LOOP          154  'to 154'
              108  LOAD_FAST                'posture_specs'
              110  GET_ITER         
            112_0  COME_FROM           142  '142'
              112  FOR_ITER            152  'to 152'
              114  STORE_FAST               'spec'

 L.4294       116  LOAD_FAST                'spec'
              118  LOAD_ATTR                body
              120  LOAD_ATTR                target
              122  LOAD_GLOBAL              PostureSpecVariable
              124  COMPARE_OP               in
              126  POP_JUMP_IF_TRUE    144  'to 144'
              128  LOAD_DEREF               'node'
              130  LOAD_ATTR                body
              132  LOAD_ATTR                target
              134  LOAD_FAST                'spec'
              136  LOAD_ATTR                body
              138  LOAD_ATTR                target
              140  COMPARE_OP               is
              142  POP_JUMP_IF_FALSE   112  'to 112'
            144_0  COME_FROM           126  '126'

 L.4295       144  LOAD_CONST               True
              146  STORE_FAST               'is_routing_vehicle'

 L.4296       148  BREAK_LOOP       
              150  JUMP_BACK           112  'to 112'
              152  POP_BLOCK        
            154_0  COME_FROM_LOOP      106  '106'
              154  JUMP_BACK            66  'to 66'
              156  POP_BLOCK        
            158_0  COME_FROM_LOOP       60  '60'
            158_1  COME_FROM            58  '58'
            158_2  COME_FROM            50  '50'

 L.4298       158  LOAD_FAST                'is_mobile_at_none'
              160  POP_JUMP_IF_TRUE    166  'to 166'
              162  LOAD_FAST                'is_routing_vehicle'
              164  JUMP_IF_FALSE_OR_POP   170  'to 170'
            166_0  COME_FROM           160  '160'
              166  LOAD_DEREF               'force_carry_path'
              168  UNARY_NOT        
            170_0  COME_FROM           164  '164'
              170  STORE_FAST               'skip_adjacent'

 L.4303       172  LOAD_DEREF               'node'
              174  LOAD_ATTR                body_posture
              176  LOAD_ATTR                mobile
              178  POP_JUMP_IF_FALSE   192  'to 192'
              180  LOAD_DEREF               'node'
              182  LOAD_ATTR                body_posture
              184  LOAD_ATTR                skip_route
              186  POP_JUMP_IF_FALSE   192  'to 192'

 L.4304       188  LOAD_CONST               False
              190  STORE_FAST               'skip_adjacent'
            192_0  COME_FROM           186  '186'
            192_1  COME_FROM           178  '178'

 L.4306       192  LOAD_FAST                'allow_carried'
              194  POP_JUMP_IF_TRUE    204  'to 204'
              196  LOAD_FAST                'skip_adjacent'
              198  POP_JUMP_IF_FALSE   204  'to 204'

 L.4307       200  LOAD_CONST               None
              202  RETURN_VALUE     
            204_0  COME_FROM           198  '198'
            204_1  COME_FROM           194  '194'

 L.4309       204  LOAD_CLOSURE             'force_carry_path'
              206  LOAD_CLOSURE             'node'
              208  LOAD_CLOSURE             'self'
              210  LOAD_CLOSURE             'sim'
              212  LOAD_CLOSURE             'valid_edge_test'
              214  LOAD_CLOSURE             'var_map'
              216  BUILD_TUPLE_6         6 
              218  LOAD_CODE                <code_object _edge_validation>
              220  LOAD_STR                 'PostureGraphService._adjacent_nodes_gen.<locals>._edge_validation'
              222  MAKE_FUNCTION_8          'closure'
              224  STORE_FAST               '_edge_validation'

 L.4331   226_228  SETUP_LOOP          582  'to 582'
              230  LOAD_FAST                'get_successors_fn'
              232  LOAD_DEREF               'node'
              234  CALL_FUNCTION_1       1  '1 positional argument'
              236  GET_ITER         
            238_0  COME_FROM           570  '570'
            238_1  COME_FROM           262  '262'
          238_240  FOR_ITER            580  'to 580'
              242  STORE_FAST               'successor'

 L.4332       244  LOAD_FAST                'successor'
              246  LOAD_ATTR                body_target
              248  STORE_FAST               'body_target'

 L.4333       250  LOAD_FAST                'skip_adjacent'
          252_254  POP_JUMP_IF_FALSE   274  'to 274'

 L.4334       256  LOAD_FAST                'body_target'
              258  LOAD_CONST               None
              260  COMPARE_OP               is
              262  POP_JUMP_IF_TRUE    238  'to 238'
              264  LOAD_FAST                'body_target'
              266  LOAD_ATTR                is_sim
          268_270  POP_JUMP_IF_TRUE    274  'to 274'

 L.4335       272  CONTINUE            238  'to 238'
            274_0  COME_FROM           268  '268'
            274_1  COME_FROM           252  '252'

 L.4337       274  LOAD_FAST                'reverse_path'
          276_278  POP_JUMP_IF_FALSE   288  'to 288'
              280  LOAD_FAST                'successor'
              282  LOAD_DEREF               'node'
              284  BUILD_TUPLE_2         2 
              286  JUMP_FORWARD        294  'to 294'
            288_0  COME_FROM           276  '276'
              288  LOAD_DEREF               'node'
              290  LOAD_FAST                'successor'
              292  BUILD_TUPLE_2         2 
            294_0  COME_FROM           286  '286'
              294  STORE_FAST               'forward_nodes'

 L.4338       296  LOAD_FAST                'forward_nodes'
              298  UNPACK_SEQUENCE_2     2 
              300  STORE_FAST               'first'
              302  STORE_FAST               'second'

 L.4340       304  LOAD_FAST                'allow_pickups'
          306_308  POP_JUMP_IF_TRUE    336  'to 336'

 L.4341       310  LOAD_FAST                'first'
              312  LOAD_ATTR                carry_target
              314  LOAD_CONST               None
              316  COMPARE_OP               is
          318_320  POP_JUMP_IF_FALSE   336  'to 336'
              322  LOAD_FAST                'second'
              324  LOAD_ATTR                carry_target
              326  LOAD_CONST               None
              328  COMPARE_OP               is-not
          330_332  POP_JUMP_IF_FALSE   336  'to 336'

 L.4342       334  CONTINUE            238  'to 238'
            336_0  COME_FROM           330  '330'
            336_1  COME_FROM           318  '318'
            336_2  COME_FROM           306  '306'

 L.4344       336  LOAD_FAST                'allow_putdowns'
          338_340  POP_JUMP_IF_TRUE    368  'to 368'

 L.4345       342  LOAD_FAST                'first'
              344  LOAD_ATTR                carry_target
              346  LOAD_CONST               None
              348  COMPARE_OP               is-not
          350_352  POP_JUMP_IF_FALSE   368  'to 368'
              354  LOAD_FAST                'second'
              356  LOAD_ATTR                carry_target
              358  LOAD_CONST               None
              360  COMPARE_OP               is
          362_364  POP_JUMP_IF_FALSE   368  'to 368'

 L.4346       366  CONTINUE            238  'to 238'
            368_0  COME_FROM           362  '362'
            368_1  COME_FROM           350  '350'
            368_2  COME_FROM           338  '338'

 L.4348       368  LOAD_FAST                'body_target'
              370  LOAD_CONST               None
              372  COMPARE_OP               is-not
          374_376  POP_JUMP_IF_FALSE   554  'to 554'
              378  LOAD_FAST                'body_target'
              380  LOAD_ATTR                is_sim
          382_384  POP_JUMP_IF_FALSE   554  'to 554'

 L.4351       386  SETUP_LOOP          578  'to 578'
              388  LOAD_DEREF               'self'
              390  LOAD_ATTR                _graph
              392  LOAD_METHOD              sim_carry_nodes_gen
              394  LOAD_FAST                'successor'
              396  CALL_METHOD_1         1  '1 positional argument'
              398  GET_ITER         
            400_0  COME_FROM           536  '536'
              400  FOR_ITER            550  'to 550'
              402  STORE_FAST               'carry_successor'

 L.4352       404  LOAD_DEREF               'node'
              406  LOAD_ATTR                body_target
              408  LOAD_FAST                'carry_successor'
              410  LOAD_ATTR                body_target
              412  COMPARE_OP               is
          414_416  POP_JUMP_IF_FALSE   422  'to 422'

 L.4353   418_420  CONTINUE            400  'to 400'
            422_0  COME_FROM           414  '414'

 L.4354       422  LOAD_FAST                'reverse_path'
          424_426  POP_JUMP_IF_FALSE   436  'to 436'
              428  LOAD_FAST                'carry_successor'
              430  LOAD_DEREF               'node'
              432  BUILD_TUPLE_2         2 
              434  JUMP_FORWARD        442  'to 442'
            436_0  COME_FROM           424  '424'
              436  LOAD_DEREF               'node'
              438  LOAD_FAST                'carry_successor'
              440  BUILD_TUPLE_2         2 
            442_0  COME_FROM           434  '434'
              442  STORE_FAST               'carry_forward_nodes'

 L.4356       444  LOAD_FAST                'carry_forward_nodes'
              446  UNPACK_SEQUENCE_2     2 
              448  STORE_FAST               'first_carry'
              450  STORE_FAST               'second_carry'

 L.4358       452  LOAD_FAST                'allow_pickups'
          454_456  POP_JUMP_IF_TRUE    486  'to 486'

 L.4359       458  LOAD_FAST                'first_carry'
              460  LOAD_ATTR                carry_target
              462  LOAD_CONST               None
              464  COMPARE_OP               is
          466_468  POP_JUMP_IF_FALSE   486  'to 486'
              470  LOAD_FAST                'second_carry'
              472  LOAD_ATTR                carry_target
              474  LOAD_CONST               None
              476  COMPARE_OP               is-not
          478_480  POP_JUMP_IF_FALSE   486  'to 486'

 L.4360   482_484  CONTINUE            400  'to 400'
            486_0  COME_FROM           478  '478'
            486_1  COME_FROM           466  '466'
            486_2  COME_FROM           454  '454'

 L.4362       486  LOAD_FAST                'allow_putdowns'
          488_490  POP_JUMP_IF_TRUE    520  'to 520'

 L.4363       492  LOAD_FAST                'first_carry'
              494  LOAD_ATTR                carry_target
              496  LOAD_CONST               None
              498  COMPARE_OP               is-not
          500_502  POP_JUMP_IF_FALSE   520  'to 520'
              504  LOAD_FAST                'second_carry'
              506  LOAD_ATTR                carry_target
              508  LOAD_CONST               None
              510  COMPARE_OP               is
          512_514  POP_JUMP_IF_FALSE   520  'to 520'

 L.4364   516_518  CONTINUE            400  'to 400'
            520_0  COME_FROM           512  '512'
            520_1  COME_FROM           500  '500'
            520_2  COME_FROM           488  '488'

 L.4366       520  LOAD_FAST                '_edge_validation'
              522  LOAD_FAST                'carry_forward_nodes'
              524  LOAD_FAST                'carry_successor'
              526  CALL_FUNCTION_2       2  '2 positional arguments'
              528  STORE_FAST               'return_node'

 L.4367       530  LOAD_FAST                'return_node'
              532  LOAD_CONST               None
              534  COMPARE_OP               is-not
          536_538  POP_JUMP_IF_FALSE   400  'to 400'

 L.4368       540  LOAD_FAST                'return_node'
              542  YIELD_VALUE      
              544  POP_TOP          
          546_548  JUMP_BACK           400  'to 400'
              550  POP_BLOCK        
              552  JUMP_BACK           238  'to 238'
            554_0  COME_FROM           382  '382'
            554_1  COME_FROM           374  '374'

 L.4370       554  LOAD_FAST                '_edge_validation'
              556  LOAD_FAST                'forward_nodes'
              558  LOAD_FAST                'successor'
              560  CALL_FUNCTION_2       2  '2 positional arguments'
              562  STORE_FAST               'return_node'

 L.4371       564  LOAD_FAST                'return_node'
              566  LOAD_CONST               None
              568  COMPARE_OP               is-not
              570  POP_JUMP_IF_FALSE   238  'to 238'

 L.4372       572  LOAD_FAST                'return_node'
              574  YIELD_VALUE      
              576  POP_TOP          
            578_0  COME_FROM_LOOP      386  '386'
              578  JUMP_BACK           238  'to 238'
              580  POP_BLOCK        
            582_0  COME_FROM_LOOP      226  '226'

Parse error at or near `STORE_FAST' instruction at offset 170

    @staticmethod
    def _get_destination_locations_for_estimate(route_target, mobile_node):
        locations = route_target.get_position_and_routing_surface_for_posture(mobile_node)
        return locations

    def get_vehicle_destination_target(self, source, destinations):
        if source.body_target is None:
            return
        destination_body_target = None
        for dest in destinations:
            if not dest.body_posture.is_vehicle:
                return
                if destination_body_target is not None:
                    if destination_body_target != dest.body_target:
                        return
                destination_body_target = dest.body_target

        if destination_body_target is not None:
            if source.body_target.id == destination_body_target.id:
                return destination_body_target

    def _left_path_gen(self, sim, source, destinations, interaction, constraint, var_map, valid_edge_test, is_complete, force_carry_path):
        carry_target = var_map.get(PostureSpecVariable.CARRY_TARGET)
        allow_carried = False
        sim_routing_context = sim.get_routing_context()
        if is_complete:
            if source.body.posture_type.mobile:
                if source.surface.target is None:
                    if not source.body.posture_type.is_vehicle:
                        if all((dest.body.target != source.body.target for dest in destinations)):
                            return
            else:
                search_destinations = set(destinations) - self._graph.all_mobile_nodes_at_none
                return search_destinations or None
        else:
            if carry_target is sim:
                destination_body = PostureAspectBody(PostureTuning.SIM_CARRIED_POSTURE, interaction.sim)
                destination_surface = PostureAspectSurface(None, None, None)
                search_destinations = {source.clone(body=destination_body, surface=destination_surface)}
                allow_carried = True
            else:
                search_destinations = set(STAND_AT_NONE_NODES)
                if sim.is_human:
                    search_destinations.update(self._graph.all_mobile_nodes_at_none_no_carry)
                    if source.body_posture.is_vehicle:
                        if source in destinations:
                            search_destinations.update(self._graph.vehicle_nodes)
                        else:
                            vehicle_destination_target = self.get_vehicle_destination_target(source, destinations)
                            if vehicle_destination_target is not None:
                                search_destinations.update(self._graph.nodes_for_object_gen(vehicle_destination_target))
                    else:
                        search_destinations.update(self._graph.all_mobile_nodes_at_none)
                else:
                    ensemble = None
                    if not allow_carried:
                        if force_carry_path:
                            ensemble = services.ensemble_service().get_most_important_ensemble_for_sim(sim)
                        distance_fn = functools.partial(self.distance_fn, sim, var_map, interaction, ensemble)
                        allow_pickups = False
                        if is_complete and carry_target is not None and carry_target.definition is not carry_target:
                            if carry_target.is_in_sim_inventory(sim=sim):
                                allow_pickups = True
                            else:
                                if carry_target.parent is not None:
                                    if carry_target.parent.is_same_object_or_part(sim.posture_state.surface_target) or carry_target.parent.is_same_object_or_part(sim):
                                        allow_pickups = True
                            if carry_target.routing_surface is not None:
                                sim_constraint = interactions.constraints.Transform((sim.intended_transform), routing_surface=(sim.intended_routing_surface))
                                carry_constraint = carry_target.get_carry_transition_constraint(sim, (carry_target.position), (carry_target.routing_surface), mobile=False)
                                if sim_constraint.intersect(carry_constraint).valid:
                                    if carry_target.parent is not None:
                                        ignored_objects = (
                                         sim.posture_state.body_target, sim.posture_state.surface_target)
                    else:
                        ignored_objects = (
                         sim.posture_state.body_target,)
                result, _ = carry_target.check_line_of_sight((sim.intended_transform), additional_ignored_objects=ignored_objects, for_carryable=True)
                if result:
                    allow_pickups = True
                allow_putdowns = allow_pickups
                adjacent_nodes_gen = functools.partial((self._adjacent_nodes_gen),
                  sim, (self._graph.get_successors), valid_edge_test, constraint, var_map,
                  reverse_path=False, allow_pickups=allow_pickups, allow_putdowns=allow_putdowns, allow_carried=allow_carried,
                  force_carry_path=force_carry_path)

                def left_distance_fn(curr_node, next_node):
                    if isinstance(curr_node, _MobileNode):
                        curr_node = curr_node.graph_node
                    if isinstance(next_node, _MobileNode):
                        next_node = next_node.graph_node
                    if next_node is None:
                        if curr_node in destinations:
                            return self._get_goal_cost(sim, interaction, constraint, var_map, curr_node)
                        return 0.0
                    return distance_fn(curr_node, next_node)

                def heuristic_fn_left(node):
                    is_mobile_node = isinstance(node, _MobileNode)
                    if is_mobile_node:
                        graph_node = node.graph_node
                        node = node.prev
                        heuristic = 0
                    else:
                        graph_node = node
                        heuristic = postures.posture_specs.PostureOperation.COST_STANDARD
                    if node.body_target is None or node.body_posture.is_vehicle:
                        return 0
                    if is_mobile_node:
                        if node.body_target.is_sim:
                            return 0
                    else:
                        locations = node.body_target.get_locations_for_posture(graph_node)
                        source_locations = ((source_location.transform.translation, source_location.routing_surface if source_location.routing_surface is not None else node.body_target.routing_surface) for source_location in locations)
                        destination_locations = []
                        carry_target = var_map[PostureSpecVariable.CARRY_TARGET]
                        if carry_target is None or carry_target.definition is carry_target:
                            needs_constraint_dests = False
                            for dest in destinations:
                                if dest.body_target is not None:
                                    destination_locations += self._get_destination_locations_for_estimate(dest.body_target, graph_node)
                                elif dest.surface_target is not None:
                                    destination_locations += self._get_destination_locations_for_estimate(dest.surface_target, graph_node)
                                else:
                                    needs_constraint_dests = True

                            if needs_constraint_dests and any((sub_constraint.geometry for sub_constraint in constraint)):
                                for sub_constraint in constraint:
                                    if not sub_constraint.geometry is None:
                                        if sub_constraint.routing_surface is None:
                                            continue
                                        for polygon in sub_constraint.geometry.polygon:
                                            for polygon_corner in polygon:
                                                destination_locations.append((polygon_corner, sub_constraint.routing_surface))

                        elif carry_target.is_in_inventory():
                            inv = carry_target.get_inventory()
                            if inv.owner is not None:
                                if inv.owner.is_sim:
                                    return heuristic
                            for owner in inv.owning_objects_gen():
                                destination_locations += self._get_destination_locations_for_estimate(owner, graph_node)

                        else:
                            destination_locations += self._get_destination_locations_for_estimate(carry_target, graph_node)
                    heuristic += primitives.routing_utils.estimate_distance_between_multiple_points(source_locations, destination_locations, sim_routing_context)
                    if gsi_handlers.posture_graph_handlers.archiver.enabled:
                        gsi_handlers.posture_graph_handlers.add_heuristic_fn_score(sim, 'left', node, graph_node, heuristic)
                    return heuristic

                paths = _shortest_path_gen(sim, (source,), search_destinations, force_carry_path, adjacent_nodes_gen, left_distance_fn, heuristic_fn_left)
                for path in paths:
                    path = algos.Path(list(path), path.cost - left_distance_fn(path[-1], None))
                    yield path

    def clear_goal_costs(self):
        self._get_goal_cost.cache.clear()

    @caches.cached
    def _get_goal_cost(self, sim, interaction, constraint, var_map, dest):
        cost = self._goal_costs.get(dest, 0.0)
        node_target = dest.body_target
        if node_target is not None:
            if not dest.body.posture_type.is_vehicle:
                cost += constraint.constraint_cost(node_target.position, node_target.orientation)
        else:
            if not any((c.cost for c in constraint)):
                return cost
            if interaction.is_putdown:
                if not constraint.valid:
                    return cu.MAX_FLOAT
                if dest.surface_target is None or getattr(constraint, 'geometry', None):
                    cost += constraint.cost
                return cost
            participant_type = interaction.get_participant_type(sim)
            animation_resolver_fn = interaction.get_constraint_resolver(None)
            _, routing_data = self._get_locations_from_posture(sim,
              dest, var_map, interaction=interaction, participant_type=participant_type, animation_resolver_fn=animation_resolver_fn,
              final_constraint=constraint)
            final_constraint = routing_data[0]
            if final_constraint is None:
                final_constraint = constraint
            return final_constraint.valid or cu.MAX_FLOAT
        cost += final_constraint.cost
        return cost

    def _right_path_gen--- This code section failed: ---

 L.4701         0  LOAD_GLOBAL              functools
                2  LOAD_ATTR                partial

 L.4702         4  LOAD_DEREF               'self'
                6  LOAD_ATTR                _adjacent_nodes_gen
                8  LOAD_DEREF               'sim'
               10  LOAD_DEREF               'self'
               12  LOAD_ATTR                _graph
               14  LOAD_ATTR                get_predecessors
               16  LOAD_FAST                'valid_edge_test'
               18  LOAD_DEREF               'constraint'

 L.4703        20  LOAD_DEREF               'var_map'
               22  LOAD_CONST               True
               24  LOAD_CONST               False
               26  LOAD_CONST               True
               28  LOAD_FAST                'allow_carried'
               30  LOAD_CONST               False
               32  LOAD_CONST               ('reverse_path', 'allow_pickups', 'allow_putdowns', 'allow_carried', 'force_carry_path')
               34  CALL_FUNCTION_KW_11    11  '11 total positional and keyword args'
               36  STORE_FAST               'adjacent_nodes_gen'

 L.4705        38  LOAD_CLOSURE             'ensemble'
               40  LOAD_CLOSURE             'interaction'
               42  LOAD_CLOSURE             'self'
               44  LOAD_CLOSURE             'sim'
               46  LOAD_CLOSURE             'var_map'
               48  BUILD_TUPLE_5         5 
               50  LOAD_CODE                <code_object reversed_distance_fn>
               52  LOAD_STR                 'PostureGraphService._right_path_gen.<locals>.reversed_distance_fn'
               54  MAKE_FUNCTION_8          'closure'
               56  STORE_FAST               'reversed_distance_fn'

 L.4710        58  LOAD_CLOSURE             'constraint'
               60  LOAD_CLOSURE             'interaction'
               62  LOAD_CLOSURE             'self'
               64  LOAD_CLOSURE             'sim'
               66  LOAD_CLOSURE             'var_map'
               68  BUILD_TUPLE_5         5 
               70  LOAD_DICTCOMP            '<code_object <dictcomp>>'
               72  LOAD_STR                 'PostureGraphService._right_path_gen.<locals>.<dictcomp>'
               74  MAKE_FUNCTION_8          'closure'

 L.4711        76  LOAD_DEREF               'destinations'
               78  GET_ITER         
               80  CALL_FUNCTION_1       1  '1 positional argument'
               82  STORE_FAST               'weighted_sources'

 L.4714        84  SETUP_LOOP          144  'to 144'
               86  LOAD_GLOBAL              reversed
               88  LOAD_DEREF               'path_left'
               90  CALL_FUNCTION_1       1  '1 positional argument'
               92  GET_ITER         
             94_0  COME_FROM           122  '122'
             94_1  COME_FROM           102  '102'
               94  FOR_ITER            136  'to 136'
               96  STORE_FAST               'node'

 L.4715        98  LOAD_FAST                'node'
              100  LOAD_ATTR                body_target
              102  POP_JUMP_IF_FALSE    94  'to 94'

 L.4718       104  LOAD_FAST                'node'
              106  LOAD_ATTR                body_target
              108  LOAD_METHOD              get_locations_for_posture
              110  LOAD_DEREF               'path_left'
              112  LOAD_CONST               -1
              114  BINARY_SUBSCR    
              116  CALL_METHOD_1         1  '1 positional argument'
              118  STORE_FAST               'locations'

 L.4719       120  LOAD_FAST                'locations'
              122  POP_JUMP_IF_FALSE    94  'to 94'

 L.4720       124  LOAD_FAST                'locations'
              126  LOAD_CONST               0
              128  BINARY_SUBSCR    
              130  STORE_DEREF              'sim_location'

 L.4721       132  BREAK_LOOP       
              134  JUMP_BACK            94  'to 94'
              136  POP_BLOCK        

 L.4723       138  LOAD_DEREF               'sim'
              140  LOAD_ATTR                routing_location
              142  STORE_DEREF              'sim_location'
            144_0  COME_FROM_LOOP       84  '84'

 L.4725       144  LOAD_DEREF               'sim'
              146  LOAD_METHOD              get_routing_context
              148  CALL_METHOD_0         0  '0 positional arguments'
              150  STORE_DEREF              'sim_routing_context'

 L.4727       152  LOAD_GLOBAL              BarebonesCache
              154  LOAD_CLOSURE             'constraint'
              156  LOAD_CLOSURE             'destinations'
              158  LOAD_CLOSURE             'distance_estimator'
              160  LOAD_CLOSURE             'interaction'
              162  LOAD_CLOSURE             'path_left'
              164  LOAD_CLOSURE             'self'
              166  LOAD_CLOSURE             'sim'
              168  LOAD_CLOSURE             'sim_location'
              170  LOAD_CLOSURE             'sim_routing_context'
              172  BUILD_TUPLE_9         9 
              174  LOAD_CODE                <code_object heuristic_fn_right>
              176  LOAD_STR                 'PostureGraphService._right_path_gen.<locals>.heuristic_fn_right'
              178  MAKE_FUNCTION_8          'closure'
              180  CALL_FUNCTION_1       1  '1 positional argument'
              182  STORE_FAST               'heuristic_fn_right'

 L.4813       184  LOAD_GLOBAL              gsi_handlers
              186  LOAD_ATTR                posture_graph_handlers
              188  LOAD_ATTR                archiver
              190  LOAD_ATTR                enabled
              192  POP_JUMP_IF_FALSE   210  'to 210'

 L.4814       194  LOAD_GLOBAL              gsi_handlers
              196  LOAD_ATTR                posture_graph_handlers
              198  LOAD_METHOD              log_shortest_path_cost
              200  LOAD_DEREF               'sim'
              202  LOAD_FAST                'weighted_sources'
              204  LOAD_FAST                'heuristic_fn_right'
              206  CALL_METHOD_3         3  '3 positional arguments'
              208  POP_TOP          
            210_0  COME_FROM           192  '192'

 L.4816       210  LOAD_GLOBAL              _shortest_path_gen
              212  LOAD_DEREF               'sim'

 L.4817       214  LOAD_FAST                'weighted_sources'
              216  LOAD_GLOBAL              set
              218  LOAD_FAST                'left_destinations'
              220  CALL_FUNCTION_1       1  '1 positional argument'
              222  LOAD_CONST               False
              224  LOAD_FAST                'adjacent_nodes_gen'

 L.4818       226  LOAD_FAST                'reversed_distance_fn'
              228  LOAD_FAST                'heuristic_fn_right'
              230  CALL_FUNCTION_7       7  '7 positional arguments'
              232  STORE_FAST               'paths_reversed'

 L.4819       234  SETUP_LOOP          272  'to 272'
              236  LOAD_FAST                'paths_reversed'
              238  GET_ITER         
              240  FOR_ITER            270  'to 270'
              242  STORE_FAST               'path'

 L.4820       244  LOAD_GLOBAL              algos
              246  LOAD_METHOD              Path
              248  LOAD_GLOBAL              reversed
              250  LOAD_FAST                'path'
              252  CALL_FUNCTION_1       1  '1 positional argument'
              254  LOAD_FAST                'path'
              256  LOAD_ATTR                cost
              258  CALL_METHOD_2         2  '2 positional arguments'
              260  STORE_FAST               'path'

 L.4821       262  LOAD_FAST                'path'
              264  YIELD_VALUE      
              266  POP_TOP          
              268  JUMP_BACK           240  'to 240'
              270  POP_BLOCK        
            272_0  COME_FROM_LOOP      234  '234'

Parse error at or near `LOAD_DICTCOMP' instruction at offset 70

    def _middle_path_gen(self, path_left, path_right, sim, interaction, distance_estimator, var_map):
        if path_left[-1].carry == path_right[0].carry:
            yield
            return
        carry_target = var_map[PostureSpecVariable.CARRY_TARGET]
        if carry_target is None:
            raise ValueError('Interaction requires a carried object in its animation but has no carry_target: {} {}', interaction, var_map)
        if isinstance(carry_target, Definition):
            return
        pickup_cost = PostureOperation.PickUpObject.get_pickup_cost(path_left[-1])
        if carry_target.is_sim:
            surface_target = carry_target.posture_state.surface_target
            if surface_target is not None:
                pickup_path = self.get_pickup_path(surface_target, interaction)
                pickup_path.cost += pickup_cost
                yield pickup_path
                return
        else:
            parent_slot = carry_target.parent_slot
            if parent_slot is not None:
                if parent_slot.owner is not sim:
                    if parent_slot.owner.is_sim:
                        return []
                    if not carry_target.parented_to_routable_object:
                        surface_target = parent_slot.owner
                        if not surface_target.is_surface():
                            raise ValueError('Cannot pick up an object: {} from an invalid surface: {}'.format(carry_target, surface_target))
                        pickup_path = self.get_pickup_path(surface_target, interaction)
                        pickup_path.cost += pickup_cost
                        yield pickup_path
                        return
            carry_target_inventory = carry_target.get_inventory()
            if carry_target_inventory is None or carry_target.is_in_sim_inventory():
                carry_routing_surface = carry_target.routing_surface
                if carry_routing_surface is not None and carry_routing_surface.type == routing.SurfaceType.SURFACETYPE_POOL:
                    yield algos.Path([SWIM_AT_NONE, SWIM_AT_NONE_CARRY], pickup_cost)
                else:
                    yield algos.Path([STAND_AT_NONE, STAND_AT_NONE_CARRY], pickup_cost)
                return
            if interaction is not None:
                obj_with_inventory = interaction.object_with_inventory
                if obj_with_inventory is not None:
                    if not obj_with_inventory.can_access_for_pickup(sim):
                        return
                    pickup_path = self.get_pickup_path(obj_with_inventory, interaction)
                    pickup_path.cost += pickup_cost
                    yield pickup_path
                    return
            inv_objects = list(carry_target_inventory.owning_objects_gen())
            if not inv_objects:
                logger.warn('Attempt to plan a middle path for an inventory with no owning objects: {} on interaction: {}', carry_target_inventory,
                  interaction, owner='bhill')
                return
            for node in path_right:
                if not node.body_target:
                    if node.surface_target:
                        pass
                    right_target = node.body_target or node.surface_target
                    break
            else:
                right_target = None

            def inv_owner_dist(owner):
                routing_position, _ = Constraint.get_validated_routing_position(owner)
                routing_location = routing.Location(routing_position, orientation=(owner.orientation),
                  routing_surface=(owner.routing_surface))
                dist = distance_estimator.estimate_distance((sim.location, routing_location))
                dist += distance_estimator.get_preferred_object_cost(owner)
                if right_target:
                    right_target_position, _ = Constraint.get_validated_routing_position(right_target)
                    right_target_location = routing.Location(right_target_position, orientation=(right_target.orientation),
                      routing_surface=(right_target.routing_surface))
                    dist += distance_estimator.estimate_distance((routing_location, right_target_location))
                return dist

            inv_objects.sort(key=inv_owner_dist)
            for inv_object in inv_objects:
                if not inv_object.can_access_for_pickup(sim):
                    continue
                pickup_path = self.get_pickup_path(inv_object, interaction)
                pickup_path.cost += pickup_cost
                yield pickup_path

    def _get_all_paths(self, sim, source, destinations, var_map, constraint, valid_edge_test, interaction=None, allow_complete=True):
        distance_estimator = DistanceEstimator(self, sim, interaction, constraint)
        segmented_paths = []
        stand_path = SegmentedPath(self,
          sim, source, destinations, var_map, constraint, valid_edge_test,
          interaction, is_complete=False, distance_estimator=distance_estimator)
        segmented_paths.append(stand_path)
        if allow_complete:
            complete = SegmentedPath(self,
              sim, source, destinations, var_map, constraint, valid_edge_test,
              interaction, is_complete=True, distance_estimator=distance_estimator)
            segmented_paths.append(complete)
        return segmented_paths

    def get_pickup_path(self, surface_target, interaction):
        cost_pickup = 0
        path_pickup = [STAND_AT_NONE]
        sequence_pickup = get_pick_up_spec_sequence(STAND_AT_NONE, surface_target)
        path_pickup.extend(sequence_pickup)
        path_pickup.append(STAND_AT_NONE_CARRY)
        if interaction is not None:
            preferred_objects = interaction.preferred_objects
            cost_pickup += postures.posture_scoring.PostureScoring.get_preferred_object_cost((
             surface_target,), preferred_objects)
        return algos.Path(path_pickup, cost_pickup)

    def any_template_passes_destination_test(self, templates, si, sim, node):
        if not node.body_posture._supports_carry:
            return False
        for template in templates.values():
            for dest_spec, var_map in template:
                if postures.posture_specs.destination_test(sim, node, (dest_spec,), var_map, None, si):
                    return True

        return False

    def get_segmented_paths(self, sim, posture_dest_list, additional_template_list, interaction, participant_type, valid_destination_test, valid_edge_test, preferences, final_constraint, included_sis):
        possible_destinations = []
        all_segmented_paths = []
        self._goal_costs.clear()
        if gsi_handlers.posture_graph_handlers.archiver.enabled:
            gsi_templates = [(ds, vm, c) for c, value in posture_dest_list.items() for ds, vm in iter(value)]
            gsi_handlers.posture_graph_handlers.add_templates_to_gsi(sim, gsi_templates)
        guaranteed_sis = list(sim.si_state.all_guaranteed_si_gen(interaction.priority, interaction.group_id))
        excluded_objects = interaction.excluded_posture_destination_objects()
        interaction_sims = set(interaction.get_participants(ParticipantType.AllSims))
        interaction_sims.discard(interaction.sim)
        relationship_bonuses = None
        if interaction.use_relationship_bonuses:
            relationship_bonuses = PostureScoring.build_relationship_bonuses(sim, (interaction.sim_affinity_posture_scoring_data),
              (interaction.sim_affinity_use_current_position_for_none),
              sims_to_consider=interaction_sims)
        main_group = sim.get_main_group()
        if main_group is not None and main_group.constraint_initialized:
            group_constraint = main_group.is_solo or main_group.get_constraint(sim)
        else:
            group_constraint = None
        found_destination_node = False
        for constraint, templates in posture_dest_list.items():
            destination_nodes = {}
            var_map_all = DEFAULT
            destination_specs = set()
            slot_types = set()
            for destination_spec, var_map in templates:
                destination_specs.add(destination_spec)
                slot = var_map.get(PostureSpecVariable.SLOT)
                if slot is not None:
                    slot_types.update(slot.slot_types)
                if var_map_all is DEFAULT:
                    var_map_all = var_map
                if gsi_handlers.posture_graph_handlers.archiver.enabled:
                    possible_destinations.append(destination_spec)

            slot_all = var_map_all.get(PostureSpecVariable.SLOT)
            if slot_all is not None:
                new_slot_manifest = slot_all.with_overrides(slot=(frozenset(slot_types)))
                var_map_all = frozendict(var_map_all, {PostureSpecVariable.SLOT: new_slot_manifest})
            source_spec = cython.declare(PostureSpec, sim.posture_state.get_posture_spec(var_map_all))
            if source_spec is None:
                continue
            if source_spec.body_posture.mobile:
                if source_spec.body_posture.unconstrained:
                    if source_spec.body_target is not None and not source_spec.body_target.is_part:
                        if source_spec.body_target.parts:
                            new_body = PostureAspectBody(source_spec.body_posture, None)
                            new_surface = PostureAspectSurface(None, None, None)
                            source_spec = source_spec.clone(body=new_body, carry=DEFAULT, surface=new_surface)
            graph = cython.declare(PostureGraph, self._graph)
            if not graph.contains(source_spec):
                if services.current_zone().is_zone_shutting_down:
                    return []
                    raise AssertionError('Source spec not in the posture graph: {} for interaction: {}'.format(source_spec, interaction))
                else:
                    source_node = source_spec
                    if gsi_handlers.posture_graph_handlers.archiver.enabled:
                        gsi_handlers.posture_graph_handlers.add_source_or_dest(sim, (source_spec,), var_map_all, 'source', source_node)
                    distance_estimator = DistanceEstimator(self, sim, interaction, constraint)
                    same_mobile_body_target = source_node.body_posture.mobile
                    if same_mobile_body_target:
                        if source_node.body_target is not None and source_node.body_target.is_part:
                            adjacent_source_parts = source_node.body_target.adjacent_parts_gen()
                        else:
                            adjacent_source_parts = ()
                    body_target_node_distances = None
                    matching_node_constraint = constraint if interaction.is_putdown else final_constraint
                    for node in graph.get_matching_nodes_gen(destination_specs, slot_types,
                      constraint=matching_node_constraint):
                        if node.get_core_objects() & excluded_objects:
                            continue
                        elif not destination_test(sim, node, destination_specs, var_map_all, valid_destination_test, interaction):
                            continue
                        else:
                            if included_sis and node.body.target is not None:
                                if any((not node.body.target.supports_affordance(si.affordance) for si in included_sis)):
                                    continue
                                if interaction.context.source == InteractionContext.SOURCE_AUTONOMY and interaction.autonomy_preference is not None and node.body_target is not None:
                                    preference_target = node.body_target
                                    if preference_target.is_part:
                                        if not preference_target.restrict_autonomy_preference:
                                            preference_target = preference_target.part_owner
                                    preference_type = sim.get_autonomy_preference_type(interaction.autonomy_preference.preference.tag, preference_target, False)
                                    if preference_type == AutonomyPreferenceType.DISALLOWED:
                                        continue
                            elif same_mobile_body_target:
                                if node.body.target is not None:
                                    if node.body.target is not source_node.body_target and node.body.target not in adjacent_source_parts:
                                        same_mobile_body_target = False
                            if interaction.is_putdown:
                                obj = node.body_target
                                if obj is not None:
                                    if obj.is_part:
                                        obj = obj.part_owner
                                    valid, distance = interaction.evaluate_putdown_distance(obj, distance_estimator)
                                    if not valid:
                                        continue
                                    if distance is not None:
                                        if body_target_node_distances is None:
                                            body_target_node_distances = {}
                                        body_target_node_distances[node] = distance
                        if additional_template_list and not interaction.is_putdown:
                            compatible = True
                            for carry_si, additional_templates in additional_template_list.items():
                                if carry_si not in guaranteed_sis:
                                    continue
                                compatible = self.any_template_passes_destination_test(additional_templates, carry_si, sim, node)
                                if compatible:
                                    break

                            if not compatible:
                                continue
                            if gsi_handlers.posture_graph_handlers.archiver.enabled:
                                gsi_handlers.posture_graph_handlers.add_source_or_dest(sim, destination_specs, var_map_all, 'destination', node)
                            destination_nodes[node] = destination_specs

                    if interaction.is_putdown:
                        if body_target_node_distances is not None:
                            nodes_to_remove = interaction.get_distant_nodes_to_remove(body_target_node_distances)
                            if nodes_to_remove:
                                for distant_node in nodes_to_remove:
                                    del destination_nodes[distant_node]

                    if destination_nodes:
                        found_destination_node = True
                    else:
                        logger.debug('No destination_nodes found for destination_specs: {}', destination_specs)
                        continue
                    PostureScoring.build_destination_costs(self._goal_costs, destination_nodes, sim, interaction, var_map_all, preferences, included_sis, additional_template_list, relationship_bonuses, constraint, group_constraint)
                    allow_complete = not source_node.body_posture.mobile or same_mobile_body_target
                    if allow_complete:
                        if source_node.body_target is None:
                            current_constraint = constraints.Transform((sim.transform), routing_surface=(sim.routing_surface))
                            intersection = current_constraint.intersect(constraint)
                            if not intersection.valid:
                                allow_complete = False
                    interaction_outfit_changes = interaction.get_tuned_outfit_changes(include_exit_changes=False)
                    if interaction_outfit_changes:
                        for outfit_change in interaction_outfit_changes:
                            if not sim.sim_info.is_wearing_outfit(outfit_change):
                                allow_complete = False

                    is_sim_carry = _is_sim_carry(interaction, sim)
                    if allow_complete:
                        source_body_target = source_node.body_target
                        if is_sim_carry:
                            complete_destinations = destination_nodes
                        else:
                            if source_body_target is None:
                                complete_destinations = [dest_node for dest_node in destination_nodes if dest_node.body_target is None]
                            else:
                                if source_body_target.is_part:
                                    source_body_target = source_body_target.part_owner
                                complete_destinations = [dest_node for dest_node in destination_nodes if source_body_target.is_same_object_or_part(dest_node.body_target)]
                        if not is_sim_carry:
                            for dest_node in complete_destinations:
                                outfit_change = dest_node.body.posture_type.outfit_change
                                if outfit_change:
                                    entry_change_outfit = outfit_change.get_on_entry_outfit(interaction, sim_info=(sim.sim_info))
                                    if entry_change_outfit is not None:
                                        if not sim.sim_info.is_wearing_outfit(entry_change_outfit):
                                            continue
                                allow_complete = True
                                break
                            else:
                                allow_complete = False

                segmented_paths = self._get_all_paths(sim,
                  source_node, destination_nodes, var_map_all, constraint, valid_edge_test,
                  interaction=interaction, allow_complete=allow_complete)
                all_segmented_paths.extend(segmented_paths)

        if self._goal_costs:
            lowest_goal_cost = min(self._goal_costs.values())
            for goal_node, cost in self._goal_costs.items():
                self._goal_costs[goal_node] = cost - lowest_goal_cost

        elif not all_segmented_paths:
            if not found_destination_node:
                set_transition_failure_reason(sim, (TransitionFailureReasons.NO_DESTINATION_NODE), transition_controller=(interaction.transition))
            else:
                set_transition_failure_reason(sim, (TransitionFailureReasons.NO_PATH_FOUND), transition_controller=(interaction.transition))
        return all_segmented_paths

    def handle_additional_pickups_and_putdowns(self, best_path_spec, additional_template_list, sim, can_defer_putdown=True):
        included_sis = set()
        return best_path_spec.transition_specs and additional_template_list or included_sis
        best_transition_specs = best_path_spec.transition_specs
        final_transition_spec = best_transition_specs[-1]
        final_node = final_transition_spec.posture_spec
        final_var_map = final_transition_spec.var_map
        final_hand = final_var_map[PostureSpecVariable.HAND]
        final_spec_constraint = best_path_spec.spec_constraint
        final_carry_target = final_var_map[PostureSpecVariable.CARRY_TARGET]
        slot_manifest_entry = final_var_map.get(PostureSpecVariable.SLOT)
        additional_template_added = False
        for carry_si, additional_templates in additional_template_list.items():
            carry_si_carryable = carry_si.carry_target
            if carry_si_carryable is None:
                if carry_si.target is not None:
                    if carry_si.target.carryable_component is not None:
                        carry_si_carryable = carry_si.target
            if carry_si_carryable is final_carry_target:
                included_sis.add(carry_si)
                additional_template_added = True
                continue
            valid_additional_intersection = False
            for destination_spec_additional, var_map_additional, constraint_additional in [(ds, vm, c) for c, value in additional_templates.items() for ds, vm in iter(value)]:
                additional_hand = var_map_additional[PostureSpecVariable.HAND]
                if final_hand == additional_hand:
                    continue
                if additional_template_added:
                    continue
                valid_destination = destination_test(sim, final_node, (destination_spec_additional,), var_map_additional, None, carry_si)
                valid_intersection = constraint_additional.intersect(final_spec_constraint).valid
                if not valid_intersection:
                    continue
                valid_additional_intersection = True
                if not valid_destination:
                    continue
                carry_target = var_map_additional[PostureSpecVariable.CARRY_TARGET]
                container = carry_target.parent
                if final_node.surface.target is container:
                    included_sis.add(carry_si)
                    continue
                additional_slot_manifest_entry = var_map_additional.get(PostureSpecVariable.SLOT)
                if additional_slot_manifest_entry is not None:
                    if slot_manifest_entry is not None:
                        if slot_manifest_entry.slot_types.intersection(additional_slot_manifest_entry.slot_types):
                            continue
                if container is not sim:
                    insertion_index = 0
                    fallback_insertion_index_and_spec = None
                    original_spec = best_transition_specs[0].posture_spec
                    if original_spec.surface.target is container:
                        fallback_insertion_index_and_spec = InsertionIndexAndSpec(insertion_index, original_spec)
                    for prev_transition_spec, transition_spec in zip(best_transition_specs, best_transition_specs[1:]):
                        insertion_index += 1
                        if transition_spec.sequence_id != prev_transition_spec.sequence_id:
                            continue
                        spec = transition_spec.posture_spec
                        if fallback_insertion_index_and_spec is None:
                            if spec.surface.target is container:
                                fallback_insertion_index_and_spec = InsertionIndexAndSpec(insertion_index, spec)
                            if prev_transition_spec.posture_spec.carry.target is None:
                                if spec.carry.target is not None:
                                    if spec.surface.target is not container:
                                        continue
                                break
                    else:
                        if fallback_insertion_index_and_spec is not None:
                            insertion_index = fallback_insertion_index_and_spec.index
                            spec = fallback_insertion_index_and_spec.spec
                        else:
                            continue
                        pick_up_sequence = get_pick_up_spec_sequence(spec,
                          container,
                          body_target=(spec.body.target))
                        slot_var_map = {PostureSpecVariable.SLOT: SlotManifestEntry(carry_target, container, carry_target.parent_slot)}
                        var_map_additional_updated = frozendict(var_map_additional, slot_var_map)
                        new_specs = []
                        for pick_up_spec in pick_up_sequence:
                            new_specs.append(TransitionSpecCython_create(best_path_spec, pick_up_spec, var_map_additional_updated,
                              sequence_id=(SequenceId.PICKUP)))

                        best_path_spec.insert_transition_specs_at_index(insertion_index, new_specs)
                final_surface_target = final_node.surface.target if final_node.surface is not None else None
                if final_surface_target is not None:
                    if PostureSpecVariable.SLOT in var_map_additional:
                        _slot_manifest_entry = var_map_additional[PostureSpecVariable.SLOT]
                        overrides = {}
                        if isinstance(_slot_manifest_entry.target, PostureSpecVariable):
                            overrides['target'] = final_surface_target
                        else:
                            interaction_target = final_var_map[PostureSpecVariable.INTERACTION_TARGET]
                            if interaction_target is not None:
                                relative_position = interaction_target.position
                            else:
                                relative_position = final_surface_target.position
                        chosen_slot = self._get_best_slot(final_surface_target, _slot_manifest_entry.slot_types, carry_target, relative_position)
                        if chosen_slot is None:
                            continue
                        overrides['slot'] = chosen_slot
                        _slot_manifest_entry = (_slot_manifest_entry.with_overrides)(**overrides)
                        slot_var_map = {PostureSpecVariable.SLOT: _slot_manifest_entry}
                        var_map_additional = frozendict(var_map_additional, slot_var_map)
                if additional_slot_manifest_entry is not None:
                    insertion_index = 0
                    fallback_insertion_index_and_spec = None
                    original_spec = best_transition_specs[0].posture_spec
                    if original_spec.surface.target is slot_manifest_entry.actor.parent:
                        fallback_insertion_index_and_spec = InsertionIndexAndSpec(insertion_index, original_spec)
                    for prev_transition_spec, transition_spec in zip(best_transition_specs, best_transition_specs[1:]):
                        insertion_index += 1
                        if transition_spec.sequence_id != prev_transition_spec.sequence_id:
                            continue
                        spec = transition_spec.posture_spec
                        if fallback_insertion_index_and_spec is None:
                            if spec.surface.target is slot_manifest_entry.actor.parent:
                                fallback_insertion_index_and_spec = InsertionIndexAndSpec(insertion_index, spec)
                            if prev_transition_spec.posture_spec.carry.target is not None and spec.carry.target is None:
                                break
                    else:
                        if fallback_insertion_index_and_spec is not None:
                            insertion_index = fallback_insertion_index_and_spec.index
                            spec = fallback_insertion_index_and_spec.spec
                        else:
                            continue
                        put_down_sequence = get_put_down_spec_sequence((spec.body.posture_type),
                          (spec.surface.target),
                          body_target=(spec.body.target))
                        new_specs = []
                        for put_down_spec in put_down_sequence:
                            new_specs.append(TransitionSpecCython_create(best_path_spec, put_down_spec, var_map_additional,
                              sequence_id=(SequenceId.PUTDOWN)))

                        best_path_spec.insert_transition_specs_at_index(insertion_index + 1, new_specs)

                    included_sis.add(carry_si)
                    additional_template_added = True
                    break
            else:
                if valid_additional_intersection or can_defer_putdown:
                    if carry_si_carryable.carryable_component.defer_putdown:
                        sim.transition_controller.has_deferred_putdown = True
                carry_si.cancel((FinishingType.TRANSITION_FAILURE), cancel_reason_msg='Posture Graph. No valid intersections for additional constraint.')

        return included_sis

    @staticmethod
    def is_valid_complete_path(sim, path, interaction):
        for posture_spec in path:
            target = posture_spec.body.target
            if target is not None:
                if target is interaction.target:
                    reservation_handler = interaction.get_interaction_reservation_handler(sim=sim)
                    if reservation_handler is None or reservation_handler.may_reserve():
                        continue
                    else:
                        reservation_handler = interaction.get_interaction_reservation_handler(sim=sim, target=target)
                        if reservation_handler is None or reservation_handler.may_reserve():
                            continue
                    can_remove, _, _ = can_remove_blocking_sims(sim, interaction, (target,))
                    if can_remove:
                        continue
                    if target.usable_by_transition_controller(sim.queue.transition_controller):
                        continue
                return False

        return True

    def get_sim_position_routing_data(self, sim):
        if sim.parent is not None:
            if sim.parent.is_sim or sim.posture_state.body.is_vehicle:
                return self.get_sim_position_routing_data(sim.parent)
        sim_position_constraint = interactions.constraints.Transform((sim.intended_transform),
          routing_surface=(sim.intended_routing_surface),
          debug_name='SimCurrentPosition')
        return (sim_position_constraint, None, None)

    @staticmethod
    def _get_new_goal_error_info():
        if False:
            if gsi_handlers.posture_graph_handlers.archiver.enabled:
                return []

    @staticmethod
    def _goal_failure_set(goals):
        return set([goal.failure_reason.name for goal in goals])

    @staticmethod
    def append_handles(sim, handle_dict, invalid_handle_dict, invalid_los_dict, routing_data, target_path, var_map, dest_spec, cur_path_id, final_constraint, entry=True, path_type=PathType.LEFT, goal_height_limit=None, perform_los_check=True):
        routing_constraint, locked_params, target = routing_data
        if routing_constraint is None:
            return
        carry_target = var_map.get(PostureSpecVariable.CARRY_TARGET)
        for_carryable = carry_target is not None
        reference_pt, top_level_parent = Constraint.get_los_reference_point(target, is_carry_target=(target is carry_target))
        if path_type == PathType.RIGHT:
            if target is carry_target:
                goal_height_limit = None
                if top_level_parent is not sim:
                    reference_pt, top_level_parent = (None, None)
        if not perform_los_check:
            reference_pt = None
        blocking_obj_id = None
        if sim.routing_master is not None and sim.routing_master.get_routing_slave_data_count(FormationRoutingType.FOLLOW):
            target_reference_override = sim.routing_master
            goal_height_limit = FormationTuning.GOAL_HEIGHT_LIMIT
        else:
            target_reference_override = None
        for sub_constraint in routing_constraint:
            if not sub_constraint.valid:
                continue
            elif sub_constraint.routing_surface is not None:
                routing_surface = sub_constraint.routing_surface
            else:
                if target is not None:
                    routing_surface = target.routing_surface
                else:
                    routing_surface = None
            connectivity_handles = sub_constraint.get_connectivity_handles(sim=sim,
              routing_surface_override=routing_surface,
              locked_params=locked_params,
              los_reference_point=reference_pt,
              entry=entry,
              target=target)
            for connectivity_handle in connectivity_handles:
                connectivity_handle.path = target_path
                connectivity_handle.var_map = var_map
                existing_data = handle_dict.get(connectivity_handle)
                if existing_data is not None:
                    if target_path.cost >= existing_data[1]:
                        continue
                if connectivity_handle.los_reference_point is None or test_point_in_compound_polygon(connectivity_handle.los_reference_point, connectivity_handle.geometry.polygon):
                    single_goal_only = True
                else:
                    single_goal_only = False
                for_source = path_type == PathType.LEFT and len(target_path) == 1
                goal_error_info = PostureGraphService._get_new_goal_error_info()
                routing_goals = connectivity_handle.get_goals(relative_object=target, for_source=for_source,
                  single_goal_only=single_goal_only,
                  for_carryable=for_carryable,
                  goal_height_limit=goal_height_limit,
                  target_reference_override=target_reference_override,
                  perform_los_check=perform_los_check,
                  out_result_info=goal_error_info,
                  check_height_clearance=False)
                if not routing_goals:
                    if gsi_handlers.posture_graph_handlers.archiver.enabled:
                        gsi_handlers.posture_graph_handlers.log_transition_handle(sim, connectivity_handle, connectivity_handle.polygons, target_path, str(goal_error_info), path_type)
                        continue
                    yield_to_irq()
                    valid_goals = []
                    invalid_goals = []
                    invalid_los_goals = []
                    ignore_los_for_vehicle = sim.posture.is_vehicle and sim.posture.target is target
                    for goal in routing_goals:
                        if not single_goal_only:
                            if goal.requires_los_check and target is not None:
                                if (target.is_sim or ignore_los_for_vehicle or goal.failure_reason) != GoalFailureType.NoError and blocking_obj_id is not None:
                                    if goal.failure_reason == GoalFailureType.LOSBlocked:
                                        invalid_los_goals.append(goal)
                            else:
                                invalid_goals.append(goal)
                                continue
                            result, blocking_obj_id = target.check_line_of_sight((goal.location.transform),
                              verbose=True, for_carryable=for_carryable, use_standard_ignored_objects=True)
                            if result == routing.RAYCAST_HIT_TYPE_IMPASSABLE:
                                invalid_goals.append(goal)
                                continue
                            else:
                                if result == routing.RAYCAST_HIT_TYPE_LOS_IMPASSABLE:
                                    invalid_los_goals.append(goal)
                                    continue
                                goal.path_id = cur_path_id
                                valid_goals.append(goal)

                    if gsi_handlers.posture_graph_handlers.archiver.enabled and not invalid_goals:
                        if invalid_los_goals:
                            failure_set = PostureGraphService._goal_failure_set(invalid_goals)
                            failure_set.union(PostureGraphService._goal_failure_set(invalid_los_goals))
                            gsi_handlers.posture_graph_handlers.log_transition_handle(sim, connectivity_handle, connectivity_handle.polygons, target_path, str(failure_set), path_type)
                    if invalid_goals:
                        invalid_handle_dict[connectivity_handle] = (
                         target_path, target_path.cost, var_map, dest_spec,
                         invalid_goals, routing_constraint, final_constraint)
                    if invalid_los_goals:
                        invalid_los_dict[connectivity_handle] = (
                         target_path, target_path.cost, var_map, dest_spec,
                         invalid_los_goals, routing_constraint, final_constraint)
                    if not valid_goals:
                        continue
                    if gsi_handlers.posture_graph_handlers.archiver.enabled:
                        valid_str = '{} usable, {}'.format(len(valid_goals), PostureGraphService._goal_failure_set(valid_goals))
                        if goal_error_info:
                            valid_str += '; rejected {}, {}'.format(len(goal_error_info), goal_error_info)
                        gsi_handlers.posture_graph_handlers.log_transition_handle(sim, connectivity_handle, connectivity_handle.polygons, target_path, valid_str, path_type)
                    handle_dict[connectivity_handle] = (target_path, target_path.cost, var_map,
                     dest_spec, valid_goals, routing_constraint,
                     final_constraint)

            if gsi_handlers.posture_graph_handlers.archiver.enabled and not connectivity_handles:
                if sub_constraint.geometry is not None:
                    gsi_handlers.posture_graph_handlers.log_transition_handle(sim, None, sub_constraint.geometry, target_path, True, path_type)

        return blocking_obj_id or None

    @staticmethod
    def copy_handles(sim, destination_handles, path, var_map):
        existing_data = destination_handles.get(DEFAULT)
        if existing_data is not None:
            existing_cost = existing_data[1]
            if path.cost >= existing_cost:
                return
        destination_spec = path.segmented_path.destination_specs.get(path[-1])
        destination_handles[DEFAULT] = (path, path.cost,
         var_map, destination_spec, [],
         Anywhere(), Anywhere())

    def _get_resolved_var_map(self, path, var_map):
        final_spec = path[-1]
        target = final_spec.body.target
        surface_target = final_spec.surface.target
        updates = {}
        if target is not None:
            original_target = var_map.get(PostureSpecVariable.INTERACTION_TARGET)
            if original_target == PostureSpecVariable.BODY_TARGET_FILTERED:
                original_target = target
            if original_target is not None:
                if original_target.id == target.id:
                    updates[PostureSpecVariable.INTERACTION_TARGET] = target
            original_carry_target = var_map.get(PostureSpecVariable.CARRY_TARGET)
            if original_carry_target is not None:
                if original_carry_target.id == target.id:
                    updates[PostureSpecVariable.CARRY_TARGET] = target
        if surface_target is not None:
            slot_manifest_entry = var_map.get(PostureSpecVariable.SLOT)
            if slot_manifest_entry is not None:
                if slot_manifest_entry.target is not None:
                    if isinstance(slot_manifest_entry.target, PostureSpecVariable) or slot_manifest_entry.target.id == surface_target.id:
                        slot_manifest_entry = SlotManifestEntry(slot_manifest_entry.actor, surface_target, slot_manifest_entry.slot)
                        updates[PostureSpecVariable.SLOT] = slot_manifest_entry
        return frozendict(var_map, updates)

    def _generate_left_handles(self, sim, interaction, participant_type, left_path, var_map, destination_spec, final_constraint, unique_id, sim_position_routing_data):
        left_handles = {}
        invalid = {}
        invalid_los = {}
        blocking_obj_ids = []
        if not left_path[0].body.posture_type.use_containment_slot_for_exit:
            blocking_obj_id = self.append_handles(sim,
              left_handles, invalid, invalid_los, sim_position_routing_data, left_path,
              var_map, destination_spec, unique_id, final_constraint, path_type=(PathType.LEFT))
            if blocking_obj_id is not None:
                blocking_obj_ids.append(blocking_obj_id)
        else:
            exit_spec, _, _ = self.find_exit_posture_spec(sim, left_path, var_map)
            transition_posture_name = left_path[-1].body_posture.name
            if exit_spec == left_path[0] and sim.posture.is_puppet:
                with create_puppet_postures(sim):
                    use_previous_position, routing_data = self._get_locations_from_posture(sim,
                      exit_spec, var_map, participant_type=participant_type, transition_posture_name=transition_posture_name)
            else:
                use_previous_position, routing_data = self._get_locations_from_posture(sim,
                  exit_spec, var_map, mobile_posture_spec=(left_path[-1]), participant_type=participant_type,
                  transition_posture_name=transition_posture_name,
                  left_most_spec=(left_path[0]))
            if use_previous_position:
                routing_data = sim_position_routing_data
            blocking_obj_id = self.append_handles(sim,
              left_handles, invalid, invalid_los, routing_data, left_path, var_map,
              destination_spec, unique_id, final_constraint, entry=False, path_type=(PathType.LEFT))
            if blocking_obj_id is not None:
                blocking_obj_ids.append(blocking_obj_id)
            return (left_handles, invalid, invalid_los, blocking_obj_ids)

    def _generate_right_handles(self, sim, interaction, participant_type, right_path, var_map, destination_spec, final_constraint, unique_id, animation_resolver_fn):
        right_handles = {}
        invalid = {}
        invalid_los = {}
        blocking_obj_ids = []
        first_spec = right_path[0]
        if first_spec.body.posture_type.mobile:
            entry_spec, constrained_edge, _ = first_spec.body.target is None or first_spec.body.posture_type.unconstrained or self.find_entry_posture_spec(sim, right_path, var_map)
            final_spec = right_path[-1]
            relevant_interaction = interaction if entry_spec is final_spec else None
            right_var_map = self._get_resolved_var_map(right_path, right_path.segmented_path.var_map)
            right_path.segmented_path.var_map_resolved = right_var_map
            transition_posture_name = first_spec.body_posture.name
            use_previous_pos, routing_data = self._get_locations_from_posture(sim,
              entry_spec, right_var_map, interaction=relevant_interaction,
              mobile_posture_spec=first_spec,
              participant_type=participant_type,
              constrained_edge=constrained_edge,
              animation_resolver_fn=animation_resolver_fn,
              final_constraint=final_constraint,
              transition_posture_name=transition_posture_name)
            if use_previous_pos:
                self.copy_handles(sim, right_handles, right_path, right_var_map)
        elif routing_data[0].valid:
            perform_los_check = interaction.should_perform_routing_los_check
            blocking_obj_id = self.append_handles(sim,
              right_handles, invalid, invalid_los, routing_data, right_path,
              right_var_map, destination_spec, unique_id, final_constraint,
              path_type=(PathType.RIGHT), goal_height_limit=(interaction.goal_height_limit),
              perform_los_check=perform_los_check)
            if blocking_obj_id is not None:
                blocking_obj_ids.append(blocking_obj_id)
        else:
            if first_spec.body_target is not None:
                if first_spec.body_target.is_sim:
                    right_var_map = self._get_resolved_var_map(right_path, right_path.segmented_path.var_map)
                    right_path.segmented_path.var_map_resolved = right_var_map
                    self.copy_handles(sim, right_handles, right_path, right_var_map)
        return (
         right_handles, invalid, invalid_los, blocking_obj_ids)

    def _generate_middle_handles--- This code section failed: ---

 L.6132         0  BUILD_MAP_0           0 
                2  STORE_FAST               'middle_handles'

 L.6133         4  BUILD_MAP_0           0 
                6  STORE_FAST               'invalid'

 L.6134         8  BUILD_MAP_0           0 
               10  STORE_FAST               'invalid_los'

 L.6136        12  BUILD_LIST_0          0 
               14  STORE_FAST               'blocking_obj_ids'

 L.6141        16  LOAD_FAST                'self'
               18  LOAD_METHOD              find_entry_posture_spec
               20  LOAD_DEREF               'sim'
               22  LOAD_FAST                'middle_path'
               24  LOAD_FAST                'var_map'
               26  CALL_METHOD_3         3  '3 positional arguments'
               28  UNPACK_SEQUENCE_3     3 
               30  STORE_FAST               'entry_spec'
               32  STORE_FAST               'constrained_edge'
               34  STORE_FAST               'carry_spec'

 L.6143        36  LOAD_FAST                'var_map'
               38  LOAD_GLOBAL              PostureSpecVariable
               40  LOAD_ATTR                CARRY_TARGET
               42  BINARY_SUBSCR    
               44  STORE_DEREF              'carry_target'

 L.6145        46  LOAD_FAST                'constrained_edge'
               48  LOAD_CONST               None
               50  COMPARE_OP               is
               52  POP_JUMP_IF_FALSE   130  'to 130'

 L.6146        54  LOAD_DEREF               'carry_target'
               56  LOAD_CONST               None
               58  COMPARE_OP               is-not
               60  POP_JUMP_IF_FALSE    88  'to 88'
               62  LOAD_DEREF               'carry_target'
               64  LOAD_METHOD              is_in_sim_inventory
               66  CALL_METHOD_0         0  '0 positional arguments'
               68  POP_JUMP_IF_FALSE    88  'to 88'

 L.6150        70  LOAD_FAST                'self'
               72  LOAD_METHOD              copy_handles
               74  LOAD_DEREF               'sim'
               76  LOAD_FAST                'middle_handles'
               78  LOAD_FAST                'middle_path'
               80  LOAD_FAST                'var_map'
               82  CALL_METHOD_4         4  '4 positional arguments'
               84  POP_TOP          
               86  JUMP_FORWARD        632  'to 632'
             88_0  COME_FROM            68  '68'
             88_1  COME_FROM            60  '60'

 L.6162        88  LOAD_GLOBAL              PostureGraphMiddlePathError

 L.6173        90  LOAD_STR                 '\n                   Have a middle path to pick up an object that is not in the\n                   inventory and we cannot generate a constrained_edge:\n                    \n                   carry target: {}\n                   interaction: {}\n                   final constraint: {}\n                   dest spec: {}\n                   entry spec: {}\n                   sim location: {}\n                   carry target location: {}\n                   '
               92  LOAD_METHOD              format
               94  LOAD_DEREF               'carry_target'
               96  LOAD_FAST                'interaction'
               98  LOAD_FAST                'final_constraint'

 L.6174       100  LOAD_FAST                'destination_spec'
              102  LOAD_FAST                'entry_spec'
              104  LOAD_DEREF               'sim'
              106  LOAD_ATTR                location

 L.6175       108  LOAD_DEREF               'carry_target'
              110  POP_JUMP_IF_FALSE   118  'to 118'
              112  LOAD_DEREF               'carry_target'
              114  LOAD_ATTR                location
              116  JUMP_FORWARD        120  'to 120'
            118_0  COME_FROM           110  '110'
              118  LOAD_STR                 'NO CARRY TARGET'
            120_0  COME_FROM           116  '116'
              120  CALL_METHOD_7         7  '7 positional arguments'
              122  CALL_FUNCTION_1       1  '1 positional argument'
              124  RAISE_VARARGS_1       1  'exception instance'
          126_128  JUMP_FORWARD        632  'to 632'
            130_0  COME_FROM            52  '52'

 L.6180       130  LOAD_FAST                'constrained_edge'
              132  LOAD_METHOD              get_constraint
              134  LOAD_DEREF               'sim'
              136  LOAD_FAST                'carry_spec'
              138  LOAD_FAST                'var_map'
              140  CALL_METHOD_3         3  '3 positional arguments'
              142  STORE_FAST               'carry_transition_constraint'

 L.6182       144  LOAD_DEREF               'carry_target'
              146  LOAD_CONST               None
              148  COMPARE_OP               is-not
              150  POP_JUMP_IF_FALSE   178  'to 178'
              152  LOAD_DEREF               'carry_target'
              154  LOAD_ATTR                is_sim
              156  POP_JUMP_IF_FALSE   178  'to 178'

 L.6183       158  LOAD_FAST                'animation_resolver_fn'
              160  STORE_DEREF              '_animation_resolver_fn'

 L.6198       162  LOAD_CLOSURE             '_animation_resolver_fn'
              164  LOAD_CLOSURE             'carry_target'
              166  LOAD_CLOSURE             'sim'
              168  BUILD_TUPLE_3         3 
              170  LOAD_CODE                <code_object animation_resolver_fn>
              172  LOAD_STR                 'PostureGraphService._generate_middle_handles.<locals>.animation_resolver_fn'
              174  MAKE_FUNCTION_8          'closure'
              176  STORE_FAST               'animation_resolver_fn'
            178_0  COME_FROM           156  '156'
            178_1  COME_FROM           150  '150'

 L.6208       178  LOAD_FAST                'carry_transition_constraint'
              180  LOAD_CONST               None
              182  COMPARE_OP               is-not
          184_186  POP_JUMP_IF_FALSE   358  'to 358'

 L.6209       188  BUILD_LIST_0          0 
              190  STORE_FAST               'carry_transition_constraints'

 L.6210       192  SETUP_LOOP          350  'to 350'
              194  LOAD_FAST                'carry_transition_constraint'
              196  GET_ITER         
              198  FOR_ITER            348  'to 348'
              200  STORE_FAST               'carry_transition_sub_constraint'

 L.6211       202  LOAD_DEREF               'carry_target'
              204  LOAD_CONST               None
              206  COMPARE_OP               is-not
          208_210  POP_JUMP_IF_FALSE   288  'to 288'
              212  LOAD_DEREF               'carry_target'
              214  LOAD_ATTR                is_sim
          216_218  POP_JUMP_IF_FALSE   288  'to 288'

 L.6215       220  LOAD_FAST                'interaction'
              222  LOAD_ATTR                transition
              224  LOAD_METHOD              add_on_target_location_changed_callback
              226  LOAD_DEREF               'carry_target'
              228  CALL_METHOD_1         1  '1 positional argument'
              230  POP_TOP          

 L.6217       232  LOAD_FAST                'carry_transition_sub_constraint'
              234  LOAD_ATTR                posture_state_spec
              236  LOAD_CONST               None
              238  COMPARE_OP               is-not
          240_242  POP_JUMP_IF_FALSE   288  'to 288'

 L.6218       244  LOAD_FAST                'carry_transition_sub_constraint'
              246  LOAD_ATTR                posture_state_spec
              248  LOAD_ATTR                body_target
              250  STORE_FAST               'carry_body_target'

 L.6219       252  LOAD_FAST                'carry_body_target'
              254  LOAD_CONST               None
              256  COMPARE_OP               is-not
          258_260  POP_JUMP_IF_FALSE   288  'to 288'

 L.6227       262  LOAD_GLOBAL              PostureAspectBody
              264  LOAD_FAST                'carry_spec'
              266  LOAD_ATTR                body
              268  LOAD_ATTR                posture_type
              270  LOAD_FAST                'carry_body_target'
              272  CALL_FUNCTION_2       2  '2 positional arguments'
              274  STORE_FAST               'body_aspect'

 L.6228       276  LOAD_FAST                'carry_spec'
              278  LOAD_ATTR                clone
              280  LOAD_FAST                'body_aspect'
              282  LOAD_CONST               ('body',)
              284  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              286  STORE_FAST               'carry_spec'
            288_0  COME_FROM           258  '258'
            288_1  COME_FROM           240  '240'
            288_2  COME_FROM           216  '216'
            288_3  COME_FROM           208  '208'

 L.6231       288  LOAD_GLOBAL              postures
              290  LOAD_ATTR                posture_state
              292  LOAD_ATTR                PostureState
              294  LOAD_DEREF               'sim'
              296  LOAD_CONST               None
              298  LOAD_FAST                'carry_spec'

 L.6232       300  LOAD_FAST                'var_map'
              302  LOAD_CONST               True
              304  LOAD_CONST               ('invalid_expected',)
              306  CALL_FUNCTION_KW_5     5  '5 total positional and keyword args'
              308  STORE_FAST               'target_posture_state'

 L.6237       310  LOAD_FAST                'interaction'
              312  LOAD_ATTR                transition
              314  LOAD_METHOD              add_relevant_object
              316  LOAD_FAST                'target_posture_state'
              318  LOAD_ATTR                body_target
              320  CALL_METHOD_1         1  '1 positional argument'
              322  POP_TOP          

 L.6239       324  LOAD_FAST                'carry_transition_sub_constraint'
              326  LOAD_METHOD              apply_posture_state

 L.6240       328  LOAD_FAST                'target_posture_state'
              330  LOAD_FAST                'animation_resolver_fn'
              332  CALL_METHOD_2         2  '2 positional arguments'
              334  STORE_FAST               'carry_transition_sub_constraint'

 L.6241       336  LOAD_FAST                'carry_transition_constraints'
              338  LOAD_METHOD              append
              340  LOAD_FAST                'carry_transition_sub_constraint'
              342  CALL_METHOD_1         1  '1 positional argument'
              344  POP_TOP          
              346  JUMP_BACK           198  'to 198'
              348  POP_BLOCK        
            350_0  COME_FROM_LOOP      192  '192'

 L.6242       350  LOAD_GLOBAL              create_constraint_set
              352  LOAD_FAST                'carry_transition_constraints'
              354  CALL_FUNCTION_1       1  '1 positional argument'
              356  STORE_FAST               'carry_transition_constraint'
            358_0  COME_FROM           184  '184'

 L.6244       358  LOAD_FAST                'carry_transition_constraint'
              360  LOAD_CONST               None
              362  COMPARE_OP               is-not
          364_366  POP_JUMP_IF_FALSE   632  'to 632'

 L.6245       368  LOAD_GLOBAL              any
              370  LOAD_GENEXPR             '<code_object <genexpr>>'
              372  LOAD_STR                 'PostureGraphService._generate_middle_handles.<locals>.<genexpr>'
              374  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              376  LOAD_FAST                'carry_transition_constraint'
              378  GET_ITER         
              380  CALL_FUNCTION_1       1  '1 positional argument'
              382  CALL_FUNCTION_1       1  '1 positional argument'
              384  STORE_FAST               'constraint_has_geometry'

 L.6246       386  LOAD_FAST                'constraint_has_geometry'
          388_390  POP_JUMP_IF_TRUE    448  'to 448'

 L.6252       392  LOAD_GLOBAL              services
              394  LOAD_METHOD              current_zone
              396  CALL_METHOD_0         0  '0 positional arguments'
              398  LOAD_ATTR                posture_graph_service
              400  STORE_FAST               'posture_graph_service'

 L.6253       402  LOAD_FAST                'posture_graph_service'
              404  LOAD_METHOD              get_compatible_mobile_posture_target
              406  LOAD_DEREF               'sim'
              408  CALL_METHOD_1         1  '1 positional argument'
              410  STORE_FAST               'posture_object'

 L.6254       412  LOAD_FAST                'posture_object'
              414  LOAD_CONST               None
              416  COMPARE_OP               is-not
          418_420  POP_JUMP_IF_FALSE   448  'to 448'

 L.6255       422  LOAD_FAST                'posture_object'
              424  LOAD_ATTR                get_edge_constraint
              426  LOAD_DEREF               'sim'
              428  LOAD_CONST               ('sim',)
              430  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              432  STORE_FAST               'edge_constraint'

 L.6256       434  LOAD_FAST                'carry_transition_constraint'
              436  LOAD_METHOD              intersect
              438  LOAD_FAST                'edge_constraint'
              440  CALL_METHOD_1         1  '1 positional argument'
              442  STORE_FAST               'carry_transition_constraint'

 L.6257       444  LOAD_CONST               True
              446  STORE_FAST               'constraint_has_geometry'
            448_0  COME_FROM           418  '418'
            448_1  COME_FROM           388  '388'

 L.6261       448  LOAD_FAST                'carry_spec'
              450  LOAD_ATTR                surface
              452  STORE_FAST               'carry_spec_surface_spec'

 L.6262       454  LOAD_FAST                'carry_spec_surface_spec'
              456  LOAD_CONST               None
              458  COMPARE_OP               is-not
          460_462  POP_JUMP_IF_FALSE   472  'to 472'

 L.6263       464  LOAD_FAST                'carry_spec_surface_spec'
              466  LOAD_ATTR                target
              468  STORE_FAST               'relative_object'
              470  JUMP_FORWARD        476  'to 476'
            472_0  COME_FROM           460  '460'

 L.6265       472  LOAD_CONST               None
              474  STORE_FAST               'relative_object'
            476_0  COME_FROM           470  '470'

 L.6266       476  LOAD_FAST                'relative_object'
              478  LOAD_CONST               None
              480  COMPARE_OP               is
          482_484  POP_JUMP_IF_FALSE   494  'to 494'

 L.6267       486  LOAD_FAST                'carry_spec'
              488  LOAD_ATTR                body
              490  LOAD_ATTR                target
              492  STORE_FAST               'relative_object'
            494_0  COME_FROM           482  '482'

 L.6268       494  LOAD_FAST                'relative_object'
              496  LOAD_CONST               None
              498  COMPARE_OP               is
          500_502  POP_JUMP_IF_FALSE   534  'to 534'

 L.6269       504  LOAD_FAST                'entry_spec'
              506  LOAD_ATTR                carry
              508  LOAD_ATTR                target
              510  STORE_FAST               'relative_object'

 L.6270       512  LOAD_GLOBAL              isinstance
              514  LOAD_FAST                'relative_object'
              516  LOAD_GLOBAL              PostureSpecVariable
              518  CALL_FUNCTION_2       2  '2 positional arguments'
          520_522  POP_JUMP_IF_FALSE   534  'to 534'

 L.6271       524  LOAD_FAST                'var_map'
              526  LOAD_METHOD              get
              528  LOAD_FAST                'relative_object'
              530  CALL_METHOD_1         1  '1 positional argument'
              532  STORE_FAST               'relative_object'
            534_0  COME_FROM           520  '520'
            534_1  COME_FROM           500  '500'

 L.6280       534  LOAD_FAST                'constraint_has_geometry'
          536_538  POP_JUMP_IF_FALSE   616  'to 616'

 L.6281       540  LOAD_FAST                'carry_transition_constraint'
              542  LOAD_ATTR                generate_single_surface_constraints
              544  LOAD_FAST                'relative_object'
              546  LOAD_ATTR                override_multi_surface_constraints
              548  LOAD_CONST               ('override_multi_surface',)
              550  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              552  STORE_FAST               'carry_transition_constraint'

 L.6282       554  LOAD_FAST                'self'
              556  LOAD_ATTR                append_handles

 L.6283       558  LOAD_DEREF               'sim'
              560  LOAD_FAST                'middle_handles'
              562  LOAD_FAST                'invalid'
              564  LOAD_FAST                'invalid_los'

 L.6284       566  LOAD_FAST                'carry_transition_constraint'
              568  LOAD_CONST               None
              570  LOAD_FAST                'relative_object'
              572  BUILD_TUPLE_3         3 

 L.6285       574  LOAD_FAST                'middle_path'
              576  LOAD_FAST                'var_map'
              578  LOAD_FAST                'destination_spec'
              580  LOAD_FAST                'unique_id'

 L.6286       582  LOAD_FAST                'final_constraint'
              584  LOAD_GLOBAL              PathType
              586  LOAD_ATTR                MIDDLE_LEFT
              588  LOAD_CONST               ('path_type',)
            590_0  COME_FROM            86  '86'
              590  CALL_FUNCTION_KW_11    11  '11 total positional and keyword args'
              592  STORE_FAST               'blocking_obj_id'

 L.6287       594  LOAD_FAST                'blocking_obj_id'
              596  LOAD_CONST               None
              598  COMPARE_OP               is-not
          600_602  POP_JUMP_IF_FALSE   632  'to 632'

 L.6288       604  LOAD_FAST                'blocking_obj_ids'
              606  LOAD_METHOD              append
              608  LOAD_FAST                'blocking_obj_id'
              610  CALL_METHOD_1         1  '1 positional argument'
              612  POP_TOP          
              614  JUMP_FORWARD        632  'to 632'
            616_0  COME_FROM           536  '536'

 L.6290       616  LOAD_FAST                'self'
              618  LOAD_METHOD              copy_handles
              620  LOAD_DEREF               'sim'
              622  LOAD_FAST                'middle_handles'
              624  LOAD_FAST                'middle_path'
              626  LOAD_FAST                'var_map'
              628  CALL_METHOD_4         4  '4 positional arguments'
              630  POP_TOP          
            632_0  COME_FROM           614  '614'
            632_1  COME_FROM           600  '600'
            632_2  COME_FROM           364  '364'
            632_3  COME_FROM           126  '126'

 L.6291       632  LOAD_FAST                'middle_handles'
              634  LOAD_FAST                'invalid'
              636  LOAD_FAST                'invalid_los'
              638  LOAD_FAST                'blocking_obj_ids'
              640  BUILD_TUPLE_4         4 
              642  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM' instruction at offset 590_0

    def _get_segmented_path_connectivity_handles(self, sim, segmented_path, interaction, participant_type, animation_resolver_fn, sim_position_routing_data, force_carry_path):
        blocking_obj_ids = []
        searched = {PathType.LEFT: set(), PathType.RIGHT: set()}
        middle_handles, invalid_middles, invalid_los_middles = {}, {}, {}
        destination_handles, invalid_destinations, invalid_los_destinations = {}, {}, {}
        source_handles, invalid_sources, invalid_los_sources = {}, {}, {}
        for path_left in segmented_path.generate_left_paths(force_carry_path):
            final_left_node = path_left[-1]
            if final_left_node in searched[PathType.LEFT]:
                continue
            source_handles, invalid_sources, invalid_los_sources, blockers = self._generate_left_handles(sim, interaction, participant_type, path_left, segmented_path.var_map, None, segmented_path.constraint, id(segmented_path), sim_position_routing_data)
            blocking_obj_ids += blockers
            if not source_handles:
                continue
            searched[PathType.LEFT].add(final_left_node)
            for path_right in segmented_path.generate_right_paths(sim, path_left):
                entry_node, _, _ = self.find_entry_posture_spec(sim, path_right, segmented_path.var_map)
                if entry_node is not None:
                    if entry_node.body_target in searched[PathType.RIGHT]:
                        continue
                    else:
                        final_right_node = path_right[-1]
                        destination_spec = segmented_path.destination_specs[final_right_node]
                        destination_handles, invalid_destinations, invalid_los_destinations, blockers = self._generate_right_handles(sim, interaction, participant_type, path_right, segmented_path.var_map, destination_spec, segmented_path.constraint, id(segmented_path), animation_resolver_fn)
                        blocking_obj_ids += blockers
                        if not destination_handles:
                            continue
                        final_body_target = final_right_node.body_target
                        final_body_posture = final_right_node.body_posture
                        if final_body_target is not None:
                            if not final_body_posture.is_vehicle or final_body_posture is not final_left_node.body_posture:
                                posture = postures.create_posture(final_body_posture, sim,
                                  final_body_target, is_throwaway=True)
                                slot_constraint = posture.slot_constraint_simple
                                if slot_constraint is not None:
                                    geometry_constraint = segmented_path.constraint.generate_geometry_only_constraint()
                                    if not slot_constraint.intersect(geometry_constraint).valid:
                                        continue
                    if entry_node is not None:
                        searched[PathType.RIGHT].add(entry_node.body_target)
                    for path_middle in segmented_path.generate_middle_paths(path_left, path_right):
                        if path_middle is None:
                            return (
                             source_handles, {}, destination_handles,
                             invalid_sources, {}, invalid_destinations,
                             invalid_los_sources, {}, invalid_los_destinations,
                             blocking_obj_ids)
                            middle_handles, invalid_middles, invalid_los_middles, blockers = self._generate_middle_handles(sim, interaction, participant_type, path_middle, segmented_path.var_map_resolved, destination_spec, segmented_path.constraint, id(segmented_path), animation_resolver_fn)
                            blocking_obj_ids += blockers
                            if middle_handles:
                                return (
                                 source_handles, middle_handles, destination_handles,
                                 invalid_sources, invalid_middles, invalid_destinations,
                                 invalid_los_sources, invalid_los_middles, invalid_los_destinations,
                                 blocking_obj_ids)

                    if all((dest in searched[PathType.RIGHT] for dest in segmented_path.left_destinations)) or len(searched[PathType.RIGHT]) >= MAX_RIGHT_PATHS:
                        break

        return (
         source_handles, {}, {},
         invalid_sources, invalid_middles, invalid_destinations,
         invalid_los_sources, invalid_los_middles, invalid_los_destinations,
         blocking_obj_ids)

    def generate_connectivity_handles--- This code section failed: ---

 L.6422         0  LOAD_GLOBAL              len
                2  LOAD_FAST                'segmented_paths'
                4  CALL_FUNCTION_1       1  '1 positional argument'
                6  LOAD_CONST               0
                8  COMPARE_OP               ==
               10  POP_JUMP_IF_FALSE    16  'to 16'

 L.6423        12  LOAD_GLOBAL              NO_CONNECTIVITY
               14  RETURN_VALUE     
             16_0  COME_FROM            10  '10'

 L.6428        16  LOAD_GLOBAL              collections
               18  LOAD_METHOD              OrderedDict
               20  CALL_METHOD_0         0  '0 positional arguments'
               22  STORE_FAST               'source_destination_sets'

 L.6429        24  LOAD_GLOBAL              collections
               26  LOAD_METHOD              OrderedDict
               28  CALL_METHOD_0         0  '0 positional arguments'
               30  STORE_FAST               'source_middle_sets'

 L.6430        32  LOAD_GLOBAL              collections
               34  LOAD_METHOD              OrderedDict
               36  CALL_METHOD_0         0  '0 positional arguments'
               38  STORE_FAST               'middle_destination_sets'

 L.6431        40  LOAD_FAST                'self'
               42  LOAD_METHOD              get_sim_position_routing_data
               44  LOAD_FAST                'sim'
               46  CALL_METHOD_1         1  '1 positional argument'
               48  STORE_FAST               'sim_position_routing_data'

 L.6433        50  LOAD_GLOBAL              EMPTY_PATH_SPEC
               52  STORE_FAST               'best_complete_path'

 L.6436     54_56  SETUP_LOOP          454  'to 454'
               58  LOAD_FAST                'segmented_paths'
               60  GET_ITER         
            62_64  FOR_ITER            452  'to 452'
               66  STORE_FAST               'segmented_path'

 L.6437        68  LOAD_FAST                'segmented_path'
               70  LOAD_ATTR                is_complete
               72  POP_JUMP_IF_TRUE     76  'to 76'

 L.6438        74  CONTINUE             62  'to 62'
             76_0  COME_FROM            72  '72'

 L.6439     76_78  SETUP_LOOP          450  'to 450'
               80  LOAD_FAST                'segmented_path'
               82  LOAD_METHOD              generate_left_paths
               84  LOAD_FAST                'force_carry_path'
               86  CALL_METHOD_1         1  '1 positional argument'
               88  GET_ITER         
             90_0  COME_FROM           442  '442'
            90_92  FOR_ITER            448  'to 448'
               94  STORE_FAST               'left_path'

 L.6440     96_98  SETUP_LOOP          436  'to 436'
              100  LOAD_FAST                'segmented_path'
              102  LOAD_METHOD              generate_right_paths
              104  LOAD_FAST                'sim'
              106  LOAD_FAST                'left_path'
              108  CALL_METHOD_2         2  '2 positional arguments'
              110  GET_ITER         
          112_114  FOR_ITER            434  'to 434'
              116  STORE_FAST               'right_path'

 L.6442       118  LOAD_FAST                'left_path'
              120  LOAD_FAST                'right_path'
              122  BINARY_ADD       
              124  STORE_FAST               'complete_path'

 L.6443       126  LOAD_FAST                'self'
              128  LOAD_METHOD              is_valid_complete_path
              130  LOAD_FAST                'sim'
              132  LOAD_FAST                'complete_path'
              134  LOAD_FAST                'interaction'
              136  CALL_METHOD_3         3  '3 positional arguments'
              138  POP_JUMP_IF_TRUE    142  'to 142'

 L.6445       140  CONTINUE            112  'to 112'
            142_0  COME_FROM           138  '138'

 L.6447       142  LOAD_FAST                'best_complete_path'
              144  LOAD_GLOBAL              EMPTY_PATH_SPEC
              146  COMPARE_OP               is-not
              148  POP_JUMP_IF_FALSE   164  'to 164'

 L.6448       150  LOAD_FAST                'best_complete_path'
              152  LOAD_ATTR                cost
              154  LOAD_FAST                'complete_path'
              156  LOAD_ATTR                cost
              158  COMPARE_OP               <=
              160  POP_JUMP_IF_FALSE   164  'to 164'

 L.6452       162  BREAK_LOOP       
            164_0  COME_FROM           160  '160'
            164_1  COME_FROM           148  '148'

 L.6454       164  LOAD_FAST                'complete_path'
              166  LOAD_CONST               -1
              168  BINARY_SUBSCR    
              170  STORE_FAST               'final_node'

 L.6461       172  LOAD_FAST                'interaction'
              174  LOAD_ATTR                privacy
              176  LOAD_CONST               None
              178  COMPARE_OP               is-not
              180  POP_JUMP_IF_FALSE   204  'to 204'
              182  LOAD_GLOBAL              len
              184  LOAD_FAST                'complete_path'
              186  CALL_FUNCTION_1       1  '1 positional argument'
              188  LOAD_CONST               1
              190  COMPARE_OP               ==
              192  POP_JUMP_IF_FALSE   204  'to 204'

 L.6462       194  LOAD_FAST                'complete_path'
              196  LOAD_METHOD              append
              198  LOAD_FAST                'final_node'
              200  CALL_METHOD_1         1  '1 positional argument'
              202  POP_TOP          
            204_0  COME_FROM           192  '192'
            204_1  COME_FROM           180  '180'

 L.6464       204  LOAD_FAST                'segmented_path'
              206  LOAD_ATTR                destination_specs
              208  LOAD_FAST                'final_node'
              210  BINARY_SUBSCR    
              212  STORE_FAST               'destination_spec'

 L.6465       214  LOAD_FAST                'self'
              216  LOAD_METHOD              _get_resolved_var_map
              218  LOAD_FAST                'complete_path'
              220  LOAD_FAST                'segmented_path'
              222  LOAD_ATTR                var_map
              224  CALL_METHOD_2         2  '2 positional arguments'
              226  STORE_FAST               'var_map'

 L.6466       228  LOAD_FAST                'segmented_path'
              230  LOAD_ATTR                constraint
              232  STORE_FAST               'constraint'

 L.6468       234  LOAD_GLOBAL              len
              236  LOAD_FAST                'complete_path'
              238  CALL_FUNCTION_1       1  '1 positional argument'
              240  LOAD_CONST               1
              242  COMPARE_OP               ==
          244_246  POP_JUMP_IF_FALSE   312  'to 312'

 L.6472       248  LOAD_CONST               None
              250  STORE_FAST               'transform_constraint'

 L.6473       252  LOAD_FAST                'sim'
              254  LOAD_ATTR                posture
              256  LOAD_ATTR                mobile
          258_260  POP_JUMP_IF_TRUE    270  'to 270'

 L.6476       262  LOAD_FAST                'sim'
              264  LOAD_ATTR                posture
              266  LOAD_ATTR                slot_constraint
              268  STORE_FAST               'transform_constraint'
            270_0  COME_FROM           258  '258'

 L.6477       270  LOAD_FAST                'transform_constraint'
              272  LOAD_CONST               None
              274  COMPARE_OP               is
          276_278  POP_JUMP_IF_FALSE   300  'to 300'

 L.6479       280  LOAD_GLOBAL              interactions
              282  LOAD_ATTR                constraints
              284  LOAD_ATTR                Transform

 L.6480       286  LOAD_FAST                'sim'
              288  LOAD_ATTR                transform
              290  LOAD_FAST                'sim'
              292  LOAD_ATTR                routing_surface
              294  LOAD_CONST               ('routing_surface',)
              296  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              298  STORE_FAST               'transform_constraint'
            300_0  COME_FROM           276  '276'

 L.6482       300  LOAD_FAST                'constraint'
              302  LOAD_METHOD              intersect
              304  LOAD_FAST                'transform_constraint'
              306  CALL_METHOD_1         1  '1 positional argument'
              308  STORE_FAST               'final_constraint'
              310  JUMP_FORWARD        352  'to 352'
            312_0  COME_FROM           244  '244'

 L.6488       312  LOAD_FAST                'self'
              314  LOAD_ATTR                _get_locations_from_posture

 L.6489       316  LOAD_FAST                'sim'
              318  LOAD_FAST                'complete_path'
              320  LOAD_CONST               -1
              322  BINARY_SUBSCR    
              324  LOAD_FAST                'var_map'
              326  LOAD_FAST                'interaction'

 L.6490       328  LOAD_FAST                'participant_type'

 L.6491       330  LOAD_FAST                'animation_resolver_fn'

 L.6492       332  LOAD_FAST                'constraint'
              334  LOAD_CONST               ('interaction', 'participant_type', 'animation_resolver_fn', 'final_constraint')
              336  CALL_FUNCTION_KW_7     7  '7 total positional and keyword args'
              338  UNPACK_SEQUENCE_2     2 
              340  STORE_FAST               '_'
              342  STORE_FAST               'routing_data'

 L.6494       344  LOAD_FAST                'routing_data'
              346  LOAD_CONST               0
              348  BINARY_SUBSCR    
              350  STORE_FAST               'final_constraint'
            352_0  COME_FROM           310  '310'

 L.6496       352  LOAD_FAST                'final_constraint'
              354  LOAD_CONST               None
              356  COMPARE_OP               is-not
          358_360  POP_JUMP_IF_FALSE   372  'to 372'
              362  LOAD_FAST                'final_constraint'
              364  LOAD_ATTR                valid
          366_368  POP_JUMP_IF_TRUE    372  'to 372'

 L.6497       370  CONTINUE            112  'to 112'
            372_0  COME_FROM           366  '366'
            372_1  COME_FROM           358  '358'

 L.6498       372  LOAD_FAST                'final_constraint'
              374  LOAD_CONST               None
              376  COMPARE_OP               is
          378_380  POP_JUMP_IF_FALSE   386  'to 386'

 L.6499       382  LOAD_FAST                'constraint'
              384  STORE_FAST               'final_constraint'
            386_0  COME_FROM           378  '378'

 L.6500       386  LOAD_GLOBAL              PathSpec

 L.6501       388  LOAD_FAST                'complete_path'
              390  LOAD_FAST                'complete_path'
              392  LOAD_ATTR                cost
              394  LOAD_FAST                'var_map'
              396  LOAD_FAST                'destination_spec'

 L.6502       398  LOAD_FAST                'final_constraint'
              400  LOAD_FAST                'constraint'
              402  LOAD_CONST               True
              404  LOAD_CONST               ('allow_tentative',)
              406  CALL_FUNCTION_KW_7     7  '7 total positional and keyword args'
              408  STORE_FAST               'best_complete_path'

 L.6504       410  LOAD_FAST                'self'
              412  LOAD_ATTR                _generate_surface_and_slot_targets

 L.6505       414  LOAD_FAST                'best_complete_path'
              416  LOAD_CONST               None
              418  LOAD_FAST                'sim'
              420  LOAD_ATTR                routing_location
              422  LOAD_GLOBAL              DEFAULT
              424  LOAD_CONST               ('objects_to_ignore',)
              426  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
              428  POP_TOP          

 L.6509       430  BREAK_LOOP       
              432  JUMP_BACK           112  'to 112'
              434  POP_BLOCK        
            436_0  COME_FROM_LOOP       96  '96'

 L.6513       436  LOAD_FAST                'best_complete_path'
              438  LOAD_GLOBAL              EMPTY_PATH_SPEC
              440  COMPARE_OP               is-not
              442  POP_JUMP_IF_FALSE    90  'to 90'

 L.6514       444  BREAK_LOOP       
              446  JUMP_BACK            90  'to 90'
              448  POP_BLOCK        
            450_0  COME_FROM_LOOP       76  '76'
              450  JUMP_BACK            62  'to 62'
              452  POP_BLOCK        
            454_0  COME_FROM_LOOP       54  '54'

 L.6517       454  BUILD_LIST_0          0 
              456  STORE_FAST               'blocking_obj_ids'

 L.6519   458_460  SETUP_LOOP          740  'to 740'
              462  LOAD_FAST                'segmented_paths'
              464  GET_ITER         
          466_468  FOR_ITER            738  'to 738'
              470  STORE_FAST               'segmented_path'

 L.6520       472  LOAD_FAST                'segmented_path'
              474  LOAD_ATTR                is_complete
          476_478  POP_JUMP_IF_FALSE   484  'to 484'

 L.6521   480_482  CONTINUE            466  'to 466'
            484_0  COME_FROM           476  '476'

 L.6523       484  SETUP_EXCEPT        512  'to 512'

 L.6524       486  LOAD_FAST                'self'
              488  LOAD_METHOD              _get_segmented_path_connectivity_handles

 L.6525       490  LOAD_FAST                'sim'
              492  LOAD_FAST                'segmented_path'
              494  LOAD_FAST                'interaction'
              496  LOAD_FAST                'participant_type'

 L.6526       498  LOAD_FAST                'animation_resolver_fn'
              500  LOAD_FAST                'sim_position_routing_data'
              502  LOAD_FAST                'force_carry_path'
              504  CALL_METHOD_7         7  '7 positional arguments'
              506  STORE_FAST               'handles'
              508  POP_BLOCK        
              510  JUMP_FORWARD        534  'to 534'
            512_0  COME_FROM_EXCEPT    484  '484'

 L.6527       512  DUP_TOP          
              514  LOAD_GLOBAL              PostureGraphError
              516  COMPARE_OP               exception-match
          518_520  POP_JUMP_IF_FALSE   532  'to 532'
              522  POP_TOP          
              524  POP_TOP          
              526  POP_TOP          

 L.6528       528  LOAD_GLOBAL              NO_CONNECTIVITY
              530  RETURN_VALUE     
            532_0  COME_FROM           518  '518'
              532  END_FINALLY      
            534_0  COME_FROM           510  '510'

 L.6533       534  LOAD_FAST                'handles'
              536  UNPACK_SEQUENCE_10    10 
              538  STORE_FAST               'source_handles'
              540  STORE_FAST               'middle_handles'
              542  STORE_DEREF              'destination_handles'
              544  STORE_FAST               'invalid_sources'
              546  STORE_FAST               'invalid_middles'
              548  STORE_FAST               'invalid_destinations'
              550  STORE_FAST               'invalid_los_sources'
              552  STORE_FAST               'invalid_los_middles'
              554  STORE_FAST               'invalid_los_destinations'
              556  STORE_FAST               'blockers'

 L.6536       558  LOAD_FAST                'blocking_obj_ids'
              560  LOAD_FAST                'blockers'
              562  INPLACE_ADD      
              564  STORE_FAST               'blocking_obj_ids'

 L.6541       566  LOAD_FAST                'middle_handles'
          568_570  POP_JUMP_IF_FALSE   622  'to 622'

 L.6542       572  LOAD_FAST                'source_handles'
              574  LOAD_FAST                'middle_handles'

 L.6543       576  BUILD_MAP_0           0 
              578  BUILD_MAP_0           0 

 L.6544       580  LOAD_FAST                'invalid_middles'
              582  LOAD_FAST                'invalid_los_middles'
              584  BUILD_TUPLE_6         6 
              586  STORE_FAST               'value'

 L.6545       588  LOAD_FAST                'value'
              590  LOAD_FAST                'source_middle_sets'
              592  LOAD_FAST                'segmented_path'
              594  STORE_SUBSCR     

 L.6547       596  LOAD_CONST               None
              598  LOAD_DEREF               'destination_handles'
              600  LOAD_FAST                'invalid_middles'

 L.6548       602  LOAD_FAST                'invalid_los_middles'
              604  LOAD_FAST                'invalid_destinations'

 L.6549       606  LOAD_FAST                'invalid_los_destinations'
              608  BUILD_LIST_6          6 
              610  STORE_FAST               'value'

 L.6550       612  LOAD_FAST                'value'
              614  LOAD_FAST                'middle_destination_sets'
              616  LOAD_FAST                'segmented_path'
              618  STORE_SUBSCR     
              620  JUMP_BACK           466  'to 466'
            622_0  COME_FROM           568  '568'

 L.6555       622  LOAD_GLOBAL              DEFAULT
              624  LOAD_DEREF               'destination_handles'
              626  COMPARE_OP               in
          628_630  POP_JUMP_IF_FALSE   710  'to 710'

 L.6556       632  LOAD_CLOSURE             'destination_handles'
              634  BUILD_TUPLE_1         1 
              636  LOAD_DICTCOMP            '<code_object <dictcomp>>'
              638  LOAD_STR                 'PostureGraphService.generate_connectivity_handles.<locals>.<dictcomp>'
              640  MAKE_FUNCTION_8          'closure'

 L.6557       642  LOAD_FAST                'source_handles'
              644  GET_ITER         
              646  CALL_FUNCTION_1       1  '1 positional argument'
              648  STORE_FAST               'default_values'

 L.6558       650  SETUP_LOOP          694  'to 694'
              652  LOAD_FAST                'default_values'
              654  LOAD_METHOD              items
              656  CALL_METHOD_0         0  '0 positional arguments'
              658  GET_ITER         
              660  FOR_ITER            692  'to 692'
              662  UNPACK_SEQUENCE_2     2 
              664  STORE_FAST               'dest_handle'
              666  UNPACK_SEQUENCE_7     7 
              668  STORE_FAST               'dest_path'
              670  STORE_FAST               '_'
              672  STORE_FAST               '_'
              674  STORE_FAST               '_'
              676  STORE_FAST               '_'
              678  STORE_FAST               '_'
              680  STORE_FAST               '_'

 L.6559       682  LOAD_FAST                'dest_path'
              684  LOAD_FAST                'dest_handle'
              686  STORE_ATTR               path
          688_690  JUMP_BACK           660  'to 660'
              692  POP_BLOCK        
            694_0  COME_FROM_LOOP      650  '650'

 L.6560       694  LOAD_DEREF               'destination_handles'
              696  LOAD_GLOBAL              DEFAULT
              698  DELETE_SUBSCR    

 L.6561       700  LOAD_DEREF               'destination_handles'
              702  LOAD_METHOD              update
              704  LOAD_FAST                'default_values'
              706  CALL_METHOD_1         1  '1 positional argument'
              708  POP_TOP          
            710_0  COME_FROM           628  '628'

 L.6562       710  LOAD_FAST                'source_handles'
              712  LOAD_DEREF               'destination_handles'

 L.6563       714  BUILD_MAP_0           0 
              716  BUILD_MAP_0           0 

 L.6564       718  LOAD_FAST                'invalid_destinations'
              720  LOAD_FAST                'invalid_los_destinations'
              722  BUILD_TUPLE_6         6 
              724  STORE_FAST               'value'

 L.6565       726  LOAD_FAST                'value'
              728  LOAD_FAST                'source_destination_sets'
              730  LOAD_FAST                'segmented_path'
              732  STORE_SUBSCR     
          734_736  JUMP_BACK           466  'to 466'
              738  POP_BLOCK        
            740_0  COME_FROM_LOOP      458  '458'

 L.6567       740  LOAD_FAST                'best_complete_path'
              742  LOAD_GLOBAL              EMPTY_PATH_SPEC
              744  COMPARE_OP               is
          746_748  POP_JUMP_IF_FALSE   818  'to 818'

 L.6568       750  LOAD_FAST                'source_destination_sets'
          752_754  POP_JUMP_IF_TRUE    818  'to 818'
              756  LOAD_FAST                'source_middle_sets'
          758_760  POP_JUMP_IF_FALSE   768  'to 768'
              762  LOAD_FAST                'middle_destination_sets'
          764_766  POP_JUMP_IF_TRUE    818  'to 818'
            768_0  COME_FROM           758  '758'

 L.6569       768  LOAD_FAST                'blocking_obj_ids'
          770_772  POP_JUMP_IF_FALSE   800  'to 800'

 L.6570       774  LOAD_GLOBAL              set_transition_failure_reason
              776  LOAD_FAST                'sim'
              778  LOAD_GLOBAL              TransitionFailureReasons
              780  LOAD_ATTR                BLOCKING_OBJECT

 L.6571       782  LOAD_FAST                'blocking_obj_ids'
              784  LOAD_CONST               0
              786  BINARY_SUBSCR    

 L.6572       788  LOAD_FAST                'interaction'
              790  LOAD_ATTR                transition
              792  LOAD_CONST               ('target_id', 'transition_controller')
              794  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
              796  POP_TOP          
              798  JUMP_FORWARD        818  'to 818'
            800_0  COME_FROM           770  '770'

 L.6574       800  LOAD_GLOBAL              set_transition_failure_reason
              802  LOAD_FAST                'sim'
              804  LOAD_GLOBAL              TransitionFailureReasons
              806  LOAD_ATTR                NO_VALID_INTERSECTION

 L.6575       808  LOAD_FAST                'interaction'
              810  LOAD_ATTR                transition
              812  LOAD_CONST               ('transition_controller',)
              814  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              816  POP_TOP          
            818_0  COME_FROM           798  '798'
            818_1  COME_FROM           764  '764'
            818_2  COME_FROM           752  '752'
            818_3  COME_FROM           746  '746'

 L.6577       818  LOAD_GLOBAL              Connectivity
              820  LOAD_FAST                'best_complete_path'
              822  LOAD_FAST                'source_destination_sets'

 L.6578       824  LOAD_FAST                'source_middle_sets'
              826  LOAD_FAST                'middle_destination_sets'
              828  CALL_FUNCTION_4       4  '4 positional arguments'
              830  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `LOAD_DICTCOMP' instruction at offset 636

    def find_best_path_pair(self, interaction, sim, connectivity, timeline):
        best_complete_path, source_destination_sets, source_middle_sets, middle_destination_sets = connectivity
        success, best_non_complete_path = yield from self._find_best_path_pair(interaction, sim, source_destination_sets, source_middle_sets, middle_destination_sets, timeline)
        if best_complete_path is EMPTY_PATH_SPEC:
            if success == False:
                return (
                 success, best_non_complete_path)
        best_non_complete_path = best_non_complete_path.get_carry_sim_merged_path_spec()
        best_non_complete_path = best_non_complete_path.get_stand_to_carry_sim_direct_path_spec()
        if best_complete_path is EMPTY_PATH_SPEC:
            return (
             success, best_non_complete_path)
        if best_non_complete_path is EMPTY_PATH_SPEC:
            return (True, best_complete_path)
        force_complete = False
        if interaction.is_putdown and sim in (interaction.target, interaction.carry_target):
            force_complete = True
        else:
            for node in best_complete_path.path:
                if node.body_target is not None:
                    if node.body_target.is_sim:
                        for other_node in best_non_complete_path.path[1:]:
                            if node == other_node:
                                force_complete = True
                                break

                if force_complete:
                    break

        if not success or force_complete or best_complete_path.cost <= best_non_complete_path.total_cost:
            best_non_complete_path.cleanup_path_spec(sim)
            return (True, best_complete_path)
        return (success, best_non_complete_path)
        if False:
            yield None

    def _find_best_path_pair(self, interaction, sim, source_destination_sets, source_middle_sets, middle_destination_sets, timeline):
        source_dest_success = False
        source_dest_path_spec = EMPTY_PATH_SPEC
        source_dest_cost = cu.MAX_FLOAT
        middle_success = False
        middle_path_spec = EMPTY_PATH_SPEC
        middle_cost = cu.MAX_FLOAT
        if source_destination_sets:
            source_dest_success, source_dest_path_spec, _ = yield from self.get_best_path_between_handles(interaction, sim, source_destination_sets, timeline)
            source_dest_cost = source_dest_path_spec.total_cost
        elif middle_destination_sets:
            middle_success, middle_path_spec, selected_goal = yield from self.get_best_path_between_handles(interaction, sim, source_middle_sets, timeline, path_type=(PathType.MIDDLE_LEFT))
            if middle_path_spec.is_failure_path:
                if source_dest_success:
                    return (
                     source_dest_success, source_dest_path_spec)
                return (
                 middle_success, middle_path_spec)
            if middle_success:
                geometry = create_transform_geometry(selected_goal.location.transform)
                middle_handle = selected_goal.connectivity_handle.clone(routing_surface_override=(selected_goal.routing_surface_id),
                  geometry=geometry)
                middle_handle.path = middle_path = algos.Path(middle_path_spec.path[-1:])
                middle_path.segmented_path = selected_goal.connectivity_handle.path.segmented_path
                middle_handle.var_map = middle_path.segmented_path.var_map_resolved
                selected_goal.connectivity_handle = middle_handle
                middle_handle_set = {middle_handle: (middle_path,
                                 0, middle_path_spec.var_map,
                                 None,
                                 [
                                  selected_goal],
                                 None, None)}
                for middle_dest_set in middle_destination_sets.values():
                    middle_dest_set[0] = middle_handle_set

                middle_success, best_right_path_spec, _ = yield from self.get_best_path_between_handles(interaction, sim, middle_destination_sets, timeline, path_type=(PathType.MIDDLE_RIGHT))
                if middle_success:
                    middle_path_spec = middle_path_spec.combine(best_right_path_spec)
                    middle_cost = middle_path_spec.total_cost
                if source_dest_success == middle_success:
                    if source_dest_cost <= middle_cost:
                        result_success, result_path_spec = source_dest_success, source_dest_path_spec
            else:
                result_success, result_path_spec = middle_success, middle_path_spec
        else:
            if source_dest_success:
                result_success, result_path_spec = source_dest_success, source_dest_path_spec
            else:
                result_success, result_path_spec = middle_success, middle_path_spec
        return (
         result_success, result_path_spec)
        if False:
            yield None

    def _get_best_slot(self, slot_target, slot_types, obj, location, objects_to_ignore=DEFAULT):
        runtime_slots = tuple(slot_target.get_runtime_slots_gen(slot_types=slot_types))
        if not runtime_slots:
            return
        chosen_slot = None
        closest_distance = None
        for runtime_slot in runtime_slots:
            if runtime_slot.is_valid_for_placement(obj=obj, objects_to_ignore=objects_to_ignore):
                transform = runtime_slot.transform
                slot_routing_location = routing.Location(transform.translation, transform.orientation, runtime_slot.routing_surface)
                distance = (location - slot_routing_location.position).magnitude_2d_squared()
                if closest_distance is None or distance < closest_distance:
                    chosen_slot = runtime_slot
                    closest_distance = distance

        return chosen_slot

    def _generate_surface_and_slot_targets(self, path_spec_right, path_spec_left, final_sim_routing_location, objects_to_ignore):
        slot_var = path_spec_right.var_map.get(PostureSpecVariable.SLOT)
        if slot_var is None:
            return True
        slot_target = slot_var.target
        if isinstance(slot_target, PostureSpecVariable):
            return False
        chosen_slot = self._get_best_slot(slot_target, slot_var.slot_types, slot_var.actor, final_sim_routing_location.position, objects_to_ignore)
        if chosen_slot is None:
            return False
        path_spec_right._final_constraint = path_spec_right.final_constraint.generate_constraint_with_slot_info(slot_var.actor, slot_target, chosen_slot)
        path_spec_right._spec_constraint = path_spec_right.spec_constraint.generate_constraint_with_slot_info(slot_var.actor, slot_target, chosen_slot)

        def get_frozen_manifest_entry():
            for constraint in path_spec_right.spec_constraint:
                if constraint.posture_state_spec is not None:
                    for manifest_entry in constraint.posture_state_spec.slot_manifest:
                        return manifest_entry

            raise AssertionError('Spec constraint with no manifest entries: {}'.format(path_spec_right.spec_constraint))

        frozen_manifest_entry = get_frozen_manifest_entry()

        def replace_var_map_for_path_spec(path_spec):
            for spec in path_spec.transition_specs:
                if PostureSpecVariable.SLOT in spec.var_map:
                    new_var_map = {}
                    new_var_map[PostureSpecVariable.SLOT] = frozen_manifest_entry
                    spec.var_map = frozendict(spec.var_map, new_var_map)

        replace_var_map_for_path_spec(path_spec_right)
        if path_spec_left is not None:
            replace_var_map_for_path_spec(path_spec_left)
        return True

    def _valid_vehicle_dest_handle(self, dest, cost, in_vehicle_posture):
        if not sims4.math.almost_equal(cost, 0.0):
            return False
        else:
            if len(dest.path) < 1:
                return in_vehicle_posture
            next_posture = dest.path[0].body_posture
            if next_posture is None:
                return in_vehicle_posture
            return in_vehicle_posture or next_posture.is_vehicle
        return next_posture.is_vehicle or not next_posture.mobile

    def get_best_path_between_handles--- This code section failed: ---

 L.6867         0  BUILD_LIST_0          0 
                2  STORE_FAST               'non_suppressed_source_goals'

 L.6868         4  BUILD_LIST_0          0 
                6  STORE_FAST               'non_suppressed_goals'

 L.6873         8  BUILD_LIST_0          0 
               10  STORE_FAST               'suppressed_source_goals'

 L.6874        12  BUILD_LIST_0          0 
               14  STORE_FAST               'suppressed_goals'

 L.6876        16  LOAD_FAST                'interaction'
               18  LOAD_ATTR                carry_target
               20  LOAD_CONST               None
               22  COMPARE_OP               is-not
               24  STORE_FAST               'for_carryable'

 L.6885        26  LOAD_CONST               False
               28  STORE_FAST               'carry_object_at_pool'

 L.6886        30  LOAD_FAST                'for_carryable'
               32  POP_JUMP_IF_FALSE    68  'to 68'
               34  LOAD_FAST                'interaction'
               36  LOAD_ATTR                carry_target
               38  LOAD_ATTR                routing_surface
               40  LOAD_CONST               None
               42  COMPARE_OP               is-not
               44  POP_JUMP_IF_FALSE    68  'to 68'
               46  LOAD_FAST                'interaction'
               48  LOAD_ATTR                carry_target
               50  LOAD_ATTR                routing_surface
               52  LOAD_ATTR                type
               54  LOAD_GLOBAL              routing
               56  LOAD_ATTR                SurfaceType
               58  LOAD_ATTR                SURFACETYPE_POOL
               60  COMPARE_OP               ==
               62  POP_JUMP_IF_FALSE    68  'to 68'

 L.6887        64  LOAD_CONST               True
               66  STORE_FAST               'carry_object_at_pool'
             68_0  COME_FROM            62  '62'
             68_1  COME_FROM            44  '44'
             68_2  COME_FROM            32  '32'

 L.6889        68  LOAD_FAST                'sim'
               70  LOAD_ATTR                location
               72  LOAD_ATTR                routing_surface
               74  LOAD_CONST               None
               76  COMPARE_OP               is-not
               78  POP_JUMP_IF_FALSE    90  'to 90'
               80  LOAD_FAST                'sim'
               82  LOAD_ATTR                location
               84  LOAD_ATTR                routing_surface
               86  LOAD_ATTR                type
               88  JUMP_FORWARD         92  'to 92'
             90_0  COME_FROM            78  '78'
               90  LOAD_CONST               None
             92_0  COME_FROM            88  '88'
               92  STORE_FAST               'sim_surface_type'

 L.6891        94  LOAD_CONST               None
               96  STORE_FAST               'target_reference_override'

 L.6892        98  LOAD_FAST                'interaction'
              100  LOAD_ATTR                goal_height_limit
              102  STORE_FAST               'interaction_goal_height_limit'

 L.6896       104  LOAD_FAST                'sim'
              106  LOAD_ATTR                routing_master
              108  LOAD_CONST               None
              110  COMPARE_OP               is-not
              112  POP_JUMP_IF_FALSE   140  'to 140'
              114  LOAD_FAST                'sim'
              116  LOAD_ATTR                routing_master
              118  LOAD_METHOD              get_routing_slave_data_count
              120  LOAD_GLOBAL              FormationRoutingType
              122  LOAD_ATTR                FOLLOW
              124  CALL_METHOD_1         1  '1 positional argument'
              126  POP_JUMP_IF_FALSE   140  'to 140'

 L.6899       128  LOAD_FAST                'sim'
              130  LOAD_ATTR                routing_master
              132  STORE_FAST               'target_reference_override'

 L.6900       134  LOAD_GLOBAL              FormationTuning
              136  LOAD_ATTR                GOAL_HEIGHT_LIMIT
              138  STORE_FAST               'interaction_goal_height_limit'
            140_0  COME_FROM           126  '126'
            140_1  COME_FROM           112  '112'

 L.6902   140_142  SETUP_LOOP          546  'to 546'
              144  LOAD_FAST                'source_destination_sets'
              146  LOAD_METHOD              values
              148  CALL_METHOD_0         0  '0 positional arguments'
              150  GET_ITER         
          152_154  FOR_ITER            544  'to 544'
              156  UNPACK_SEQUENCE_6     6 
              158  STORE_FAST               'source_handles'
              160  STORE_FAST               '_'
              162  STORE_FAST               '_'
              164  STORE_FAST               '_'
              166  STORE_FAST               '_'
              168  STORE_FAST               '_'

 L.6903   170_172  SETUP_LOOP          542  'to 542'
              174  LOAD_FAST                'source_handles'
              176  GET_ITER         
          178_180  FOR_ITER            540  'to 540'
              182  STORE_FAST               'source_handle'

 L.6904       184  LOAD_FAST                'source_handle'
              186  LOAD_GLOBAL              DEFAULT
              188  COMPARE_OP               is
              190  POP_JUMP_IF_FALSE   196  'to 196'

 L.6905       192  LOAD_GLOBAL              AssertionError
              194  RAISE_VARARGS_1       1  'exception instance'
            196_0  COME_FROM           190  '190'

 L.6906       196  LOAD_FAST                'source_handles'
              198  LOAD_FAST                'source_handle'
              200  BINARY_SUBSCR    
              202  LOAD_CONST               1
              204  BINARY_SUBSCR    
              206  STORE_FAST               'path_cost'

 L.6908       208  LOAD_FAST                'source_handle'
              210  LOAD_ATTR                get_goals
              212  LOAD_FAST                'source_handle'
              214  LOAD_ATTR                target
              216  LOAD_FAST                'for_carryable'
              218  LOAD_CONST               True
              220  LOAD_CONST               ('relative_object', 'for_carryable', 'for_source')
              222  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              224  STORE_FAST               'source_goals'

 L.6910       226  LOAD_CONST               True
              228  STORE_FAST               'same_interaction_source_target'

 L.6911       230  LOAD_FAST                'interaction'
              232  LOAD_ATTR                target
              234  LOAD_CONST               None
              236  COMPARE_OP               is-not
          238_240  POP_JUMP_IF_FALSE   276  'to 276'
              242  LOAD_FAST                'source_handle'
              244  LOAD_ATTR                target
              246  LOAD_CONST               None
              248  COMPARE_OP               is-not
          250_252  POP_JUMP_IF_FALSE   276  'to 276'
              254  LOAD_FAST                'interaction'
              256  LOAD_ATTR                target
              258  LOAD_ATTR                id
              260  LOAD_FAST                'source_handle'
              262  LOAD_ATTR                target
              264  LOAD_ATTR                id
              266  COMPARE_OP               !=
          268_270  POP_JUMP_IF_FALSE   276  'to 276'

 L.6918       272  LOAD_CONST               False
              274  STORE_FAST               'same_interaction_source_target'
            276_0  COME_FROM           268  '268'
            276_1  COME_FROM           250  '250'
            276_2  COME_FROM           238  '238'

 L.6919   276_278  SETUP_LOOP          538  'to 538'
              280  LOAD_FAST                'source_goals'
              282  GET_ITER         
              284  FOR_ITER            536  'to 536'
              286  STORE_FAST               'source_goal'

 L.6920       288  LOAD_CONST               True
              290  STORE_FAST               'source_is_valid'

 L.6922       292  LOAD_FAST                'path_type'
              294  LOAD_GLOBAL              PathType
              296  LOAD_ATTR                MIDDLE_RIGHT
              298  COMPARE_OP               !=
          300_302  POP_JUMP_IF_FALSE   370  'to 370'

 L.6923       304  LOAD_FAST                'same_interaction_source_target'
          306_308  POP_JUMP_IF_FALSE   370  'to 370'

 L.6924       310  LOAD_FAST                'sim_surface_type'
              312  LOAD_CONST               None
              314  COMPARE_OP               is-not
          316_318  POP_JUMP_IF_FALSE   370  'to 370'

 L.6925       320  LOAD_FAST                'sim_surface_type'
              322  LOAD_GLOBAL              routing
              324  LOAD_ATTR                SurfaceType
              326  LOAD_ATTR                SURFACETYPE_POOL
              328  COMPARE_OP               !=
          330_332  POP_JUMP_IF_FALSE   370  'to 370'

 L.6926       334  LOAD_FAST                'source_goal'
              336  LOAD_ATTR                routing_surface_id
              338  LOAD_ATTR                type
              340  LOAD_GLOBAL              routing
              342  LOAD_ATTR                SurfaceType
              344  LOAD_ATTR                SURFACETYPE_POOL
              346  COMPARE_OP               !=
          348_350  POP_JUMP_IF_FALSE   370  'to 370'

 L.6927       352  LOAD_FAST                'sim_surface_type'
              354  LOAD_FAST                'source_goal'
              356  LOAD_ATTR                routing_surface_id
              358  LOAD_ATTR                type
              360  COMPARE_OP               !=
          362_364  POP_JUMP_IF_FALSE   370  'to 370'

 L.6941   366_368  CONTINUE            284  'to 284'
            370_0  COME_FROM           362  '362'
            370_1  COME_FROM           348  '348'
            370_2  COME_FROM           330  '330'
            370_3  COME_FROM           316  '316'
            370_4  COME_FROM           306  '306'
            370_5  COME_FROM           300  '300'

 L.6943       370  LOAD_FAST                'source_goal'
              372  LOAD_ATTR                requires_los_check
          374_376  POP_JUMP_IF_FALSE   498  'to 498'

 L.6944       378  LOAD_FAST                'source_handle'
              380  LOAD_ATTR                target
              382  LOAD_CONST               None
              384  COMPARE_OP               is-not
          386_388  POP_JUMP_IF_FALSE   498  'to 498'
              390  LOAD_FAST                'source_handle'
              392  LOAD_ATTR                target
              394  LOAD_ATTR                is_sim
          396_398  POP_JUMP_IF_TRUE    498  'to 498'

 L.6945       400  LOAD_FAST                'source_goal'
              402  LOAD_ATTR                location
              404  LOAD_ATTR                routing_surface
              406  STORE_FAST               'goal_routing_surface'

 L.6946       408  LOAD_FAST                'source_goal'
              410  LOAD_ATTR                location
              412  LOAD_ATTR                transform
              414  STORE_FAST               'goal_transform'

 L.6947       416  LOAD_GLOBAL              routing
              418  LOAD_METHOD              test_point_placement_in_navmesh
              420  LOAD_FAST                'goal_routing_surface'
              422  LOAD_FAST                'goal_transform'
              424  LOAD_ATTR                translation
              426  CALL_METHOD_2         2  '2 positional arguments'
          428_430  POP_JUMP_IF_FALSE   494  'to 494'

 L.6948       432  LOAD_FAST                'sim'
              434  LOAD_METHOD              validate_location
              436  LOAD_GLOBAL              sims4
              438  LOAD_ATTR                math
              440  LOAD_METHOD              Location
              442  LOAD_FAST                'goal_transform'
              444  LOAD_FAST                'goal_routing_surface'
              446  CALL_METHOD_2         2  '2 positional arguments'
              448  CALL_METHOD_1         1  '1 positional argument'
          450_452  POP_JUMP_IF_FALSE   494  'to 494'

 L.6949       454  LOAD_FAST                'source_handle'
              456  LOAD_ATTR                target
              458  LOAD_ATTR                check_line_of_sight
              460  LOAD_FAST                'goal_transform'

 L.6950       462  LOAD_CONST               True
              464  LOAD_FAST                'for_carryable'
              466  LOAD_CONST               ('verbose', 'for_carryable')
              468  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              470  UNPACK_SEQUENCE_2     2 
              472  STORE_FAST               'result'
              474  STORE_FAST               '_'

 L.6951       476  LOAD_FAST                'result'
              478  LOAD_GLOBAL              routing
              480  LOAD_ATTR                RAYCAST_HIT_TYPE_NONE
              482  COMPARE_OP               !=
          484_486  POP_JUMP_IF_FALSE   498  'to 498'

 L.6952       488  LOAD_CONST               False
              490  STORE_FAST               'source_is_valid'
              492  JUMP_FORWARD        498  'to 498'
            494_0  COME_FROM           450  '450'
            494_1  COME_FROM           428  '428'

 L.6954       494  LOAD_CONST               False
              496  STORE_FAST               'source_is_valid'
            498_0  COME_FROM           492  '492'
            498_1  COME_FROM           484  '484'
            498_2  COME_FROM           396  '396'
            498_3  COME_FROM           386  '386'
            498_4  COME_FROM           374  '374'

 L.6956       498  LOAD_FAST                'path_cost'
              500  LOAD_FAST                'source_goal'
              502  STORE_ATTR               path_cost

 L.6958       504  LOAD_FAST                'source_is_valid'
          506_508  POP_JUMP_IF_FALSE   522  'to 522'

 L.6959       510  LOAD_FAST                'non_suppressed_source_goals'
              512  LOAD_METHOD              append
              514  LOAD_FAST                'source_goal'
              516  CALL_METHOD_1         1  '1 positional argument'
              518  POP_TOP          
              520  JUMP_BACK           284  'to 284'
            522_0  COME_FROM           506  '506'

 L.6961       522  LOAD_FAST                'suppressed_source_goals'
              524  LOAD_METHOD              append
              526  LOAD_FAST                'source_goal'
              528  CALL_METHOD_1         1  '1 positional argument'
              530  POP_TOP          
          532_534  JUMP_BACK           284  'to 284'
              536  POP_BLOCK        
            538_0  COME_FROM_LOOP      276  '276'
              538  JUMP_BACK           178  'to 178'
              540  POP_BLOCK        
            542_0  COME_FROM_LOOP      170  '170'
              542  JUMP_BACK           152  'to 152'
              544  POP_BLOCK        
            546_0  COME_FROM_LOOP      140  '140'

 L.6966       546  LOAD_FAST                'sim'
              548  LOAD_ATTR                routing_context
              550  STORE_FAST               'routing_context'

 L.6967       552  LOAD_FAST                'interaction'
              554  LOAD_METHOD              min_height_clearance
              556  LOAD_FAST                'routing_context'
              558  CALL_METHOD_1         1  '1 positional argument'
              560  STORE_FAST               'required_height_clearance'

 L.6968       562  LOAD_FAST                'sim'
              564  STORE_FAST               'routing_agent'

 L.6969       566  LOAD_FAST                'sim'
              568  LOAD_ATTR                posture
              570  LOAD_ATTR                target
              572  STORE_FAST               'current_posture_target'

 L.6970       574  LOAD_FAST                'current_posture_target'
              576  LOAD_CONST               None
              578  COMPARE_OP               is
          580_582  POP_JUMP_IF_FALSE   588  'to 588'
              584  LOAD_CONST               False
              586  JUMP_FORWARD        596  'to 596'
            588_0  COME_FROM           580  '580'
              588  LOAD_FAST                'current_posture_target'
              590  LOAD_ATTR                vehicle_component
              592  LOAD_CONST               None
              594  COMPARE_OP               is-not
            596_0  COME_FROM           586  '586'
              596  STORE_FAST               'in_vehicle'

 L.6971       598  LOAD_FAST                'sim'
              600  LOAD_ATTR                posture
              602  LOAD_ATTR                is_vehicle
              604  STORE_DEREF              'in_vehicle_posture'

 L.6972       606  LOAD_CONST               False
              608  STORE_FAST               'force_vehicle_route'

 L.6973       610  BUILD_LIST_0          0 
              612  STORE_FAST               'vehicle_dest_handles'

 L.6974       614  LOAD_FAST                'in_vehicle'
          616_618  POP_JUMP_IF_TRUE    624  'to 624'
              620  LOAD_CONST               None
              622  JUMP_FORWARD        626  'to 626'
            624_0  COME_FROM           616  '616'
              624  LOAD_FAST                'current_posture_target'
            626_0  COME_FROM           622  '622'
              626  STORE_FAST               'vehicle'

 L.6975       628  LOAD_FAST                'vehicle'
              630  LOAD_CONST               None
              632  COMPARE_OP               is-not
          634_636  POP_JUMP_IF_FALSE   894  'to 894'
              638  LOAD_FAST                'vehicle'
              640  LOAD_ATTR                vehicle_component
              642  LOAD_CONST               None
              644  COMPARE_OP               is-not
          646_648  POP_JUMP_IF_FALSE   894  'to 894'

 L.6978       650  LOAD_FAST                'vehicle'
              652  LOAD_ATTR                routing_component
              654  LOAD_ATTR                pathplan_context
              656  STORE_FAST               'vehicle_pathplan_context'

 L.6979       658  LOAD_CONST               None
              660  STORE_FAST               'connectivity'

 L.6980       662  LOAD_FAST                'non_suppressed_source_goals'
              664  STORE_FAST               'vehicle_source_goals'

 L.6981       666  LOAD_FAST                'non_suppressed_source_goals'
          668_670  POP_JUMP_IF_FALSE   680  'to 680'
              672  LOAD_FAST                'non_suppressed_source_goals'
              674  LOAD_CONST               0
              676  BINARY_SUBSCR    
              678  JUMP_FORWARD        682  'to 682'
            680_0  COME_FROM           668  '668'
              680  LOAD_CONST               None
            682_0  COME_FROM           678  '678'
              682  STORE_FAST               'source_goal'

 L.6982       684  LOAD_FAST                'source_goal'
              686  LOAD_CONST               None
              688  COMPARE_OP               is
          690_692  POP_JUMP_IF_FALSE   716  'to 716'

 L.6985       694  LOAD_FAST                'suppressed_source_goals'
              696  STORE_FAST               'vehicle_source_goals'

 L.6986       698  LOAD_FAST                'suppressed_source_goals'
          700_702  POP_JUMP_IF_FALSE   712  'to 712'
              704  LOAD_FAST                'suppressed_source_goals'
              706  LOAD_CONST               0
              708  BINARY_SUBSCR    
              710  JUMP_FORWARD        714  'to 714'
            712_0  COME_FROM           700  '700'
              712  LOAD_CONST               None
            714_0  COME_FROM           710  '710'
              714  STORE_FAST               'source_goal'
            716_0  COME_FROM           690  '690'

 L.6987       716  LOAD_FAST                'source_goal'
              718  LOAD_CONST               None
              720  COMPARE_OP               is-not
          722_724  POP_JUMP_IF_FALSE   814  'to 814'

 L.6988       726  BUILD_LIST_0          0 
              728  STORE_FAST               'dest_handles'

 L.6989       730  SETUP_LOOP          786  'to 786'
              732  LOAD_FAST                'source_destination_sets'
              734  LOAD_METHOD              values
              736  CALL_METHOD_0         0  '0 positional arguments'
              738  GET_ITER         
              740  FOR_ITER            784  'to 784'
              742  UNPACK_SEQUENCE_6     6 
              744  STORE_FAST               '_'
              746  STORE_FAST               'destination_handles'
              748  STORE_FAST               '_'
              750  STORE_FAST               '_'
              752  STORE_FAST               '_'
              754  STORE_FAST               '_'

 L.6990       756  LOAD_FAST                'dest_handles'
              758  LOAD_METHOD              extend
              760  LOAD_LISTCOMP            '<code_object <listcomp>>'
              762  LOAD_STR                 'PostureGraphService.get_best_path_between_handles.<locals>.<listcomp>'
              764  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              766  LOAD_FAST                'destination_handles'
              768  LOAD_METHOD              keys
              770  CALL_METHOD_0         0  '0 positional arguments'
              772  GET_ITER         
              774  CALL_FUNCTION_1       1  '1 positional argument'
              776  CALL_METHOD_1         1  '1 positional argument'
              778  POP_TOP          
          780_782  JUMP_BACK           740  'to 740'
              784  POP_BLOCK        
            786_0  COME_FROM_LOOP      730  '730'

 L.6991       786  LOAD_FAST                'dest_handles'
          788_790  POP_JUMP_IF_FALSE   814  'to 814'

 L.6992       792  LOAD_GLOBAL              routing
              794  LOAD_ATTR                test_connectivity_batch
              796  LOAD_FAST                'source_goal'
              798  LOAD_ATTR                connectivity_handle
              800  BUILD_TUPLE_1         1 
              802  LOAD_FAST                'dest_handles'

 L.6993       804  LOAD_FAST                'vehicle_pathplan_context'

 L.6994       806  LOAD_CONST               True
              808  LOAD_CONST               ('routing_context', 'compute_cost')
              810  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
              812  STORE_FAST               'connectivity'
            814_0  COME_FROM           788  '788'
            814_1  COME_FROM           722  '722'

 L.6995       814  LOAD_FAST                'connectivity'
              816  LOAD_CONST               None
              818  COMPARE_OP               is-not
          820_822  POP_JUMP_IF_FALSE   894  'to 894'

 L.6996       824  LOAD_CLOSURE             'in_vehicle_posture'
              826  LOAD_CLOSURE             'self'
              828  BUILD_TUPLE_2         2 
              830  LOAD_SETCOMP             '<code_object <setcomp>>'
              832  LOAD_STR                 'PostureGraphService.get_best_path_between_handles.<locals>.<setcomp>'
              834  MAKE_FUNCTION_8          'closure'
              836  LOAD_FAST                'connectivity'
              838  GET_ITER         
              840  CALL_FUNCTION_1       1  '1 positional argument'
              842  STORE_FAST               'vehicle_dest_handles'

 L.6997       844  LOAD_FAST                'vehicle_dest_handles'
          846_848  POP_JUMP_IF_FALSE   894  'to 894'

 L.6998       850  LOAD_CONST               True
              852  STORE_FAST               'force_vehicle_route'

 L.7001       854  LOAD_FAST                'vehicle'
              856  STORE_FAST               'routing_agent'

 L.7002       858  LOAD_FAST                'vehicle_pathplan_context'
              860  STORE_FAST               'routing_context'

 L.7004       862  SETUP_LOOP          894  'to 894'
              864  LOAD_FAST                'vehicle_source_goals'
              866  GET_ITER         
              868  FOR_ITER            892  'to 892'
              870  STORE_FAST               'goal'

 L.7005       872  LOAD_FAST                'goal'
              874  LOAD_ATTR                connectivity_handle
              876  LOAD_ATTR                clone
              878  LOAD_FAST                'vehicle'
              880  LOAD_CONST               ('sim',)
              882  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              884  LOAD_FAST                'goal'
              886  STORE_ATTR               connectivity_handle
          888_890  JUMP_BACK           868  'to 868'
              892  POP_BLOCK        
            894_0  COME_FROM_LOOP      862  '862'
            894_1  COME_FROM           846  '846'
            894_2  COME_FROM           820  '820'
            894_3  COME_FROM           646  '646'
            894_4  COME_FROM           634  '634'

 L.7009       894  LOAD_FAST                'path_type'
              896  LOAD_CONST               None
              898  COMPARE_OP               is-not
          900_902  JUMP_IF_FALSE_OR_POP   912  'to 912'
              904  LOAD_FAST                'path_type'
              906  LOAD_GLOBAL              PathType
              908  LOAD_ATTR                MIDDLE_LEFT
              910  COMPARE_OP               ==
            912_0  COME_FROM           900  '900'
              912  STORE_FAST               'middle_path_pickup'

 L.7011   914_916  SETUP_LOOP         1602  'to 1602'
              918  LOAD_FAST                'source_destination_sets'
              920  LOAD_METHOD              values
              922  CALL_METHOD_0         0  '0 positional arguments'
              924  GET_ITER         
          926_928  FOR_ITER           1600  'to 1600'
              930  UNPACK_SEQUENCE_6     6 
              932  STORE_FAST               '_'
              934  STORE_FAST               'destination_handles'
              936  STORE_FAST               '_'
              938  STORE_FAST               '_'
              940  STORE_FAST               '_'
              942  STORE_FAST               '_'

 L.7012   944_946  SETUP_LOOP         1596  'to 1596'
              948  LOAD_FAST                'destination_handles'
              950  LOAD_METHOD              items
              952  CALL_METHOD_0         0  '0 positional arguments'
              954  GET_ITER         
          956_958  FOR_ITER           1594  'to 1594'
              960  UNPACK_SEQUENCE_2     2 
              962  STORE_FAST               'destination_handle'
              964  UNPACK_SEQUENCE_7     7 
              966  STORE_FAST               'right_path'
              968  STORE_FAST               'path_cost'
              970  STORE_FAST               'var_map'
              972  STORE_FAST               'dest_spec'
              974  STORE_FAST               '_'
              976  STORE_FAST               '_'
              978  STORE_FAST               '_'

 L.7013       980  BUILD_LIST_0          0 
              982  STORE_FAST               'additional_dest_handles'

 L.7014       984  LOAD_FAST                'destination_handle'
              986  LOAD_GLOBAL              DEFAULT
              988  COMPARE_OP               is
          990_992  POP_JUMP_IF_FALSE  1060  'to 1060'

 L.7015       994  SETUP_LOOP         1102  'to 1102'
              996  LOAD_FAST                'source_destination_sets'
              998  LOAD_METHOD              values
             1000  CALL_METHOD_0         0  '0 positional arguments'
             1002  GET_ITER         
             1004  FOR_ITER           1056  'to 1056'
             1006  UNPACK_EX_1+0           
             1008  STORE_FAST               'source_handles'
             1010  STORE_FAST               '_'

 L.7016      1012  SETUP_LOOP         1052  'to 1052'
             1014  LOAD_FAST                'source_handles'
             1016  GET_ITER         
             1018  FOR_ITER           1050  'to 1050'
             1020  STORE_FAST               'source_handle'

 L.7017      1022  LOAD_FAST                'source_handle'
             1024  LOAD_METHOD              clone
             1026  CALL_METHOD_0         0  '0 positional arguments'
             1028  STORE_FAST               'destination_handle'

 L.7018      1030  LOAD_FAST                'right_path'
             1032  LOAD_FAST                'destination_handle'
             1034  STORE_ATTR               path

 L.7019      1036  LOAD_FAST                'additional_dest_handles'
             1038  LOAD_METHOD              append
             1040  LOAD_FAST                'destination_handle'
             1042  CALL_METHOD_1         1  '1 positional argument'
             1044  POP_TOP          
         1046_1048  JUMP_BACK          1018  'to 1018'
             1050  POP_BLOCK        
           1052_0  COME_FROM_LOOP     1012  '1012'
         1052_1054  JUMP_BACK          1004  'to 1004'
             1056  POP_BLOCK        
             1058  JUMP_FORWARD       1102  'to 1102'
           1060_0  COME_FROM           990  '990'

 L.7020      1060  LOAD_FAST                'force_vehicle_route'
         1062_1064  POP_JUMP_IF_FALSE  1096  'to 1096'

 L.7023      1066  LOAD_FAST                'destination_handle'
             1068  LOAD_FAST                'vehicle_dest_handles'
             1070  COMPARE_OP               in
         1072_1074  POP_JUMP_IF_FALSE  1102  'to 1102'

 L.7026      1076  LOAD_FAST                'destination_handle'
             1078  LOAD_ATTR                clone
             1080  LOAD_FAST                'routing_agent'
             1082  LOAD_CONST               ('sim',)
             1084  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
             1086  STORE_FAST               'destination_handle'

 L.7027      1088  LOAD_FAST                'destination_handle'
             1090  BUILD_LIST_1          1 
             1092  STORE_FAST               'additional_dest_handles'
             1094  JUMP_FORWARD       1102  'to 1102'
           1096_0  COME_FROM          1062  '1062'

 L.7029      1096  LOAD_FAST                'destination_handle'
             1098  BUILD_LIST_1          1 
             1100  STORE_FAST               'additional_dest_handles'
           1102_0  COME_FROM          1094  '1094'
           1102_1  COME_FROM          1072  '1072'
           1102_2  COME_FROM          1058  '1058'
           1102_3  COME_FROM_LOOP      994  '994'

 L.7031  1102_1104  SETUP_LOOP         1590  'to 1590'
             1106  LOAD_FAST                'additional_dest_handles'
             1108  GET_ITER         
         1110_1112  FOR_ITER           1588  'to 1588'
             1114  STORE_FAST               'dest_handle'

 L.7034      1116  LOAD_FAST                'interaction_goal_height_limit'
             1118  STORE_FAST               'height_limit'

 L.7035      1120  LOAD_FAST                'target_reference_override'
             1122  LOAD_CONST               None
             1124  COMPARE_OP               is
         1126_1128  POP_JUMP_IF_FALSE  1154  'to 1154'
             1130  LOAD_FAST                'interaction'
             1132  LOAD_ATTR                carry_target
             1134  LOAD_FAST                'dest_handle'
             1136  LOAD_ATTR                target
             1138  COMPARE_OP               is
         1140_1142  POP_JUMP_IF_FALSE  1154  'to 1154'
             1144  LOAD_FAST                'middle_path_pickup'
         1146_1148  POP_JUMP_IF_TRUE   1154  'to 1154'

 L.7036      1150  LOAD_CONST               None
             1152  STORE_FAST               'height_limit'
           1154_0  COME_FROM          1146  '1146'
           1154_1  COME_FROM          1140  '1140'
           1154_2  COME_FROM          1126  '1126'

 L.7037      1154  LOAD_FAST                'dest_handle'
             1156  LOAD_ATTR                get_goals
             1158  LOAD_FAST                'dest_handle'
             1160  LOAD_ATTR                target

 L.7038      1162  LOAD_FAST                'for_carryable'

 L.7039      1164  LOAD_FAST                'height_limit'

 L.7040      1166  LOAD_FAST                'target_reference_override'

 L.7041      1168  LOAD_CONST               False
             1170  LOAD_CONST               ('relative_object', 'for_carryable', 'goal_height_limit', 'target_reference_override', 'check_height_clearance')
             1172  CALL_FUNCTION_KW_5     5  '5 total positional and keyword args'
             1174  STORE_FAST               'dest_goals'

 L.7043      1176  LOAD_FAST                'dest_handle'
             1178  LOAD_ATTR                target
             1180  LOAD_CONST               None
             1182  COMPARE_OP               is-not
         1184_1186  JUMP_IF_FALSE_OR_POP  1204  'to 1204'
             1188  LOAD_FAST                'dest_handle'
             1190  LOAD_ATTR                constraint
             1192  LOAD_ATTR                restricted_on_slope
         1194_1196  JUMP_IF_FALSE_OR_POP  1204  'to 1204'

 L.7044      1198  LOAD_FAST                'interaction'
             1200  LOAD_ATTR                ignore_slope_restrictions
             1202  UNARY_NOT        
           1204_0  COME_FROM          1194  '1194'
           1204_1  COME_FROM          1184  '1184'
             1204  STORE_FAST               'slope_restricted'

 L.7045  1206_1208  SETUP_LOOP         1584  'to 1584'
             1210  LOAD_FAST                'dest_goals'
             1212  GET_ITER         
         1214_1216  FOR_ITER           1582  'to 1582'
             1218  STORE_FAST               'dest_goal'

 L.7046      1220  LOAD_FAST                'middle_path_pickup'
         1222_1224  POP_JUMP_IF_FALSE  1254  'to 1254'
             1226  LOAD_FAST                'carry_object_at_pool'
         1228_1230  POP_JUMP_IF_FALSE  1254  'to 1254'

 L.7047      1232  LOAD_FAST                'dest_goal'
             1234  LOAD_ATTR                routing_surface_id
             1236  LOAD_ATTR                type
             1238  LOAD_GLOBAL              routing
             1240  LOAD_ATTR                SurfaceType
             1242  LOAD_ATTR                SURFACETYPE_POOL
             1244  COMPARE_OP               !=
         1246_1248  POP_JUMP_IF_FALSE  1254  'to 1254'

 L.7055  1250_1252  CONTINUE           1214  'to 1214'
           1254_0  COME_FROM          1246  '1246'
           1254_1  COME_FROM          1228  '1228'
           1254_2  COME_FROM          1222  '1222'

 L.7056      1254  LOAD_CONST               True
             1256  STORE_FAST               'dest_is_valid'

 L.7057      1258  LOAD_FAST                'path_cost'
             1260  LOAD_FAST                'dest_goal'
             1262  STORE_ATTR               path_cost

 L.7066      1264  LOAD_FAST                'slope_restricted'
         1266_1268  POP_JUMP_IF_FALSE  1386  'to 1386'
             1270  LOAD_FAST                'dest_goal'
             1272  LOAD_ATTR                routing_surface_id
             1274  LOAD_ATTR                type
             1276  LOAD_GLOBAL              routing
             1278  LOAD_ATTR                SurfaceType
             1280  LOAD_ATTR                SURFACETYPE_WORLD
             1282  COMPARE_OP               ==
         1284_1286  POP_JUMP_IF_FALSE  1386  'to 1386'

 L.7067      1288  LOAD_FAST                'dest_goal'
             1290  LOAD_ATTR                position
             1292  LOAD_ATTR                y
             1294  LOAD_GLOBAL              routing_constants
             1296  LOAD_ATTR                INVALID_TERRAIN_HEIGHT
             1298  COMPARE_OP               !=
         1300_1302  POP_JUMP_IF_FALSE  1386  'to 1386'

 L.7071      1304  LOAD_FAST                'dest_handle'
             1306  LOAD_ATTR                target
             1308  LOAD_METHOD              get_parenting_root
             1310  CALL_METHOD_0         0  '0 positional arguments'
             1312  STORE_FAST               'positional_target'

 L.7072      1314  LOAD_FAST                'positional_target'
             1316  LOAD_ATTR                is_part
         1318_1320  POP_JUMP_IF_FALSE  1330  'to 1330'
             1322  LOAD_FAST                'positional_target'
             1324  LOAD_ATTR                part_owner
             1326  LOAD_ATTR                position
             1328  JUMP_FORWARD       1334  'to 1334'
           1330_0  COME_FROM          1318  '1318'
             1330  LOAD_FAST                'positional_target'
             1332  LOAD_ATTR                position
           1334_0  COME_FROM          1328  '1328'
             1334  STORE_FAST               'target_position'

 L.7073      1336  LOAD_GLOBAL              abs
             1338  LOAD_FAST                'target_position'
             1340  LOAD_ATTR                y
             1342  LOAD_FAST                'dest_goal'
             1344  LOAD_ATTR                position
             1346  LOAD_ATTR                y
             1348  BINARY_SUBTRACT  
             1350  CALL_FUNCTION_1       1  '1 positional argument'
             1352  STORE_FAST               'height_difference'

 L.7074      1354  LOAD_FAST                'height_difference'
             1356  LOAD_GLOBAL              PostureTuning
             1358  LOAD_ATTR                CONSTRAINT_HEIGHT_TOLERANCE
             1360  COMPARE_OP               >
         1362_1364  POP_JUMP_IF_FALSE  1386  'to 1386'

 L.7075      1366  LOAD_GLOBAL              set_transition_failure_reason
             1368  LOAD_FAST                'sim'
             1370  LOAD_GLOBAL              TransitionFailureReasons
             1372  LOAD_ATTR                GOAL_ON_SLOPE
             1374  CALL_FUNCTION_2       2  '2 positional arguments'
             1376  POP_TOP          

 L.7076      1378  LOAD_CONST               False
             1380  STORE_FAST               'dest_is_valid'

 L.7077  1382_1384  CONTINUE           1214  'to 1214'
           1386_0  COME_FROM          1362  '1362'
           1386_1  COME_FROM          1300  '1300'
           1386_2  COME_FROM          1284  '1284'
           1386_3  COME_FROM          1266  '1266'

 L.7081      1386  LOAD_FAST                'required_height_clearance'
             1388  LOAD_FAST                'dest_goal'
             1390  LOAD_ATTR                height_clearance
             1392  COMPARE_OP               >
         1394_1396  POP_JUMP_IF_FALSE  1418  'to 1418'

 L.7082      1398  LOAD_GLOBAL              set_transition_failure_reason
             1400  LOAD_FAST                'sim'
             1402  LOAD_GLOBAL              TransitionFailureReasons
             1404  LOAD_ATTR                INSUFFICIENT_HEAD_CLEARANCE
             1406  CALL_FUNCTION_2       2  '2 positional arguments'
             1408  POP_TOP          

 L.7083      1410  LOAD_CONST               False
             1412  STORE_FAST               'dest_is_valid'

 L.7084  1414_1416  CONTINUE           1214  'to 1214'
           1418_0  COME_FROM          1394  '1394'

 L.7090      1418  LOAD_FAST                'dest_goal'
             1420  LOAD_ATTR                requires_los_check
         1422_1424  POP_JUMP_IF_FALSE  1550  'to 1550'

 L.7091      1426  LOAD_FAST                'dest_handle'
             1428  LOAD_ATTR                target
             1430  LOAD_CONST               None
             1432  COMPARE_OP               is-not
         1434_1436  POP_JUMP_IF_FALSE  1550  'to 1550'
             1438  LOAD_FAST                'dest_handle'
             1440  LOAD_ATTR                target
             1442  LOAD_ATTR                is_sim
         1444_1446  POP_JUMP_IF_TRUE   1550  'to 1550'

 L.7092      1448  LOAD_FAST                'in_vehicle'
         1450_1452  POP_JUMP_IF_FALSE  1466  'to 1466'
             1454  LOAD_FAST                'current_posture_target'
             1456  LOAD_FAST                'dest_handle'
             1458  LOAD_ATTR                target
             1460  COMPARE_OP               is
         1462_1464  POP_JUMP_IF_TRUE   1550  'to 1550'
           1466_0  COME_FROM          1450  '1450'

 L.7093      1466  LOAD_FAST                'dest_handle'
             1468  LOAD_ATTR                target
             1470  LOAD_ATTR                check_line_of_sight
             1472  LOAD_FAST                'dest_goal'
             1474  LOAD_ATTR                location
             1476  LOAD_ATTR                transform

 L.7094      1478  LOAD_CONST               True
             1480  LOAD_FAST                'for_carryable'

 L.7095      1482  LOAD_CONST               True
             1484  LOAD_CONST               ('verbose', 'for_carryable', 'use_standard_ignored_objects')
             1486  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
             1488  UNPACK_SEQUENCE_2     2 
             1490  STORE_FAST               'result'
             1492  STORE_FAST               'blocking_obj_id'

 L.7099      1494  LOAD_FAST                'result'
             1496  LOAD_GLOBAL              routing
             1498  LOAD_ATTR                RAYCAST_HIT_TYPE_IMPASSABLE
             1500  COMPARE_OP               ==
         1502_1504  POP_JUMP_IF_FALSE  1518  'to 1518'
             1506  LOAD_FAST                'blocking_obj_id'
             1508  LOAD_CONST               0
             1510  COMPARE_OP               ==
         1512_1514  POP_JUMP_IF_FALSE  1518  'to 1518'

 L.7100      1516  JUMP_FORWARD       1550  'to 1550'
           1518_0  COME_FROM          1512  '1512'
           1518_1  COME_FROM          1502  '1502'

 L.7101      1518  LOAD_FAST                'result'
             1520  LOAD_GLOBAL              routing
             1522  LOAD_ATTR                RAYCAST_HIT_TYPE_NONE
             1524  COMPARE_OP               !=
         1526_1528  POP_JUMP_IF_FALSE  1550  'to 1550'

 L.7103      1530  LOAD_GLOBAL              set_transition_failure_reason
             1532  LOAD_FAST                'sim'
             1534  LOAD_GLOBAL              TransitionFailureReasons
             1536  LOAD_ATTR                BLOCKING_OBJECT
             1538  LOAD_FAST                'blocking_obj_id'
             1540  LOAD_CONST               ('target_id',)
             1542  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
             1544  POP_TOP          

 L.7104      1546  LOAD_CONST               False
             1548  STORE_FAST               'dest_is_valid'
           1550_0  COME_FROM          1526  '1526'
           1550_1  COME_FROM          1516  '1516'
           1550_2  COME_FROM          1462  '1462'
           1550_3  COME_FROM          1444  '1444'
           1550_4  COME_FROM          1434  '1434'
           1550_5  COME_FROM          1422  '1422'

 L.7106      1550  LOAD_FAST                'dest_is_valid'
         1552_1554  POP_JUMP_IF_FALSE  1568  'to 1568'

 L.7107      1556  LOAD_FAST                'non_suppressed_goals'
             1558  LOAD_METHOD              append
             1560  LOAD_FAST                'dest_goal'
             1562  CALL_METHOD_1         1  '1 positional argument'
             1564  POP_TOP          
             1566  JUMP_BACK          1214  'to 1214'
           1568_0  COME_FROM          1552  '1552'

 L.7109      1568  LOAD_FAST                'suppressed_goals'
             1570  LOAD_METHOD              append
             1572  LOAD_FAST                'dest_goal'
             1574  CALL_METHOD_1         1  '1 positional argument'
             1576  POP_TOP          
         1578_1580  JUMP_BACK          1214  'to 1214'
             1582  POP_BLOCK        
           1584_0  COME_FROM_LOOP     1206  '1206'
         1584_1586  JUMP_BACK          1110  'to 1110'
             1588  POP_BLOCK        
           1590_0  COME_FROM_LOOP     1102  '1102'
         1590_1592  JUMP_BACK           956  'to 956'
             1594  POP_BLOCK        
           1596_0  COME_FROM_LOOP      944  '944'
         1596_1598  JUMP_BACK           926  'to 926'
             1600  POP_BLOCK        
           1602_0  COME_FROM_LOOP      914  '914'

 L.7111      1602  LOAD_FAST                'non_suppressed_source_goals'
         1604_1606  POP_JUMP_IF_TRUE   1612  'to 1612'

 L.7116      1608  LOAD_FAST                'suppressed_source_goals'
             1610  STORE_FAST               'non_suppressed_source_goals'
           1612_0  COME_FROM          1604  '1604'

 L.7117      1612  LOAD_FAST                'non_suppressed_source_goals'
             1614  STORE_FAST               'all_source_goals'

 L.7118      1616  LOAD_FAST                'non_suppressed_goals'
         1618_1620  JUMP_IF_TRUE_OR_POP  1624  'to 1624'
             1622  LOAD_FAST                'suppressed_goals'
           1624_0  COME_FROM          1618  '1618'
             1624  STORE_FAST               'all_dest_goals'

 L.7120      1626  LOAD_FAST                'all_source_goals'
         1628_1630  POP_JUMP_IF_FALSE  1638  'to 1638'
             1632  LOAD_FAST                'all_dest_goals'
         1634_1636  POP_JUMP_IF_TRUE   1674  'to 1674'
           1638_0  COME_FROM          1628  '1628'

 L.7121      1638  LOAD_DEREF               'self'
             1640  LOAD_ATTR                _get_failure_path_spec_gen
             1642  LOAD_FAST                'timeline'
             1644  LOAD_FAST                'sim'
             1646  LOAD_FAST                'source_destination_sets'
             1648  LOAD_FAST                'interaction'
             1650  LOAD_FAST                'path_type'
             1652  LOAD_CONST               ('interaction', 'failed_path_type')
             1654  CALL_FUNCTION_KW_5     5  '5 total positional and keyword args'
             1656  GET_YIELD_FROM_ITER
             1658  LOAD_CONST               None
             1660  YIELD_FROM       
             1662  STORE_FAST               'failure_path'

 L.7122      1664  LOAD_CONST               False
             1666  LOAD_FAST                'failure_path'
             1668  LOAD_CONST               None
             1670  BUILD_TUPLE_3         3 
             1672  RETURN_VALUE     
           1674_0  COME_FROM          1634  '1634'

 L.7125      1674  SETUP_LOOP         1714  'to 1714'
             1676  LOAD_GLOBAL              itertools
             1678  LOAD_METHOD              chain
             1680  LOAD_FAST                'all_source_goals'
             1682  LOAD_FAST                'all_dest_goals'
             1684  CALL_METHOD_2         2  '2 positional arguments'
             1686  GET_ITER         
             1688  FOR_ITER           1712  'to 1712'
             1690  STORE_FAST               'goal'

 L.7126      1692  LOAD_FAST                'goal'
             1694  DUP_TOP          
             1696  LOAD_ATTR                cost
             1698  LOAD_FAST                'goal'
             1700  LOAD_ATTR                path_cost
             1702  INPLACE_ADD      
             1704  ROT_TWO          
             1706  STORE_ATTR               cost
         1708_1710  JUMP_BACK          1688  'to 1688'
             1712  POP_BLOCK        
           1714_0  COME_FROM_LOOP     1674  '1674'

 L.7141      1714  LOAD_GLOBAL              gsi_handlers
             1716  LOAD_ATTR                posture_graph_handlers
             1718  LOAD_ATTR                archiver
             1720  LOAD_ATTR                enabled
         1722_1724  POP_JUMP_IF_FALSE  1822  'to 1822'

 L.7142      1726  SETUP_LOOP         1774  'to 1774'
             1728  LOAD_FAST                'all_source_goals'
             1730  GET_ITER         
             1732  FOR_ITER           1772  'to 1772'
             1734  STORE_FAST               'source_goal'

 L.7143      1736  LOAD_GLOBAL              gsi_handlers
             1738  LOAD_ATTR                posture_graph_handlers
             1740  LOAD_METHOD              log_possible_goal

 L.7144      1742  LOAD_FAST                'sim'
             1744  LOAD_FAST                'source_goal'
             1746  LOAD_ATTR                connectivity_handle
             1748  LOAD_ATTR                path
             1750  LOAD_FAST                'source_goal'

 L.7145      1752  LOAD_FAST                'source_goal'
             1754  LOAD_ATTR                cost
             1756  LOAD_STR                 'Source'
             1758  LOAD_GLOBAL              id
             1760  LOAD_FAST                'source_destination_sets'
             1762  CALL_FUNCTION_1       1  '1 positional argument'
             1764  CALL_METHOD_6         6  '6 positional arguments'
             1766  POP_TOP          
         1768_1770  JUMP_BACK          1732  'to 1732'
             1772  POP_BLOCK        
           1774_0  COME_FROM_LOOP     1726  '1726'

 L.7146      1774  SETUP_LOOP         1822  'to 1822'
             1776  LOAD_FAST                'all_dest_goals'
             1778  GET_ITER         
             1780  FOR_ITER           1820  'to 1820'
             1782  STORE_FAST               'dest_goal'

 L.7147      1784  LOAD_GLOBAL              gsi_handlers
             1786  LOAD_ATTR                posture_graph_handlers
             1788  LOAD_METHOD              log_possible_goal

 L.7148      1790  LOAD_FAST                'sim'
             1792  LOAD_FAST                'dest_goal'
             1794  LOAD_ATTR                connectivity_handle
             1796  LOAD_ATTR                path
             1798  LOAD_FAST                'dest_goal'

 L.7149      1800  LOAD_FAST                'dest_goal'
             1802  LOAD_ATTR                cost
             1804  LOAD_STR                 'Dest'
             1806  LOAD_GLOBAL              id
             1808  LOAD_FAST                'source_destination_sets'
             1810  CALL_FUNCTION_1       1  '1 positional argument'
             1812  CALL_METHOD_6         6  '6 positional arguments'
             1814  POP_TOP          
         1816_1818  JUMP_BACK          1780  'to 1780'
             1820  POP_BLOCK        
           1822_0  COME_FROM_LOOP     1774  '1774'
           1822_1  COME_FROM          1722  '1722'

 L.7152      1822  LOAD_DEREF               'self'
             1824  LOAD_METHOD              normalize_goal_costs
             1826  LOAD_FAST                'all_source_goals'
             1828  CALL_METHOD_1         1  '1 positional argument'
             1830  POP_TOP          

 L.7153      1832  LOAD_DEREF               'self'
             1834  LOAD_METHOD              normalize_goal_costs
             1836  LOAD_FAST                'all_dest_goals'
             1838  CALL_METHOD_1         1  '1 positional argument'
             1840  POP_TOP          

 L.7155      1842  LOAD_GLOBAL              routing
             1844  LOAD_ATTR                Route
             1846  LOAD_FAST                'all_source_goals'
             1848  LOAD_CONST               0
             1850  BINARY_SUBSCR    
             1852  LOAD_ATTR                location
             1854  LOAD_FAST                'all_dest_goals'

 L.7156      1856  LOAD_FAST                'all_source_goals'

 L.7157      1858  LOAD_FAST                'routing_context'
             1860  LOAD_CONST               ('additional_origins', 'routing_context')
             1862  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
             1864  STORE_FAST               'route'

 L.7159      1866  LOAD_FAST                'all_dest_goals'
             1868  LOAD_FAST                'suppressed_goals'
             1870  COMPARE_OP               is
             1872  STORE_FAST               'is_failure_path'

 L.7160      1874  LOAD_GLOBAL              interactions
             1876  LOAD_ATTR                utils
             1878  LOAD_ATTR                routing
             1880  LOAD_ATTR                PlanRoute

 L.7161      1882  LOAD_FAST                'route'
             1884  LOAD_FAST                'routing_agent'

 L.7162      1886  LOAD_FAST                'is_failure_path'

 L.7163      1888  LOAD_FAST                'interaction'
             1890  LOAD_CONST               ('is_failure_route', 'interaction')
             1892  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
             1894  STORE_FAST               'plan_primitive'

 L.7165      1896  LOAD_GLOBAL              element_utils
             1898  LOAD_METHOD              run_child
             1900  LOAD_FAST                'timeline'
             1902  LOAD_GLOBAL              elements
             1904  LOAD_METHOD              MustRunElement
             1906  LOAD_FAST                'plan_primitive'
             1908  CALL_METHOD_1         1  '1 positional argument'
             1910  CALL_METHOD_2         2  '2 positional arguments'
             1912  GET_YIELD_FROM_ITER
             1914  LOAD_CONST               None
             1916  YIELD_FROM       
             1918  STORE_FAST               'result'

 L.7166      1920  LOAD_FAST                'result'
         1922_1924  POP_JUMP_IF_TRUE   1934  'to 1934'

 L.7167      1926  LOAD_GLOBAL              RuntimeError
             1928  LOAD_STR                 'Unknown error when trying to run PlanRoute.run()'
             1930  CALL_FUNCTION_1       1  '1 positional argument'
             1932  RAISE_VARARGS_1       1  'exception instance'
           1934_0  COME_FROM          1922  '1922'

 L.7169      1934  LOAD_FAST                'is_failure_path'
         1936_1938  POP_JUMP_IF_FALSE  1988  'to 1988'
             1940  LOAD_FAST                'plan_primitive'
             1942  LOAD_ATTR                path
             1944  LOAD_ATTR                nodes
         1946_1948  POP_JUMP_IF_FALSE  1988  'to 1988'
             1950  LOAD_FAST                'plan_primitive'
             1952  LOAD_ATTR                path
             1954  LOAD_ATTR                nodes
             1956  LOAD_ATTR                plan_failure_object_id
         1958_1960  POP_JUMP_IF_FALSE  1988  'to 1988'

 L.7170      1962  LOAD_FAST                'plan_primitive'
             1964  LOAD_ATTR                path
             1966  LOAD_ATTR                nodes
             1968  LOAD_ATTR                plan_failure_object_id
             1970  STORE_FAST               'failure_obj_id'

 L.7171      1972  LOAD_GLOBAL              set_transition_failure_reason
             1974  LOAD_FAST                'sim'
             1976  LOAD_GLOBAL              TransitionFailureReasons
             1978  LOAD_ATTR                BLOCKING_OBJECT
             1980  LOAD_FAST                'failure_obj_id'
             1982  LOAD_CONST               ('target_id',)
             1984  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
             1986  POP_TOP          
           1988_0  COME_FROM          1958  '1958'
           1988_1  COME_FROM          1946  '1946'
           1988_2  COME_FROM          1936  '1936'

 L.7175      1988  LOAD_FAST                'is_failure_path'
         1990_1992  POP_JUMP_IF_TRUE   2006  'to 2006'
             1994  LOAD_FAST                'plan_primitive'
             1996  LOAD_ATTR                path
             1998  LOAD_ATTR                nodes
             2000  LOAD_ATTR                plan_success
         2002_2004  POP_JUMP_IF_FALSE  2016  'to 2016'
           2006_0  COME_FROM          1990  '1990'

 L.7176      2006  LOAD_FAST                'plan_primitive'
             2008  LOAD_ATTR                path
             2010  LOAD_ATTR                nodes
         2012_2014  POP_JUMP_IF_TRUE   2050  'to 2050'
           2016_0  COME_FROM          2002  '2002'

 L.7177      2016  LOAD_DEREF               'self'
             2018  LOAD_ATTR                _get_failure_path_spec_gen
             2020  LOAD_FAST                'timeline'
             2022  LOAD_FAST                'sim'
             2024  LOAD_FAST                'source_destination_sets'
             2026  LOAD_FAST                'path_type'
             2028  LOAD_CONST               ('failed_path_type',)
             2030  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
             2032  GET_YIELD_FROM_ITER
             2034  LOAD_CONST               None
             2036  YIELD_FROM       
             2038  STORE_FAST               'failure_path'

 L.7178      2040  LOAD_CONST               False
             2042  LOAD_FAST                'failure_path'
             2044  LOAD_CONST               None
             2046  BUILD_TUPLE_3         3 
             2048  RETURN_VALUE     
           2050_0  COME_FROM          2012  '2012'

 L.7181      2050  LOAD_FAST                'plan_primitive'
             2052  LOAD_ATTR                path
             2054  LOAD_ATTR                selected_start
             2056  STORE_FAST               'origin'

 L.7182      2058  LOAD_FAST                'origin'
             2060  LOAD_ATTR                connectivity_handle
             2062  LOAD_ATTR                path
             2064  STORE_FAST               'origin_path'

 L.7183      2066  LOAD_FAST                'plan_primitive'
             2068  LOAD_ATTR                path
             2070  LOAD_ATTR                selected_goal
             2072  STORE_FAST               'dest'

 L.7184      2074  LOAD_FAST                'plan_primitive'
             2076  LOAD_ATTR                path
             2078  LOAD_ATTR                final_location
             2080  LOAD_FAST                'dest'
             2082  STORE_ATTR               location

 L.7185      2084  LOAD_FAST                'dest'
             2086  LOAD_ATTR                connectivity_handle
             2088  LOAD_ATTR                path
             2090  STORE_FAST               'dest_path'

 L.7187      2092  LOAD_GLOBAL              set_transition_destinations
             2094  LOAD_FAST                'sim'
             2096  LOAD_FAST                'all_source_goals'
             2098  LOAD_FAST                'all_dest_goals'
             2100  LOAD_FAST                'origin'
             2102  LOAD_FAST                'dest'
             2104  LOAD_CONST               True
             2106  LOAD_CONST               True
             2108  LOAD_CONST               ('preserve', 'draw_both_sets')
             2110  CALL_FUNCTION_KW_7     7  '7 total positional and keyword args'
             2112  POP_TOP          

 L.7189      2114  LOAD_FAST                'origin_path'
             2116  LOAD_ATTR                segmented_path
             2118  LOAD_ATTR                destination_specs
             2120  LOAD_METHOD              get
             2122  LOAD_FAST                'dest_path'
             2124  LOAD_CONST               -1
             2126  BINARY_SUBSCR    
             2128  CALL_METHOD_1         1  '1 positional argument'
             2130  STORE_FAST               'destination_spec'

 L.7191      2132  LOAD_GLOBAL              PathSpec
             2134  LOAD_FAST                'origin_path'
             2136  LOAD_FAST                'origin'
             2138  LOAD_ATTR                path_cost

 L.7192      2140  LOAD_FAST                'origin'
             2142  LOAD_ATTR                connectivity_handle
             2144  LOAD_ATTR                var_map

 L.7193      2146  LOAD_CONST               None

 L.7194      2148  LOAD_FAST                'origin'
             2150  LOAD_ATTR                connectivity_handle
             2152  LOAD_ATTR                constraint

 L.7195      2154  LOAD_FAST                'origin_path'
             2156  LOAD_ATTR                segmented_path
             2158  LOAD_ATTR                constraint

 L.7196      2160  LOAD_FAST                'is_failure_path'
             2162  LOAD_CONST               ('is_failure_path',)
             2164  CALL_FUNCTION_KW_7     7  '7 total positional and keyword args'
             2166  STORE_FAST               'left_path_spec'

 L.7200      2168  LOAD_FAST                'origin'
             2170  LOAD_ATTR                has_slot_params
         2172_2174  POP_JUMP_IF_FALSE  2182  'to 2182'
             2176  LOAD_FAST                'origin'
             2178  LOAD_ATTR                slot_params
             2180  JUMP_FORWARD       2186  'to 2186'
           2182_0  COME_FROM          2172  '2172'
             2182  LOAD_GLOBAL              frozendict
             2184  CALL_FUNCTION_0       0  '0 positional arguments'
           2186_0  COME_FROM          2180  '2180'
             2186  STORE_FAST               'o_locked_params'

 L.7201      2188  LOAD_FAST                'left_path_spec'
             2190  LOAD_ATTR                attach_route_and_params
             2192  LOAD_CONST               None

 L.7202      2194  LOAD_FAST                'o_locked_params'
             2196  LOAD_CONST               None
             2198  LOAD_CONST               True
             2200  LOAD_CONST               ('reverse',)
             2202  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
             2204  POP_TOP          

 L.7206      2206  LOAD_GLOBAL              sims4
             2208  LOAD_ATTR                math
             2210  LOAD_METHOD              Transform
             2212  LOAD_GLOBAL              sims4
             2214  LOAD_ATTR                math
             2216  LOAD_ATTR                Vector3
             2218  LOAD_FAST                'dest'
             2220  LOAD_ATTR                location
             2222  LOAD_ATTR                position
             2224  CALL_FUNCTION_EX      0  'positional arguments only'

 L.7207      2226  LOAD_GLOBAL              sims4
             2228  LOAD_ATTR                math
             2230  LOAD_ATTR                Quaternion
             2232  LOAD_FAST                'dest'
             2234  LOAD_ATTR                location
             2236  LOAD_ATTR                orientation
             2238  CALL_FUNCTION_EX      0  'positional arguments only'
             2240  CALL_METHOD_2         2  '2 positional arguments'
             2242  STORE_FAST               'selected_dest_transform'

 L.7208      2244  LOAD_GLOBAL              isinstance
             2246  LOAD_FAST                'dest'
             2248  LOAD_GLOBAL              SlotGoal
             2250  CALL_FUNCTION_2       2  '2 positional arguments'
         2252_2254  POP_JUMP_IF_FALSE  2280  'to 2280'
             2256  LOAD_FAST                'dest_path'
             2258  LOAD_CONST               -1
             2260  BINARY_SUBSCR    
             2262  LOAD_ATTR                body
             2264  LOAD_ATTR                posture_type
             2266  LOAD_ATTR                mobile
         2268_2270  POP_JUMP_IF_TRUE   2280  'to 2280'

 L.7209      2272  LOAD_FAST                'dest'
             2274  LOAD_ATTR                containment_transform
             2276  STORE_FAST               'selected_dest_containment_transform'
             2278  JUMP_FORWARD       2284  'to 2284'
           2280_0  COME_FROM          2268  '2268'
           2280_1  COME_FROM          2252  '2252'

 L.7211      2280  LOAD_FAST                'selected_dest_transform'
             2282  STORE_FAST               'selected_dest_containment_transform'
           2284_0  COME_FROM          2278  '2278'

 L.7213      2284  LOAD_GLOBAL              interactions
             2286  LOAD_ATTR                constraints
             2288  LOAD_ATTR                Transform
             2290  LOAD_FAST                'selected_dest_containment_transform'

 L.7214      2292  LOAD_FAST                'dest'
             2294  LOAD_ATTR                routing_surface_id
             2296  LOAD_CONST               ('routing_surface',)
             2298  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
             2300  STORE_FAST               'selected_dest_constraint'

 L.7215      2302  LOAD_FAST                'dest'
             2304  LOAD_ATTR                connectivity_handle
             2306  LOAD_ATTR                constraint
             2308  STORE_FAST               'constraint'

 L.7216      2310  LOAD_FAST                'constraint'
             2312  LOAD_METHOD              apply
             2314  LOAD_FAST                'selected_dest_constraint'
             2316  CALL_METHOD_1         1  '1 positional argument'
             2318  STORE_FAST               'd_route_constraint'

 L.7221      2320  LOAD_FAST                'd_route_constraint'
             2322  LOAD_ATTR                multi_surface
         2324_2326  POP_JUMP_IF_FALSE  2340  'to 2340'

 L.7222      2328  LOAD_FAST                'd_route_constraint'
             2330  LOAD_METHOD              get_single_surface_version
             2332  LOAD_FAST                'dest'
             2334  LOAD_ATTR                routing_surface_id
             2336  CALL_METHOD_1         1  '1 positional argument'
             2338  STORE_FAST               'd_route_constraint'
           2340_0  COME_FROM          2324  '2324'

 L.7228      2340  LOAD_FAST                'd_route_constraint'
             2342  LOAD_ATTR                valid
         2344_2346  POP_JUMP_IF_TRUE   2352  'to 2352'

 L.7229      2348  LOAD_FAST                'constraint'
             2350  STORE_FAST               'd_route_constraint'
           2352_0  COME_FROM          2344  '2344'

 L.7232      2352  LOAD_GLOBAL              PathSpec
             2354  LOAD_FAST                'dest_path'
             2356  LOAD_FAST                'dest'
             2358  LOAD_ATTR                path_cost

 L.7233      2360  LOAD_FAST                'dest_path'
             2362  LOAD_ATTR                segmented_path
             2364  LOAD_ATTR                var_map_resolved

 L.7234      2366  LOAD_FAST                'destination_spec'

 L.7235      2368  LOAD_FAST                'd_route_constraint'

 L.7236      2370  LOAD_FAST                'dest_path'
             2372  LOAD_ATTR                segmented_path
             2374  LOAD_ATTR                constraint

 L.7237      2376  LOAD_FAST                'is_failure_path'
             2378  LOAD_CONST               ('is_failure_path',)
             2380  CALL_FUNCTION_KW_7     7  '7 total positional and keyword args'
             2382  STORE_FAST               'right_path_spec'

 L.7241      2384  LOAD_FAST                'dest_path'
             2386  LOAD_ATTR                segmented_path
             2388  LOAD_ATTR                constraint
             2390  LOAD_CONST               None
             2392  COMPARE_OP               is-not
         2394_2396  POP_JUMP_IF_FALSE  2454  'to 2454'

 L.7242      2398  LOAD_FAST                'interaction'
             2400  LOAD_ATTR                carry_target
             2402  LOAD_CONST               None
             2404  COMPARE_OP               is-not
         2406_2408  POP_JUMP_IF_FALSE  2420  'to 2420'

 L.7243      2410  LOAD_FAST                'interaction'
             2412  LOAD_ATTR                carry_target
             2414  BUILD_TUPLE_1         1 
             2416  STORE_FAST               'objects_to_ignore'
             2418  JUMP_FORWARD       2424  'to 2424'
           2420_0  COME_FROM          2406  '2406'

 L.7245      2420  LOAD_GLOBAL              DEFAULT
             2422  STORE_FAST               'objects_to_ignore'
           2424_0  COME_FROM          2418  '2418'

 L.7246      2424  LOAD_DEREF               'self'
             2426  LOAD_METHOD              _generate_surface_and_slot_targets
             2428  LOAD_FAST                'right_path_spec'

 L.7247      2430  LOAD_FAST                'left_path_spec'
             2432  LOAD_FAST                'dest'
             2434  LOAD_ATTR                location
             2436  LOAD_FAST                'objects_to_ignore'
             2438  CALL_METHOD_4         4  '4 positional arguments'
         2440_2442  POP_JUMP_IF_TRUE   2454  'to 2454'

 L.7248      2444  LOAD_CONST               False
             2446  LOAD_GLOBAL              EMPTY_PATH_SPEC
             2448  LOAD_CONST               None
             2450  BUILD_TUPLE_3         3 
             2452  RETURN_VALUE     
           2454_0  COME_FROM          2440  '2440'
           2454_1  COME_FROM          2394  '2394'

 L.7251      2454  LOAD_FAST                'dest'
             2456  LOAD_ATTR                has_slot_params
         2458_2460  POP_JUMP_IF_FALSE  2468  'to 2468'
             2462  LOAD_FAST                'dest'
             2464  LOAD_ATTR                slot_params
             2466  JUMP_FORWARD       2472  'to 2472'
           2468_0  COME_FROM          2458  '2458'
             2468  LOAD_GLOBAL              frozendict
             2470  CALL_FUNCTION_0       0  '0 positional arguments'
           2472_0  COME_FROM          2466  '2466'
             2472  STORE_FAST               'd_locked_params'

 L.7255      2474  LOAD_FAST                'plan_primitive'
             2476  LOAD_ATTR                path
             2478  STORE_FAST               'cur_path'

 L.7256      2480  SETUP_LOOP         2646  'to 2646'
             2482  LOAD_FAST                'cur_path'
             2484  LOAD_ATTR                next_path
             2486  LOAD_CONST               None
             2488  COMPARE_OP               is-not
         2490_2492  POP_JUMP_IF_FALSE  2644  'to 2644'

 L.7257      2494  LOAD_FAST                'cur_path'
             2496  LOAD_ATTR                portal_obj
             2498  STORE_FAST               'portal_obj'

 L.7258      2500  LOAD_FAST                'cur_path'
             2502  LOAD_ATTR                portal_id
             2504  STORE_FAST               'portal_id'

 L.7262      2506  LOAD_FAST                'left_path_spec'
             2508  LOAD_ATTR                create_route_nodes
             2510  LOAD_FAST                'cur_path'
             2512  LOAD_FAST                'portal_obj'
             2514  LOAD_FAST                'portal_id'
             2516  LOAD_CONST               ('portal_obj', 'portal_id')
             2518  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
         2520_2522  POP_JUMP_IF_TRUE   2554  'to 2554'

 L.7266      2524  LOAD_DEREF               'self'
             2526  LOAD_METHOD              _get_failure_path_spec_gen
             2528  LOAD_FAST                'timeline'
             2530  LOAD_FAST                'sim'
             2532  LOAD_FAST                'source_destination_sets'
             2534  CALL_METHOD_3         3  '3 positional arguments'
             2536  GET_YIELD_FROM_ITER
             2538  LOAD_CONST               None
             2540  YIELD_FROM       
             2542  STORE_FAST               'failure_path'

 L.7267      2544  LOAD_CONST               False
             2546  LOAD_FAST                'failure_path'
             2548  LOAD_CONST               None
             2550  BUILD_TUPLE_3         3 
             2552  RETURN_VALUE     
           2554_0  COME_FROM          2520  '2520'

 L.7272      2554  LOAD_FAST                'portal_obj'
             2556  LOAD_CONST               None
             2558  COMPARE_OP               is-not
         2560_2562  POP_JUMP_IF_FALSE  2612  'to 2612'

 L.7273      2564  LOAD_FAST                'portal_obj'
             2566  LOAD_METHOD              get_portal_by_id
             2568  LOAD_FAST                'portal_id'
             2570  CALL_METHOD_1         1  '1 positional argument'
             2572  STORE_FAST               'portal_instance'

 L.7274      2574  LOAD_FAST                'portal_instance'
             2576  LOAD_CONST               None
             2578  COMPARE_OP               is-not
         2580_2582  POP_JUMP_IF_FALSE  2612  'to 2612'
             2584  LOAD_FAST                'portal_instance'
             2586  LOAD_ATTR                traversal_type
             2588  LOAD_ATTR                discourage_portal_on_plan
         2590_2592  POP_JUMP_IF_FALSE  2612  'to 2612'

 L.7275      2594  LOAD_FAST                'portal_obj'
             2596  LOAD_ATTR                set_portal_cost_override
             2598  LOAD_FAST                'portal_id'
             2600  LOAD_GLOBAL              routing
             2602  LOAD_ATTR                PORTAL_PLAN_LOCK
             2604  LOAD_FAST                'sim'
             2606  LOAD_CONST               ('sim',)
             2608  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
             2610  POP_TOP          
           2612_0  COME_FROM          2590  '2590'
           2612_1  COME_FROM          2580  '2580'
           2612_2  COME_FROM          2560  '2560'

 L.7277      2612  LOAD_FAST                'cur_path'
             2614  LOAD_ATTR                next_path
             2616  STORE_FAST               'cur_path'

 L.7282      2618  LOAD_FAST                'cur_path'
             2620  LOAD_ATTR                selected_goal
             2622  STORE_FAST               'dest'

 L.7283      2624  LOAD_FAST                'cur_path'
             2626  LOAD_ATTR                final_location
             2628  LOAD_FAST                'dest'
             2630  STORE_ATTR               location

 L.7288      2632  LOAD_FAST                'cur_path'
             2634  LOAD_METHOD              add_destination_to_quad_tree
             2636  CALL_METHOD_0         0  '0 positional arguments'
             2638  POP_TOP          
         2640_2642  JUMP_BACK          2482  'to 2482'
           2644_0  COME_FROM          2490  '2490'
             2644  POP_BLOCK        
           2646_0  COME_FROM_LOOP     2480  '2480'

 L.7290      2646  LOAD_FAST                'left_path_spec'
             2648  LOAD_ATTR                _path
             2650  LOAD_CONST               -1
             2652  BINARY_SUBSCR    
             2654  LOAD_ATTR                posture_spec
             2656  LOAD_FAST                'right_path_spec'
             2658  LOAD_ATTR                _path
             2660  LOAD_CONST               0
             2662  BINARY_SUBSCR    
             2664  LOAD_ATTR                posture_spec
             2666  COMPARE_OP               !=
         2668_2670  POP_JUMP_IF_FALSE  2786  'to 2786'

 L.7294      2672  LOAD_GLOBAL              TransitionSpecCython_create
             2674  LOAD_FAST                'right_path_spec'
             2676  LOAD_FAST                'left_path_spec'
             2678  LOAD_ATTR                _path
             2680  LOAD_CONST               -1
             2682  BINARY_SUBSCR    
             2684  LOAD_ATTR                posture_spec

 L.7295      2686  LOAD_FAST                'right_path_spec'
             2688  LOAD_ATTR                _path
             2690  LOAD_CONST               0
             2692  BINARY_SUBSCR    
             2694  LOAD_ATTR                var_map
             2696  LOAD_GLOBAL              SequenceId
             2698  LOAD_ATTR                DEFAULT

 L.7296      2700  LOAD_FAST                'right_path_spec'
             2702  LOAD_ATTR                _path
             2704  LOAD_CONST               0
             2706  BINARY_SUBSCR    
             2708  LOAD_ATTR                portal_obj

 L.7297      2710  LOAD_FAST                'right_path_spec'
             2712  LOAD_ATTR                _path
             2714  LOAD_CONST               0
             2716  BINARY_SUBSCR    
             2718  LOAD_ATTR                portal_id
             2720  CALL_FUNCTION_6       6  '6 positional arguments'
             2722  STORE_FAST               'right_first_spec'

 L.7303      2724  LOAD_FAST                'right_first_spec'
             2726  LOAD_ATTR                portal_obj
             2728  LOAD_CONST               None
             2730  COMPARE_OP               is-not
         2732_2734  POP_JUMP_IF_FALSE  2752  'to 2752'

 L.7304      2736  LOAD_FAST                'right_path_spec'
             2738  LOAD_ATTR                _path
             2740  LOAD_METHOD              insert
             2742  LOAD_CONST               0
             2744  LOAD_FAST                'right_first_spec'
             2746  CALL_METHOD_2         2  '2 positional arguments'
             2748  POP_TOP          
             2750  JUMP_FORWARD       2762  'to 2762'
           2752_0  COME_FROM          2732  '2732'

 L.7306      2752  LOAD_FAST                'right_first_spec'
             2754  LOAD_FAST                'right_path_spec'
             2756  LOAD_ATTR                _path
             2758  LOAD_CONST               0
             2760  STORE_SUBSCR     
           2762_0  COME_FROM          2750  '2750'

 L.7308      2762  LOAD_FAST                'right_first_spec'
             2764  LOAD_METHOD              set_path
             2766  LOAD_FAST                'cur_path'
             2768  LOAD_FAST                'd_route_constraint'
             2770  CALL_METHOD_2         2  '2 positional arguments'
             2772  POP_TOP          

 L.7309      2774  LOAD_FAST                'right_first_spec'
             2776  LOAD_METHOD              set_locked_params
             2778  LOAD_FAST                'd_locked_params'
             2780  CALL_METHOD_1         1  '1 positional argument'
             2782  POP_TOP          
             2784  JUMP_FORWARD       2800  'to 2800'
           2786_0  COME_FROM          2668  '2668'

 L.7311      2786  LOAD_FAST                'right_path_spec'
             2788  LOAD_METHOD              attach_route_and_params
             2790  LOAD_FAST                'cur_path'

 L.7312      2792  LOAD_FAST                'd_locked_params'
             2794  LOAD_FAST                'd_route_constraint'
             2796  CALL_METHOD_3         3  '3 positional arguments'
             2798  POP_TOP          
           2800_0  COME_FROM          2784  '2784'

 L.7314      2800  LOAD_FAST                'left_path_spec'
             2802  LOAD_METHOD              combine
             2804  LOAD_FAST                'right_path_spec'
             2806  CALL_METHOD_1         1  '1 positional argument'
             2808  STORE_FAST               'path_spec'

 L.7315      2810  LOAD_CONST               True
             2812  LOAD_FAST                'path_spec'
             2814  LOAD_FAST                'dest'
             2816  BUILD_TUPLE_3         3 
             2818  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `LOAD_SETCOMP' instruction at offset 830

    def normalize_goal_costs(self, all_goals):
        min_cost = sims4.math.MAX_UINT16
        for goal in all_goals:
            if goal.cost < min_cost:
                min_cost = goal.cost

        if min_cost == 0:
            return
        for goal in all_goals:
            goal.cost -= min_cost

    def _get_failure_path_spec_gen(self, timeline, sim, source_destination_sets, interaction=None, failed_path_type=None):
        all_sources = {}
        all_destinations = {}
        all_invalid_sources = {}
        all_invalid_los_sources = {}
        all_invalid_destinations = {}
        all_invalid_los_destinations = {}
        for source_handles, destination_handles, invalid_sources, invalid_los_sources, invalid_destinations, invalid_los_destinations in source_destination_sets.values():
            all_sources.update(source_handles)
            all_destinations.update(destination_handles)
            all_invalid_sources.update(invalid_sources)
            all_invalid_los_sources.update(invalid_los_sources)
            all_invalid_destinations.update(invalid_destinations)
            all_invalid_los_destinations.update(invalid_los_destinations)

        set_transition_failure_reason(sim, TransitionFailureReasons.PATH_PLAN_FAILED)
        failure_sources = all_sources or all_invalid_sources or all_invalid_los_sources
        if not failure_sources:
            if sim.posture.is_vehicle:
                sim.posture.source_interaction.cancel(FinishingType.TRANSITION_FAILURE, 'Canceled Vehicle Posture from Failure Path.')
        else:
            return EMPTY_PATH_SPEC
            best_left_data = None
            best_left_cost = sims4.math.MAX_UINT32
            for source_handle, (_, path_cost, _, _, _, _, _) in failure_sources.items():
                if path_cost < best_left_cost:
                    best_left_cost = path_cost
                    best_left_data = failure_sources[source_handle]
                    best_left_goal = best_left_data[4][0]

            fail_left_path_spec = PathSpec((best_left_data[0]), (best_left_data[1]), (best_left_data[2]),
              (best_left_data[3]), (best_left_data[5]),
              (best_left_data[6]), is_failure_path=True,
              failed_path_type=failed_path_type)
            if best_left_goal is not None:
                if best_left_goal.has_slot_params:
                    if best_left_goal.slot_params:
                        fail_left_path_spec.attach_route_and_params(None,
                          (best_left_goal.slot_params), None, reverse=True)
            failure_destinations = all_destinations or all_invalid_destinations or all_invalid_los_destinations
            return failure_destinations or EMPTY_PATH_SPEC
        height_clearance_override_tuning = interaction.min_height_clearance if interaction is not None else None
        required_height_clearance = get_required_height_clearance(sim, override_tuning=height_clearance_override_tuning)
        all_destination_goals = []
        for _, _, _, _, dest_goals, _, _ in failure_destinations.values():
            all_destination_goals.extend(dest_goals)
            for goal in dest_goals:
                if required_height_clearance > goal.height_clearance:
                    all_destination_goals.remove(goal)
                    continue

        if all_destination_goals:
            route = routing.Route((best_left_goal.location), all_destination_goals, routing_context=(sim.routing_context))
            plan_element = interactions.utils.routing.PlanRoute(route, sim, interaction=interaction)
            result = yield from element_utils.run_child(timeline, plan_element)
            if not result:
                raise RuntimeError('Failed to generate a failure path.')
            if plan_element.path.nodes:
                if len(plan_element.path.nodes) > 1:
                    first_node = plan_element.path.nodes[0]
                    min_water_depth, max_water_depth = OceanTuning.make_depth_bounds_safe_for_surface_and_sim(first_node.routing_surface_id, sim)
                    for node in list(plan_element.path.nodes)[1:]:
                        depth = terrain.get_water_depth(node.position[0], node.position[2], node.routing_surface_id.secondary_id)
                        if min_water_depth is not None:
                            if depth < min_water_depth:
                                return EMPTY_PATH_SPEC
                            if max_water_depth is not None and max_water_depth < depth:
                                return EMPTY_PATH_SPEC

                fail_left_path_spec.create_route_nodes(plan_element.path)
                destinations = {goal.connectivity_handle.path[-1] for goal in all_destination_goals}
                if len(destinations) > 1:
                    logger.warn('Too many destinations: {}', destinations, trigger_breakpoint=True)
                fail_left_path_spec.destination_spec = next(iter(destinations))
                return fail_left_path_spec
        return EMPTY_PATH_SPEC
        if False:
            yield None

    def handle_teleporting_path(self, segmented_paths):
        best_left_path = None
        best_cost = None
        for segmented_path in segmented_paths:
            for left_path in segmented_path.generate_left_paths():
                cost = left_path.cost
                if best_left_path is None or cost < best_cost:
                    best_left_path = left_path
                    best_cost = cost
                    if left_path[-1] in segmented_path.destination_specs:
                        dest_spec = segmented_path.destination_specs[left_path[-1]]
                    else:
                        dest_spec = left_path[-1]
                    var_map = segmented_path.var_map_resolved
                else:
                    break

        if best_left_path is None:
            raise ValueError('No left paths found for teleporting path.')
        return PathSpec(best_left_path, (best_left_path.cost), var_map, dest_spec,
          None, None, path_as_posture_specs=True)

    def update_sim_node_caches(self, sim):
        if sim in self._graph.cached_sim_nodes:
            del self._graph.cached_sim_nodes[sim]
        zone = services.current_zone()
        if zone is None:
            return
        active_household = services.active_household()
        if active_household is None:
            return
        if zone.is_zone_shutting_down:
            self._graph.proxy_sim = None
            return
        from_init = self._graph.proxy_sim is None
        if from_init or self._graph.proxy_sim.sim_proxied is sim:
            for instanced_sim in active_household.instanced_sims_gen(allow_hidden_flags=ALL_HIDDEN_REASONS):
                if instanced_sim.sim_info.is_teen_or_older and instanced_sim is not sim:
                    self.update_generic_sim_carry_node(instanced_sim, from_init=from_init)
                    return

            sim_info_manager = services.sim_info_manager()
            for instanced_sim in sim_info_manager.instanced_sims_gen(allow_hidden_flags=ALL_HIDDEN_REASONS):
                if instanced_sim.sim_info.is_teen_or_older and instanced_sim is not sim:
                    self.update_generic_sim_carry_node(instanced_sim, from_init=from_init)
                    return

            self._graph.proxy_sim = None

    def _find_first_constrained_edge(self, sim, path, var_map, reverse=False):
        if not path:
            return (None, None, None)
        elif reverse:
            sequence = reversed(path)
        else:
            sequence = path
        for posture_spec in sequence:
            if not posture_spec.body.posture_type.unconstrained:
                return (
                 posture_spec, None, None)

        if len(path) > 1:
            sequence = zip(path, path[1:])
            if reverse:
                sequence = reversed(list(sequence))
            for spec_a, spec_b in sequence:
                edge_info = self.get_edge(spec_a, spec_b)
                if edge_info is not None:
                    for op in edge_info.operations:
                        constraint = op.get_constraint(sim, spec_a, var_map)
                        if constraint is not None and constraint is not ANYWHERE:
                            return (
                             posture_spec, op, spec_a)

        return (
         posture_spec, None, None)

    def find_entry_posture_spec(self, sim, path, var_map):
        return self._find_first_constrained_edge(sim, path, var_map)

    def find_exit_posture_spec(self, sim, path, var_map):
        return self._find_first_constrained_edge(sim, path, var_map, reverse=True)

    def _get_locations_from_posture(self, sim, posture_spec, var_map, interaction=None, participant_type=None, constrained_edge=None, mobile_posture_spec=None, animation_resolver_fn=None, final_constraint=None, transition_posture_name='stand', left_most_spec=None):
        body_target = posture_spec.body.target
        body_posture_type = posture_spec.body.posture_type
        body_unconstrained = body_posture_type.unconstrained
        should_add_vehicle_slot_constraint = mobile_posture_spec is None or posture_spec != mobile_posture_spec
        should_add_vehicle_slot_constraint |= left_most_spec is not None and left_most_spec != posture_spec
        if interaction is not None:
            if interaction.transition is not None:
                interaction.transition.add_relevant_object(body_target)
                interaction.transition.add_relevant_object(interaction.target)
        body_posture = postures.create_posture(body_posture_type, sim,
          body_target, is_throwaway=True)
        if not (body_posture.unconstrained or body_posture).is_vehicle or should_add_vehicle_slot_constraint:
            constraint_intersection = body_posture.slot_constraint
            if constraint_intersection is None:
                return (
                 True, (None, None, body_target))
                if final_constraint is not None:
                    if constraint_intersection.valid:
                        if not isinstance(final_constraint, RequiredSlotSingle):
                            constraint_geometry_only = final_constraint.generate_geometry_only_constraint()
                            constraint_intersection = constraint_intersection.intersect(constraint_geometry_only)
            else:
                if interaction is None:
                    return (True, (None, None, body_target))
                    target_posture_state = postures.posture_state.PostureState(sim,
                      None, posture_spec, var_map, invalid_expected=True, body_state_spec_only=True,
                      is_throwaway=True)
                    if any((constraint.posture_state_spec.is_filtered_target() for constraint in final_constraint if constraint.posture_state_spec is not None)):
                        base_object = body_target
                    else:
                        base_object = None
                    target = interaction.target
                    with interaction.override_var_map(sim, var_map):
                        interaction_constraint = interaction.apply_posture_state_and_interaction_to_constraint(target_posture_state,
                          final_constraint, sim=sim,
                          target=(base_object or target),
                          participant_type=participant_type,
                          base_object=base_object)
                        target_posture_state.add_constraint(self, interaction_constraint)
                    constraint_intersection = target_posture_state.constraint_intersection
                elif body_unconstrained and animation_resolver_fn is not None and constrained_edge is not None:
                    if constraint_intersection.valid:
                        edge_constraint = constrained_edge.get_constraint(sim, posture_spec, var_map)
                        edge_constraint_resolved = edge_constraint.apply_posture_state(target_posture_state, animation_resolver_fn)
                        edge_constraint_resolved_geometry_only = edge_constraint_resolved.generate_geometry_only_constraint()
                        constraint_intersection = constraint_intersection.intersect(edge_constraint_resolved_geometry_only)
                else:
                    if not constraint_intersection.valid:
                        return (
                         False, (constraint_intersection.generate_single_surface_constraints(), None, body_target))
                    for constraint in constraint_intersection:
                        if constraint.geometry is not None:
                            break
                    else:
                        return (
                         True, (None, None, body_target))

                    constraint_intersection = constraint_intersection.generate_single_surface_constraints()
                    locked_params = frozendict()
                    if body_target is not None:
                        target_name = posture_spec.body.posture_type.get_target_name(sim=sim, target=body_target)
                        if target_name is not None:
                            anim_overrides = body_target.get_anim_overrides(target_name)
                            if anim_overrides is not None:
                                locked_params += anim_overrides.params
            routing_target = None
            if body_target is not None:
                routing_target = body_target
        if interaction.target is not None:
            routing_target = posture_spec.requires_carry_target_in_hand or posture_spec.requires_carry_target_in_slot or interaction.target
        else:
            if interaction.target.parent is not sim:
                routing_target = interaction.target
            else:
                if interaction is not None:
                    if interaction.transition is not None:
                        interaction.transition.add_relevant_object(routing_target)
                locked_params += sim.get_sim_locked_params()
                if interaction is not None:
                    if interaction.is_super and body_posture_type is not None:
                        actor_name = body_posture_type.get_actor_name(sim=sim, target=body_target)
                        target_name = body_posture_type.get_target_name(sim=sim, target=body_target)
                        locked_params += interaction.get_interaction_locked_params(actor_name, target_name)
            locked_params += body_posture.get_slot_offset_locked_params()
            posture_locked_params = locked_params + {'transitionPosture': transition_posture_name}
            return (False, (constraint_intersection, posture_locked_params, routing_target))

    def get_compatible_mobile_posture_target(self, sim):
        posture_object = None
        compatible_postures_and_targets = self.get_compatible_mobile_postures_and_targets(sim)
        if compatible_postures_and_targets:
            posture_type = sim.posture_state.body.posture_type
            for target, compatible_postures in compatible_postures_and_targets.items():
                if posture_type.is_vehicle or posture_type in compatible_postures:
                    posture_object = target
                    break
            else:
                posture_object, _ = next(iter(compatible_postures_and_targets.items()))

        return posture_object

    def get_compatible_mobile_postures_and_targets(self, sim):
        mobile_postures = {}
        found_objects = self._query_quadtree_for_mobile_posture_objects(sim, test_footprint=True)
        for found_obj in found_objects:
            mobile_posture_types = found_obj.provided_mobile_posture_types
            if mobile_posture_types:
                if found_obj.has_posture_portals():
                    posture_entry, _ = found_obj.get_nearest_posture_change(sim)
            if posture_entry is not None:
                if posture_entry.body.posture_type in mobile_posture_types:
                    mobile_postures[found_obj] = (
                     posture_entry.body.posture_type,)
                    continue
                mobile_postures[found_obj] = mobile_posture_types

        return mobile_postures

    def _query_quadtree_for_mobile_posture_objects(self, sim, test_footprint=False):
        if self._mobile_posture_objects_quadtree is None:
            return []
        else:
            pathplan_context = sim.get_routing_context()
            quadtree_polygon = pathplan_context.get_quadtree_polygon()
            if not isinstance(quadtree_polygon, QtCircle):
                lower_bound, upper_bound = quadtree_polygon.bounds()
                quadtree_polygon = sims4.geometry.QtRect(sims4.math.Vector2(lower_bound.x, lower_bound.z), sims4.math.Vector2(upper_bound.x, upper_bound.z))
            query = sims4.geometry.SpatialQuery(quadtree_polygon, [
             self._mobile_posture_objects_quadtree])
            found_objs = query.run()
            found_objs = [posture_obj for posture_obj in found_objs if posture_obj.level == sim.level]
            special_obj = None
            if sim.in_pool:
                special_obj = pool_utils.get_pool_by_block_id(sim.block_id)
            else:
                if sim.routing_surface.type == SurfaceType.SURFACETYPE_POOL:
                    special_obj = services.terrain_service.ocean_object()
        if not test_footprint:
            if special_obj is not None:
                found_objs.append(special_obj)
            return found_objs
        mobile_posture_objects = []
        sim_pos = sim.position
        for mobile_obj in found_objs:
            polygon = mobile_obj.get_polygon_from_footprint_name_hashes(mobile_obj.placement_footprint_hash_set)
            if not polygon is None:
                if not test_point_in_compound_polygon(sim_pos, polygon):
                    continue
                mobile_posture_objects.append(mobile_obj)

        if special_obj is not None:
            mobile_posture_objects.append(special_obj)
        return mobile_posture_objects

    def add_object_to_mobile_posture_quadtree(self, obj):
        if not is_object_mobile_posture_compatible(obj):
            return
        location = sims4.math.Vector2(obj.position.x, obj.position.z)
        if obj.is_in_inventory():
            if location == TunableVector2.DEFAULT_ZERO:
                return
        if self._mobile_posture_objects_quadtree is None:
            self._mobile_posture_objects_quadtree = sims4.geometry.QuadTree()
        polygon = obj.get_polygon_from_footprint_name_hashes(obj.placement_footprint_hash_set)
        if polygon is None:
            return
        lower_bound, upper_bound = polygon.bounds()
        bounding_box = sims4.geometry.QtRect(sims4.math.Vector2(lower_bound.x, lower_bound.z), sims4.math.Vector2(upper_bound.x, upper_bound.z))
        self._mobile_posture_objects_quadtree.insert(obj, bounding_box)

    def remove_object_from_mobile_posture_quadtree(self, obj):
        if self._mobile_posture_objects_quadtree is None:
            return
        self._mobile_posture_objects_quadtree.remove(obj)

    def _query_mobile_posture_objects_for_reset(self, posture_obj=None, test_footprint=False):
        sims = set()
        for sim in services.sim_info_manager().instanced_sims_gen():
            if not sim.is_on_active_lot():
                continue
            found_objs = tuple(self._query_quadtree_for_mobile_posture_objects(sim, test_footprint=test_footprint))
            if posture_obj is not None:
                if posture_obj not in found_objs:
                    continue
            if found_objs:
                sims.add(sim)

        return sims

    def mobile_posture_object_location_changed(self, obj, *_, **__):
        zone = services.current_zone()
        if zone.is_zone_loading:
            return
        before_sims = self._query_mobile_posture_objects_for_reset(obj)
        self.remove_object_from_mobile_posture_quadtree(obj)
        self.add_object_to_mobile_posture_quadtree(obj)
        after_sims = self._query_mobile_posture_objects_for_reset(obj, test_footprint=True)
        affected_sims = before_sims.difference(after_sims) | after_sims
        services.get_reset_and_delete_service().trigger_batch_reset(tuple((sim for sim in affected_sims)), ResetReason.RESET_EXPECTED, obj, 'Mobile posture object moved.')

    def _can_transition_between_nodes(self, source_spec, destination_spec):
        if self.get_edge(source_spec, destination_spec, return_none_on_failure=True) is None:
            return False
        return True

    def get_edge(self, spec_a, spec_b, return_none_on_failure=False):
        try:
            edge_info, _ = self._get_edge_info(spec_a, spec_b)
            if edge_info is None:
                if spec_a.body.posture_type != spec_b.body.posture_type or spec_a.carry != spec_b.carry:
                    if not return_none_on_failure:
                        raise KeyError('Edge not found in posture graph: [{:s}] -> [{:s}]'.format(spec_a, spec_b))
                    return
                return EdgeInfo((), None, 0)
            return edge_info
        except:
            pass

    def print_summary(self, _print=logger.always):
        num_nodes = len(self._graph)
        num_edges = len(self._edge_info)
        object_totals = collections.defaultdict(collections.Counter)
        for node, node_data in self._graph.items():
            objects = {o for o in (node.body_target, node.surface_target) if o is not None}
            if objects:
                for obj in objects:
                    object_totals[obj.definition]['nodes'] += 1
                    object_totals[obj.definition]['edges'] += len(node_data.successors)

            else:
                object_totals['Untargeted']['nodes'] += 1
                object_totals['Untargeted']['edges'] += len(node_data.successors)

        unique_objects = collections.defaultdict(set)
        for node in self._graph:
            objects = {o for o in (node.body_target, node.surface_target) if o is not None}
            for obj in objects:
                unique_objects[obj.definition].add(obj.id)
                object_totals[obj.definition]['parts'] = len(obj.part_owner.parts or (1, )) if obj.is_part else 1

        for definition, instances in unique_objects.items():
            object_totals[definition]['instances'] = len(instances)

        object_totals['Untargeted']['instances'] = 1
        _print('Posture Graph Summary\n====================================================\nTotal node count = {}\nTotal edge count = {}\n\nObjects:\n===================================================\n'.format(num_nodes, num_edges))
        for definition, data in sorted((list(object_totals.items())), reverse=True, key=(lambda x: x[1]['nodes'])):
            if hasattr(definition, 'name'):
                if definition.name is None:
                    def_display = definition.id
                else:
                    def_display = definition.name
            else:
                def_display = definition
            line = ('{:<42} : {instances:>5} instances   {nodes:>5} nodes   {edges:>5} edges'.format)(
             def_display, **data)
            line += '   {:>3} parts/instance   {:>5.4} nodes/instance   {:>5.4} edges/instance'.format(data['parts'], data['nodes'] / data['instances'], data['edges'] / data['instances'])
            _print(line)

    def get_nodes_and_edges(self):
        return (
         len(self._graph), len(self._edge_info))

    def export(self, filename='posture_graph'):
        graph = cython.cast(PostureGraph, self._graph)
        edge_info = self._edge_info
        attribute_indexes = {}
        w = xml.etree.ElementTree.TreeBuilder()
        w.start('gexf', {
         'xmlns': "'http://www.gexf.net/1.2draft'", 
         'xmlns:xsi': "'http://www.w3.org/2001/XMLSchema-instance'", 
         'xsi:schemaLocation': "'http://www.gexf.net/1.2draft/gexf.xsd'", 
         'version': "'1.2'"})
        w.start('meta', {})
        w.start('creator', {})
        w.data('Electronic Arts')
        w.end('creator')
        w.start('description', {})
        w.data('Tuning topology')
        w.end('description')
        w.end('meta')
        w.start('graph', {'defaultedgetype':'directed', 
         'mode':'static'})
        TYPE_MAPPING = {str: 'string', 
         int: 'float', 
         float: 'float'}
        w.start('attributes', {'class': 'node'})
        attribute_index = 0
        for attribute_name, attribute_type in PostureSpec._attribute_definitions:
            attribute_indexes[attribute_name] = str(attribute_index)
            w.start('attribute', {'id':str(attribute_index), 
             'title':attribute_name.strip('_').title().replace('_', ' '), 
             'type':TYPE_MAPPING[attribute_type]})
            w.end('attribute')
            attribute_index += 1

        w.end('attributes')
        nodes = set()
        edge_nodes = set()
        w.start('nodes', {})
        for node in sorted((graph.nodes), key=repr):
            nodes.add(hash(node))
            w.start('node', {'id':str(hash(node)), 
             'label':str(node)})
            w.start('attvalues', {})
            for attribute_name, attribute_type in PostureSpec._attribute_definitions:
                attr_value = getattr(node, attribute_name)
                w.start('attvalue', {'for':attribute_indexes[attribute_name], 
                 'value':str(attr_value)})
                w.end('attvalue')

            w.end('attvalues')
            w.end('node')

        w.end('nodes')
        w.start('edges', {})
        edge_id = 0
        for node in sorted((graph.nodes), key=repr):
            for connected_node in sorted((graph.get_successors(node)), key=repr):
                edge_nodes.add(hash(node))
                edge_nodes.add(hash(connected_node))
                w.start('edge', {'id':str(edge_id), 
                 'label':', '.join((str(operation) for operation in edge_info[(node, connected_node)].operations)), 
                 'source':str(hash(node)), 
                 'target':str(hash(connected_node))})
                w.end('edge')
                edge_id += 1

        w.end('edges')
        w.end('graph')
        w.end('gexf')
        tree = w.close()

        def indent(elem, level=0):
            i = '\n' + level * '  '
            if len(elem):
                if not (elem.text and elem.text.strip()):
                    elem.text = i + '  '
                if not (elem.tail and elem.tail.strip()):
                    elem.tail = i
                for elem in elem:
                    indent(elem, level + 1)

                elem.tail = elem.tail and elem.tail.strip() or i
            else:
                if level:
                    elem.tail = elem.tail and elem.tail.strip() or i

        indent(tree)
        from os.path import expanduser
        path = expanduser('~')
        file = open('{}\\Desktop\\{}.gexf'.format(path, filename), 'wb')
        file.write(xml.etree.ElementTree.tostring(tree))
        file.close()
        print('DONE!')

    def build_node_counts_list(self):
        node_count_dict = {}
        graph = cython.cast(PostureGraph, self._graph)
        for node in sorted((graph.nodes), key=repr):
            if node.body_target is None:
                continue
            body_target = node.body_target if not node.body_target.is_part else node.body_target.part_owner
            if body_target.definition in node_count_dict:
                if body_target in node_count_dict[body_target.definition]:
                    node_count_dict[body_target.definition][body_target] += 1
                else:
                    node_count_dict[body_target.definition][body_target] = 1
            else:
                node_count_dict[body_target.definition] = {}
                node_count_dict[body_target.definition][body_target] = 1

        return node_count_dict