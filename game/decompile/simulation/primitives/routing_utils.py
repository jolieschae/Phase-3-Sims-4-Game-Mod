# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\primitives\routing_utils.py
# Compiled at: 2018-08-20 16:30:05
# Size of source mod 2**32: 7207 bytes
from sims4.math import MAX_FLOAT
from sims4.tuning.tunable import Tunable
import operator, routing, sims4.log, build_buy, services
logger = sims4.log.Logger('RoutingUtils')

class DistanceEstimationTuning:
    DISTANCE_PER_FLOOR = Tunable(float, 50, description='\n    The cost per floor difference in the two points. Ex: if this is tuned to 50 and a Sim is trying to use an object on the third floor of their house while on the first floor, the distance estimate would be 100 meters.')
    DISTANCE_PER_ROOM = Tunable(float, 10, description='\n    The cost per room between the points. This should be the average diameter of rooms that people tend to build.')
    UNREACHABLE_GOAL_COST = 100000


def get_block_id_for_node(node):
    block_id = build_buy.get_block_id(services.current_zone_id(), (sims4.math.Vector3)(*node.position), node.routing_surface_id.secondary_id)
    return block_id


def estimate_distance(obj_a, obj_b, options=routing.EstimatePathDistance_DefaultOptions):
    if obj_a is obj_b:
        return 0.0
    else:
        inv = obj_a.get_inventory()
        if inv is not None:
            if inv.owner.is_sim:
                obj_a = inv.owner
            else:
                obj_a_choices = inv.owning_objects_gen()
                obj_a = None
        inv = obj_b.get_inventory()
        if inv is not None:
            if inv.owner.is_sim:
                obj_b = inv.owner
            else:
                obj_b_choices = inv.owning_objects_gen()
                obj_b = None
        best_dist = MAX_FLOAT
        if obj_a is None:
            if obj_b is None:
                for a in obj_a_choices:
                    for b in obj_b_choices:
                        dist = estimate_distance_helper(a, b, options=options)
                        if dist < best_dist:
                            best_dist = dist

        else:
            for a in obj_a_choices:
                dist = estimate_distance_helper(a, obj_b, options=options)
                if dist < best_dist:
                    best_dist = dist

        return best_dist
    if obj_b is None:
        for b in obj_b_choices:
            dist = estimate_distance(obj_a, b, options=options)
            if dist < best_dist:
                best_dist = dist

        return best_dist
    return estimate_distance_helper(obj_a, obj_b, options=options)


def estimate_distance_helper(obj_a, obj_b, options=routing.EstimatePathDistance_DefaultOptions):
    floor_a = obj_a.intended_routing_surface.secondary_id
    floor_b = obj_b.intended_routing_surface.secondary_id
    floor_difference = abs(floor_a - floor_b)
    floor_cost = floor_difference * DistanceEstimationTuning.DISTANCE_PER_FLOOR
    distance = (obj_a.intended_position_with_forward_offset - obj_b.intended_position_with_forward_offset).magnitude_2d()
    return distance + floor_cost


def estimate_distance_between_multiple_points(sources, dests, routing_context=None, allow_permissive_connections=False):
    min_distance = routing.estimate_distance_between_multiple_points(sources, dests, routing_context, allow_permissive_connections)
    if min_distance is not None:
        return min_distance
    return DistanceEstimationTuning.UNREACHABLE_GOAL_COST


def sorted_estimated_distances_between_multiple_handles(source_handles, dest_handles, routing_context=None, allow_permissive_connections=False):
    if source_handles:
        if dest_handles:
            distances = routing.estimate_path_batch(source_handles, dest_handles, routing_context=routing_context, allow_permissive_connections=allow_permissive_connections,
              ignore_objects=True)
            if distances:
                distances.sort(key=(operator.itemgetter(2)))
                return distances
    return []


def estimate_distance_between_points(position_a, routing_surface_a, position_b, routing_surface_b, routing_context=None, allow_permissive_connections=False):
    return estimate_distance_between_multiple_points(((position_a, routing_surface_a),), (
     (
      position_b, routing_surface_b),), routing_context, allow_permissive_connections)