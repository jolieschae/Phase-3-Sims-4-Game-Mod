# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\pools\pond.py
# Compiled at: 2021-06-01 18:18:39
# Size of source mod 2**32: 40103 bytes
import build_buy, itertools, placement, routing, services, sims4, terrain
from collections import namedtuple
from interactions import ParticipantType
from interactions.base.super_interaction import SuperInteraction
from interactions.constraints import Nowhere, Constraint, Cone, Facing, create_constraint_set, CostFunctionBase
from objects.game_object import GameObject
from objects.pools.pond_utils import cached_pond_objects, PondUtils
from routing import SurfaceIdentifier, SurfaceType
from sims4.geometry import CompoundPolygon, build_rectangle_from_two_points_and_radius
from sims4.math import vector_normalize
from sims4.tuning.tunable import TunableVariant, TunableRange, TunableTuple
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
logger = sims4.log.Logger('Pond', default_owner='skorman')

class PondFishingConstraint(Constraint):

    def generate_forbid_small_intersections_constraint(self):
        return self


class PondFishingCostFunction(CostFunctionBase):

    def __init__(self, pond, distance_from_target, fishing_target_position):
        self.pond = pond
        self.distance_from_target = distance_from_target
        self.fishing_target_position = fishing_target_position

    def constraint_cost(self, position, orientation, routing_surface):
        target_positions_in_use = self.pond.in_use_fishing_target_positions
        if target_positions_in_use is None:
            return self.distance_from_target
        fishing_constraint_data = PondUtils.FISHING_CONSTRAINT_DATA
        for in_use_position in target_positions_in_use:
            distance_from_in_use_position_sq = (in_use_position - self.fishing_target_position).magnitude_squared()
            if distance_from_in_use_position_sq < fishing_constraint_data.near_in_use_target_max_distance:
                return self.distance_from_target + fishing_constraint_data.near_in_use_target_scoring_penalty

        return self.distance_from_target


