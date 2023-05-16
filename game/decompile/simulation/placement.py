# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\placement.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 69170 bytes
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    from routing import Location
    from sims.sim import Sim
    from sims.sim_info import SimInfo
import time
from collections import namedtuple
from sims4.sim_irq_service import yield_to_irq
from sims4.tuning.tunable import Tunable, TunableAngle, TunableRange
import enum, gsi_handlers.routing_handlers, routing, services, sims4.geometry, sims4.log, sims4.math
try:
    import _placement
    get_sim_quadtree_for_zone = _placement.get_sim_quadtree_for_zone
    get_placement_footprint_compound_polygon = _placement.get_placement_footprint_compound_polygon
    get_placement_footprint_polygon = _placement.get_placement_footprint_polygon
    get_accurate_placement_footprint_polygon = _placement.get_accurate_placement_footprint_polygon
    get_placement_footprint_bounds = _placement.get_placement_footprint_bounds
    get_routing_footprint_polygon = _placement.get_routing_footprint_polygon
    get_object_height = _placement.get_object_height
    get_object_surface_footprint_polygon = _placement.get_object_surface_footprint_polygon
    has_object_surface_footprint = _placement.has_object_surface_footprint
    validate_sim_location = _placement.validate_sim_location
    validate_los_source_location = _placement.validate_los_source_location
    surface_supports_object_placement = _placement.surface_supports_object_placement
    FGLSearch = _placement.FGLSearch
    FGLResult = _placement.FGLResult
    FGLResultStrategyDefault = _placement.FGLResultStrategyDefault
    FGLSearchStrategyRouting = _placement.FGLSearchStrategyRouting
    FGLSearchStrategyRoutingGoals = _placement.FGLSearchStrategyRoutingGoals
    ScoringFunctionLinear = _placement.ScoringFunctionLinear
    ScoringFunctionRadial = _placement.ScoringFunctionRadial
    ScoringFunctionAngular = _placement.ScoringFunctionAngular
    ScoringFunctionPolygon = _placement.ScoringFunctionPolygon
    ObjectQuadTree = _placement.ObjectQuadTree

    class ItemType(enum.Int, export=False):
        UNKNOWN = _placement.ITEMTYPE_UNKNOWN
        SIM_POSITION = _placement.ITEMTYPE_SIM_POSITION
        SIM_INTENDED_POSITION = _placement.ITEMTYPE_SIM_INTENDED_POSITION
        ROUTE_GOAL_SUPPRESSOR = _placement.ITEMTYPE_ROUTE_GOAL_SUPPRESSOR
        ROUTE_GOAL_PENALIZER = _placement.ITEMTYPE_ROUTE_GOAL_PENALIZER
        SIM_ROUTING_CONTEXT = _placement.ITEMTYPE_SIM_ROUTING_CONTEXT
        GOAL = _placement.ITEMTYPE_GOAL
        GOAL_SLOT = _placement.ITEMTYPE_GOAL_SLOT
        ROUTABLE_OBJECT_SURFACE = _placement.ITEMTYPE_ROUTABLE_OBJECT_SURFACE


    class FGLSearchType(enum.Int, export=False):
        NONE = _placement.FGL_SEARCH_TYPE_NONE
        ROUTING = _placement.FGL_SEARCH_TYPE_ROUTING
        ROUTING_GOALS = _placement.FGL_SEARCH_TYPE_ROUTING_GOALS


    class FGLSearchDataType(enum.Int, export=False):
        UNKNOWN = _placement.FGL_SEARCH_DATA_TYPE_UNKNOWN
        START_LOCATION = _placement.FGL_SEARCH_DATA_TYPE_START_LOCATION
        POLYGON = _placement.FGL_SEARCH_DATA_TYPE_POLYGON
        SCORING_FUNCTION = _placement.FGL_SEARCH_DATA_TYPE_SCORING_FUNCTION
        POLYGON_CONSTRAINT = _placement.FGL_SEARCH_DATA_TYPE_POLYGON_CONSTRAINT
        RESTRICTION = _placement.FGL_SEARCH_DATA_TYPE_RESTRICTION
        ROUTING_CONTEXT = _placement.FGL_SEARCH_DATA_TYPE_ROUTING_CONTEXT
        FLAG_CONTAINS_NOWHERE_CONSTRAINT = _placement.FGL_SEARCH_DATA_TYPE_FLAG_CONTAINS_NOWHERE_CONSTRAINT
        FLAG_CONTAINS_ANYWHERE_CONSTRAINT = _placement.FGL_SEARCH_DATA_TYPE_FLAG_CONTAINS_ANYWHERE_CONSTRAINT


    class FGLSearchResult(enum.Int, export=False):
        SUCCESS = _placement.FGL_SEARCH_RESULT_SUCCESS
        NOT_INITIALIZED = _placement.FGL_SEARCH_RESULT_NOT_INITIALIZED
        IN_PROGRESS = _placement.FGL_SEARCH_RESULT_IN_PROGRESS
        FAIL_PATHPLANNER_NOT_INITIALIZED = _placement.FGL_SEARCH_RESULT_FAIL_PATHPLANNER_NOT_INITIALIZED
        FAIL_CANNOT_LOCK_PATHPLANNER = _placement.FGL_SEARCH_RESULT_FAIL_CANNOT_LOCK_PATHPLANNER
        FAIL_BUILDBUY_SYSTEM_UNAVAILABLE = _placement.FGL_SEARCH_RESULT_FAIL_BUILDBUY_SYSTEM_UNAVAILABLE
        FAIL_LOT_UNAVAILABLE = _placement.FGL_SEARCH_RESULT_FAIL_LOT_UNAVAILABLE
        FAIL_INVALID_INPUT = _placement.FGL_SEARCH_RESULT_FAIL_INVALID_INPUT
        FAIL_INVALID_INPUT_START_LOCATION = _placement.FGL_SEARCH_RESULT_FAIL_INVALID_INPUT_START_LOCATION
        FAIL_INVALID_INPUT_POLYGON = _placement.FGL_SEARCH_RESULT_FAIL_INVALID_INPUT_POLYGON
        FAIL_INVALID_INPUT_OBJECT_ID = _placement.FGL_SEARCH_RESULT_FAIL_INVALID_INPUT_OBJECT_ID
        FAIL_INCOMPATIBLE_SEARCH_STRATEGY = _placement.FGL_SEARCH_RESULT_FAIL_INCOMPATIBLE_SEARCH_STRATEGY
        FAIL_INCOMPATIBLE_RESULT_STRATEGY = _placement.FGL_SEARCH_RESULT_FAIL_INCOMPATIBLE_RESULT_STRATEGY
        FAIL_NO_GOALS_FOUND = _placement.FGL_SEARCH_RESULT_FAIL_NO_GOALS_FOUND
        FAIL_CONTAINS_NOWHERE_CONSTRAINT = _placement.FGL_SEARCH_RESULT_FAIL_CONTAINS_NOWHERE_CONSTRAINT
        FAIL_FAILED_RAYTEST_INTERSECTION = _placement.FGL_SEARCH_RESULT_FAIL_FAILED_RAYTEST_INTERSECTION
        FAIL_UNKNOWN = _placement.FGL_SEARCH_RESULT_FAIL_UNKNOWN


