# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\socials\jigs\jig_type_explicit.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 8750 bytes
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    from objects.script_object import ScriptObject
    from routing import Location, SurfaceIdentifier
from routing import FootprintType
from sims4.geometry import PolygonFootprint
from sims4.tuning.geometric import TunableVector2
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableTuple, TunableAngle, TunableList
from socials.jigs.jig_reserved_space import TunableReservedSpace
from socials.jigs.jig_utils import generate_jig_polygon, _generate_poly_points, generate_jig_polygon_solo
import sims4.math

class SocialJigExplicit(AutoFactoryInit, HasTunableSingletonFactory):

    class TunablePositionAndOrientation(TunableTuple):

        def __init__(self, **kwargs):
            (super().__init__)(position=TunableVector2(description='\n                    Position of this actor in the scene.\n                    ',
  default=(sims4.math.Vector2.ZERO())), 
             rotation=TunableAngle(description='\n                    Angle of this actor in the scene.\n                    ',
  default=0), **kwargs)

    FACTORY_TUNABLES = {'actor_a_reserved_space':TunableReservedSpace(description='\n            The clearance required for the actor Sim.\n            '), 
     'actor_b_reserved_space':TunableReservedSpace(description='\n            The clearance required for the target Sim.\n            '), 
     'actor_a':TunablePositionAndOrientation(), 
     'actor_b':TunableList(description='\n            A list of valid positions the target Sim may be in. Only one is\n            ultimately picked.\n            ',
       tunable=TunablePositionAndOrientation(),
       minlength=1)}

    def get_transforms_gen(self, actor, target, actor_loc=None, target_loc=None, fallback_routing_surface=None, fgl_kwargs=None, **kwargs):
        ignored_objects = set()
        if actor is not None:
            loc_a = actor.location
            ignored_objects.add(actor.id)
        if actor_loc is not None:
            loc_a = actor_loc
        if target is not None:
            loc_b = target.location
            ignored_objects.add(target.id)
        if target_loc is not None:
            loc_b = target_loc
        fgl_kwargs = fgl_kwargs if fgl_kwargs is not None else {}
        ignored_ids = fgl_kwargs.get('ignored_object_ids')
        if ignored_ids is not None:
            ignored_objects.update(ignored_ids)
        fgl_kwargs['ignored_object_ids'] = ignored_objects
        for actor_b in self.actor_b:
            translation_a, orientation_a, translation_b, orientation_b, routing_surface = generate_jig_polygon(loc_a, self.actor_a.position, self.actor_a.rotation, loc_b, actor_b.position, actor_b.rotation,
 self.actor_a_reserved_space.left, self.actor_a_reserved_space.right, self.actor_a_reserved_space.front, self.actor_a_reserved_space.back,
 self.actor_b_reserved_space.left, self.actor_b_reserved_space.right, self.actor_b_reserved_space.front, self.actor_b_reserved_space.back, fallback_routing_surface=fallback_routing_surface, **fgl_kwargs)
            if translation_a is None:
                continue
            yield (
             sims4.math.Transform(translation_a, orientation_a), sims4.math.Transform(translation_b, orientation_b), routing_surface, ())

    def get_footprint_polygon(self, sim_a, sim_b, sim_a_transform, sim_b_transform, routing_surface):
        polygon = _generate_poly_points(sim_a_transform.translation, sim_a_transform.orientation.transform_vector(sims4.math.Vector3.Z_AXIS()), sim_b_transform.translation, sim_b_transform.orientation.transform_vector(sims4.math.Vector3.Z_AXIS()), self.actor_a_reserved_space.left, self.actor_a_reserved_space.right, self.actor_a_reserved_space.front, self.actor_a_reserved_space.back, self.actor_b_reserved_space.left, self.actor_b_reserved_space.right, self.actor_b_reserved_space.front, self.actor_b_reserved_space.back)
        return PolygonFootprint(polygon, routing_surface=(sim_a.routing_surface), cost=25, footprint_type=(FootprintType.FOOTPRINT_TYPE_OBJECT), enabled=True)


class SoloJigExplicit(AutoFactoryInit, HasTunableSingletonFactory):
    FACTORY_TUNABLES = {'actor_reserved_space':TunableReservedSpace(description='\n            The clearance required for the actor.\n            '), 
     'actor_rotation':TunableAngle(description='\n            Angle of this actor relative to the starting location.\n            ',
       default=0)}

    def get_transform(self, actor, starting_location_override=None, fallback_routing_surface=None, fgl_kwargs=None, **kwargs):
        ignored_objects = set()
        starting_location = None
        if actor is not None:
            starting_location = actor.location
            ignored_objects.add(actor.id)
        if starting_location_override is not None:
            starting_location = starting_location_override
        if starting_location is None:
            return (None, None)
        fgl_kwargs = fgl_kwargs or {}
        ignored_ids = fgl_kwargs.get('ignored_object_ids')
        if ignored_ids is not None:
            ignored_objects.update(ignored_ids)
        fgl_kwargs['ignored_object_ids'] = ignored_objects
        translation, orientation, routing_surface = generate_jig_polygon_solo(starting_location, self.actor_rotation,
 self.actor_reserved_space.left, self.actor_reserved_space.right,
 self.actor_reserved_space.front, self.actor_reserved_space.back, fallback_routing_surface=fallback_routing_surface, **fgl_kwargs)
        if translation is None:
            return (None, None)
        return (
         sims4.math.Transform(translation, orientation), routing_surface)

    def get_polygon(self, transform: 'sims4.math.Transform') -> 'sims4.geometry.Polygon':
        return _generate_poly_points(transform.translation, transform.orientation.transform_vector(sims4.math.Vector3.Z_AXIS()), None, None, self.actor_reserved_space.left, self.actor_reserved_space.right, self.actor_reserved_space.front, self.actor_reserved_space.back, None, None, None, None)

    def get_footprint_polygon(self, actor, actor_transform, cost=0):
        polygon = self.get_polygon(actor_transform)
        return PolygonFootprint(polygon, routing_surface=(actor.routing_surface), cost=cost, footprint_type=(FootprintType.FOOTPRINT_TYPE_OBJECT),
          enabled=True)