class Pond(GameObject):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._cached_edges = None
        self._cached_outer_edges = None
        self._pond_id = None
        self._fish_provider_objects = None
        self._wading_contour_polygons = None
        self._target_positions_to_fishing_constraints = None
        self._fishing_target_positions_to_edges = {}
        self._fishing_target_positions_in_use = None

    @classmethod
    def _verify_tuning_callback(cls):
        fishing_location_component = cls._components.fishing_location
        if fishing_location_component is None:
            logger.error('Fishing location component is not tuned on Pond objects!')
            return
        if fishing_location_component.fishing_data.possible_fish:
            logger.error('Pond has fish tuned in its fishing data. This is not allowed. Pond fishing data must come from fishing sign objects because ponds may be recreated when modified, which could alter the list of possible fish set by players.')
        if not fishing_location_component.can_modify_fishing_data:
            logger.error("Pond object does not have 'can modify fishing data' checked in its fishing location component. This needs to be checked for the fish provider objects on the pond to stay in sync.")

    @property
    def pond_id(self):
        if self._pond_id is not None:
            return self._pond_id
        self._pond_id = build_buy.get_pond_id(self._location.transform.translation)
        return self._pond_id

    def on_add(self):
        super().on_add()
        cached_pond_objects.add(self)

    def on_remove(self):
        super().on_remove()
        cached_pond_objects.discard(self)

    def on_buildbuy_exit(self):
        self._cached_edges = None
        self._target_positions_to_fishing_constraints = None
        self._pond_id = None
        self._cached_outer_edges = None
        self._wading_contour_polygons = None

    def edges(self, outer_edges_only=False):
        if outer_edges_only:
            if self._cached_outer_edges is not None:
                return self._cached_outer_edges
        else:
            if not outer_edges_only:
                if self._cached_edges is not None:
                    return self._cached_edges
            edges = build_buy.get_pond_edges(self.pond_id)
            edges or logger.error('No edges for pond {} found.', self)
            return
        original_edges_dict = {edge[0]: edge for edge in edges}
        sorted_edges = [original_edges_dict.pop(edges[0][0])]
        potential_edge_loops = []
        while original_edges_dict:
            next_edge = sorted_edges[0][1]
            if next_edge in original_edges_dict:
                sorted_edges.insert(0, original_edges_dict.pop(next_edge))
                if not original_edges_dict:
                    potential_edge_loops.append(sorted_edges)
            else:
                add_onto_existing_loop = False
                for loop in potential_edge_loops:
                    if loop[-1][0] == sorted_edges[0][1]:
                        loop.extend(sorted_edges)
                        add_onto_existing_loop = True
                        break

                if not add_onto_existing_loop:
                    potential_edge_loops.append(sorted_edges)
                if original_edges_dict:
                    sorted_edges = [original_edges_dict.popitem()[1]]

        if outer_edges_only:
            LargestLoop = namedtuple('LargestLoop', ['area', 'edges'])
            largest_loop = None
            for edges in potential_edge_loops:
                polygon = sims4.geometry.Polygon([edge[0] for edge in edges])
                if not polygon.valid():
                    polygon = polygon.get_convex_hull()
                    if not polygon.valid():
                        continue
                    area = polygon.area()
                    if largest_loop is None:
                        largest_loop = LargestLoop(area, edges)
                    elif area > largest_loop.area:
                        largest_loop = LargestLoop(area, edges)

            self._cached_outer_edges = largest_loop.edges if largest_loop is not None else None
            return sorted_edges
        edges = list(itertools.chain.from_iterable(potential_edge_loops))
        self._cached_edges = edges
        return edges

    def get_wading_contour_cluster_polygons(self, min_depth, max_depth):
        cache_key = (
         min_depth, max_depth)
        if self._wading_contour_polygons is None:
            self._wading_contour_polygons = {}
        if cache_key in self._wading_contour_polygons:
            return self._wading_contour_polygons.get(cache_key)
        routing_surface = SurfaceIdentifier(services.current_zone_id(), 0, SurfaceType.SURFACETYPE_WORLD)
        contours = build_buy.get_pond_contours_for_wading_depth(self.pond_id, min_depth, max_depth, routing_surface)
        if not contours:
            self._wading_contour_polygons[cache_key] = None
            return
        constraint_constants = PondUtils.POND_CONSTRAINT_DATA
        polygons = [sims4.geometry.Polygon(contour) for contour in contours]
        contour_cluster_polygons = []
        while polygons:
            poly = polygons.pop()
            if not routing.test_point_placement_in_navmesh(routing_surface, poly.centroid()):
                continue
            polys_by_distance = sorted(polygons, key=(lambda p: (p.centroid() - poly.centroid()).magnitude_2d_squared()))
            grouped_verticies = list(poly)
            for p in polys_by_distance:
                if not routing.test_point_placement_in_navmesh(routing_surface, p.centroid()):
                    continue
                if (p.centroid() - poly.centroid()).magnitude_2d_squared() < constraint_constants.contour_grouping_max_distance ** 2:
                    grouped_verticies.extend(list(p))
                    polygons.remove(p)
                else:
                    break

            grouped_poly = sims4.geometry.Polygon(grouped_verticies)
            grouped_poly = grouped_poly.get_convex_hull()
            contour_cluster_polygons.append(grouped_poly)

        if not contour_cluster_polygons:
            self._wading_contour_polygons[cache_key] = None
            return
        self._wading_contour_polygons[cache_key] = contour_cluster_polygons
        return contour_cluster_polygons

    def _get_fish_provider_objs(self):
        if self._fish_provider_objects is not None:
            return self._fish_provider_objects
        self._fish_provider_objects = []
        obj_manager = services.object_manager()
        for obj in (obj_manager.get_objects_with_tags_gen)(*PondUtils.FISH_PROVIDER_TAGS):
            fishing_location_component = obj.fishing_location_component
            if fishing_location_component is None:
                logger.error('Object {} has one of the fish provider tags tuned in PondUtils ({}), but does not have a fishing location component.', obj, PondUtils.FISH_PROVIDER_TAGS)
                continue
            if not fishing_location_component.can_modify_fishing_data:
                continue
            if fishing_location_component.associated_pond_obj is self:
                self._fish_provider_objects.append(obj)

        return self._fish_provider_objects

    def on_fish_provider_obj_removed(self, obj):
        objs = self._get_fish_provider_objs()
        if obj in objs:
            objs.remove(obj)
        if not objs:
            if self.fishing_location_component is not None:
                self.fishing_location_component.fishing_data.possible_fish = []

    def on_fish_provider_obj_added(self, added_obj):
        fishing_location_component = added_obj.fishing_location_component
        if fishing_location_component is None:
            logger.error('Object {} has one of the fish provider tags tuned in PondUtils ({}), but does not have a fishing location component.', added_obj, PondUtils.FISH_PROVIDER_TAGS)
            return
        else:
            return fishing_location_component.can_modify_fishing_data or None
        objs = self._get_fish_provider_objs()
        if added_obj not in objs:
            objs.append(added_obj)
        fishing_data = fishing_location_component.fishing_data
        possible_fish_info = fishing_data.possible_fish
        fish_definitions = [info.fish for info in possible_fish_info]
        self.update_and_sync_fish_data(fish_definitions, added_obj)
        pond_possible_fish_info = self.fishing_location_component.fishing_data.possible_fish
        pond_fish = [info.fish for info in pond_possible_fish_info]
        fishing_data.add_possible_fish(pond_fish)

    def update_and_sync_fish_data(self, fish_definitions, source, is_add=True):
        objs = list(self._get_fish_provider_objs())
        objs.append(self)
        if source in objs:
            objs.remove(source)
        for obj in objs:
            if not obj.fishing_location_component:
                continue
            fishing_data = obj.fishing_location_component.fishing_data
            if is_add:
                fishing_data.add_possible_fish(fish_definitions, should_sync_pond=False)
            else:
                fishing_data.remove_possible_fish(fish_definitions, should_sync_pond=False)

    @property
    def in_use_fishing_target_positions(self):
        return self._fishing_target_positions_in_use

    @property
    def fishing_target_positions_to_edges(self):
        return self._fishing_target_positions_to_edges

    def claim_fishing_target_position(self, position):
        if self._fishing_target_positions_in_use is None:
            self._fishing_target_positions_in_use = []
        position = sims4.math.Vector3(position.x, position.y, position.z)
        self._fishing_target_positions_in_use.append(position)

    def unclaim_fishing_target_position(self, position):
        position = sims4.math.Vector3(position.x, position.y, position.z)
        if position in self._fishing_target_positions_in_use:
            self._fishing_target_positions_in_use.remove(position)
        if not self._fishing_target_positions_in_use:
            self._fishing_target_positions_in_use = None

    def validate_fishing_target_position(self, fishing_target_position, edge_midpoint):
        constraint_constants = PondUtils.FISHING_CONSTRAINT_DATA
        water_depth = terrain.get_water_depth(fishing_target_position.x, fishing_target_position.z, 0)
        if water_depth < constraint_constants.target_min_water_depth:
            return False
        if placement.ray_intersects_placement_3d(services.current_zone_id(), edge_midpoint, fishing_target_position):
            return False
        return True

    def _get_target_distance_from_sim(self, edge_start, edge_stop):
        constraint_constants = PondUtils.FISHING_CONSTRAINT_DATA
        edge_midpoint = (edge_start + edge_stop) / 2
        along = vector_normalize(edge_stop - edge_start)
        outward = sims4.math.vector_cross(along, sims4.math.Vector3.Y_AXIS())
        sim_distance_from_edge = 0
        routing_surface = SurfaceIdentifier(services.current_zone_id(), 0, SurfaceType.SURFACETYPE_WORLD)
        path_plan_context = routing.PathPlanContext()
        while sim_distance_from_edge < constraint_constants.max_distance_from_sim_to_edge:
            slope_eval_position = edge_midpoint + outward * sim_distance_from_edge
            stand_position = edge_midpoint + outward * (sim_distance_from_edge + constraint_constants.slope_eval_distance)
            height_difference = terrain.get_terrain_height(stand_position.x, stand_position.z, routing_surface) - terrain.get_terrain_height(slope_eval_position.x, slope_eval_position.z, routing_surface)
            sim_distance_from_edge = sim_distance_from_edge + constraint_constants.slope_eval_distance
            if abs(height_difference) >= constraint_constants.slope_tolerance:
                continue
            test_point = slope_eval_position + outward * (path_plan_context.agent_radius + 0.01)
            poly = build_rectangle_from_two_points_and_radius(stand_position, test_point, path_plan_context.agent_radius)
            if not routing.test_polygon_placement_in_navmesh(routing_surface, poly):
                return
            distance_from_sim_to_fishing_target = sim_distance_from_edge + constraint_constants.distance_from_edge_to_fishing_target
            return distance_from_sim_to_fishing_target

    def _get_fishing_target_location(self, edge_start, edge_stop):
        constraint_constants = PondUtils.FISHING_CONSTRAINT_DATA
        edge_midpoint = (edge_start + edge_stop) / 2
        along = vector_normalize(edge_stop - edge_start)
        inward = sims4.math.vector_cross(sims4.math.Vector3.Y_AXIS(), along)
        fishing_target_position = edge_midpoint + inward * constraint_constants.distance_from_edge_to_fishing_target
        return fishing_target_position is None or self.validate_fishing_target_position(fishing_target_position, edge_midpoint) or None
        fishing_target_position = sims4.math.Vector3(fishing_target_position.x, self.position.y, fishing_target_position.z)
        if self._fishing_target_positions_to_edges.get(fishing_target_position) is not None:
            return
        self._fishing_target_positions_to_edges[fishing_target_position] = (
         edge_start, edge_stop)
        angle = sims4.math.vector3_angle(edge_midpoint - fishing_target_position)
        routing_surface = SurfaceIdentifier(services.current_zone_id(), 0, SurfaceType.SURFACETYPE_POOL)
        fishing_loc = routing.Location(fishing_target_position, sims4.math.angle_to_yaw_quaternion(angle), routing_surface)
        return fishing_loc

    def _get_fishing_constraints_for_target_loc(self, fishing_target_loc, edge_start, edge_stop):
        constraint_constants = PondUtils.FISHING_CONSTRAINT_DATA
        fishing_target_position = fishing_target_loc.transform.translation
        routing_surface = SurfaceIdentifier(services.current_zone_id(), 0, SurfaceType.SURFACETYPE_WORLD)
        forward = fishing_target_loc.orientation.transform_vector(sims4.math.Vector3.Z_AXIS())
        sim_to_fishing_target_distance = self._get_target_distance_from_sim(edge_start, edge_stop)
        if sim_to_fishing_target_distance is None:
            return
        scoring_functions = (
         PondFishingCostFunction(self, sim_to_fishing_target_distance, fishing_target_position),)
        constraint = PondFishingConstraint()
        cone = Cone(fishing_target_position, forward,
          min_radius=sim_to_fishing_target_distance,
          max_radius=sim_to_fishing_target_distance,
          angle=(constraint_constants.constraint_angle),
          routing_surface=routing_surface,
          los_reference_point=fishing_target_position,
          max_water_depth=0,
          scoring_functions=scoring_functions)
        constraint = constraint.intersect(cone)
        constraint = constraint.intersect(Facing(target_position=fishing_target_position, facing_range=(constraint_constants.facing_range)))
        return constraint

    def get_target_positions_to_fishing_constraints(self):
        if self._target_positions_to_fishing_constraints is not None:
            return self._target_positions_to_fishing_constraints
        else:
            self._fishing_target_positions_to_edges = {}
            self._target_positions_to_fishing_constraints = {}
            constraint_constants = PondUtils.FISHING_CONSTRAINT_DATA
            edges = self.edges()
            return edges or self._target_positions_to_fishing_constraints
        sublist_size = int(max(1, min(constraint_constants.edges_per_constraint, len(edges) / constraint_constants.minimum_constraints_per_pond)))
        edge_sublists = [edges[sublist_size * i:sublist_size * (i + 1)] for i in range(len(edges) // sublist_size + 1)]
        constraints_per_sublists = []
        for edge_sublist in edge_sublists:
            sublist_constraints = []
            while len(edge_sublist) > 0:
                edge = edge_sublist.pop(len(edge_sublist) // 2)
                start, stop = edge
                fishing_target_loc = self._get_fishing_target_location(start, stop)
                if fishing_target_loc is None:
                    continue
                constraint = self._get_fishing_constraints_for_target_loc(fishing_target_loc, start, stop)
                if constraint is not None:
                    sublist_constraints.append((fishing_target_loc, constraint, edge))
                    if len(constraints_per_sublists) >= constraint_constants.minimum_constraints_per_pond:
                        break

            if sublist_constraints:
                constraints_per_sublists.append(sublist_constraints)

        has_iterated_once = False
        while len(self._target_positions_to_fishing_constraints) < constraint_constants.minimum_constraints_per_pond:
            for sublist in constraints_per_sublists:
                target_loc, constraint, edge = sublist.pop(0)
                fishing_target_position = target_loc.transform.translation
                fishing_target_position = sims4.math.Vector3(fishing_target_position.x, fishing_target_position.y, fishing_target_position.z)
                self._fishing_target_positions_to_edges[fishing_target_position] = edge
                self._target_positions_to_fishing_constraints[fishing_target_position] = constraint
                if has_iterated_once and len(self._target_positions_to_fishing_constraints) >= constraint_constants.minimum_constraints_per_pond:
                    break

            constraints_per_sublists = [constraint_list for constraint_list in constraints_per_sublists if constraint_list]
            if not constraints_per_sublists:
                break
            has_iterated_once = True

        return self._target_positions_to_fishing_constraints

    def get_fishing_constraint(self, check_in_use=True):
        available_constraints = []
        target_positions_to_fishing_constraints = self.get_target_positions_to_fishing_constraints()
        if not target_positions_to_fishing_constraints:
            return Nowhere('No pond edges')
            if check_in_use:
                for target_position, constraint in target_positions_to_fishing_constraints.items():
                    if self._fishing_target_positions_in_use is not None:
                        if target_position in self._fishing_target_positions_in_use:
                            continue
                    available_constraints.append(constraint)

        else:
            available_constraints = list(target_positions_to_fishing_constraints.values())
        return create_constraint_set(available_constraints)


class PondConstraintSuperInteraction(SuperInteraction):
    OUTER_EDGE_CONSTRAINT = 1
    INSTANCE_TUNABLES = {'constraint_type': TunableVariant(description='\n            The type of constraint to use.\n            ',
                          inside_pond_constraint=TunableTuple(min_water_depth=TunableRange(description='\n                    The minimum water depth required for the sim to stand when\n                    running this interaction.\n                    \n                    Please note that the pond edges are based on water tiles,\n                    which may be partially covered by terrain. Because of that,\n                    this must be at least 0.1 if you want the sim to stand \n                    inside the pond.\n                    ',
                          tunable_type=float,
                          default=0.1,
                          minimum=0.1),
                          max_water_depth=TunableRange(description='\n                    The maximum water depth required for the sim to stand when\n                    running this interaction.\n                    \n                    This is capped at the maximum possible wading depth since\n                    swimming in ponds is not currently supported, and having a \n                    large allowed water depth range will impact performance. \n                    ',
                          tunable_type=float,
                          default=0.7,
                          maximum=0.7)),
                          locked_args={'outer_edge_constraint': OUTER_EDGE_CONSTRAINT},
                          default='inside_pond_constraint',
                          tuning_group=(GroupNames.CONSTRAINTS))}

    @flexmethod
    def _get_constraint_geometry(cls, inst, pond, sim):
        inst_or_cls = inst if inst is not None else cls
        edges = pond.edges(outer_edges_only=True)
        if not edges:
            return Nowhere("PondConstraintSuperInteraction({}) target {} doesn't have any pond edges.", inst_or_cls, pond)
        edge_points = list((edge[0] for edge in edges))
        pond_polygon = sims4.geometry.Polygon(edge_points)
        if not pond_polygon.valid():
            pond_polygon = pond_polygon.get_convex_hull()
        constraint_type = inst_or_cls.constraint_type
        if constraint_type == inst_or_cls.OUTER_EDGE_CONSTRAINT:
            polygon = pond_polygon
        else:
            min_depth = constraint_type.min_water_depth
            max_depth = constraint_type.max_water_depth
            contour_cluster_polygons = pond.get_wading_contour_cluster_polygons(min_depth, max_depth)
            if contour_cluster_polygons is None:
                return Nowhere('Pond does not have any wading contours at thespecified depths.')
            constraint_constants = PondUtils.POND_CONSTRAINT_DATA
            contour_cluster_polygons.sort(key=(lambda p: (p.centroid() - sim.position).magnitude_2d_squared()))
            if pond_polygon.valid() and constraint_constants.max_geometry_area > pond_polygon.area():
                polygon = pond_polygon
            else:
                total_area = 0
                closest_cluster_polygons = []
                for cluster_polygon in contour_cluster_polygons:
                    if not total_area > constraint_constants.max_geometry_area:
                        if len(closest_cluster_polygons) > constraint_constants.max_contour_polygon_clusters:
                            break
                        closest_cluster_polygons.append(cluster_polygon)
                        total_area += cluster_polygon.area()

                polygon = CompoundPolygon(closest_cluster_polygons)
        return sims4.geometry.RestrictedPolygon(polygon, ())

    @flexmethod
    def _constraint_gen(cls, inst, sim, target, participant_type=ParticipantType.Actor, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        pond = target
        if target is None:
            pond_id = build_buy.get_pond_id(sim.location.transform.translation)
            if pond_id:
                pond = PondUtils.get_pond_obj_by_pond_id(pond_id)
        if not isinstance(pond, Pond):
            yield Nowhere('PondConstraintSuperInteraction({}) target {} is not a pond.', inst_or_cls, pond)
            return
        routing_surface = SurfaceIdentifier(services.current_zone_id(), 0, SurfaceType.SURFACETYPE_WORLD)
        constraint_type = inst_or_cls.constraint_type
        if constraint_type == inst_or_cls.OUTER_EDGE_CONSTRAINT:
            min_water_depth = 0
            max_water_depth = 0
        else:
            min_water_depth = constraint_type.min_water_depth
            max_water_depth = constraint_type.max_water_depth
        geometry = inst_or_cls._get_constraint_geometry(pond, sim)
        if isinstance(geometry, Nowhere):
            yield geometry
            return
        yield from (super(__class__, inst_or_cls)._constraint_gen)(sim, target, participant_type, **kwargs)
        yield Constraint(geometry=geometry, routing_surface=routing_surface,
          min_water_depth=min_water_depth,
          max_water_depth=max_water_depth)