except ImportError:

    class _placement:

        @staticmethod
        def test_object_placement(pos, ori, resource_key):
            return False


    class ScoringFunctionLinear:

        def __init__(self, *args, **kwargs):
            pass


    class ScoringFunctionRadial:

        def __init__(self, *args, **kwargs):
            pass


    class ScoringFunctionAngular:

        def __init__(self, *args, **kwargs):
            pass


    class ScoringFunctionPolygon:

        def __init__(self, *args, **kwargs):
            pass


    @staticmethod
    def get_sim_quadtree_for_zone(*_, **__):
        pass


    @staticmethod
    def get_placement_footprint_compound_polygon(*_, **__):
        pass


    @staticmethod
    def get_placement_footprint_polygon(*_, **__):
        pass


    @staticmethod
    def get_accurate_placement_footprint_polygon(*_, **__):
        pass


    @staticmethod
    def get_placement_footprint_bounds(*_, **__):
        pass


    @staticmethod
    def get_object_surface_footprint_polygon(*_, **__):
        pass


    @staticmethod
    def has_object_surface_footprint(*_, **__):
        pass


    @staticmethod
    def get_routing_footprint_polygon(*_, **__):
        pass


    @staticmethod
    def get_object_height(*_, **__):
        pass


    class ItemType(enum.Int, export=False):
        UNKNOWN = 0
        SIM_POSITION = 5
        SIM_INTENDED_POSITION = 6
        GOAL = 7
        GOAL_SLOT = 8
        ROUTE_GOAL_SUPPRESSOR = 30
        ROUTE_GOAL_PENALIZER = 31
        ROUTABLE_OBJECT_SURFACE = 32


    class FGLSearchType(enum.Int, export=False):
        UNKNOWN = 0


    class FGLSearchDataType(enum.Int, export=False):
        UNKNOWN = 0


    class FGLSearchResult(enum.Int, export=False):
        FAIL_UNKNOWN = 11


    class ObjectQuadTree:

        def __init__(self, *args, **kwargs):
            pass


    class FGLSearch:

        def __init__(self, *args, **kwargs):
            pass


    class FGLResultStrategyDefault:

        def __init__(self, *args, **kwargs):
            pass


    class FGLSearchStrategyRoutingGoals:

        def __init__(self, *args, **kwargs):
            pass


