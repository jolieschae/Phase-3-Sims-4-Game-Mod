# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\routing_commands.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 13867 bytes
from _math import Vector3
from timeit import itertools
from elements import GeneratorElement
from interactions.constraints import Circle, Constraint, create_constraint_set
from interactions.utils.routing import PlanRoute, FollowPath
from objects.components.types import ROUTING_COMPONENT
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target, TunableInstanceParam, find_substring_in_repr, extract_floats
from server_commands.visualization_commands import POLYGON_STR, POLYGON_END_PARAM
from sims4.commands import CommandType
from sims4.geometry import RestrictedPolygon
import debugvis, element_utils, postures, routing, services, sims4.commands, placement
from placement import FGLSearchFlagsDefaultForSim

@sims4.commands.Command('routing.debug.fgl')
def routing_debug_fgl(x=None, y=None, z=None, m_steps=10, m_results=10, pos_increment=0.5, _connection=None):
    if x is None or y is None or z is None:
        return False
    start_pos = sims4.math.Vector3(x, y, z)
    starting_location = placement.create_starting_location(position=start_pos)
    pos_increment_info = placement.PositionIncrementInfo(position_increment=pos_increment, from_exception=False)
    s_flags = FGLSearchFlagsDefaultForSim
    fgl_context = placement.FindGoodLocationContext(starting_routing_location=starting_location, max_steps=m_steps,
      position_increment_info=pos_increment_info,
      search_flags=s_flags,
      max_results=m_results)
    translation, orientation, res_message = fgl_context.find_good_location()
    output = sims4.commands.Output(_connection)
    output(str(res_message))
    return True


@sims4.commands.Command('routing.debug.follow')
def routing_debug_follow(x=None, y=None, z=None, obj=None, _connection=None):
    if x is None or y is None or z is None:
        return False
    obj = get_optional_target(obj, _connection=_connection)
    if obj is None:
        return False
    routing_component = obj.get_component(ROUTING_COMPONENT)
    if routing_component is None:
        return False

    def _do_route_gen(timeline):
        location = routing.Location((Vector3(x, y, z)), routing_surface=(obj.routing_surface))
        goal = routing.Goal(location)
        routing_context = obj.get_routing_context()
        route = routing.Route((obj.routing_location), (goal,), routing_context=routing_context)
        plan_primitive = PlanRoute(route, obj)
        result = yield from element_utils.run_child(timeline, plan_primitive)
        if not result:
            return result
        else:
            nodes = plan_primitive.path.nodes
            return nodes and nodes.plan_success or False
            follow_path_element = FollowPath(obj, plan_primitive.path)
            result = yield from element_utils.run_child(timeline, follow_path_element)
            return result or result
        return True
        if False:
            yield None

    timeline = services.time_service().sim_timeline
    timeline.schedule(GeneratorElement(_do_route_gen))
    return True


@sims4.commands.Command('routing.debug.waypoints')
def routing_debug_waypoints(*waypoint_data, _connection=None):
    obj = get_optional_target(None, _connection=_connection)
    if obj is None:
        return False
    routing_component = obj.get_component(ROUTING_COMPONENT)
    if routing_component is None:
        return False
    object_manager = services.object_manager()
    waypoints = []
    for is_float, data_points in itertools.groupby(waypoint_data, lambda d: '.' in d):
        while True:
            try:
                if is_float:
                    position = Vector3(float(next(data_points)), float(next(data_points)), float(next(data_points)))
                    routing_surface = routing.SurfaceIdentifier(services.current_zone_id(), 0, routing.SurfaceType.SURFACETYPE_WORLD)
                    location = routing.Location(position, routing_surface=routing_surface)
                else:
                    o = object_manager.get(int(next(data_points)))
                    if o is None:
                        continue
                    routing_surface = o.provided_routing_surface
                    if routing_surface is None:
                        continue
                    location = routing.Location((o.position), routing_surface=routing_surface)
                waypoints.append((routing.Goal(location),))
            except StopIteration:
                break

    def _do_route_gen(timeline):
        routing_context = obj.get_routing_context()
        route = routing.Route((obj.routing_location), (waypoints[-1]), waypoints=(waypoints[:-1]), routing_context=routing_context)
        plan_primitive = PlanRoute(route, obj)
        result = yield from element_utils.run_child(timeline, plan_primitive)
        if not result:
            return result
        else:
            nodes = plan_primitive.path.nodes
            return nodes and nodes.plan_success or False
            follow_path_element = FollowPath(obj, plan_primitive.path)
            result = yield from element_utils.run_child(timeline, follow_path_element)
            return result or result
        return True
        if False:
            yield None

    timeline = services.time_service().sim_timeline
    timeline.schedule(GeneratorElement(_do_route_gen))
    return True


