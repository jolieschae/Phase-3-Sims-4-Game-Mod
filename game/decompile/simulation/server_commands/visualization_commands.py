# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\visualization_commands.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 58158 bytes
import math
from debugvis import Context, KEEP_ALTITUDE
from interactions.constraints import Constraint, ANYWHERE
from objects.components import types
from objects.components.types import ROUTING_COMPONENT
from objects.pools.pond_utils import PondUtils
from objects.pools.pond_visualizer import PondVisualizer
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target, find_substring_in_repr, extract_floats, GeometryParam, PathParam, RequiredTargetParam
from services.fire_visualization import FireQuadTreeVisualizer
from sims4.color import Color, pseudo_random_color
from sims4.commands import CommandType
from visualization.autonomy_timer_visualizer import AutonomyTimerVisualizer
from visualization.broadcaster_visualizer import BroadcasterVisualizer
from visualization.carry_visualizer import PutDownVisualizer
from visualization.connectivity_handles_visualizer import ConnectivityHandlesVisualizer
from visualization.constraint_visualizer import SimConstraintVisualizer, SimLOSVisualizer, _draw_constraint
from visualization.ensemble_visualizer import EnsembleVisualizer
from visualization.formation_visualizer import RoutingFormationVisualizer
from visualization.jig_visualizer import JigVisualizer
from visualization.locator_visualizer import LocatorVisualizer
from visualization.mood_visualizer import MoodVisualizer
from visualization.path_goal_visualizer import PathGoalVisualizer
from visualization.portal_visualizer import PortalVisualizer
from visualization.quad_tree_visualizer import QuadTreeVisualizer
from visualization.sectional_sofa_visualizer import SectionalSofaVisualizer
from visualization.sim_position_visualizer import SimPositionVisualizer
from visualization.sim_route_visualizer import ObjectRouteVisualizer
from visualization.social_group_visualizer import SocialGroupVisualizer
from visualization.spawn_point_visualizer import SpawnPointVisualizer
from visualization.spawner_visualizer import SpawnerVisualizer
from visualization.transition_constraint_visualizer import TransitionConstraintVisualizer
from visualization.transition_path_visualizer import SimShortestTransitionPathVisualizer
import indexed_manager, objects.components, postures.posture, routing, routing.waypoints, services, sims.sim, sims4.color, sims4.commands, sims4.log, sims4.math, sims4.reload
logger = sims4.log.Logger('Debugvis')
with sims4.reload.protected(globals()):
    _social_layer_visualizers = {}
    _sim_layer_visualizers = {}
    _constraint_layer_visualizers = {}
    _quadtree_layer_visualizers = {}
    _broadcaster_visualizers = {}
    _routing_formation_visualizers = {}
    _path_goals_layer_visualizers = {}
    _connectivity_handles_layer_visualizers = {}
    _constraint_callbacks = {}
    _social_callbacks = {}
    _spawn_point_visualizers = {}
    _mood_visualizers = {}
    _autonomy_timer_visualizers = {}
    _draw_visualizers = {}
    _ensemble_visualizers = {}
    _locator_visualizers = {}
    _object_route_visualizers = {}
    _portal_visualizers = {}
    _sectional_sofa_visualizers = {}
    _waypoint_visualizers = {}
    _spawner_visualizers = {}
    _pond_visualizers = {}
    _putdown_visualizers = {}
    _all_mood_visualization_enabled = set()
    _all_autonomy_timer_visualization_enabled = set()

@sims4.commands.Command('debugvis.test')
def debugvis_test(name, _connection=None):
    client = services.client_manager().get(_connection)
    sim = client.active_sim
    time = services.time_service().sim_now
    hour = time.hour() % 12 * sims4.math.TWO_PI / 12
    minute = time.minute() * sims4.math.TWO_PI / 60
    a = sim.position + sims4.math.Vector3(0, 1, 0)
    b = a + sims4.math.Vector3(math.cos(hour), 0, math.sin(hour)) * 3
    c = a + sims4.math.Vector3(math.cos(minute), 0, math.sin(minute)) * 4
    with Context(name, routing_surface=(sim.routing_surface)) as (layer):
        layer.set_color(Color.YELLOW)
        layer.add_segment(a, b, color=(Color.CYAN))
        layer.add_segment(a, c, color=(Color.RED))
        layer.add_point(a, size=0.2)
        layer.add_point(b, size=0.1, color=(Color.BLUE))
        layer.add_point(c, size=0.1, color=(Color.MAGENTA))
        layer.add_circle(a, 5, color=(Color.GREEN))
        for i in range(12):
            theta = i * sims4.math.TWO_PI / 12
            x = sims4.math.Vector3(4.75 * math.cos(theta), 0, 4.75 * math.sin(theta))
            color = sims4.color.interpolate(Color.YELLOW, Color.BLUE, i / 11)
            layer.add_arrow((a + x), (0.5 * sims4.math.PI - theta), end_arrow=False, color=color)
            layer.add_text_world((a + x), (str(i)), color_foreground=(pseudo_random_color(i)))

        layer.add_text_screen(sims4.math.Vector2(4, 32), 'Displaying debug visualization tests.')
        for i in range(200):
            layer.add_text_object(sim, (sims4.math.Vector3.ZERO()), (str(i)), bone_index=i)

    return 1


@sims4.commands.Command('debugvis.stopall')
def stop_all_visualizers(_connection):
    _stop_all_sim_visualizer(_connection, _social_layer_visualizers)
    _stop_all_sim_visualizer(_connection, _sim_layer_visualizers)
    _stop_all_sim_visualizer(_connection, _constraint_layer_visualizers)
    debugvis_sim_quadtree_stop(_connection)
    debugvis_broadcasters_stop(_connection)
    _stop_all_sim_visualizer(_connection, _routing_formation_visualizers)
    _stop_all_sim_visualizer(_connection, _path_goals_layer_visualizers)
    _stop_all_sim_visualizer(_connection, _connectivity_handles_layer_visualizers)
    _debugvis_selected_toggle_helper(_connection, _constraint_callbacks, None, _debugvis_constraints_stop)
    _debugvis_selected_toggle_helper(_connection, _social_callbacks, None, _debugvis_socials_stop)
    debugvis_spawn_points_stop(_connection)
    _stop_all_sim_visualizer(_connection, _mood_visualizers)
    _stop_all_sim_visualizer(_connection, _autonomy_timer_visualizers)
    debugvis_draw_stop(_connection)
    debugvis_ensembles_stop(_connection)
    _stop_all_sim_visualizer(_connection, _putdown_visualizers)