class FGLTuning:
    MAX_FGL_DISTANCE = Tunable(description='\n        The maximum distance searched by the Find Good Location code.\n        ',
      tunable_type=float,
      default=100.0)
    SOCIAL_FGL_HEIGHT_TOLERANCE = Tunable(description='\n        Maximum height tolerance on the terrain we will use for the placement \n        of social jigs.\n        If this value needs to be retuned a GPE, an Animator and Motech should\n        be involved.\n        ',
      tunable_type=float,
      default=0.1)
    MAX_PUTDOWN_STEPS = TunableRange(description='\n        The maximum steps the Find Good Location search will run when putting down a sim/object.\n        ',
      tunable_type=int,
      default=8,
      minimum=1)
    MAX_PUTDOWN_DISTANCE = Tunable(description='\n        The maximum distance searched by the Find Good Location code when putting down a sim/object\n        ',
      tunable_type=float,
      default=10.0)


logger = sims4.log.Logger('Placement')

def generate_routing_goals_for_polygon(sim, polygon, polygon_surface, orientation_restrictions=None, object_ids_to_ignore=None, flush_planner=False, sim_location_bonus=0.0, add_sim_location_as_goal=True, los_reference_pt=None, max_points=100, ignore_outer_penalty_amount=2, target_object=2, target_object_id=0, even_coverage_step=2, single_goal_only=False, los_routing_context=None, all_blocking_edges_block_los=False, provided_points=(), min_water_depth=None, max_water_depth=None, min_pond_water_depth=None, max_pond_water_depth=None, terrain_tags=None):
    yield_to_irq()
    routing_context = sim.get_routing_context()
    if los_routing_context is None:
        los_routing_context = routing_context
    return _placement.generate_routing_goals_for_polygon(sim.routing_location, polygon, polygon_surface, None, orientation_restrictions, object_ids_to_ignore, routing_context, flush_planner, -sim_location_bonus, add_sim_location_as_goal, los_reference_pt, 2.5, max_points, ignore_outer_penalty_amount, target_object_id, even_coverage_step, single_goal_only, los_routing_context, all_blocking_edges_block_los, provided_points, min_water_depth, max_water_depth, min_pond_water_depth, max_pond_water_depth, terrain_tags)


