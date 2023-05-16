# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\socials\jigs\jig_type_definition.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 4579 bytes
from interactions.utils.routing import fgl_and_get_two_person_transforms_for_jig
from routing import FootprintType
from sims4.geometry import PolygonFootprint
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableReference, OptionalTunable, TunableRange, TunableTuple, Tunable, TunableEnumEntry
from socials.jigs.jig_utils import JigPositioning
import placement, services

class SocialJigFromDefinition(AutoFactoryInit, HasTunableSingletonFactory):
    FACTORY_TUNABLES = {'jig_definition':TunableReference(description='\n            The jig to use for finding a place to do the social.\n            ',
       manager=services.definition_manager()), 
     'override_polygon_and_cost':OptionalTunable(description='\n            If disabled, uses a CompoundPolygon of the object as footprint polygon. \n            If enabled, uses the largest placement polygon of the object as footprint\n            polygon. Then we will be able to add footprint cost to the polygon. This \n            can be used to discourage other sims from entering this area.\n            ',
       tunable=TunableTuple(footprint_cost=TunableRange(description='\n                    Footprint cost of the jig, this can be used to discourage/block other\n                    sims from entering this area.\n                    ',
       tunable_type=int,
       default=20,
       minimum=1))), 
     'jig_positioning_type':TunableEnumEntry(description='\n            Determines the type of positioning used for this Jig.\n            The other sim will come over to the relative sim.\n            ',
       tunable_type=JigPositioning,
       default=JigPositioning.RelativeToSimB)}

    def get_transforms_gen(self, actor, target, actor_slot_index=0, target_slot_index=1, fallback_routing_surface=None, fgl_kwargs=None, **kwargs):
        fgl_kwargs = fgl_kwargs if fgl_kwargs is not None else {}
        if self.jig_positioning_type == JigPositioning.RelativeToSimA:
            actor, target = target, actor
            actor_slot_index, target_slot_index = target_slot_index, actor_slot_index
        actor_transform, target_transform, routing_surface = fgl_and_get_two_person_transforms_for_jig(self.jig_definition, actor, actor_slot_index, target, target_slot_index, fallback_routing_surface=fallback_routing_surface, **fgl_kwargs)
        yield (actor_transform, target_transform, routing_surface, ())

    def get_footprint_polygon(self, sim_a, sim_b, sim_a_transform, sim_b_transform, routing_surface):
        if self.jig_positioning_type == JigPositioning.RelativeToSimA:
            footprint_translation = sim_a_transform.translation
            footprint_orientation = sim_a_transform.orientation
        else:
            footprint_translation = sim_b_transform.translation
            footprint_orientation = sim_b_transform.orientation
        if self.override_polygon_and_cost is not None:
            polygon = placement.get_placement_footprint_polygon(footprint_translation, footprint_orientation, routing_surface, self.jig_definition.get_footprint(0))
            return PolygonFootprint(polygon, routing_surface=routing_surface, cost=(self.override_polygon_and_cost.footprint_cost), footprint_type=(FootprintType.FOOTPRINT_TYPE_PATH),
              enabled=True)
        return placement.get_placement_footprint_compound_polygon(footprint_translation, footprint_orientation, routing_surface, self.jig_definition.get_footprint(0))