@sims4.commands.Command('routing.debug.generate_routing_goals_geometry', command_type=(CommandType.DebugOnly))
def routing_debug_generate_routing_goals_from_geometry(*args, obj: OptionalTargetParam=None, _connection=None):
    output = sims4.commands.Output(_connection)
    obj = get_optional_target(obj, _connection=_connection)
    if obj is None:
        return False
    routing_component = obj.get_component(ROUTING_COMPONENT)
    if routing_component is None:
        return False
    total_string = ''.join(args)
    polygon_strs = find_substring_in_repr(total_string, POLYGON_STR, POLYGON_END_PARAM)
    if not polygon_strs:
        output('No valid polygons. must start with {} and end with {}'.format(POLYGON_STR, POLYGON_END_PARAM))
        return
    constraints = []
    routing_surface = routing.SurfaceIdentifier(services.current_zone_id(), 0, routing.SurfaceType.SURFACETYPE_OBJECT)
    for poly_str in polygon_strs:
        point_list = extract_floats(poly_str)
        if not point_list or len(point_list) % 2 != 0:
            output('Point list is not valid length. Too few or one too many.')
            return
        vertices = []
        for index in range(0, len(point_list), 2):
            vertices.append(sims4.math.Vector3(point_list[index], 0.0, point_list[index + 1]))

        polygon = sims4.geometry.Polygon(vertices)
        geometry = RestrictedPolygon(polygon, [])
        constraints.append(Constraint(geometry=geometry, routing_surface=routing_surface))

    constraint_set = create_constraint_set(constraints)
    if not postures.posture_graph.enable_debug_goals_visualization:
        sims4.commands.execute('debugvis.goals.enable', _connection)
    handles = constraint_set.get_connectivity_handles(obj)
    handles_str = 'Handles: {}'.format(len(handles))
    sims4.commands.output(handles_str, _connection)
    all_goals = []
    for handle in handles:
        goal_list = handle.get_goals()
        goals_str = '\tGoals: {}'.format(len(goal_list))
        sims4.commands.output(goals_str, _connection)
        all_goals.extend(goal_list)

    if postures.posture_graph.enable_debug_goals_visualization:
        for constraint in constraints:
            with debugvis.Context('goal_scoring', routing_surface=(constraint.routing_surface)) as (layer):
                for polygon in constraint.geometry.polygon:
                    layer.add_polygon(polygon, routing_surface=(constraint.routing_surface))

                for goal in all_goals:
                    position = goal.location.transform.translation
                    layer.add_point(position, routing_surface=(constraint.routing_surface))