def _create_layer(vis_name, handle):
    return '{0}_{1:08x}'.format(vis_name, handle)


def _start_visualizer(_connection, vis_name, container, handle, visualizer, layer=None):
    if handle in container:
        return False
    if layer is None:
        layer = _create_layer(vis_name, handle)
    sims4.commands.output('Added visualization: {0}'.format(layer), _connection)
    container[handle] = visualizer
    sims4.commands.client_cheat('debugvis.layer.enable {0}'.format(layer), _connection)
    return True


def _start_sim_visualizer(opt_sim, _connection, vis_name, container, visualizer_class):
    if isinstance(opt_sim, sims.sim.Sim):
        sim = opt_sim
    else:
        sim = get_optional_target(opt_sim, _connection)
    if not isinstance(sim, sims.sim.Sim):
        if not sim.has_component(ROUTING_COMPONENT):
            logger.error('Invalid Sim id specified in call to debugvis.{0}.start', vis_name)
            return False
    layer = _create_layer(vis_name, sim.id)
    visualizer = visualizer_class(sim, layer)
    return _start_visualizer(_connection, vis_name, container, (sim.id, vis_name), visualizer, layer=layer)


def _stop_visualizer(_connection, vis_name, container, handle):
    if handle in container:
        visualizer = container[handle]
        if visualizer is None:
            return False
        visualizer.stop()
        del container[handle]
        with Context(visualizer.layer):
            pass
        sims4.commands.output('Removed visualization: {0}'.format(visualizer.layer), _connection)
        sims4.commands.client_cheat('debugvis.layer.disable {0}'.format(visualizer.layer), _connection)
    return True


def _stop_sim_visualizer(opt_sim: OptionalTargetParam, _connection, vis_name, container):
    if isinstance(opt_sim, sims.sim.Sim):
        sim = opt_sim
    else:
        sim = get_optional_target(opt_sim, _connection)
    if not isinstance(sim, sims.sim.Sim):
        if not sim.has_component(ROUTING_COMPONENT):
            logger.error('Invalid Sim id specified in call to debugvis.{0}.stop', vis_name)
            return False
    handle = (
     sim.id, vis_name)
    if handle not in container:
        sims4.commands.output('No visualizer for Sim {0:08x}'.format(sim.id), _connection)
        return False
    return _stop_visualizer(_connection, vis_name, container, handle)


def _stop_all_sim_visualizer(_connection, container):
    for handle in tuple(container):
        vis_name = handle
        _stop_visualizer(_connection, vis_name, container, handle)


@sims4.commands.Command('debugvis.waypoints.start', command_type=(sims4.commands.CommandType.Automation))
def debugvis_waypoints_start(_connection=None):
    routing.waypoints.waypoint_generator.enable_waypoint_visualization = True
    sims4.commands.client_cheat('debugvis.layer.enable {}'.format(routing.waypoints.waypoint_generator.DEBUGVIS_WAYPOINT_LAYER_NAME), _connection)
    sims4.commands.output('Waypoint Visualization Enabled', _connection)


@sims4.commands.Command('debugvis.waypoints.stop', command_type=(sims4.commands.CommandType.Automation))
def debugvis_waypoints_stop(_connection=None):
    routing.waypoints.waypoint_generator.enable_waypoint_visualization = False
    sims4.commands.client_cheat('debugvis.layer.disable {}'.format(routing.waypoints.waypoint_generator.DEBUGVIS_WAYPOINT_LAYER_NAME), _connection)
    sims4.commands.output('Waypoint Visualization Disabled', _connection)


@sims4.commands.Command('debugvis.socials.start')
def debugvis_socials_start(opt_sim: OptionalTargetParam=None, _connection=None):
    return _debugvis_socials_start(opt_sim=opt_sim, _connection=_connection)


def _debugvis_socials_start(opt_sim: OptionalTargetParam=None, _connection=None):
    return _start_sim_visualizer(opt_sim, _connection, 'socials', _social_layer_visualizers, SocialGroupVisualizer)


@sims4.commands.Command('debugvis.socials.stop')
def debugvis_socials_stop(opt_sim: OptionalTargetParam=None, _connection=None):
    return _debugvis_socials_stop(opt_sim=opt_sim, _connection=_connection)


def _debugvis_socials_stop(opt_sim: OptionalTargetParam=None, _connection=None):
    return _stop_sim_visualizer(opt_sim, _connection, 'socials', _social_layer_visualizers)


@sims4.commands.Command('debugvis.putdown.start')
def debugvis_putdown_start(opt_sim: OptionalTargetParam=None, _connection=None):
    return _debugvis_putdown_start(opt_sim=opt_sim, _connection=_connection)


def _debugvis_putdown_start(opt_sim: OptionalTargetParam=None, _connection=None):
    return _start_sim_visualizer(opt_sim, _connection, 'putdown', _putdown_visualizers, PutDownVisualizer)


@sims4.commands.Command('debugvis.putdown.stop')
def debugvis_putdown_stop(opt_sim: OptionalTargetParam=None, _connection=None):
    return _debugvis_putdown_stop(opt_sim=opt_sim, _connection=_connection)


def _debugvis_putdown_stop(opt_sim: OptionalTargetParam=None, _connection=None):
    return _stop_sim_visualizer(opt_sim, _connection, 'putdown', _putdown_visualizers)


@sims4.commands.Command('debugvis.sim_position.start')
def debugvis_simposition_start(opt_sim: OptionalTargetParam=None, _connection=None):
    if opt_sim is None:
        object_manager = services.object_manager()
        if object_manager is None:
            return False
        for obj in object_manager.get_all_objects_with_component_gen(types.ROUTING_COMPONENT):
            routing_component = obj.routing_component
            if routing_component is None:
                continue
            if obj.id in _sim_layer_visualizers:
                continue
            layer = '{0}_{1:08x}'.format('sim_pos', obj.id)
            visualizer = SimPositionVisualizer(obj, layer)
            _sim_layer_visualizers[obj.id] = visualizer
            sims4.commands.output('Added visualization: {0}'.format(layer), _connection)
            sims4.commands.client_cheat('debugvis.layer.enable {0}'.format(layer), _connection)

    else:
        return _start_sim_visualizer(opt_sim, _connection, 'sim_pos', _sim_layer_visualizers, SimPositionVisualizer) or 0
    return 1