class FGLSearchFlag(enum.IntFlags):
    NONE = 0
    USE_RANDOM_WEIGHTING = 1
    USE_RANDOM_ORIENTATION = 2
    CONTAINS_NOWHERE_CONSTRAINT = 4
    CONTAINS_ANYWHERE_CONSTRAINT = 8
    ALLOW_TOO_CLOSE_TO_OBSTACLE = 16
    ALLOW_GOALS_IN_SIM_POSITIONS = 32
    ALLOW_GOALS_IN_SIM_INTENDED_POSITIONS = 64
    SHOULD_TEST_ROUTING = 128
    SHOULD_TEST_BUILDBUY = 256
    USE_SIM_FOOTPRINT = 512
    STAY_IN_SAME_CONNECTIVITY_GROUP = 1024
    STAY_IN_CONNECTED_CONNECTIVITY_GROUP = 2048
    STAY_IN_CURRENT_BLOCK = 4096
    STAY_OUTSIDE = 8192
    ALLOW_INACTIVE_PLEX = 16384
    SHOULD_RAYTEST = 32768
    SPIRAL_INWARDS = 65536
    STAY_IN_LOT = 131072
    ENCLOSED_ROOM_ONLY = 262144
    LOT_TERRAIN_ONLY = 524288
    CALCULATE_RESULT_TERRAIN_HEIGHTS = 1048576
    DONE_ON_MAX_RESULTS = 2097152


FGLSearchFlagsDefault = FGLSearchFlag.STAY_IN_CONNECTED_CONNECTIVITY_GROUP | FGLSearchFlag.SHOULD_TEST_ROUTING | FGLSearchFlag.CALCULATE_RESULT_TERRAIN_HEIGHTS | FGLSearchFlag.DONE_ON_MAX_RESULTS
FGLSearchFlagsDefaultForObject = FGLSearchFlagsDefault | FGLSearchFlag.SHOULD_TEST_BUILDBUY
FGLSearchFlagsDefaultForSim = FGLSearchFlagsDefault | FGLSearchFlag.USE_SIM_FOOTPRINT
FGLSearchFlagsDeprecated = FGLSearchFlag.USE_RANDOM_WEIGHTING | FGLSearchFlag.USE_RANDOM_ORIENTATION

class PlacementConstants:
    rotation_increment = TunableAngle((sims4.math.PI / 8), description='The size of the angle-range that sims should use when determining facing constraints.')


def _get_nearby_items_gen(position, surface_id, radius=None, exclude=None, flags=sims4.geometry.ObjectQuadTreeQueryFlag.NONE, *, query_filter):
    if radius is None:
        radius = routing.get_default_agent_radius()
    position_2d = sims4.math.Vector2(position.x, position.z) if isinstance(position, sims4.math.Vector3) else position
    bounds = sims4.geometry.QtCircle(position_2d, radius)
    exclude_ids = []
    if exclude:
        for routing_agent in exclude:
            exclude_ids.append(routing_agent.id)

    query = services.sim_quadtree().query(bounds, surface_id,
      filter=query_filter,
      flags=flags,
      exclude=exclude_ids)
    for q in query:
        obj = q[0]
        if exclude:
            if obj in exclude:
                continue
        yield q[0]


def get_nearby_sims_gen(position, surface_id, radius=None, exclude=None, flags=sims4.geometry.ObjectQuadTreeQueryFlag.NONE, only_sim_position=False, only_sim_intended_position=False, include_bassinets=False):
    query_filter = (
     ItemType.SIM_POSITION, ItemType.SIM_INTENDED_POSITION)
    if only_sim_position:
        query_filter = ItemType.SIM_POSITION
    else:
        if only_sim_intended_position:
            query_filter = ItemType.SIM_INTENDED_POSITION
    for obj in _get_nearby_items_gen(position=position, surface_id=surface_id, radius=radius, exclude=exclude, flags=flags, query_filter=query_filter):
        if not obj.is_sim:
            if not include_bassinets or obj.is_bassinet:
                yield obj


fgl_id = 0

def find_good_location(context):
    if context is None:
        return (None, None, 'FGL failed. No valid context found.')
    return context.find_good_location()


FGL_DEFAULT_POSITION_INCREMENT = 0.3
FGL_FOOTPRINT_POSITION_INCREMENT_MULTIPLIER = 0.5
PositionIncrementInfo = namedtuple('PositionIncrementInfo', ('position_increment',
                                                             'from_exception'))
RaytestInfo = namedtuple('RaytestInfo', ('raytest_start_offset', 'raytest_end_offset',
                                         'raytest_radius', 'raytest_ignore_flags',
                                         'raytest_start_point_override'), defaults=[
 0.0, 0.0, 0.0, 0, None])