@sims4.commands.Command('routing.debug.generate_routing_goals_circle', command_type=(CommandType.DebugOnly))
def routing_debug_generate_routing_goals--- This code section failed: ---

 L. 236         0  LOAD_FAST                'x'
                2  LOAD_CONST               None
                4  COMPARE_OP               is
                6  POP_JUMP_IF_TRUE     32  'to 32'
                8  LOAD_FAST                'y'
               10  LOAD_CONST               None
               12  COMPARE_OP               is
               14  POP_JUMP_IF_TRUE     32  'to 32'
               16  LOAD_FAST                'z'
               18  LOAD_CONST               None
               20  COMPARE_OP               is
               22  POP_JUMP_IF_TRUE     32  'to 32'
               24  LOAD_FAST                'radius'
               26  LOAD_CONST               None
               28  COMPARE_OP               is
               30  POP_JUMP_IF_FALSE    50  'to 50'
             32_0  COME_FROM            22  '22'
             32_1  COME_FROM            14  '14'
             32_2  COME_FROM             6  '6'

 L. 237        32  LOAD_GLOBAL              sims4
               34  LOAD_ATTR                commands
               36  LOAD_METHOD              output
               38  LOAD_STR                 'Please enter 4 floats for x,y,z and radius'
               40  LOAD_FAST                '_connection'
               42  CALL_METHOD_2         2  '2 positional arguments'
               44  POP_TOP          

 L. 238        46  LOAD_CONST               False
               48  RETURN_VALUE     
             50_0  COME_FROM            30  '30'

 L. 240        50  LOAD_GLOBAL              get_optional_target
               52  LOAD_FAST                'obj'
               54  LOAD_FAST                '_connection'
               56  LOAD_CONST               ('_connection',)
               58  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
               60  STORE_FAST               'obj'

 L. 241        62  LOAD_FAST                'obj'
               64  LOAD_CONST               None
               66  COMPARE_OP               is
               68  POP_JUMP_IF_FALSE    74  'to 74'

 L. 242        70  LOAD_CONST               False
               72  RETURN_VALUE     
             74_0  COME_FROM            68  '68'

 L. 244        74  LOAD_FAST                'obj'
               76  LOAD_METHOD              get_component
               78  LOAD_GLOBAL              ROUTING_COMPONENT
               80  CALL_METHOD_1         1  '1 positional argument'
               82  STORE_FAST               'routing_component'

 L. 245        84  LOAD_FAST                'routing_component'
               86  LOAD_CONST               None
               88  COMPARE_OP               is
               90  POP_JUMP_IF_FALSE    96  'to 96'

 L. 246        92  LOAD_CONST               False
               94  RETURN_VALUE     
             96_0  COME_FROM            90  '90'

 L. 248        96  LOAD_GLOBAL              postures
               98  LOAD_ATTR                posture_graph
              100  LOAD_ATTR                enable_debug_goals_visualization
              102  POP_JUMP_IF_TRUE    118  'to 118'

 L. 249       104  LOAD_GLOBAL              sims4
              106  LOAD_ATTR                commands
              108  LOAD_METHOD              execute
              110  LOAD_STR                 'debugvis.goals.enable'
              112  LOAD_FAST                '_connection'
              114  CALL_METHOD_2         2  '2 positional arguments'
              116  POP_TOP          
            118_0  COME_FROM           102  '102'

 L. 251       118  LOAD_GLOBAL              Vector3
              120  LOAD_FAST                'x'
              122  LOAD_FAST                'y'
              124  LOAD_FAST                'z'
              126  CALL_FUNCTION_3       3  '3 positional arguments'
              128  STORE_FAST               'position'

 L. 252       130  LOAD_GLOBAL              routing
              132  LOAD_METHOD              SurfaceIdentifier
              134  LOAD_GLOBAL              services
              136  LOAD_METHOD              current_zone_id
              138  CALL_METHOD_0         0  '0 positional arguments'
              140  LOAD_CONST               0
              142  LOAD_GLOBAL              routing
              144  LOAD_ATTR                SurfaceType
              146  LOAD_ATTR                SURFACETYPE_WORLD
              148  CALL_METHOD_3         3  '3 positional arguments'
              150  STORE_FAST               'routing_surface'

 L. 253       152  LOAD_GLOBAL              Circle
              154  LOAD_FAST                'position'
              156  LOAD_FAST                'radius'
              158  LOAD_FAST                'routing_surface'
              160  CALL_FUNCTION_3       3  '3 positional arguments'
              162  STORE_FAST               'constraint'

 L. 255       164  LOAD_FAST                'constraint'
              166  LOAD_METHOD              get_connectivity_handles
              168  LOAD_FAST                'obj'
              170  CALL_METHOD_1         1  '1 positional argument'
              172  STORE_FAST               'handles'

 L. 256       174  LOAD_STR                 'Handles: {}'
              176  LOAD_METHOD              format
              178  LOAD_GLOBAL              len
              180  LOAD_FAST                'handles'
              182  CALL_FUNCTION_1       1  '1 positional argument'
              184  CALL_METHOD_1         1  '1 positional argument'
              186  STORE_FAST               'handles_str'

 L. 257       188  LOAD_GLOBAL              sims4
              190  LOAD_ATTR                commands
              192  LOAD_METHOD              output
              194  LOAD_FAST                'handles_str'
              196  LOAD_FAST                '_connection'
              198  CALL_METHOD_2         2  '2 positional arguments'
              200  POP_TOP          

 L. 258       202  BUILD_LIST_0          0 
              204  STORE_FAST               'all_goals'

 L. 259       206  SETUP_LOOP          266  'to 266'
              208  LOAD_FAST                'handles'
              210  GET_ITER         
              212  FOR_ITER            264  'to 264'
              214  STORE_FAST               'handle'

 L. 260       216  LOAD_FAST                'handle'
              218  LOAD_METHOD              get_goals
              220  CALL_METHOD_0         0  '0 positional arguments'
              222  STORE_FAST               'goal_list'

 L. 261       224  LOAD_STR                 '\tGoals: {}'
              226  LOAD_METHOD              format
              228  LOAD_GLOBAL              len
              230  LOAD_FAST                'goal_list'
              232  CALL_FUNCTION_1       1  '1 positional argument'
              234  CALL_METHOD_1         1  '1 positional argument'
              236  STORE_FAST               'goals_str'

 L. 262       238  LOAD_GLOBAL              sims4
              240  LOAD_ATTR                commands
              242  LOAD_METHOD              output
              244  LOAD_FAST                'goals_str'
              246  LOAD_FAST                '_connection'
              248  CALL_METHOD_2         2  '2 positional arguments'
              250  POP_TOP          

 L. 263       252  LOAD_FAST                'all_goals'
              254  LOAD_METHOD              extend
              256  LOAD_FAST                'goal_list'
              258  CALL_METHOD_1         1  '1 positional argument'
              260  POP_TOP          
              262  JUMP_BACK           212  'to 212'
              264  POP_BLOCK        
            266_0  COME_FROM_LOOP      206  '206'

 L. 265       266  LOAD_GLOBAL              postures
              268  LOAD_ATTR                posture_graph
              270  LOAD_ATTR                enable_debug_goals_visualization
          272_274  POP_JUMP_IF_FALSE   376  'to 376'

 L. 266       276  LOAD_GLOBAL              debugvis
              278  LOAD_ATTR                Context
              280  LOAD_STR                 'goal_scoring'
              282  LOAD_FAST                'routing_surface'
              284  LOAD_CONST               ('routing_surface',)
              286  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              288  SETUP_WITH          370  'to 370'
              290  STORE_FAST               'layer'

 L. 267       292  SETUP_LOOP          326  'to 326'
              294  LOAD_FAST                'constraint'
              296  LOAD_ATTR                geometry
              298  LOAD_ATTR                polygon
              300  GET_ITER         
              302  FOR_ITER            324  'to 324'
              304  STORE_FAST               'polygon'

 L. 268       306  LOAD_FAST                'layer'
              308  LOAD_ATTR                add_polygon
              310  LOAD_FAST                'polygon'
              312  LOAD_FAST                'routing_surface'
              314  LOAD_CONST               ('routing_surface',)
              316  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              318  POP_TOP          
          320_322  JUMP_BACK           302  'to 302'
              324  POP_BLOCK        
            326_0  COME_FROM_LOOP      292  '292'

 L. 270       326  SETUP_LOOP          366  'to 366'
              328  LOAD_FAST                'all_goals'
              330  GET_ITER         
              332  FOR_ITER            364  'to 364'
              334  STORE_FAST               'goal'

 L. 271       336  LOAD_FAST                'goal'
              338  LOAD_ATTR                location
              340  LOAD_ATTR                transform
              342  LOAD_ATTR                translation
              344  STORE_FAST               'position'

 L. 272       346  LOAD_FAST                'layer'
              348  LOAD_ATTR                add_point
              350  LOAD_FAST                'position'
              352  LOAD_FAST                'routing_surface'
              354  LOAD_CONST               ('routing_surface',)
              356  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              358  POP_TOP          
          360_362  JUMP_BACK           332  'to 332'
              364  POP_BLOCK        
            366_0  COME_FROM_LOOP      326  '326'
              366  POP_BLOCK        
              368  LOAD_CONST               None
            370_0  COME_FROM_WITH      288  '288'
              370  WITH_CLEANUP_START
              372  WITH_CLEANUP_FINISH
              374  END_FINALLY      
            376_0  COME_FROM           272  '272'

