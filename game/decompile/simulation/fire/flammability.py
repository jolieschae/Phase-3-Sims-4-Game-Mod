# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\fire\flammability.py
# Compiled at: 2019-11-25 21:07:12
# Size of source mod 2**32: 5066 bytes
from sims4.tuning.tunable import TunableVariant, HasTunableSingletonFactory, Tunable, AutoFactoryInit
import placement, sims4.math, sims4.log
logger = sims4.log.Logger('flammability', default_owner='nabaker')

class TunableFlammableAreaVariant(TunableVariant):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, circle_around_object=DefaultObjectRadialFlammability.TunableFactory(), 
         placement_footprint=ObjectFootprintFlammability.TunableFactory(), 
         default='circle_around_object', **kwargs)


class DefaultObjectRadialFlammability(HasTunableSingletonFactory):

    def get_bounds_for_flammable_object(self, obj, fire_retardant_bonus):
        location = sims4.math.Vector2(obj.position.x, obj.position.z)
        radius = obj.object_radius
        if obj.fire_retardant:
            radius += fire_retardant_bonus
        object_bounds = sims4.geometry.QtCircle(location, radius)
        return object_bounds


class ObjectFootprintFlammability(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'use_largest_polygon': Tunable(description="\n            When set, we use the largest polygon in the object's placement\n            footprint to generate the bounding box area.  Use this for complex\n            footprints with multiple placement polys like the large green screen;\n            if we can rely on the largest polygon as a good base.\n            ",
                              tunable_type=bool,
                              default=False)}

    def get_bounds_for_flammable_object(self, obj, fire_retardant_bonus):
        try:
            if self.use_largest_polygon:
                placement_footprint = placement.get_placement_footprint_polygon(obj.position, obj.orientation, obj.routing_surface, obj.get_footprint())
            else:
                placement_footprint = placement.get_accurate_placement_footprint_polygon(obj.position, obj.orientation, obj.scale, obj.get_footprint())
            lower_bound, upper_bound = placement_footprint.bounds()
            bounding_box = sims4.geometry.QtRect(sims4.math.Vector2(lower_bound.x, lower_bound.z), sims4.math.Vector2(upper_bound.x, upper_bound.z))
        except ValueError as e:
            try:
                logger.warn('{} in get_bounds_for_flammable_object.\nObject: {}\nOrientation: {}', e, obj, obj.orientation)
                location = sims4.math.Vector2(obj.position.x, obj.position.z)
                radius = obj.object_radius
                if obj.fire_retardant:
                    radius += fire_retardant_bonus
                bounding_box = sims4.geometry.QtCircle(location, radius)
            finally:
                e = None
                del e

        return bounding_box