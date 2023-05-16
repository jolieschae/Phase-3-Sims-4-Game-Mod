# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\privacy_handlers.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 7824 bytes
import services, gsi_handlers, weakref, sims4
from timeit import itertools
from routing import FootprintType
from gsi_handlers.gsi_utils import parse_filter_to_list
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
ACTIVE_FILTER = 'Is Active'
HAS_VIOLATORS_FILTER = 'Has Current Violators'
NO_VIOLATORS_STR = 'No Current Violators'
privacy_management_schema = GsiGridSchema(label='Privacy Management')
privacy_management_schema.add_field('is_active', label='Is Active', width=0.02)
privacy_management_schema.add_field('privacy_interaction', label='Privacy Interaction', width=0.05)
privacy_management_schema.add_field('sim_violators', label='Current Sim Violators', width=0.05)
privacy_management_schema.add_field('vehicle_violators', label='Current Vehicle Violators', width=0.05)
privacy_management_schema.add_field('late_violators', label='Late Privacy Violators', width=0.05)
privacy_management_schema.add_field('all_past_violators', label='All Past Instance Violators', width=0.055)
privacy_management_schema.add_field('privacy_violators', label='Privacy Violators', width=0.05)
privacy_management_schema.add_field('central_object', label='Central Object', width=0.05)
privacy_management_schema.add_field('has_shooed', label='Has Shooed', width=0.03)
privacy_management_schema.add_field('max_los', label='Max Line of Sight Radius', width=0.05)
privacy_management_schema.add_field('shoo_cons', label='Shoo Constraint Radius', width=0.05)
privacy_management_schema.add_field('privacy_discouragement_cost', label='Privacy Discouragement Cost', width=0.055)
privacy_management_schema.add_field('min_room_area_for_discouragement', label='Min Room Area for Discouragement', width=0.05)
with privacy_management_schema.add_has_many('privacy_constraints', GsiGridSchema, label='Constraints') as (sub_schema):
    sub_schema.add_field('cost', label='Cost')
    sub_schema.add_field('enabled', label='Enabled')
    sub_schema.add_field('footprint_id', label='Footprint Id')
    sub_schema.add_field('footprint_type', label='Footprint Type')
    sub_schema.add_field('polygon', label='Polygon')
with privacy_management_schema.add_has_many('affordances', GsiGridSchema, label='Affordances') as (sub_schema):
    sub_schema.add_field('embarrassed_affordance', label='Embarrassed Affordance')
    sub_schema.add_field('post_route_affordance', label='Post Route Affordance')
with privacy_management_schema.add_has_many('allowed', GsiGridSchema, label='Allowed/Exempt Sims') as (sub_schema):
    sub_schema.add_field('allowed_sims', label='Allowed Sims')
    sub_schema.add_field('disallowed_sims', label='Disallowed Sims')
    sub_schema.add_field('exempt_sims', label='Sims Exempt From Shooing')
privacy_management_schema.add_filter(ACTIVE_FILTER)
privacy_management_schema.add_filter(HAS_VIOLATORS_FILTER)
with sims4.reload.protected(globals()):
    privacy_instance_to_violators = weakref.WeakKeyDictionary()

@GsiHandler('privacy_management', privacy_management_schema)
def generate_privacy_management_data(filter=None):
    privacy_management_data = []
    active_instances = []
    filter_list = parse_filter_to_list(filter)
    privacy_service = services.privacy_service()
    if privacy_service is None:
        return privacy_management_data
    for instance in privacy_service._privacy_instances:
        if instance.is_active:
            active_instances.append(instance)
        if not filter_list is None:
            if ACTIVE_FILTER not in filter_list:
                if instance.is_active:
                    continue
            if filter_list is not None:
                if HAS_VIOLATORS_FILTER in filter_list:
                    if not instance.find_violating_vehicles():
                        if not instance.find_violating_sims():
                            if not instance._late_violators:
                                continue
            entry = {'is_active':str(instance.is_active), 
             'max_los':str(instance._max_line_of_sight_radius), 
             'has_shooed':str(instance.has_shooed), 
             'privacy_violators':str(instance.privacy_violators), 
             'privacy_discouragement_cost':str(instance.privacy_discouragement_cost), 
             'privacy_interaction':str(instance._interaction), 
             'central_object':str(instance.central_object), 
             'min_room_area_for_discouragement':str(instance._min_room_area_for_discouragement or instance._MIN_ROOM_AREA_FOR_DISCOURAGEMENT), 
             'shoo_cons':str(instance._shoo_constraint_radius or instance._SHOO_CONSTRAINT_RADIUS), 
             'affordances':{'embarrassed_affordance':str(instance._embarrassed_affordance or instance._EMBARRASSED_AFFORDANCE), 
              'post_route_affordance':str(instance._post_route_affordance)}, 
             'allowed':{'allowed_sims':gsi_handlers.gsi_utils.format_object_list_names(instance._allowed_sims) if instance._allowed_sims else 'None', 
              'disallowed_sims':gsi_handlers.gsi_utils.format_object_list_names(instance._disallowed_sims) if instance._disallowed_sims else 'None', 
              'exempt_sims':gsi_handlers.gsi_utils.format_object_list_names(instance._exempt_sims) if instance._exempt_sims else 'None'}, 
             'privacy_constraints':[]}
            populate_violators(entry, instance, active_instances)
            for constraint in instance._privacy_constraints:
                constraint_type = next((constraint_type for constraint_type, value in vars(FootprintType).items() if value == constraint.footprint_type))
                entry['privacy_constraints'].append({'cost':str(constraint.cost),  'enabled':str(constraint.enabled), 
                 'footprint_id':str(constraint.footprint_id), 
                 'footprint_type':str(constraint_type), 
                 'polygon':str(constraint.polygon)})

            privacy_management_data.append(entry)

    return privacy_management_data