WaterDepthInfo = namedtuple('WaterDepthInfo', ('max_water_depth', 'min_water_depth',
                                               'max_pond_water_depth', 'min_pond_water_depth'), defaults=[
 None, None, None, None])
OffsetInfo = namedtuple('OffsetInfo', ('offset_distance', 'offset_restrictions'), defaults=[0.0, None])

class FindGoodLocationContext:

    def __init__(self, starting_routing_location, object_id=None, object_def_id=None, object_def_state_index=None, object_footprints=None, object_polygons=None, routing_context=None, ignored_object_ids=None, min_distance=None, max_distance=None, position_increment_info=None, additional_avoid_sim_radius=0, restrictions=None, scoring_functions=None, offset_info=None, random_range_weighting=None, max_results=0, max_steps=1, height_tolerance=None, terrain_tags=None, raytest_info=None, search_flags=FGLSearchFlagsDefault, water_depth_info=None, connectivity_group_override_point=None, min_head_room=None, **kwargs):
        self.search_strategy = _placement.FGLSearchStrategyRouting(start_location=starting_routing_location)
        self.result_strategy = _placement.FGLResultStrategyDefault()
        self.search = _placement.FGLSearch(self.search_strategy, self.result_strategy)
        self.routing_context = routing_context
        if routing_context is not None:
            self.search_strategy.routing_context = routing_context
        self.set_object_id_info(object_id, object_def_id,
          object_def_state_index,
          should_test_buildbuy=(search_flags & FGLSearchFlag.SHOULD_TEST_BUILDBUY))
        self.add_object_polygons(object_polygons, object_footprints)
        self.ignored_object_ids = ignored_object_ids
        if ignored_object_ids is not None:
            for obj_id in ignored_object_ids:
                self.search_strategy.add_ignored_object_id(obj_id)

        self.set_raytest_info(raytest_info)
        if min_distance is not None:
            self.search_strategy.min_distance = min_distance
        self.search_strategy.max_distance = FGLTuning.MAX_FGL_DISTANCE if max_distance is None else max_distance
        self.search_strategy.rotation_increment = PlacementConstants.rotation_increment
        self.set_position_increment_info(position_increment_info)
        self.add_restrictions(restrictions)
        if scoring_functions is not None:
            for sf in scoring_functions:
                self.search_strategy.add_scoring_function(sf)

        self.set_offset_info(offset_info)
        if additional_avoid_sim_radius > 0:
            self.search_strategy.avoid_sim_radius = additional_avoid_sim_radius
        self.result_strategy.max_results = max_results
        self.search_strategy.max_steps = max_steps
        if height_tolerance is not None:
            self.search_strategy.height_tolerance = height_tolerance
        if terrain_tags is not None:
            self.search_strategy.terrain_tags = terrain_tags
        if random_range_weighting is not None:
            self.search_strategy.use_random_weighting = True
            self.search_strategy.random_range_weighting = random_range_weighting
        self.set_search_flags(search_flags)
        if connectivity_group_override_point is not None:
            self.search_strategy.connectivity_group_position = connectivity_group_override_point
        if min_head_room is not None:
            self.search_strategy.min_head_room = min_head_room
        else:
            if routing_context is not None:
                self.search_strategy.min_head_room = routing_context.get_required_height_clearance()
            self.set_water_depth_info(water_depth_info, routing_context)
            self.additional_gsi_values = None
            if gsi_handlers.routing_handlers.FGL_archiver.enabled:
                self.additional_gsi_values = {'starting_routing_location': 'starting_routing_location', 
                 'max_results': 'max_results', 
                 'max_steps': 'max_steps', 
                 'min_distance': 'min_distance', 
                 'max_distance': 'max_distance', 
                 'min_head_room': 'min_head_room', 
                 'additional_avoid_sim_radius': 'additional_avoid_sim_radius', 
                 'random_range_weighting': 'random_range_weighting', 
                 'height_tolerance': 'height_tolerance', 
                 'terrain_tags': 'terrain_tags', 
                 'connectivity_group_override_point': 'connectivity_group_override_point', 
                 'position_increment_info': 'position_increment_info'}

    def add_object_polygons(self, object_polygons=None, object_footprints=None):
        self.object_footprints = object_footprints
        self.object_polygons = object_polygons
        starting_routing_location = self.search_strategy.start_location
        if object_polygons is not None:
            for polygon_wrapper in object_polygons:
                if isinstance(polygon_wrapper, sims4.geometry.Polygon):
                    self.search_strategy.add_polygon(polygon_wrapper, starting_routing_location.routing_surface)
                else:
                    p = polygon_wrapper[0]
                    p_routing_surface = polygon_wrapper[1]
                    if p_routing_surface is None:
                        p_routing_surface = starting_routing_location.routing_surface
                    self.search_strategy.add_polygon(p, p_routing_surface)

        if object_footprints is not None:
            for footprint_wrapper in object_footprints:
                if footprint_wrapper is None:
                    logger.error('None footprint wrapper found during FGL: {}', self)
                    continue
                if isinstance(footprint_wrapper, sims4.resources.Key):
                    compound_polygon = _placement.get_placement_footprint_compound_polygon(starting_routing_location.position, starting_routing_location.orientation, starting_routing_location.routing_surface, footprint_wrapper)
                    for polygon in compound_polygon:
                        self.search_strategy.add_polygon(polygon, starting_routing_location.routing_surface)

                else:
                    fp_key = footprint_wrapper[0]
                    t = footprint_wrapper[1]
                    p_routing_surface = footprint_wrapper[2]
                    if p_routing_surface is None:
                        p_routing_surface = starting_routing_location.routing_surface
                    compound_polygon = _placement.get_placement_footprint_compound_polygon(t.translation, t.orientation, p_routing_surface, fp_key)
                    for polygon in compound_polygon:
                        self.search_strategy.add_polygon(polygon, p_routing_surface)

    def set_object_id_info(self, object_id=None, object_def_id=None, object_def_state_index=None, should_test_buildbuy=False):
        if not should_test_buildbuy:
            if object_id is not None or object_def_id is not None:
                logger.warn('Passing object_id: {}, object_def_id: {} to FGLContext without SHOULD_TEST_BUILDBUY flag. These fields will not be used.', object_id,
                  object_def_id,
                  owner='msundaram')
        if object_id is not None:
            self.search_strategy.object_id = object_id
        if object_def_id is not None:
            self.search_strategy.object_def_id = object_def_id
        if object_def_state_index is not None:
            self.search_strategy.object_def_state_index = object_def_state_index

    def set_position_increment_info(self, value):
        if value is None or value.position_increment is None:
            self.pos_increment = FGL_DEFAULT_POSITION_INCREMENT
            self.failed_to_find_objects_footprint = False
        else:
            self.pos_increment = value.position_increment
            self.failed_to_find_objects_footprint = value.from_exception
        self.search_strategy.position_increment = self.pos_increment

    def add_restrictions(self, restrictions):
        if restrictions is None:
            return
        for r in restrictions:
            self.search_strategy.add_restriction(r)

    def set_search_flags(self, value):
        if value is None:
            return
        self.search_strategy.set_search_flags(value)
        self.result_strategy.calculate_result_terrain_heights = value & FGLSearchFlag.CALCULATE_RESULT_TERRAIN_HEIGHTS
        self.result_strategy.done_on_max_results = value & FGLSearchFlag.DONE_ON_MAX_RESULTS

    def set_raytest_info(self, info):
        if info is None:
            self.search_strategy.should_raytest = False
            return
        self.search_strategy.should_raytest = True
        self.search_strategy.set_raytest_info(info)

    def set_water_depth_info(self, water_depth_info=None, routing_context=None):
        if water_depth_info is None:
            return
            max_water_depth = None if water_depth_info.max_water_depth is None else float(water_depth_info.max_water_depth)
            max_pond_water_depth = None if water_depth_info.max_pond_water_depth is None else float(water_depth_info.max_pond_water_depth)
            min_water_depth = None if water_depth_info.min_water_depth is None else float(water_depth_info.min_water_depth)
            min_pond_water_depth = None if water_depth_info.min_pond_water_depth is None else float(water_depth_info.min_pond_water_depth)
            if max_pond_water_depth is None:
                if routing_context is not None:
                    max_pond_water_depth = routing_context.max_allowed_wading_depth
        elif max_water_depth is not None:
            max_pond_water_depth = min(max_pond_water_depth, max_water_depth)
        water_depth_info = WaterDepthInfo(max_water_depth, min_water_depth, max_pond_water_depth, min_pond_water_depth)
        self.search_strategy.set_water_depth_info(water_depth_info)

    def set_offset_info(self, offset_info):
        if offset_info is None or offset_info.offset_distance <= 0:
            return
        self.search_strategy.set_offset_info(offset_info)

    def get_water_depth_info(self):
        return WaterDepthInfo._make(self.search_strategy.get_water_depth_info())

    def get_raytest_info(self):
        return RaytestInfo._make(self.search_strategy.get_raytest_info())

    def get_offset_info(self):
        return OffsetInfo._make(self.search_strategy.get_offset_info())

    def get_result_locations_for_gsi_gen(self):
        for result in self.search.get_results():
            yield (
             result.location, result.score, FGLSearchType(result.search_type))

    def get_bb_args_gsi_entry(self):
        values = [
         {'name':'Should Test Build/Buy', 
          'value':str(self.search_strategy.should_test_buildbuy)},
         {'name':'object_id', 
          'value':str(self.search_strategy.object_id)},
         {'name':'object_def_id', 
          'value':str(self.search_strategy.object_def_id)},
         {'name':'object_def_state_index', 
          'value':str(self.search_strategy.object_def_state_index)}]
        return values

    def get_search_flags_gsi_entry(self):
        search_flags_entry = []
        flags = self.search_strategy.get_search_flags()
        if flags is not None:
            flags = FGLSearchFlag(flags)
            for flag in flags:
                search_flags_entry.append({'flag': str(flag)})

        calculate_result_terrain_heights = self.result_strategy.calculate_result_terrain_heights & FGLSearchFlag.CALCULATE_RESULT_TERRAIN_HEIGHTS
        if calculate_result_terrain_heights:
            search_flags_entry.append({'flag': str(FGLSearchFlag.CALCULATE_RESULT_TERRAIN_HEIGHTS)})
        done_on_max_results = self.result_strategy.done_on_max_results & FGLSearchFlag.DONE_ON_MAX_RESULTS
        if done_on_max_results:
            search_flags_entry.append({'flag': str(FGLSearchFlag.DONE_ON_MAX_RESULTS)})
        return search_flags_entry

    def find_good_location(self):
        global fgl_id
        fgl_id = fgl_id + 1
        start_time = 0
        if gsi_handlers.routing_handlers.FGL_archiver.enabled:
            start_time = time.time()
        else:
            self.search.search()
            search_result = FGLSearchResult(self.search.search_result)
            if gsi_handlers.routing_handlers.FGL_archiver.enabled:
                gsi_handlers.routing_handlers.archive_FGL(fgl_id, self, search_result, time.time() - start_time)
            elif search_result == FGLSearchResult.SUCCESS:
                temp_list = self.search.get_results()
                if temp_list is not None:
                    if len(temp_list) > 0:
                        fgl_loc = temp_list[0]
                        fgl_pos = sims4.math.Vector3(fgl_loc.position.x, fgl_loc.position.y, fgl_loc.position.z)
                        if not self.result_strategy.calculate_result_terrain_heights:
                            terrain_instance = services.terrain_service.terrain_object()
                            fgl_pos.y = terrain_instance.get_routing_surface_height_at(fgl_loc.position.x, fgl_loc.position.z, fgl_loc.routing_surface_id)
                        result_message = 'FGL Successful'
                        return (fgl_pos, fgl_loc.orientation, result_message)
            else:
                if search_result == FGLSearchResult.FAIL_NO_GOALS_FOUND:
                    result_message = 'FGL Failed: search returned 0 results.'
                    logger.debug(result_message)
                else:
                    result_message = 'FGL Failed: ' + str(search_result)
                    logger.warn(result_message)
        return (
         None, None, result_message)


