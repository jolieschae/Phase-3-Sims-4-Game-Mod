# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\posture_graph_handlers.py
# Compiled at: 2020-12-02 17:28:38
# Size of source mod 2**32: 23897 bytes
import re, weakref
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
from uid import UniqueIdGenerator
import algos, postures, sims4.log
from sims4.utils import setdefault_callable
from routing import GoalFailureType
logger = sims4.log.Logger('GSI')
with sims4.reload.protected(globals()):
    gsi_path_id = UniqueIdGenerator()
    posture_transition_logs = weakref.WeakKeyDictionary()
    current_transition_interactions = weakref.WeakKeyDictionary()

class PostureTransitionGSILog:

    def __init__(self):
        self.clear_log()

    def clear_log(self):
        self.current_pass = 0
        self.path = None
        self.path_success = False
        self.path_cost = 0
        self.dest_spec = None
        self.all_goals = []
        self.path_progress = 0
        self.path_cost_log = []
        self.path_goal_costs = {}
        self.possible_constraints = []
        self.possible_path_destinations = {}
        self.all_handles = []
        self.sources_and_destinations = []
        self.transition_templates = []
        self.cur_posture_interaction = None
        self.all_possible_paths = []
        self.all_goal_costs = []
        self.tried_destinations = []
        self.heuristic_fn_costs = []