@sims4.commands.Command('debugvis.sim_position.stop')
def debugvis_simposition_stop(opt_sim: OptionalTargetParam=None, _connection=None):
    if opt_sim is None:
        while _sim_layer_visualizers:
            _, visualizer = _sim_layer_visualizers.popitem()
            visualizer.stop()
            sims4.commands.output('Removed visualization: {0}'.format(visualizer.layer), _connection)
            sims4.commands.client_cheat('debugvis.layer.disable {0}'.format(visualizer.layer), _connection)

    else:
        return _stop_sim_visualizer(opt_sim, _connection, 'sim_pos', _sim_layer_visualizers) or 0
    return 1


@sims4.commands.Command('debugvis.constraints.start')
def debugvis_constraints_start(opt_sim: OptionalTargetParam=None, _connection=None):
    return _debugvis_constraints_start(opt_sim=opt_sim, _connection=_connection)


def _debugvis_constraints_start(opt_sim: OptionalTargetParam=None, _connection=None):
    return _start_sim_visualizer(opt_sim, _connection, 'constraints', _constraint_layer_visualizers, SimConstraintVisualizer)


@sims4.commands.Command('debugvis.constraints.stop')
def debugvis_constraints_stop(opt_sim: OptionalTargetParam=None, _connection=None):
    return _debugvis_constraints_stop(opt_sim=opt_sim, _connection=_connection)


def _debugvis_constraints_stop(opt_sim: OptionalTargetParam=None, _connection=None):
    return _stop_sim_visualizer(opt_sim, _connection, 'constraints', _constraint_layer_visualizers)


@sims4.commands.Command('debugvis.constraints.selected.toggle', command_type=(CommandType.Automation))
def debugvis_constraints_selected_toggle(_connection=None):
    _debugvis_selected_toggle_helper(_connection, _constraint_callbacks, _debugvis_constraints_start, _debugvis_constraints_stop)
    return True


@sims4.commands.Command('debugvis.socials.selected.toggle', command_type=(CommandType.Automation))
def debugvis_socials_selected_toggle(_connection=None):
    _debugvis_selected_toggle_helper(_connection, _social_callbacks, _debugvis_socials_start, _debugvis_socials_stop)
    return True


def _debugvis_selected_toggle_helper(_connection, callback_dictionary, start_function, stop_function):
    client = services.client_manager().get(_connection)
    if client is not None:
        callback = callback_dictionary.get(client)
        if callback is not None:
            client.unregister_active_sim_changed(callback)
            stop_function(_connection=_connection)
            del callback_dictionary[client]
        else:
            if start_function is not None:
                callback = get_on_selected_sim_changed(_connection, start_function, stop_function)
                callback_dictionary[client] = callback
                client.register_active_sim_changed(callback)
                start_function(_connection=_connection)


def get_on_selected_sim_changed(_connection, start_function, stop_function):

    def on_selected_sim_changed(old_sim, new_sim):
        if old_sim is not None:
            stop_function(opt_sim=old_sim, _connection=_connection)
        if new_sim is not None:
            start_function(opt_sim=new_sim, _connection=_connection)

    return on_selected_sim_changed


@sims4.commands.Command('debugvis.sim_los.start')
def debugvis_sim_los_start(opt_sim: OptionalTargetParam=None, _connection=None):
    return _start_sim_visualizer(opt_sim, _connection, 'sim_los', _constraint_layer_visualizers, SimLOSVisualizer)


@sims4.commands.Command('debugvis.sim_los.stop')
def debugvis_sim_los_stop(opt_sim: OptionalTargetParam=None, _connection=None):
    return _stop_sim_visualizer(opt_sim, _connection, 'sim_los', _constraint_layer_visualizers)


@sims4.commands.Command('debugvis.spawn_points.start', command_type=(sims4.commands.CommandType.Automation))
def debugvis_spawn_points_start(_connection=None):
    commands = [
     'debug.validate_spawn_points']
    for command in commands:
        sims4.commands.output('>|' + command, _connection)
        sims4.commands.execute(command, _connection)

    vis_name = 'spawn_points'
    handle = 0
    layer = _create_layer(vis_name, handle)
    visualizer = SpawnPointVisualizer(layer)
    for spawn_point_str in visualizer.get_spawn_point_string_gen():
        sims4.commands.output(spawn_point_str, _connection)

    if not _start_visualizer(_connection, vis_name, _spawn_point_visualizers, handle, visualizer, layer=layer):
        return 0
    return 1


@sims4.commands.Command('debugvis.spawn_points.stop', command_type=(sims4.commands.CommandType.Automation))
def debugvis_spawn_points_stop(_connection=None):
    if not _stop_visualizer(_connection, 'spawn_points', _spawn_point_visualizers, 0):
        return 0
    return 1


@sims4.commands.Command('debugvis.spawner_component.start', command_type=(sims4.commands.CommandType.Automation))
def debugvis_spawner_component_start(_connection=None):
    vis_name = 'spawner_components'
    handle = 0
    layer = _create_layer(vis_name, handle)
    visualizer = SpawnerVisualizer(layer)
    if not _start_visualizer(_connection, vis_name, _spawner_visualizers, handle, visualizer, layer=layer):
        return 0
    return 1


@sims4.commands.Command('debugvis.spawner_component.stop', command_type=(sims4.commands.CommandType.Automation))
def debugvis_spawner_component_stop(_connection=None):
    if not _stop_visualizer(_connection, 'spawner_components', _spawner_visualizers, 0):
        return 0
    return 1


LOCATOR_VIS_NAME = 'locators'

@sims4.commands.Command('debugvis.locators.start', command_type=(sims4.commands.CommandType.Automation))
def debugvis_locators_start(_connection=None):
    handle = 0
    layer = _create_layer(LOCATOR_VIS_NAME, handle)
    visualizer = LocatorVisualizer(layer)
    sims4.commands.output('Locator Visualization Enabled', _connection)
    if not _start_visualizer(_connection, LOCATOR_VIS_NAME, _locator_visualizers, handle, visualizer, layer=layer):
        return 0
    return 1