def create_fgl_context_for_object(starting_location, obj_to_place, search_flags=FGLSearchFlagsDefault, test_buildbuy_allowed=True, **kwargs):
    footprint = obj_to_place.get_footprint()
    should_test_buildbuy = test_buildbuy_allowed and obj_to_place.definition is not obj_to_place
    if should_test_buildbuy:
        search_flags |= FGLSearchFlag.SHOULD_TEST_BUILDBUY
    return FindGoodLocationContext(starting_location, object_id=obj_to_place.id if should_test_buildbuy else None, 
     object_footprints=(footprint,) if footprint is not None else None, 
     search_flags=search_flags, **kwargs)


def create_fgl_context_for_sim(starting_location, sim_to_place, search_flags=FGLSearchFlagsDefaultForSim, water_depth_info=None, **kwargs):
    object_id = None
    if search_flags & FGLSearchFlag.SHOULD_TEST_BUILDBUY:
        object_id = sim_to_place.id
    if water_depth_info is None:
        if not sim_to_place.can_swim():
            water_depth_info = WaterDepthInfo(max_water_depth=0.0)
    return FindGoodLocationContext(starting_location, object_id=object_id, 
     search_flags=search_flags, 
     water_depth_info=water_depth_info, **kwargs)


def create_fgl_context_for_object_off_lot(starting_location, obj_to_place, search_flags=FGLSearchFlagsDefault, location=None, footprint=None, **kwargs):
    try:
        if obj_to_place is None:
            position = location.transform.translation
            orientation = location.transform.orientation
            scale = 1.0
        else:
            position = obj_to_place.position
            orientation = obj_to_place.orientation
            scale = obj_to_place.scale
            footprint = obj_to_place.get_footprint()
        polygon = get_accurate_placement_footprint_polygon(position, orientation, scale, footprint)
    except AttributeError as exc:
        try:
            raise AttributeError('Getting footprint polygon for {} threw an error :{}'.format(obj_to_place if obj_to_place is not None else footprint, exc))
        finally:
            exc = None
            del exc

    except Exception as e:
        try:
            logger.error("Error getting polygon for {}'s footprint {}:{}".format(obj_to_place if obj_to_place is not None else footprint, footprint, e))
            raise e
        finally:
            e = None
            del e

    return FindGoodLocationContext(starting_location, object_polygons=(
 polygon,), 
     search_flags=search_flags, **kwargs)


