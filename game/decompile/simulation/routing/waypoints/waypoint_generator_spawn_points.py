# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\waypoints\waypoint_generator_spawn_points.py
# Compiled at: 2019-11-22 20:19:59
# Size of source mod 2**32: 8721 bytes
from interactions.constraints import Circle, create_constraint_set
from routing.waypoints.waypoint_generator import _WaypointGeneratorBase
from sims.sim_info_types import SimInfoSpawnerTags
from sims4.random import pop_weighted
from sims4.tuning.tunable import OptionalTunable, TunableEnumWithFilter, TunableSet, TunableRange
from tag import Tag, SPAWN_PREFIX
from world.spawn_point import SpawnPoint
import routing, services, sims4.math

class _WaypointGeneratorSpawnPoints(_WaypointGeneratorBase):
    FACTORY_TUNABLES = {'constraint_radius':TunableRange(description='\n            The radius, in meters, for each of the generated waypoint\n            constraints.\n            ',
       tunable_type=float,
       default=6,
       minimum=0), 
     'spawn_point_tags':OptionalTunable(description='\n            Controls which spawn points can be used as waypoints.\n            ',
       tunable=TunableSet(tunable=TunableEnumWithFilter(tunable_type=Tag,
       default=(Tag.INVALID),
       filter_prefixes=SPAWN_PREFIX)))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._sim = self._context.sim
        if self._context.pick is not None:
            pick_position = self._context.pick.location
            self._pick_vector = pick_position - self._sim.position
            self._pick_vector /= self._pick_vector.magnitude()
        else:
            self._pick_vector = self._sim.forward
        if self._sim.is_on_active_lot():
            plex_service = services.get_plex_service()
            if plex_service.is_active_zone_a_plex():
                tags = (SpawnPoint.VISITOR_ARRIVAL_SPAWN_POINT_TAG,)
            else:
                tags = (
                 SpawnPoint.ARRIVAL_SPAWN_POINT_TAG,)
            spawn_point = services.current_zone().get_spawn_point(lot_id=(services.active_lot_id()), sim_spawner_tags=tags)
            self._origin_position = spawn_point.get_approximate_center()
            self._except_lot_id = services.active_lot_id()
        else:
            self._origin_position = self._sim.position
            self._except_lot_id = None
        self._routing_surface = routing.SurfaceIdentifier(services.current_zone_id(), 0, routing.SurfaceType.SURFACETYPE_WORLD)
        self._start_constraint = Circle((self._origin_position), (self.constraint_radius), routing_surface=(self._routing_surface), los_reference_point=None)
        self._start_constraint = self._start_constraint.intersect(self.get_water_constraint())

    def get_start_constraint(self):
        return self._start_constraint

    def get_waypoint_constraints_gen(self, routing_agent, waypoint_count):
        zone = services.current_zone()
        constraint_set = zone.get_spawn_points_constraint(except_lot_id=(self._except_lot_id), sim_spawner_tags=(self.spawn_point_tags),
          generalize=True)
        if routing_agent is not None:
            if routing_agent.vehicle_component is not None:
                routing_context = routing_agent.routing_component.pathplan_context
                source_handle = routing.connectivity.Handle(routing_agent.position, routing_agent.routing_surface)
                dest_handles = set()
                for constraint in constraint_set:
                    handles = constraint.get_connectivity_handles(routing_agent)
                    dest_handles.update(handles)

                if handles:
                    connectivity = routing.test_connectivity_batch((source_handle,), dest_handles, routing_context=routing_context,
                      compute_cost=True)
                    if connectivity is not None:
                        vehicle_dest_handles = {dest for _, dest, cost in connectivity if sims4.math.almost_equal(cost, 0.0)}
                        if vehicle_dest_handles:
                            constraint_set = create_constraint_set([handle.constraint for handle in vehicle_dest_handles])
        constraints_weighted = []
        min_score = sims4.math.MAX_FLOAT
        for constraint in constraint_set:
            spawn_point_vector = constraint.average_position - self._sim.position
            score = sims4.math.vector_dot_2d(self._pick_vector, spawn_point_vector)
            if score < min_score:
                min_score = score
            constraints_weighted.append((score, constraint))

        constraints_weighted = [(score - min_score, constraint) for score, constraint in constraints_weighted]
        constraints_weighted = sorted(constraints_weighted, key=(lambda i: i[0]))
        first_constraint = constraints_weighted[-1][1]
        del constraints_weighted[-1]
        first_constraint_circle = Circle((first_constraint.average_position), (self.constraint_radius), routing_surface=(first_constraint.routing_surface))
        jog_waypoint_constraints = []
        jog_waypoint_constraints.append(first_constraint_circle)
        last_waypoint_position = first_constraint.average_position
        for _ in range(waypoint_count - 1):
            constraints_weighted_next = []
            for _, constraint in constraints_weighted:
                average_position = constraint.average_position
                distance_last = (average_position - last_waypoint_position).magnitude_2d()
                distance_home = (average_position - self._origin_position).magnitude_2d()
                constraints_weighted_next.append((distance_last + distance_home, constraint))

            if not constraints_weighted_next:
                break
            next_constraint = pop_weighted(constraints_weighted_next)
            next_constraint_circle = Circle((next_constraint.average_position), (self.constraint_radius), routing_surface=(next_constraint.routing_surface))
            jog_waypoint_constraints.append(next_constraint_circle)
            constraints_weighted = constraints_weighted_next
            if not constraints_weighted:
                break
            last_waypoint_position = next_constraint.average_position

        jog_waypoint_constraints = self.apply_water_constraint(jog_waypoint_constraints)
        yield from jog_waypoint_constraints
        yield self._start_constraint