@sims4.commands.Command('debugvis.locators.stop', command_type=(sims4.commands.CommandType.Automation))
def debugvis_locators_stop(_connection=None):
    sims4.commands.output('Locator Visualization Disabled', _connection)
    if not _stop_visualizer(_connection, LOCATOR_VIS_NAME, _locator_visualizers, 0):
        return 0
    return 1


PORTAL_VIS_NAME = 'portals'

@sims4.commands.Command('debugvis.portals.start', command_type=(sims4.commands.CommandType.Automation))
def debugvis_portals_start(portal_obj_id: int=0, there_id: int=0, back_id: int=0, _connection=None):
    handle = portal_obj_id
    portal_id = there_id or back_id
    if handle:
        _stop_visualizer(_connection, PORTAL_VIS_NAME, _portal_visualizers, handle)
    else:
        layer = _create_layer(PORTAL_VIS_NAME, handle)
        visualizer = PortalVisualizer(layer, portal_obj_id=portal_obj_id, portal_id=portal_id)
        sims4.commands.output('Portal Visualization Enabled', _connection)
        return _start_visualizer(_connection, LOCATOR_VIS_NAME, _portal_visualizers, handle, visualizer, layer=layer) or 0
    return 1


@sims4.commands.Command('debugvis.portals.stop', command_type=(sims4.commands.CommandType.Automation))
def debugvis_portals_stop(portal_obj_id: int=0, _connection=None):
    sims4.commands.output('Portal Visualization Disabled', _connection)
    if not portal_obj_id:
        handles = [handle for handle in _portal_visualizers]
        for handle in handles:
            _stop_visualizer(_connection, PORTAL_VIS_NAME, _portal_visualizers, handle)

    else:
        return _stop_visualizer(_connection, PORTAL_VIS_NAME, _portal_visualizers, portal_obj_id) or 0
    return 1


POND_VIS_NAME = 'pond'

@sims4.commands.Command('debugvis.pond.start', command_type=(sims4.commands.CommandType.Automation))
def debugvis_pond_start(draw_contours: bool=False, _connection=None):
    handle = 0
    layer = _create_layer(POND_VIS_NAME, handle)
    visualizer = PondVisualizer(layer, draw_contours=draw_contours)
    if not _start_visualizer(_connection, POND_VIS_NAME, _pond_visualizers,
      handle, visualizer, layer=layer):
        return 0
    sims4.commands.output('Pond Visualization Enabled', _connection)
    return 1


@sims4.commands.Command('debugvis.pond.stop', command_type=(sims4.commands.CommandType.Automation))
def debugvis_pond_stop(_connection=None):
    if not _stop_visualizer(_connection, POND_VIS_NAME, _pond_visualizers, 0):
        return 0
    sims4.commands.output('Pond Visualization Disabled', _connection)
    return 1


SECTIONAL_SOFAS_VIS_NAME = 'sectional_sofas'

@sims4.commands.Command('debugvis.sectional_sofas.start', command_type=(sims4.commands.CommandType.Automation))
def debugvis_sectional_sofas_start(sofa_obj_param: RequiredTargetParam, piece_id: int=0, _connection=None):
    sofa_obj = sofa_obj_param.get_target()
    if sofa_obj is None:
        sims4.commands.output(f"Object {sofa_obj_param.target_id} not found", _connection)
        return 0
    else:
        handle = sofa_obj.id
        if handle:
            _stop_visualizer(_connection, SECTIONAL_SOFAS_VIS_NAME, _sectional_sofa_visualizers, handle)
        layer = _create_layer(SECTIONAL_SOFAS_VIS_NAME, handle)
        visualizer = SectionalSofaVisualizer(layer, (sofa_obj.id), sectional_sofa_piece_id=piece_id)
        sims4.commands.output('Sectional Sofa Visualization Enabled', _connection)
        return _start_visualizer(_connection, SECTIONAL_SOFAS_VIS_NAME, _sectional_sofa_visualizers, handle, visualizer, layer=layer) or 0
    return 1


@sims4.commands.Command('debugvis.sectional_sofas.stop', command_type=(sims4.commands.CommandType.Automation))
def debugvis_sectional_sofas_stop(sofa_obj_id: int=0, _connection=None):
    sims4.commands.output('Sectional Sofa Visualization Disabled', _connection)
    if not sofa_obj_id:
        handles = [handle for handle in _sectional_sofa_visualizers]
        for handle in handles:
            _stop_visualizer(_connection, SECTIONAL_SOFAS_VIS_NAME, _sectional_sofa_visualizers, handle)

    else:
        return _stop_visualizer(_connection, SECTIONAL_SOFAS_VIS_NAME, _sectional_sofa_visualizers, sofa_obj_id) or 0
    return 1


@sims4.commands.Command('debugvis.sim_quadtree.start')
def debugvis_sim_quadtree_start(_connection=None):
    vis_name = 'sim_quadtree'
    handle = 0
    layer = _create_layer(vis_name, handle)
    visualizer = QuadTreeVisualizer(layer)
    if not _start_visualizer(_connection, vis_name, _quadtree_layer_visualizers, handle, visualizer, layer=layer):
        return 0
    return 1


@sims4.commands.Command('debugvis.sim_quadtree.stop')
def debugvis_sim_quadtree_stop(_connection=None):
    if not _stop_visualizer(_connection, 'sim_quadtree', _quadtree_layer_visualizers, 0):
        return 0
    return 1


