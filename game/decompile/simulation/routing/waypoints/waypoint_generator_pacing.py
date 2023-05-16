# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\waypoints\waypoint_generator_pacing.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 13248 bytes
import random
from build_buy import is_location_outside
from interactions.constraints import Circle, Nowhere, SmallAreaConstraint
from placement import FGLSearchFlagsDefaultForSim, FGLSearchFlag, WaterDepthInfo
from routing import Location
from routing.waypoints.waypoint_generator import _WaypointGeneratorBase
from sims4.color import Color
from sims4.tuning.geometric import TunableDistanceSquared
from sims4.tuning.tunable import TunableRange, Tunable, TunableTuple, OptionalTunable
import placement, routing, services, sims4.log, debugvis
logger = sims4.log.Logger('WaypointGeneratorPacing', default_owner='rmcord')

class _WaypointGeneratorPacing(_WaypointGeneratorBase):
    FACTORY_TUNABLES = {'constraint_parameters':TunableTuple(description='\n            Parameters used to generate the constraints that will be used\n            to generate waypoints.\n            ',
       object_constraint_radius=TunableRange(description='\n                The radius, in meters, of the generated constraint around the \n                target object where the waypoints will be generated.\n                ',
       tunable_type=float,
       default=2,
       minimum=0),
       waypoint_constraint_radius=TunableRange(description='\n                The radius, in meters, for each generated waypoint inside the \n                object constraint radius for the Sim to route to.\n                ',
       tunable_type=float,
       default=1,
       minimum=0.1),
       min_water_depth=OptionalTunable(description='\n                If enabled, generate waypoints at locations that are at least\n                this deep.\n                ',
       tunable=TunableRange(description='\n                    The minimum water depth allowed for each waypoint.\n                    ',
       tunable_type=float,
       default=0,
       minimum=0)),
       max_water_depth=OptionalTunable(description='\n                If enabled, generate waypoints at locations that are at most\n                this deep.\n                ',
       tunable=TunableRange(description='\n                    The maximum water depth allowed for each waypoint.\n                    ',
       tunable_type=float,
       default=1000.0,
       minimum=0,
       maximum=1000.0))), 
     'waypoint_min_distance':TunableDistanceSquared(description='\n            Minimum distance between the waypoints. We want to space them out\n            as much as possible. If after several tries we still cannot get\n            a waypoint that satisfies this min distance, we pick the furthest. \n            ',
       default=1), 
     'outside_only':Tunable(description='\n            If enabled, we will attempt to place a jig outside to find a\n            starting location, then validate all goals in the constraint radius\n            to ensure they are outside. Otherwise, we will route fail.\n            \n            Note: This will generate points on the world routing surface.\n            ',
       tunable_type=bool,
       default=False)}
    MAX_WAYPOINT_RANDOM_TRIES = 5

    @classmethod
    def _verify_tuning_callback(cls):
        if cls.constraint_parameters.object_constraint_radius <= cls.waypoint_min_distance:
            logger.error('Constraint radius is smaller than waypoint minimum. Waypoints will not obey minimum distance for: {}', cls)

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        if self._target is None:
            self._start_constraint = Nowhere('No target for _WaypointGeneratorPacing')
            self._los_reference_point = None
            return
        self._los_reference_point = self._target.position
        if self._target.is_terrain:
            self._los_reference_point = None
        else:
            water_constraint = self.get_water_constraint(self.constraint_parameters.min_water_depth, self.constraint_parameters.max_water_depth)
            water_depth_info = WaterDepthInfo(min_water_depth=(water_constraint.get_min_water_depth()), max_water_depth=(water_constraint.get_max_water_depth()))
            if self.outside_only:
                self._routing_surface = routing.SurfaceIdentifier(services.current_zone_id(), 0, routing.SurfaceType.SURFACETYPE_WORLD)
                starting_location = Location(position=(self._target.position), routing_surface=(self._routing_surface))
                search_flags = FGLSearchFlagsDefaultForSim | FGLSearchFlag.STAY_OUTSIDE
                fgl_context = placement.FindGoodLocationContext(starting_location, routing_context=(self._context.sim.routing_context),
                  additional_avoid_sim_radius=(routing.get_default_agent_radius()),
                  max_results=1,
                  max_steps=10,
                  search_flags=search_flags,
                  water_depth_info=water_depth_info)
                trans, _, _ = fgl_context.find_good_location()
                if trans is not None:
                    geometry = sims4.geometry.RestrictedPolygon(sims4.geometry.CompoundPolygon(sims4.geometry.Polygon((trans,))), ())
                    self._start_constraint = SmallAreaConstraint(geometry=geometry, debug_name='WaypointPacingStartingConstraint',
                      routing_surface=(self._routing_surface),
                      min_water_depth=(water_depth_info.min_water_depth),
                      max_water_depth=(water_depth_info.max_water_depth))
                else:
                    self._start_constraint = Nowhere('WaypointGeneratorPacing requires outside, but we failed to find a good location.')
            else:
                self._start_constraint = Circle((self._target.position), (self.constraint_parameters.object_constraint_radius), routing_surface=(self._routing_surface),
                  los_reference_point=(self._los_reference_point),
                  min_water_depth=(water_depth_info.min_water_depth),
                  max_water_depth=(water_depth_info.max_water_depth))

    def get_start_constraint(self):
        return self._start_constraint

    def get_waypoint_constraints_gen(self, routing_agent, waypoint_count):
        water_constraint = self.get_water_constraint(self.constraint_parameters.min_water_depth, self.constraint_parameters.max_water_depth)
        debugvis_constraints = []
        target_position = self._target.position
        object_radius_constraint = Circle(target_position, (self.constraint_parameters.object_constraint_radius), routing_surface=(self._start_constraint.routing_surface),
          los_reference_point=(self._los_reference_point),
          min_water_depth=(water_constraint.get_min_water_depth()),
          max_water_depth=(water_constraint.get_max_water_depth()))
        debugvis_constraints.append((target_position, self.constraint_parameters.object_constraint_radius))
        area_goals = []
        handles = object_radius_constraint.get_connectivity_handles(routing_agent)
        for handle in handles:
            area_goals.extend(handle.get_goals(relative_object=(self._target), always_reject_invalid_goals=True))

        if self.outside_only:
            area_goals = [goal for goal in area_goals if is_location_outside(goal.position, goal.location.routing_surface.secondary_id)]
        if not area_goals:
            yield Circle(target_position, (self.constraint_parameters.object_constraint_radius), routing_surface=(self._start_constraint.routing_surface),
              los_reference_point=(self._los_reference_point),
              min_water_depth=(water_constraint.get_min_water_depth()),
              max_water_depth=(water_constraint.get_max_water_depth()))
            return
        min_dist_sq = self.waypoint_min_distance
        current_point = None
        for _ in range(waypoint_count):
            if current_point is None:
                current_point = random.choice(area_goals)
                debugvis_constraints.append((current_point.position, self.constraint_parameters.waypoint_constraint_radius))
                yield Circle((current_point.position), (self.constraint_parameters.waypoint_constraint_radius), routing_surface=(self._start_constraint.routing_surface),
                  los_reference_point=(self._los_reference_point),
                  min_water_depth=(water_constraint.get_min_water_depth()),
                  max_water_depth=(water_constraint.get_max_water_depth()))
            farthest_point = None
            farthest_dist = 0
            for _ in range(self.MAX_WAYPOINT_RANDOM_TRIES):
                try_point = random.choice(area_goals)
                try_dist = (try_point.position - current_point.position).magnitude_squared()
                if try_dist > min_dist_sq:
                    farthest_point = try_point
                    break
                if not farthest_point is None:
                    if farthest_point is not None:
                        if try_dist > farthest_dist:
                            pass
                        farthest_point = try_point
                        farthest_dist = try_dist

            current_point = farthest_point
            debugvis_constraints.append((current_point.position, self.constraint_parameters.waypoint_constraint_radius))
            yield Circle((current_point.position), (self.constraint_parameters.waypoint_constraint_radius), routing_surface=(self._start_constraint.routing_surface),
              los_reference_point=(self._los_reference_point),
              min_water_depth=(water_constraint.get_min_water_depth()),
              max_water_depth=(water_constraint.get_max_water_depth()))