Parse error at or near `END_FINALLY' instruction at offset 374


@sims4.commands.Command('routing.debug.set_behavior')
def routing_debug_set_behavior(object_routing_behavior: TunableInstanceParam(sims4.resources.Types.SNIPPET), obj: OptionalTargetParam=None, _connection=None):
    if object_routing_behavior is None:
        return False
    obj = get_optional_target(obj)
    if obj is None:
        return False
    routing_component = obj.get_component(ROUTING_COMPONENT)
    if routing_component is None:
        return False
    timeline = services.time_service().sim_timeline
    timeline.schedule(object_routing_behavior(obj))
    return True


@sims4.commands.Command('routing.object_routing_soft_cap', command_type=(CommandType.Automation))
def routing_debug_set_object_routing_soft_cap(soft_cap: int=-1, _connection=None):
    object_routing_service = services.get_object_routing_service()
    if object_routing_service is None:
        return False
    override = None if soft_cap is -1 else soft_cap
    object_routing_service.set_object_routing_soft_cap_debug_override(override)
    return True


@sims4.commands.Command('routing.object_routing_hard_cap', command_type=(CommandType.Automation))
def routing_debug_set_object_routing_hard_cap(hard_cap: int=-1, _connection=None):
    object_routing_service = services.get_object_routing_service()
    if object_routing_service is None:
        return False
    override = None if hard_cap is -1 else hard_cap
    object_routing_service.set_object_routing_hard_cap_debug_override(override)
    return True


@sims4.commands.Command('routing.object_routing_soft_cap_threshold', command_type=(CommandType.Automation))
def routing_debug_set_object_routing_soft_cap_threshold(threshold: int=-1, _connection=None):
    object_routing_service = services.get_object_routing_service()
    if object_routing_service is None:
        return False
    override = None if threshold is -1 else threshold
    object_routing_service.set_object_routing_soft_cap_threshold_debug_override(override)
    return True