def populate_violators--- This code section failed: ---

 L. 107         0  LOAD_FAST                'instance'
                2  LOAD_METHOD              find_violating_sims
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  POP_JUMP_IF_FALSE    24  'to 24'
                8  LOAD_GLOBAL              gsi_handlers
               10  LOAD_ATTR                gsi_utils
               12  LOAD_METHOD              format_object_list_names
               14  LOAD_FAST                'instance'
               16  LOAD_METHOD              find_violating_sims
               18  CALL_METHOD_0         0  '0 positional arguments'
               20  CALL_METHOD_1         1  '1 positional argument'
               22  JUMP_FORWARD         26  'to 26'
             24_0  COME_FROM             6  '6'
               24  LOAD_GLOBAL              NO_VIOLATORS_STR
             26_0  COME_FROM            22  '22'
               26  LOAD_FAST                'entry'
               28  LOAD_STR                 'sim_violators'
               30  STORE_SUBSCR     

 L. 108        32  LOAD_FAST                'instance'
               34  LOAD_ATTR                _late_violators
               36  POP_JUMP_IF_FALSE    52  'to 52'
               38  LOAD_GLOBAL              gsi_handlers
               40  LOAD_ATTR                gsi_utils
               42  LOAD_METHOD              format_object_list_names
               44  LOAD_FAST                'instance'
               46  LOAD_ATTR                _late_violators
               48  CALL_METHOD_1         1  '1 positional argument'
               50  JUMP_FORWARD         54  'to 54'
             52_0  COME_FROM            36  '36'
               52  LOAD_GLOBAL              NO_VIOLATORS_STR
             54_0  COME_FROM            50  '50'
               54  LOAD_FAST                'entry'
               56  LOAD_STR                 'late_violators'
               58  STORE_SUBSCR     

 L. 109        60  LOAD_FAST                'instance'
               62  LOAD_METHOD              find_violating_vehicles
               64  CALL_METHOD_0         0  '0 positional arguments'
               66  POP_JUMP_IF_FALSE    84  'to 84'
               68  LOAD_GLOBAL              gsi_handlers
               70  LOAD_ATTR                gsi_utils
               72  LOAD_METHOD              format_object_list_names
               74  LOAD_FAST                'instance'
               76  LOAD_METHOD              find_violating_vehicles
               78  CALL_METHOD_0         0  '0 positional arguments'
               80  CALL_METHOD_1         1  '1 positional argument'
               82  JUMP_FORWARD         86  'to 86'
             84_0  COME_FROM            66  '66'
               84  LOAD_GLOBAL              NO_VIOLATORS_STR
             86_0  COME_FROM            82  '82'
               86  LOAD_FAST                'entry'
               88  LOAD_STR                 'vehicle_violators'
               90  STORE_SUBSCR     

 L. 111        92  SETUP_LOOP          194  'to 194'
               94  LOAD_GLOBAL              itertools
               96  LOAD_METHOD              chain
               98  LOAD_FAST                'instance'
              100  LOAD_METHOD              find_violating_sims
              102  CALL_METHOD_0         0  '0 positional arguments'
              104  LOAD_FAST                'instance'
              106  LOAD_METHOD              find_violating_vehicles
              108  CALL_METHOD_0         0  '0 positional arguments'
              110  LOAD_FAST                'instance'
              112  LOAD_ATTR                _late_violators
              114  CALL_METHOD_3         3  '3 positional arguments'
              116  GET_ITER         
              118  FOR_ITER            192  'to 192'
              120  STORE_FAST               'violator'

 L. 112       122  LOAD_GLOBAL              privacy_instance_to_violators
              124  POP_JUMP_IF_FALSE   170  'to 170'
              126  LOAD_FAST                'instance'
              128  LOAD_GLOBAL              privacy_instance_to_violators
              130  COMPARE_OP               in
              132  POP_JUMP_IF_FALSE   170  'to 170'

 L. 113       134  LOAD_GLOBAL              str
              136  LOAD_FAST                'violator'
              138  CALL_FUNCTION_1       1  '1 positional argument'
              140  LOAD_GLOBAL              privacy_instance_to_violators
              142  LOAD_FAST                'instance'
              144  BINARY_SUBSCR    
              146  COMPARE_OP               not-in
              148  POP_JUMP_IF_FALSE   190  'to 190'

 L. 114       150  LOAD_GLOBAL              privacy_instance_to_violators
              152  LOAD_FAST                'instance'
              154  BINARY_SUBSCR    
              156  LOAD_METHOD              append
              158  LOAD_GLOBAL              str
              160  LOAD_FAST                'violator'
              162  CALL_FUNCTION_1       1  '1 positional argument'
              164  CALL_METHOD_1         1  '1 positional argument'
              166  POP_TOP          
              168  JUMP_BACK           118  'to 118'
            170_0  COME_FROM           132  '132'
            170_1  COME_FROM           124  '124'

 L. 116       170  LOAD_GLOBAL              privacy_instance_to_violators
              172  LOAD_METHOD              update
              174  LOAD_FAST                'instance'
              176  LOAD_GLOBAL              str
              178  LOAD_FAST                'violator'
              180  CALL_FUNCTION_1       1  '1 positional argument'
              182  BUILD_LIST_1          1 
              184  BUILD_MAP_1           1 
              186  CALL_METHOD_1         1  '1 positional argument'
              188  POP_TOP          
            190_0  COME_FROM           148  '148'
              190  JUMP_BACK           118  'to 118'
              192  POP_BLOCK        
            194_0  COME_FROM_LOOP       92  '92'

 L. 118       194  SETUP_LOOP          252  'to 252'
              196  LOAD_GLOBAL              privacy_instance_to_violators
              198  LOAD_METHOD              items
              200  CALL_METHOD_0         0  '0 positional arguments'
              202  GET_ITER         
            204_0  COME_FROM           218  '218'
              204  FOR_ITER            242  'to 242'
              206  UNPACK_SEQUENCE_2     2 
              208  STORE_FAST               'key'
              210  STORE_FAST               'value'

 L. 119       212  LOAD_FAST                'key'
              214  LOAD_FAST                'instance'
              216  COMPARE_OP               is
              218  POP_JUMP_IF_FALSE   204  'to 204'

 L. 120       220  LOAD_LISTCOMP            '<code_object <listcomp>>'
              222  LOAD_STR                 'populate_violators.<locals>.<listcomp>'
              224  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              226  LOAD_FAST                'value'
              228  GET_ITER         
              230  CALL_FUNCTION_1       1  '1 positional argument'
              232  LOAD_FAST                'entry'
              234  LOAD_STR                 'all_past_violators'
              236  STORE_SUBSCR     

 L. 121       238  BREAK_LOOP       
              240  JUMP_BACK           204  'to 204'
              242  POP_BLOCK        

 L. 123       244  LOAD_GLOBAL              NO_VIOLATORS_STR
              246  LOAD_FAST                'entry'
              248  LOAD_STR                 'all_past_violators'
              250  STORE_SUBSCR     
            252_0  COME_FROM_LOOP      194  '194'

 L. 125       252  LOAD_CLOSURE             'active_instances'
              254  BUILD_TUPLE_1         1 
              256  LOAD_DICTCOMP            '<code_object <dictcomp>>'
              258  LOAD_STR                 'populate_violators.<locals>.<dictcomp>'
              260  MAKE_FUNCTION_8          'closure'
              262  LOAD_GLOBAL              privacy_instance_to_violators
              264  LOAD_METHOD              items
              266  CALL_METHOD_0         0  '0 positional arguments'
              268  GET_ITER         
              270  CALL_FUNCTION_1       1  '1 positional argument'
              272  STORE_GLOBAL             privacy_instance_to_violators

Parse error at or near `LOAD_DICTCOMP' instruction at offset 256


# global privacy_instance_to_violators ## Warning: Unused global