trans_path_archive_schema = GsiGridSchema(label='Transition Log', sim_specific=True)
trans_path_archive_schema.add_field('archive_id', label='ID', hidden=True)
trans_path_archive_schema.add_field('sim_name', label='Sim Name', width=150, hidden=True)
trans_path_archive_schema.add_field('interaction', label='Interaction', width=150)
trans_path_archive_schema.add_field('path_success', label='Success', width=65)
trans_path_archive_schema.add_field('path_progress', label='Progress', width=150)
trans_path_archive_schema.add_field('path', label='Chosen Path', width=450)
trans_path_archive_schema.add_field('destSpec', label='Dest Spec', width=350)
trans_path_archive_schema.add_field('pathCost', label='Cost')
trans_path_archive_schema.add_field('posture_state', label='Posture State', hidden=True)
with trans_path_archive_schema.add_has_many('all_constraints', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('build_pass', label='Pass', width=0.15)
    sub_schema.add_field('cur_constraint', label='Constraint')
    sub_schema.add_field('constraint_type', label='Type', width=0.15)
    sub_schema.add_field('constraint_geometry', label='Geometry')
with trans_path_archive_schema.add_has_many('templates', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('build_pass', label='Pass', width=0.15)
    sub_schema.add_field('spec', label='Spec')
    sub_schema.add_field('var_maps', label='Var Maps')
with trans_path_archive_schema.add_has_many('sources_and_dests', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('build_pass', label='Pass', width=0.15)
    sub_schema.add_field('posture_specs', label='Posture Specs')
    sub_schema.add_field('var_map', label='Var Map')
    sub_schema.add_field('type', label='Type', width=0.5)
    sub_schema.add_field('node', label='Node')
with trans_path_archive_schema.add_has_many('all_possible_paths', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('build_pass', label='Pass', width=0.15)
    sub_schema.add_field('path', label='Path', width=10)
    sub_schema.add_field('type', label='Type')
    sub_schema.add_field('cost', label='Cost', type=(GsiFieldVisualizers.FLOAT))
    sub_schema.add_field('constraint', label='Constraint')
with trans_path_archive_schema.add_has_many('all_handles', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('build_pass', label='Pass', width=0.15)
    sub_schema.add_field('handle', label='Handle', width=4)
    sub_schema.add_field('polygons', label='Polygons', width=4)
    sub_schema.add_field('path', label='Path', width=4)
    sub_schema.add_field('type', label='Type')
    sub_schema.add_field('valid', label='Valid')
with trans_path_archive_schema.add_has_many('path_costs', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('build_pass', label='Pass', width=0.15)
    sub_schema.add_field('currNode', label='Current Node')
    sub_schema.add_field('nextNode', label='Next Node')
    sub_schema.add_field('transCost', label='Cost')
with trans_path_archive_schema.add_has_many('goal_costs', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('build_pass', label='Pass', width=0.15, hidden=True)
    sub_schema.add_field('currNode', label='Current Node', width=2)
    sub_schema.add_field('searchCost', label='Final Cost', type=(GsiFieldVisualizers.FLOAT))
    sub_schema.add_field('constraintCost', label='Constraint Cost', width=0.75, type=(GsiFieldVisualizers.FLOAT))
    sub_schema.add_field('transCost', label='Goal Node Cost', width=0.75, type=(GsiFieldVisualizers.FLOAT))
    sub_schema.add_field('info', label='Cost Info', width=3)
with trans_path_archive_schema.add_has_many('all_goal_costs', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('build_pass', label='Pass', width=0.15)
    sub_schema.add_field('path', label='Path', width=10)
    sub_schema.add_field('location', label='Loc', width=6)
    sub_schema.add_field('type', label='Type')
    sub_schema.add_field('cost', label='Cost', type=(GsiFieldVisualizers.FLOAT))
    sub_schema.add_field('slot_params', label='Slot Parameters', width=3)
    sub_schema.add_field('source_dest_id', label='Set Id', type=(GsiFieldVisualizers.INT))
    sub_schema.add_field('error', label='Error', width=2)
with trans_path_archive_schema.add_has_many('heuristics', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('build_pass', label='Pass', width=0.15)
    sub_schema.add_field('node', label='Node', width=5)
    sub_schema.add_field('mobile_node', label='Mobile')
    sub_schema.add_field('path_type', label='Type')
    sub_schema.add_field('cost', label='Cost', type=(GsiFieldVisualizers.FLOAT), width=2)
with trans_path_archive_schema.add_has_many('tried_destinations', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('build_pass', label='Pass', width=0.15)
    sub_schema.add_field('sim', label='Sim')
    sub_schema.add_field('destination', label='Type')
archiver = GameplayArchiver('transition_path', trans_path_archive_schema, add_to_archive_enable_functions=True)

def get_sim_transition_log(sim, interaction=None):
    all_transition_logs = setdefault_callable(posture_transition_logs, sim, weakref.WeakKeyDictionary)
    if interaction is None:
        interaction_ref = current_transition_interactions.get(sim, None)
        if interaction_ref is None:
            return
        interaction = interaction_ref()
        if interaction is None:
            del current_transition_interactions[sim]
            return
    posture_log = setdefault_callable(all_transition_logs, interaction, PostureTransitionGSILog)
    return posture_log


def increment_build_pass(sim, interaction):
    transition_log = get_sim_transition_log(sim, interaction=interaction)
    if transition_log is None:
        return
    transition_log.current_pass += 1


def add_tried_destinations(sim, interaction, tried_destinations):
    transition_log = get_sim_transition_log(sim, interaction=interaction)
    if transition_log is None:
        return
    for cur_sim, destinations in tried_destinations.items():
        for destination in destinations:
            transition_log.tried_destinations.append({'build_pass':transition_log.current_pass, 
             'sim':str(cur_sim), 
             'destination':str(destination)})


def add_heuristic_fn_score(sim, path_type, node, mobile_node, cost):
    transition_log = get_sim_transition_log(sim)
    if transition_log is None:
        return
    transition_log.heuristic_fn_costs.append({'build_pass':transition_log.current_pass, 
     'path_type':path_type, 
     'node':str(node), 
     'mobile_node':str(mobile_node), 
     'cost':cost})


def format_interaction_for_transition_log(interaction):
    return '{} (id:{})'.format(type(interaction).__name__, interaction.id)


def add_possible_constraints(sim, constraints, type_str):
    transition_log = get_sim_transition_log(sim)
    if transition_log is None:
        return
    geometry = [str(constraint.geometry) for constraint in constraints]
    for constraint in constraints:
        transition_log.possible_constraints.append({'build_pass':transition_log.current_pass,  'cur_constraint':str(constraint), 
         'constraint_type':type_str, 
         'constraint_geometry':','.join(geometry)})


def add_source_or_dest(sim, posture_specs, var_map, node_type, node):
    transition_log = get_sim_transition_log(sim)
    if transition_log is None:
        return
    specs_str = '\n'.join((str(spec) for spec in posture_specs))
    transition_log.sources_and_destinations.append({'build_pass':transition_log.current_pass,  'posture_specs':specs_str, 
     'var_map':str(var_map), 
     'type':node_type, 
     'node':str(node)})


def add_templates_to_gsi(sim, templates):
    transition_log = get_sim_transition_log(sim)
    if transition_log is None:
        return
    for spec, spec_vars, _ in templates:
        spec_var_strs = []
        for var_map in spec_vars:
            spec_var_strs.append(str(var_map))

        transition_log.transition_templates.append({'build_pass':transition_log.current_pass,  'spec':str(spec), 
         'var_maps':'\n'.join(spec_var_strs)})


def set_current_posture_interaction(sim, interaction):
    current_transition_interactions[sim] = weakref.ref(interaction)
    transition_log = get_sim_transition_log(sim)
    transition_log.cur_posture_interaction = format_interaction_for_transition_log(interaction)


def log_path_cost(sim, curr_node, next_node, cost_str_list):
    transition_log = get_sim_transition_log(sim)
    if transition_log is None:
        return
    transition_log.path_cost_log.append({'build_pass':transition_log.current_pass,  'currNode':str(curr_node), 
     'nextNode':str(next_node),  'transCost':', '.join(cost_str_list)})


def _convert_goal_dict_to_json(goal_cost_dict):
    json_entries = []
    for key, dict_item in goal_cost_dict.items():
        dict_item['currNode'] = str(key)
        json_entries.append(dict_item)

    return json_entries


def _create_goal_if_needed(transition_log, curr_node):
    if curr_node in transition_log.path_goal_costs:
        return
    transition_log.path_goal_costs[curr_node] = {'build_pass': transition_log.current_pass}


def log_shortest_path_cost(sim, sources, heuristic_fn):
    transition_log = get_sim_transition_log(sim)
    if transition_log is None:
        return
    min_costs = dict(sources) if isinstance(sources, dict) else {source: 0 for source in sources}
    for source, cost in min_costs.items():
        _create_goal_if_needed(transition_log, source)
        search_cost = cost + (0 if heuristic_fn is None else heuristic_fn(source))
        transition_log.path_goal_costs[source]['constraintCost'] = cost
        transition_log.path_goal_costs[source]['searchCost'] = search_cost


def log_goal_cost(sim, curr_node, cost, cost_str_list):
    transition_log = get_sim_transition_log(sim)
    if transition_log is None:
        return
    _create_goal_if_needed(transition_log, curr_node)
    transition_log.path_goal_costs[curr_node]['transCost'] = cost
    transition_log.path_goal_costs[curr_node]['info'] = ', '.join(cost_str_list)


def mark_selected_destination(sim, path_index, goal_index):
    transition_log = get_sim_transition_log(sim)
    if transition_log is None:
        return
    transition_log.possible_path_destinations[path_index][goal_index]['handle'] += ' (Selected)'


def log_transition_handle(sim, handle, geometry, path, valid, type_str):
    transition_log = get_sim_transition_log(sim)
    if transition_log is None:
        return
    entry = {'build_pass':transition_log.current_pass, 
     'handle':'{} Surface: {}'.format(handle, handle.routing_surface if handle is not None else None), 
     'polygons':str(geometry), 
     'path':str(path), 
     'type':str(type_str).replace('PathType.', ''), 
     'valid':valid}
    transition_log.all_handles.append(entry)


def log_possible_segmented_paths(sim, all_possible_segmented_paths):
    transition_log = get_sim_transition_log(sim)
    if transition_log is None:
        return
    all_scored_paths = transition_log.all_possible_paths

    def add_path_to_log(path, constraint, path_type):
        if path:
            all_scored_paths.append({'build_pass':transition_log.current_pass,  'path':' -> '.join(map(str, path)), 
             'type':path_type, 
             'cost':path.cost, 
             'constraint':str(constraint)})

    for segmented_path in all_possible_segmented_paths:
        if segmented_path:
            add_path_to_log(getattr(segmented_path, '_path_left', None), segmented_path.constraint, 'Left')
            add_path_to_log(getattr(segmented_path, '_path_middle', None), segmented_path.constraint, 'Middle')
            add_path_to_log(getattr(segmented_path, '_path_right', None), segmented_path.constraint, 'Right')


def log_possible_goal(sim, path_spec, goal, cost, type_str, source_dest_id):
    transition_log = get_sim_transition_log(sim)
    if transition_log is None:
        return
        if goal.has_slot_params:
            slot_params = ''
            for param_name, param_value in goal.slot_params.items():
                if isinstance(param_name, tuple):
                    slot_params += param_name[0] + ':' + param_name[1]
                else:
                    slot_params += param_name
                slot_params += '=' + str(param_value) + '\n'

    else:
        slot_params = '<no slot params>'
    entry = {'build_pass':transition_log.current_pass,  'path':str(path_spec), 
     'location':'{} {}'.format(goal.location.transform, goal.location.routing_surface), 
     'type':type_str, 
     'cost':cost, 
     'slot_params':slot_params, 
     'source_dest_id':source_dest_id, 
     'error':goal.failure_reason.name}
    transition_log.all_goal_costs.append(entry)


def archive_path(sim, best_path_spec, path_success, path_progress, interaction=None):
    transition_log = get_sim_transition_log(sim, interaction=interaction)
    if transition_log is None:
        return
    elif best_path_spec is not None:
        transition_log.path = str(best_path_spec)
        transition_log.path_cost = best_path_spec.cost
        transition_log.dest_spec = best_path_spec.destination_spec
    else:
        if path_progress < postures.posture_graph.TransitionSequenceStage.COMPLETE:
            transition_log.path = '---'
            transition_log.dest_spec = '---'
        else:
            transition_log.path = 'EMPTY_PATH_SPEC'
    transition_log.path_success = path_success
    for goal_list in transition_log.possible_path_destinations.values():
        transition_log.all_goals.extend(goal_list)

    transition_log.path_progress = path_progress
    log_path_data_to_gsi(sim)


def archive_current_spec_valid(sim, interaction):
    transition_log = get_sim_transition_log(sim, interaction=interaction)
    if transition_log is None:
        return
    transition_log.path = 'Current Spec Valid'
    transition_log.path_success = True
    log_path_data_to_gsi(sim, interaction=interaction)


def log_path_data_to_gsi(sim, interaction=None):
    transition_log = get_sim_transition_log(sim, interaction=interaction)
    if transition_log is None:
        return
    archive_data = {'archive_id':gsi_path_id(), 
     'sim_name':sim.full_name, 
     'interaction':transition_log.cur_posture_interaction, 
     'path':transition_log.path, 
     'path_success':transition_log.path_success, 
     'path_progress':str(transition_log.path_progress), 
     'pathCost':transition_log.path_cost, 
     'destSpec':str(transition_log.dest_spec), 
     'path_costs':transition_log.path_cost_log, 
     'goal_costs':_convert_goal_dict_to_json(transition_log.path_goal_costs), 
     'all_handles':transition_log.all_handles, 
     'all_possible_paths':transition_log.all_possible_paths, 
     'connected_destinations':transition_log.all_goals, 
     'all_constraints':transition_log.possible_constraints, 
     'sources_and_dests':transition_log.sources_and_destinations, 
     'templates':transition_log.transition_templates, 
     'posture_state':str(sim.posture_state), 
     'all_goal_costs':transition_log.all_goal_costs, 
     'tried_destinations':transition_log.tried_destinations, 
     'heuristics':transition_log.heuristic_fn_costs}
    archiver.archive(data=archive_data, object_id=(sim.id))
    if sim.transition_path_logging:
        log_transition_path_automation(sim, archive_data)


def archive_canceled_transition(sim, interaction, finishing_type, test_result):
    transition_log = get_sim_transition_log(sim, interaction=interaction)
    if transition_log is None:
        return
    transition_log.path = 'CANCELED: Finishing Type: {}, Result: {}'.format(finishing_type, test_result)
    transition_log.path_success = False
    transition_log.cur_posture_interaction = format_interaction_for_transition_log(interaction)
    log_path_data_to_gsi(sim, interaction=interaction)


def archive_derailed_transition(sim, interaction, reason, test_result):
    transition_log = get_sim_transition_log(sim, interaction=interaction)
    if transition_log is None:
        return
    transition_log.path = 'DERAILED: {} Result: {}'.format(reason, test_result)
    transition_log.cur_posture_interaction = format_interaction_for_transition_log(interaction)
    log_path_data_to_gsi(sim, interaction=interaction)


def log_transition_path_automation--- This code section failed: ---

 L. 509         0  LOAD_FAST                'sim'
                2  LOAD_CONST               None
                4  COMPARE_OP               is
                6  POP_JUMP_IF_TRUE     38  'to 38'
                8  LOAD_FAST                'sim'
               10  LOAD_ATTR                client
               12  LOAD_CONST               None
               14  COMPARE_OP               is
               16  POP_JUMP_IF_TRUE     38  'to 38'
               18  LOAD_FAST                'data'
               20  LOAD_CONST               None
               22  COMPARE_OP               is
               24  POP_JUMP_IF_TRUE     38  'to 38'

 L. 510        26  LOAD_FAST                'data'
               28  LOAD_STR                 'interaction'
               30  BINARY_SUBSCR    
               32  LOAD_CONST               None
               34  COMPARE_OP               is
               36  POP_JUMP_IF_FALSE    42  'to 42'
             38_0  COME_FROM            24  '24'
             38_1  COME_FROM            16  '16'
             38_2  COME_FROM             6  '6'

 L. 511        38  LOAD_CONST               False
               40  RETURN_VALUE     
             42_0  COME_FROM            36  '36'

 L. 515        42  LOAD_GLOBAL              re
               44  LOAD_METHOD              split
               46  LOAD_STR                 ':0x....,|:0x......]'
               48  LOAD_FAST                'data'
               50  LOAD_STR                 'path'
               52  BINARY_SUBSCR    
               54  CALL_METHOD_2         2  '2 positional arguments'
               56  STORE_FAST               'pathStr'

 L. 516        58  LOAD_STR                 ''
               60  LOAD_METHOD              join
               62  LOAD_FAST                'pathStr'
               64  CALL_METHOD_1         1  '1 positional argument'
               66  STORE_FAST               'pathStr'

 L. 517        68  LOAD_GLOBAL              re
               70  LOAD_METHOD              split
               72  LOAD_STR                 ':0x....$|:0x......]$'
               74  LOAD_FAST                'pathStr'
               76  CALL_METHOD_2         2  '2 positional arguments'
               78  STORE_FAST               'pathStr'

 L. 518        80  LOAD_STR                 ''
               82  LOAD_METHOD              join
               84  LOAD_FAST                'pathStr'
               86  CALL_METHOD_1         1  '1 positional argument'
               88  STORE_FAST               'pathStr'

 L. 520        90  LOAD_GLOBAL              re
               92  LOAD_METHOD              split
               94  LOAD_STR                 ':0x....,|:0x......]'
               96  LOAD_FAST                'data'
               98  LOAD_STR                 'destSpec'
              100  BINARY_SUBSCR    
              102  CALL_METHOD_2         2  '2 positional arguments'
              104  STORE_FAST               'destStr'

 L. 521       106  LOAD_STR                 ''
              108  LOAD_METHOD              join
              110  LOAD_FAST                'destStr'
              112  CALL_METHOD_1         1  '1 positional argument'
              114  STORE_FAST               'destStr'

 L. 522       116  LOAD_GLOBAL              re
              118  LOAD_METHOD              split
              120  LOAD_STR                 ':0x....$|:0x......]$'
              122  LOAD_FAST                'destStr'
              124  CALL_METHOD_2         2  '2 positional arguments'
              126  STORE_FAST               'destStr'

 L. 523       128  LOAD_STR                 ''
              130  LOAD_METHOD              join
              132  LOAD_FAST                'destStr'
              134  CALL_METHOD_1         1  '1 positional argument'
              136  STORE_FAST               'destStr'

 L. 525       138  LOAD_GLOBAL              sims4
              140  LOAD_ATTR                commands
              142  LOAD_METHOD              AutomationOutput
              144  LOAD_FAST                'sim'
              146  LOAD_ATTR                client
              148  LOAD_ATTR                id
              150  CALL_METHOD_1         1  '1 positional argument'
              152  STORE_FAST               'output'

 L. 527       154  LOAD_FAST                'output'

 L. 531       156  LOAD_STR                 '[AreaInstanceTransitionPath] SimTransPathData;         Interaction:%s,         Path:%s,         PathCost:%s,         DestSpec:%s'

 L. 532       158  LOAD_FAST                'data'
              160  LOAD_STR                 'interaction'
              162  BINARY_SUBSCR    
              164  LOAD_METHOD              split
              166  CALL_METHOD_0         0  '0 positional arguments'
              168  LOAD_CONST               0
              170  BINARY_SUBSCR    

 L. 533       172  LOAD_FAST                'pathStr'

 L. 534       174  LOAD_FAST                'data'
              176  LOAD_STR                 'pathCost'
              178  BINARY_SUBSCR    

 L. 535       180  LOAD_FAST                'destStr'
              182  LOAD_METHOD              replace
              184  LOAD_STR                 ','
              186  LOAD_STR                 ''
              188  CALL_METHOD_2         2  '2 positional arguments'
              190  BUILD_TUPLE_4         4 
              192  BINARY_MODULO    
              194  CALL_FUNCTION_1       1  '1 positional argument'
              196  POP_TOP          

Parse error at or near `CALL_FUNCTION_1' instruction at offset 194