@sims4.commands.Command('debugvis.fire_quadtree.start')
def debugvis_fire_quadtree_start--- This code section failed: ---

 L. 642         0  LOAD_GLOBAL              services
                2  LOAD_METHOD              get_fire_service
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  STORE_FAST               'fire_service'

 L. 643         8  LOAD_FAST                'fire_service'
               10  LOAD_ATTR                fire_quadtree
               12  STORE_FAST               'fire_quadtree'

 L. 644        14  LOAD_FAST                'fire_service'
               16  LOAD_ATTR                flammable_objects_quadtree
               18  STORE_FAST               'flammable_quadtree'

 L. 645        20  LOAD_FAST                'fire_quadtree'
               22  LOAD_CONST               None
               24  COMPARE_OP               is-not
               26  POP_JUMP_IF_TRUE     36  'to 36'
               28  LOAD_FAST                'flammable_quadtree'
               30  LOAD_CONST               None
               32  COMPARE_OP               is-not
               34  POP_JUMP_IF_FALSE    86  'to 86'
             36_0  COME_FROM            26  '26'

 L. 646        36  LOAD_STR                 'fire_quadtree'
               38  STORE_FAST               'fire_vis_name'

 L. 647        40  LOAD_CONST               1
               42  STORE_FAST               'handle'

 L. 648        44  LOAD_GLOBAL              _create_layer
               46  LOAD_FAST                'fire_vis_name'
               48  LOAD_FAST                'handle'
               50  CALL_FUNCTION_2       2  '2 positional arguments'
               52  STORE_FAST               'fire_layer'

 L. 649        54  LOAD_GLOBAL              FireQuadTreeVisualizer
               56  LOAD_FAST                'fire_layer'
               58  CALL_FUNCTION_1       1  '1 positional argument'
               60  STORE_FAST               'fire_visualizer'

 L. 650        62  LOAD_GLOBAL              _start_visualizer
               64  LOAD_FAST                '_connection'
               66  LOAD_FAST                'fire_vis_name'
               68  LOAD_GLOBAL              _quadtree_layer_visualizers
               70  LOAD_FAST                'handle'
               72  LOAD_FAST                'fire_visualizer'

 L. 651        74  LOAD_FAST                'fire_layer'
               76  LOAD_CONST               ('layer',)
               78  CALL_FUNCTION_KW_6     6  '6 total positional and keyword args'
               80  POP_JUMP_IF_TRUE     86  'to 86'

 L. 652        82  LOAD_CONST               0
               84  RETURN_VALUE     
             86_0  COME_FROM            80  '80'
             86_1  COME_FROM            34  '34'

 L. 654        86  LOAD_CONST               1
               88  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `RETURN_VALUE' instruction at offset 88


@sims4.commands.Command('debugvis.fire_quadtree.stop')
def debugvis_fire_quadtree_stop(_connection=None):
    if not _stop_visualizer(_connection, 'fire_quadtree', _quadtree_layer_visualizers, 1):
        return 0
    return 1


@sims4.commands.Command('debugvis.broadcasters.start')
def debugvis_broadcasters_start(_connection=None):
    layer = _create_layer('broadcasters', 0)
    visualizer = BroadcasterVisualizer(layer)
    return _start_visualizer(_connection, 'broadcasters', _broadcaster_visualizers, 0, visualizer, layer)


@sims4.commands.Command('debugvis.broadcasters.stop')
def debugvis_broadcasters_stop(_connection=None):
    return _stop_visualizer(_connection, 'broadcasters', _broadcaster_visualizers, 0)


@sims4.commands.Command('debugvis.routing_formations.start')
def debugvis_routing_formations_start(opt_sim: OptionalTargetParam=None, _connection=None):
    return _start_sim_visualizer(opt_sim, _connection, 'formations', _routing_formation_visualizers, RoutingFormationVisualizer)


@sims4.commands.Command('debugvis.routing_formations.stop')
def debugvis_routing_formations_stop(opt_sim: OptionalTargetParam=None, _connection=None):
    return _stop_sim_visualizer(opt_sim, _connection, 'formations', _routing_formation_visualizers)


@sims4.commands.Command('debugvis.mood.start')
def debugvis_mood_start(opt_sim: OptionalTargetParam=None, _connection=None):
    if not _start_sim_visualizer(opt_sim, _connection, 'mood', _mood_visualizers, MoodVisualizer):
        return 0
    return 1


@sims4.commands.Command('debugvis.mood.stop')
def debugvis_mood_stop(opt_sim: OptionalTargetParam=None, _connection=None):
    if not _stop_sim_visualizer(opt_sim, _connection, 'mood', _mood_visualizers):
        return 0
    return 1


@sims4.commands.Command('debugvis.mood.toggle')
def debugvis_mood_toggle(_connection=None):

    def _on_object_add(obj):
        if obj.is_sim:
            for _connection in _all_mood_visualization_enabled:
                debugvis_mood_start(opt_sim=obj, _connection=_connection)

    def _on_object_remove(obj):
        if obj.is_sim:
            for _connection in _all_mood_visualization_enabled:
                debugvis_mood_stop(opt_sim=obj, _connection=_connection)

    def _on_client_remove(client):
        if client.id in _all_mood_visualization_enabled:
            debugvis_mood_toggle(_connection=(client.id))

    enable = _connection not in _all_mood_visualization_enabled
    old_registered = True if _all_mood_visualization_enabled else False
    om = services.object_manager()
    infom = services.sim_info_manager()
    cm = services.client_manager()
    if enable:
        _all_mood_visualization_enabled.add(_connection)
        for sim in infom.instanced_sims_gen():
            debugvis_mood_start(opt_sim=sim, _connection=_connection)

    else:
        _all_mood_visualization_enabled.remove(_connection)
        for sim in infom.instanced_sims_gen():
            debugvis_mood_stop(opt_sim=sim, _connection=_connection)

    new_registered = True if _all_mood_visualization_enabled else False
    if not old_registered:
        if new_registered:
            om.register_callback(indexed_manager.CallbackTypes.ON_OBJECT_ADD, _on_object_add)
            om.register_callback(indexed_manager.CallbackTypes.ON_OBJECT_REMOVE, _on_object_remove)
            cm.register_callback(indexed_manager.CallbackTypes.ON_OBJECT_REMOVE, _on_client_remove)
    if old_registered:
        if not new_registered:
            om.unregister_callback(indexed_manager.CallbackTypes.ON_OBJECT_ADD, _on_object_add)
            om.unregister_callback(indexed_manager.CallbackTypes.ON_OBJECT_REMOVE, _on_object_remove)
            cm.unregister_callback(indexed_manager.CallbackTypes.ON_OBJECT_REMOVE, _on_client_remove)


@sims4.commands.Command('debugvis.autonomy_timer.start')
def debugvis_autonomy_timer_start(opt_sim: OptionalTargetParam=None, _connection=None):
    if not _start_sim_visualizer(opt_sim, _connection, 'autonomy_timer', _autonomy_timer_visualizers, AutonomyTimerVisualizer):
        return 0
    return 1


@sims4.commands.Command('debugvis.autonomy_timer.stop')
def debugvis_autonomy_timer_stop(opt_sim: OptionalTargetParam=None, _connection=None):
    if not _stop_sim_visualizer(opt_sim, _connection, 'autonomy_timer', _autonomy_timer_visualizers):
        return 0
    return 1


@sims4.commands.Command('debugvis.autonomy_timer.toggle')
def debugvis_autonomy_timer_toggle(_connection=None):

    def _on_object_add(obj):
        if obj.is_sim:
            for _connection in _all_autonomy_timer_visualization_enabled:
                debugvis_autonomy_timer_start(opt_sim=obj, _connection=_connection)

    def _on_object_remove(obj):
        if obj.is_sim:
            for _connection in _all_autonomy_timer_visualization_enabled:
                debugvis_autonomy_timer_stop(opt_sim=obj, _connection=_connection)

    def _on_client_remove(client):
        if client.id in _all_autonomy_timer_visualization_enabled:
            debugvis_autonomy_timer_toggle(_connection=(client.id))

    enable = _connection not in _all_autonomy_timer_visualization_enabled
    old_registered = True if _all_autonomy_timer_visualization_enabled else False
    object_manager = services.object_manager()
    sim_info_manager = services.sim_info_manager()
    client_manager = services.client_manager()
    if enable:
        _all_autonomy_timer_visualization_enabled.add(_connection)
        for sim in sim_info_manager.instanced_sims_gen():
            debugvis_autonomy_timer_start(opt_sim=sim, _connection=_connection)

    else:
        _all_autonomy_timer_visualization_enabled.remove(_connection)
        for sim in sim_info_manager.instanced_sims_gen():
            debugvis_autonomy_timer_stop(opt_sim=sim, _connection=_connection)

    new_registered = True if _all_autonomy_timer_visualization_enabled else False
    if not old_registered:
        if new_registered:
            object_manager.register_callback(indexed_manager.CallbackTypes.ON_OBJECT_ADD, _on_object_add)
            object_manager.register_callback(indexed_manager.CallbackTypes.ON_OBJECT_REMOVE, _on_object_remove)
            client_manager.register_callback(indexed_manager.CallbackTypes.ON_OBJECT_REMOVE, _on_client_remove)
    if old_registered:
        if not new_registered:
            object_manager.unregister_callback(indexed_manager.CallbackTypes.ON_OBJECT_ADD, _on_object_add)
            object_manager.unregister_callback(indexed_manager.CallbackTypes.ON_OBJECT_REMOVE, _on_object_remove)
            client_manager.unregister_callback(indexed_manager.CallbackTypes.ON_OBJECT_REMOVE, _on_client_remove)


@sims4.commands.Command('debugvis.connectivity_handles.start')
def debugvis_connectivity_handles_start(opt_sim: OptionalTargetParam=None, _connection=None):
    if not _start_sim_visualizer(opt_sim, _connection, 'cg_handles', _connectivity_handles_layer_visualizers, ConnectivityHandlesVisualizer):
        return 0
    return 1


@sims4.commands.Command('debugvis.connectivity_handles.stop')
def debugvis_connectivity_handles_stop(opt_sim: OptionalTargetParam=None, _connection=None):
    if not _stop_sim_visualizer(opt_sim, _connection, 'cg_handles', _connectivity_handles_layer_visualizers):
        return 0
    return 1


@sims4.commands.Command('debugvis.social_clustering.refresh')
def debugvis_social_clustering(detailed_obj_id: int=None, _connection=None):
    with Context('social_clustering') as (layer):
        for cluster in services.social_group_cluster_service().get_clusters_gen(regenerate=True):
            layer.routing_surface = cluster.routing_surface
            for obj in cluster.objects_gen():
                layer.set_color(Color.CYAN)
                layer.add_segment(obj.position, cluster.position)
                if obj.id == detailed_obj_id:
                    layer.set_color(Color.WHITE)
                    layer.add_polygon(cluster.polygon)
                    detailed_obj_id = None
                layer.set_color(Color.YELLOW)
                layer.add_circle(obj.position, 0.65)

            layer.set_color(Color.CYAN)
            layer.add_circle(cluster.position, 0.35)
            _draw_constraint(layer, cluster.constraint, Color.GREEN)

    sims4.commands.client_cheat('debugvis.layer.enable social_clustering', _connection)
    return True


@sims4.commands.Command('debugvis.look_ats.start')
def debugvis_look_ats_start(_connection):
    sims4.commands.client_cheat('animation.debugviz.global lookat on', _connection)


@sims4.commands.Command('debugvis.look_ats.stop')
def debugvis_look_ats_stop(_connection):
    sims4.commands.client_cheat('animation.debugviz.global lookat off', _connection)


@sims4.commands.Command('debugvis.los.enable')
def debugvis_los_enable(_connection=None):
    objects.components.line_of_sight_component.enable_visualization = True


@sims4.commands.Command('debugvis.los.disable')
def debugvis_los_disable(_connection=None):
    objects.components.line_of_sight_component.enable_visualization = False


@sims4.commands.Command('debugvis.goals.enable')
def debugvis_goals_enable(opt_sim: OptionalTargetParam=None, _connection=None):
    postures.posture_graph.enable_debug_goals_visualization = True
    sims4.commands.client_cheat('debugvis.layer.enable goal_scoring', _connection)
    sims4.commands.client_cheat('debugvis.layer.enable destination_cost', _connection)
    _start_sim_visualizer(opt_sim, _connection, 'pathgoals', _path_goals_layer_visualizers, PathGoalVisualizer)
    _start_sim_visualizer(opt_sim, _connection, 'sim_trans_dests', _constraint_layer_visualizers, SimShortestTransitionPathVisualizer)


@sims4.commands.Command('debugvis.goals.disable')
def debugvis_goals_disable(opt_sim: OptionalTargetParam=None, _connection=None):
    postures.posture_graph.enable_debug_goals_visualization = False
    sims4.commands.client_cheat('debugvis.layer.disable goal_scoring', _connection)
    sims4.commands.client_cheat('debugvis.layer.disable destination_cost', _connection)
    _stop_sim_visualizer(opt_sim, _connection, 'pathgoals', _path_goals_layer_visualizers)
    _stop_sim_visualizer(opt_sim, _connection, 'sim_trans_dests', _constraint_layer_visualizers)


@sims4.commands.Command('debugvis.transitions.start')
def debugvis_transition_constraints_start(_connection=None):
    vis_name = 'transitions'
    handle = 0
    layer = _create_layer(vis_name, handle)
    visualizer = TransitionConstraintVisualizer(layer)
    if not _start_visualizer(_connection, vis_name, _constraint_layer_visualizers, handle, visualizer, layer=layer):
        return 0
    return 1


@sims4.commands.Command('debugvis.transitions.stop')
def debugvis_transition_constraints_stop(_connection=None):
    if not _stop_visualizer(_connection, 'transitions', _constraint_layer_visualizers, 0):
        return 0
    return 1


DYNAMIC_JIG_VIZ_NAME = 'dynamic_jigs'

@sims4.commands.Command('debugvis.dynamic_jigs.start', command_type=(sims4.commands.CommandType.Automation))
def debugvis_dynamic_jig_start(_connection=None):
    handle = 0
    layer = _create_layer(DYNAMIC_JIG_VIZ_NAME, handle)
    visualizer = JigVisualizer(layer)
    if not _start_visualizer(_connection, DYNAMIC_JIG_VIZ_NAME, _constraint_layer_visualizers, handle, visualizer, layer=layer):
        return 0
    return 1


@sims4.commands.Command('debugvis.dynamic_jigs.stop')
def debugvis_dynamic_jig_stop(_connection=None):
    if not _stop_visualizer(_connection, DYNAMIC_JIG_VIZ_NAME, _constraint_layer_visualizers, 0):
        return 0
    return 1


class DrawVisualizer:

    def __init__(self, layer):
        self.layer = layer

    def _start(self):
        pass

    def stop(self):
        pass


_draw_viz_layer = None

@sims4.commands.Command('debugvis.draw.start')
def debugvis_draw_start(_connection=None):
    global _draw_viz_layer
    if _draw_viz_layer is None:
        vis_name = 'draw'
        handle = 0
        _draw_viz_layer = _create_layer(vis_name, handle)
        visualizer = DrawVisualizer(_draw_viz_layer)
        if not _start_visualizer(_connection, vis_name, _draw_visualizers, handle, visualizer, layer=_draw_viz_layer):
            return 0
    return 1


@sims4.commands.Command('debugvis.draw.stop')
def debugvis_draw_stop(_connection=None):
    global _draw_viz_layer
    _stop_visualizer(_connection, 'draw', _draw_visualizers, 0)
    _draw_viz_layer = None


@sims4.commands.Command('debugvis.draw.circle')
def debugvis_draw_circle(x=0.0, y=0.0, z=0.0, rad=0.1, snap_to_terrain=False, _connection=None):
    debugvis_draw_start(_connection)
    pos = sims4.math.Vector3(x, y, z)
    altitude = KEEP_ALTITUDE
    if snap_to_terrain == True:
        altitude = None
    with Context(_draw_viz_layer, preserve=True) as (layer):
        layer.add_circle(pos, radius=rad, altitude=altitude)


@sims4.commands.Command('debugvis.draw.point')
def debugvis_draw_point(x=0.0, y=0.0, z=0.0, snap_to_terrain=False, color=None, _connection=None):
    debugvis_draw_start(_connection)
    pos = sims4.math.Vector3(x, y, z)
    altitude = KEEP_ALTITUDE
    if snap_to_terrain == True:
        altitude = None
    with Context(_draw_viz_layer, preserve=True) as (layer):
        layer.add_point(pos, altitude=altitude, color=color)


@sims4.commands.Command('debugvis.draw.arrow')
def debugvis_draw_arrow(x=0.0, y=0.0, z=0.0, angle=0.0, length=0.5, snap_to_terrain=False, color=None, _connection=None):
    debugvis_draw_start(_connection)
    pos = sims4.math.Vector3(x, y, z)
    altitude = KEEP_ALTITUDE
    if snap_to_terrain == True:
        altitude = None
    with Context(_draw_viz_layer, preserve=True) as (layer):
        layer.add_arrow(pos, angle, length, altitude=altitude, color=color)


@sims4.commands.Command('debugvis.draw.line')
def debugvis_draw_line(x1=0.0, y1=0.0, z1=0.0, x2=0.0, y2=0.0, z2=0.0, snap_to_terrain=False, color=None, _connection=None):
    debugvis_draw_start(_connection)
    start = sims4.math.Vector3(x1, y1, z1)
    dest = sims4.math.Vector3(x2, y2, z2)
    altitude = KEEP_ALTITUDE
    if snap_to_terrain == True:
        altitude = None
    with Context(_draw_viz_layer, preserve=True) as (layer):
        layer.add_segment(start, dest, altitude=altitude, color=color)


@sims4.commands.Command('debugvis.draw.text')
def debugvis_draw_text(x=0.0, y=0.0, z=0.0, text='test', snap_to_terrain=False, _connection=None):
    debugvis_draw_start(_connection)
    pos = sims4.math.Vector3(x, y, z)
    altitude = KEEP_ALTITUDE
    if snap_to_terrain == True:
        altitude = None
    with Context(_draw_viz_layer, preserve=True) as (layer):
        layer.add_text_world(pos, text, altitude=altitude)


POLYGON_STR = 'Polygon{'
POLYGON_END_PARAM = '}'
POLYGON_FLAGS_PARAM = "Flags='CCW'"
POINT_STR = 'Point('
VECTOR3_STR = 'Vector3('
VECTOR3_END_PARAM = ')'
TRANSFORM_STR = 'Transform('
TRANSFORM_END_STR = '))'

@sims4.commands.Command('debugvis.draw_polygons_in_str')
def draw_polygons_in_string(*args, _connection=None):
    total_string = ''.join(args)
    polygon_strs = find_substring_in_repr(total_string, POLYGON_STR, POLYGON_END_PARAM)
    for poly_str in polygon_strs:
        poly_str = poly_str.replace(POLYGON_FLAGS_PARAM, '')
        draw_polygon_str(poly_str, _connection)


def draw_polygon_str(polygon_str, _connection):
    point_list = extract_floats(polygon_str)
    draw_polygon(point_list, _connection)


def draw_polygon(point_list, _connection):
    color = pseudo_random_color(id(point_list))
    num_floats = len(point_list)
    if num_floats == 2:
        debugvis_draw_point(point_list[0], 0.0, point_list[1], True, color, _connection)
    else:
        if num_floats % 2 == 0:
            point_list.append(point_list[0])
            point_list.append(point_list[1])
            for index in range(0, num_floats, 2):
                debugvis_draw_line(point_list[index], 0.0, point_list[index + 1], point_list[index + 2], 0.0, point_list[index + 3], True, color, _connection)


def draw_transform(transform_str, _connection=None):
    transform_str = transform_str.replace(VECTOR3_STR, '')
    float_list = extract_floats(transform_str)
    color = pseudo_random_color(id(float_list))
    num_floats = len(float_list)
    if num_floats == 7:
        transform_quaternion = sims4.math.Quaternion(float_list[3], float_list[4], float_list[5], float_list[6])
        angle = sims4.math.yaw_quaternion_to_angle(transform_quaternion)
        debugvis_draw_arrow((float_list[0]), (float_list[1]), (float_list[2]), angle=angle,
          snap_to_terrain=True,
          color=color,
          _connection=_connection)
        debugvis_draw_point((float_list[0]), (float_list[1]), (float_list[2]), snap_to_terrain=True,
          color=color,
          _connection=_connection)
    else:
        logger.warn("Transform string doesn't have vector3 and orientation: {}", transform_str)


@sims4.commands.Command('debugvis.draw_transforms_in_str')
def draw_transform_in_string(*args, _connection=None):
    total_string = ''.join(args)
    transform_strs = find_substring_in_repr(total_string, TRANSFORM_STR, TRANSFORM_END_STR)
    for transform_str in transform_strs:
        draw_transform(transform_str, _connection)


def draw_vector3(vector3_str, _connection):
    point_list = extract_floats(vector3_str)
    color = pseudo_random_color(id(point_list))
    num_floats = len(point_list)
    if num_floats == 3:
        debugvis_draw_point(point_list[0], point_list[1], point_list[2], True, color, _connection)
    else:
        logger.warn("Vector3 string doesn't have 3 points: {}", vector3_str)


@sims4.commands.Command('debugvis.draw_vector3_in_str')
def draw_vector3_in_string(*args, _connection=None):
    total_string = ''.join(args)
    vector3_strs = find_substring_in_repr(total_string, VECTOR3_STR, VECTOR3_END_PARAM)
    for vector3_str in vector3_strs:
        draw_vector3(vector3_str, _connection)


@sims4.commands.Command('debugvis.draw_geometry_in_str')
def draw_geometry_in_string(*args, _connection=None):
    draw_transform_in_string(*args, **{'_connection': _connection})
    draw_vector3_in_string(*args, **{'_connection': _connection})
    draw_polygons_in_string(*args, **{'_connection': _connection})


@sims4.commands.Command('debugvis.ensembles.start')
def debugvis_ensembles_start(_connection=None):
    layer = _create_layer('ensembles', 0)
    visualizer = EnsembleVisualizer(layer)
    return _start_visualizer(_connection, 'ensembles', _ensemble_visualizers, 0, visualizer, layer)


@sims4.commands.Command('debugvis.ensembles.stop')
def debugvis_ensembles_stop(_connection=None):
    return _stop_visualizer(_connection, 'ensembles', _ensemble_visualizers, 0)


@sims4.commands.Command('debugvis.polygon_intersection')
def polygon_intersection(*args, _connection=None):
    output = sims4.commands.Output(_connection)
    total_string = ''.join(args)
    polygon_strs = find_substring_in_repr(total_string, POLYGON_STR, POLYGON_END_PARAM)
    if not polygon_strs:
        output('No valid polygons. must start with {} and end with {}'.format(POLYGON_STR, POLYGON_END_PARAM))
        return
    constraints = []
    for poly_str in polygon_strs:
        point_list = extract_floats(poly_str)
        if not point_list or len(point_list) % 2 != 0:
            output('Point list is not valid length. Too few or one too many.')
            return
        vertices = []
        for index in range(0, len(point_list), 2):
            vertices.append(sims4.math.Vector3(point_list[index], 0.0, point_list[index + 1]))

        polygon = sims4.geometry.Polygon(vertices)
        geometry = sims4.geometry.RestrictedPolygon(polygon, [])
        constraint = Constraint(geometry=geometry, routing_surface=(routing.SurfaceIdentifier(services.current_zone_id(), 0, routing.SurfaceType.SURFACETYPE_WORLD)))
        constraints.append(constraint)

    intersection = ANYWHERE
    for constraint in constraints:
        new_intersection = intersection.intersect(constraint)
        if not new_intersection.valid:
            output('Constraint intersection failed. Drawing incompatible geometry. {}'.format(new_intersection))
            if intersection.geometry is not None:
                draw_geometry_in_string((str(intersection.geometry)), _connection=_connection)
            draw_geometry_in_string((str(constraint.geometry)), _connection=_connection)
            return
            intersection = new_intersection

    if intersection.valid:
        draw_geometry_in_string((str(intersection.geometry)), _connection=_connection)
        output('Intersection valid. Drawing Polygon.')


@sims4.commands.Command('debugvis.draw_lot_edge_polygons')
def draw_lot_edge_polygons(width=10, depth=2.0, _connection=None):
    lot = services.current_zone().lot
    edge_polygons = lot.get_edge_polygons(width=(int(width)), depth=(int(depth)))
    for polygon in edge_polygons:
        floats = []
        for vertex in polygon:
            floats.append(vertex.x)
            floats.append(vertex.z)

        draw_polygon(floats, _connection)


OBJECT_ROUTE_VIS_NAME = 'object_route'

@sims4.commands.Command('debugvis.object_route.draw_path')
def draw_path(path_id: int, route: PathParam, _connection=None):
    _stop_visualizer(_connection, OBJECT_ROUTE_VIS_NAME, _object_route_visualizers, 0)
    erase_paths(_connection)
    return draw_additional_path(path_id, route, _connection)


@sims4.commands.Command('debugvis.object_route.draw_additional_path')
def draw_additional_path(path_id: int, route: PathParam, _connection=None):
    if route is None:
        sims4.commands.output('Failed to parse PathParam.', _connection)
        return 0
    else:
        layer = _create_layer(OBJECT_ROUTE_VIS_NAME, path_id)
        visualizer = ObjectRouteVisualizer(layer, route=route)
        sims4.commands.output('Object Route Visualization Enabled', _connection)
        return _start_visualizer(_connection, OBJECT_ROUTE_VIS_NAME, _object_route_visualizers, path_id, visualizer, layer=layer) or 0
    return 1


@sims4.commands.Command('debugvis.object_route.erase_all_paths')
def erase_paths(_connection=None):
    handles = [handle for handle in _object_route_visualizers]
    for handle in handles:
        _stop_visualizer(_connection, OBJECT_ROUTE_VIS_NAME, _object_route_visualizers, handle)