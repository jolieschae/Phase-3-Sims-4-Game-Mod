# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\waypoints\waypoint_generator_object_mixin.py
# Compiled at: 2021-04-26 18:29:47
# Size of source mod 2**32: 6083 bytes
import operator, random
from interactions.constraints import Circle
from routing.waypoints.waypoint_generator import _WaypointGeneratorBase
from sims4.tuning.geometric import TunableDistanceSquared
from sims4.tuning.tunable import TunableRange, TunableVariant, HasTunableSingletonFactory, AutoFactoryInit, OptionalTunable, Tunable
import services

class _WaypointObjectDefaultStrategy(HasTunableSingletonFactory, AutoFactoryInit):

    def get_waypoint_objects(self, obj_list):
        return obj_list


class _WaypointObjectSortedDistanceStrategy(HasTunableSingletonFactory, AutoFactoryInit):

    def get_waypoint_objects(self, obj_list):
        sorted_list = sorted(obj_list, key=(operator.attrgetter('position.x')))
        return sorted_list


class _WaypointGeneratorMultipleObjectMixin(_WaypointGeneratorBase):
    FACTORY_TUNABLES = {'object_max_distance':TunableDistanceSquared(description='\n            The maximum distance to check for an object as the next target\n            of our waypoint interaction.\n            ',
       default=5), 
     'constrain_radius':TunableRange(description='\n            The radius of the circle that will be generated around the objects\n            where the waypoints will be generated.\n            ',
       tunable_type=float,
       default=5,
       minimum=0), 
     'object_search_strategy':TunableVariant(description='\n            Search strategies to find and soft the possible objects where the\n            waypoints will be generated.\n            ',
       default_waypoints=_WaypointObjectDefaultStrategy.TunableFactory(),
       sorted_by_distance=_WaypointObjectSortedDistanceStrategy.TunableFactory(),
       default='default_waypoints'), 
     'placement_restriction':OptionalTunable(description='\n            If enabled the objects where the waypoints will be generated will\n            be restricted to either the inside of outside.\n            ',
       tunable=Tunable(description='\n                If checked objects will be restricted to the inside the \n                house, otherwise only objects outside will be considered.\n                ',
       tunable_type=bool,
       default=True),
       enabled_name='inside_only',
       disabled_name='no_restrictions'), 
     'randomize_order':Tunable(description='\n            If checked, the waypoints will be shuffled into a random order each\n            time the route is generated. If not they will be the same (but\n            still non-deterministic) order each time, for a given run.\n            ',
       tunable_type=bool,
       default=False)}

    def _get_objects(self):
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._sim = self._context.sim
        self._valid_objects = []
        for obj in self._get_objects():
            if self.placement_restriction is not None:
                if self.placement_restriction == obj.is_outside:
                    continue
            distance_from_sim = obj.position - self._sim.position
            if distance_from_sim.magnitude_squared() <= self.object_max_distance and obj.is_connected(self._sim):
                self._valid_objects.append(obj)

        self._valid_objects = self.object_search_strategy.get_waypoint_objects(self._valid_objects)
        if not self._valid_objects:
            self._start_constraint = Circle((self._sim.position), (self.constrain_radius), routing_surface=(self._sim.routing_surface),
              los_reference_point=None)
            return
        if self.randomize_order:
            random.shuffle(self._valid_objects)
        starting_object = self._valid_objects.pop(0)
        self._start_constraint = Circle((starting_object.position), (self.constrain_radius), routing_surface=(starting_object.routing_surface),
          los_reference_point=None)
        self._start_constraint = self._start_constraint.intersect(self.get_water_constraint())

    def get_start_constraint(self):
        return self._start_constraint

    def get_waypoint_constraints_gen(self, routing_agent, waypoint_count):
        water_constraint = self.get_water_constraint()
        for _ in range(waypoint_count - 1):
            if not self._valid_objects:
                return
                obj = self._valid_objects.pop(0)
                next_constraint_circle = Circle((obj.position), (self.constrain_radius), los_reference_point=None, routing_surface=(obj.routing_surface))
                next_constraint_circle = next_constraint_circle.intersect(water_constraint)
                yield next_constraint_circle