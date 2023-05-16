# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\pools\pond_utils.py
# Compiled at: 2021-06-01 18:18:39
# Size of source mod 2**32: 9018 bytes
import enum, services, sims4
from _weakrefset import WeakSet
from animation.animation_utils import StubActor
from objects import ALL_HIDDEN_REASONS
from sims.sim_info_types import SpeciesExtended, Age
from sims4.tuning.geometric import TunableDistanceSquared
from sims4.tuning.tunable import Tunable, TunableTuple, TunableAngle, TunableReference, TunableMapping, TunableEnumEntry, TunableList, TunableEnumSet, TunedInterval, TunableVariant, HasTunableSingletonFactory
from tag import TunableTags
logger = sims4.log.Logger('Pond Utils', default_owner='skorman')
with sims4.reload.protected(globals()):
    cached_pond_objects = WeakSet()

class PondUtils:
    FIXED_DISTANCE_FROM_EDGE = 1
    FIXED_DISTANCE_FROM_SIM = 2
    FISHING_CONSTRAINT_DATA = TunableTuple(description='\n        Data used to create the constraint for fishing in ponds. Please ask a \n        GPE before changing these values.\n        ',
      target_min_water_depth=Tunable(description='\n            The minimum water depth allowed for a fishing target location.\n            ',
      tunable_type=float,
      default=1.0),
      slope_eval_distance=Tunable(description='\n            The distance in front of the sim to test slope tolerance relative\n            to the sim. \n            ',
      tunable_type=float,
      default=0.75),
      slope_tolerance=Tunable(description='\n            The allowed terrain height difference between the potential sim \n            location and the slope eval location.\n            ',
      tunable_type=float,
      default=0.08),
      distance_from_edge_to_fishing_target=Tunable(description='\n            The distance from the edge to the fishing target location.\n            ',
      tunable_type=float,
      default=3),
      max_distance_from_sim_to_edge=Tunable(description='\n            The maximum distance the sim can stand away from their\n            constrained pond edge when fishing.\n            ',
      tunable_type=float,
      default=5),
      facing_range=TunableAngle(description='\n            The max angle offset (in radians), the Sim can face away from the\n            target fishing location.\n            ',
      default=(sims4.math.PI / 8)),
      constraint_angle=TunableAngle(description='\n            The angle of the cone constraint generated to constrain the sim \n            relative to the fishing target location. This should be kept \n            relatively narrow or else the distance between the sim and the \n            target may appear to be smaller than tuned. \n            ',
      default=(sims4.math.PI / 12)),
      edges_per_constraint=Tunable(description='\n            The number of edges to skip between each constraint generated.\n            ',
      tunable_type=int,
      default=5),
      minimum_constraints_per_pond=Tunable(description="\n            Each pond will attempt to generate at least this minimum number\n            of constraints.\n            \n            Minimum Constraints Per Pond is prioritized over Edges Per Constraint.\n            \n            If a pond doesn't have enough edges to meet the Edges Per Constraint\n            requirement, that value will scale down automatically so that the\n            constraints will still try to be evenly spaced while meeting the\n            Minimum Constraints Per Pond requirement. \n            ",
      tunable_type=int,
      default=10),
      near_in_use_target_scoring_penalty=Tunable(description='\n            Scoring penalty for using a fishing target position that is near \n            an in-use fishing target position. This is used to prevent sims\n            from bunching up next to each other.\n            ',
      tunable_type=float,
      default=30.0),
      near_in_use_target_max_distance=TunableDistanceSquared(description='\n            The maximum distance a fishing target can be from an in use fishing\n            target to warrant the "near_in_use_target_scoring_penalty" scoring\n            penalty.\n            ',
      default=1.3))
    INVISIBLE_FISHING_TARGET = TunableReference(description='\n        The invisible fishing target object that will be created at the water\n        surface to play vfx. \n        ',
      manager=(services.definition_manager()))
    FISH_PROVIDER_TAGS = TunableTags(description='\n        Tags for fish provider objects. When these objects are placed in the\n        pond, they will share their fishing data (from the fishing location \n        component) with the pond and all other fish provider objects inside\n        the pond.\n        ',
      filter_prefixes=('func', ))
    WADING_WALKSTYLE_WATER_DEPTHS = TunableMapping(description="\n        The species-age mapping to wading depth minimum values. This will\n        be used to determine at what water depth to replace the sim's walkstyle\n        with the wading walkstyle.\n        ",
      key_name='species',
      key_type=TunableEnumEntry(description='\n            The extended species that this data is for.\n            ',
      tunable_type=SpeciesExtended,
      default=(SpeciesExtended.HUMAN)),
      value_name='age_data',
      value_type=TunableList(description='\n            The ages and their minimum wading depth.\n            ',
      tunable=TunableTuple(description='\n                The ages and their minimum wading depth.\n                ',
      ages=TunableEnumSet(description='\n                    The age of the actor.\n                    ',
      enum_type=Age),
      minimum_wading_depth=Tunable(description="\n                    The minimum water depth to replace the sim's walkstyle\n                    with the wading walkstyle.\n                    ",
      tunable_type=float,
      default=1.0))))
    POND_CONSTRAINT_DATA = TunableTuple(description='\n        Data used to make constraints for PondConstraintSuperInteractions. \n        Please ask a GPE before changing these values.\n        ',
      contour_grouping_max_distance=Tunable(description='\n            The max distance away that a contour polygon is allowed to be from \n            another contour polygon to group the two together. \n            ',
      tunable_type=float,
      default=5.0),
      max_contour_polygon_clusters=Tunable(description='\n            The max number of contour polygon clusters to use as the constraint.\n            ',
      tunable_type=int,
      default=5),
      max_geometry_area=Tunable(description='\n            The max area to use for the geometry of the constraint. Note that\n            this is a soft restriction, and the actual max geometry area may \n            be slightly larger than what is tuned. \n            ',
      tunable_type=int,
      default=100))

    @classmethod
    def get_main_pond_objects_gen(cls):
        yield from cached_pond_objects
        if False:
            yield None

    @classmethod
    def get_pond_obj_by_pond_id(cls, pond_id):
        for pond in PondUtils.get_main_pond_objects_gen():
            if pond.pond_id == pond_id:
                return pond

    @classmethod
    def get_actor_wading_interval(cls, actor):
        if not actor.is_sim:
            return
        sim_info = actor.sim_info
        actor = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if actor is None:
            return
        species_data = PondUtils.WADING_WALKSTYLE_WATER_DEPTHS.get(actor.extended_species, None)
        if species_data is None:
            return
        actor_age = actor.age
        for age_data in species_data:
            if actor_age in age_data.ages:
                return TunedInterval(age_data.minimum_wading_depth, actor.routing_component.routing_context.max_allowed_wading_depth)