def create_starting_location(position=None, orientation=None, transform=None, routing_surface=None, location=None):
    starting_routing_location = None
    if location is None:
        if routing_surface is None:
            zone_id = services.current_zone_id()
            routing_surface = routing.SurfaceIdentifier(zone_id, 0, routing.SurfaceType.SURFACETYPE_WORLD)
        if transform is None:
            if position is None:
                logger.error('Trying to create a starting location for a FindGoodLocationContext but position is None. If position is going to remain None then either location or transform need to be passed in instead. -trevor')
            if orientation is None:
                orientation = sims4.math.angle_to_yaw_quaternion(0.0)
            starting_routing_location = routing.Location(position, orientation, routing_surface)
        else:
            starting_routing_location = routing.Location(transform.translation, transform.orientation, routing_surface)
    else:
        starting_routing_location = routing.Location(location.transform.translation, location.transform.orientation, location.routing_surface or location.world_routing_surface)
    return starting_routing_location


def add_placement_footprint(owner):
    _placement.add_placement_footprint(owner.id, owner.zone_id, owner.footprint, owner.position, owner.orientation, owner.scale)
    owner.clear_raycast_context()


def remove_placement_footprint(owner):
    _placement.remove_placement_footprint(owner.id, owner.zone_id)


DEFAULT_RAY_RADIUS = 0.001

def ray_intersects_placement_3d(zone_id, ray_start, ray_end, objects_to_ignore=None, intersection_flags=0, radius=DEFAULT_RAY_RADIUS):
    return _placement.ray_intersects_placement_3d(zone_id, ray_start, ray_end, objects_to_ignore, intersection_flags, radius)