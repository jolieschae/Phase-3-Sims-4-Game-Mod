# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\inventory_handlers.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 4556 bytes
import itertools, gsi_handlers, services
from gsi_handlers.gsi_utils import parse_filter_to_list
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
inventory_schema = GsiGridSchema(label='Inventories')
inventory_schema.add_field('objId', label='Object Id', width=1, unique_field=True, hidden=True)
inventory_schema.add_field('inventoryOwner', label='Inventory Owner', width=3)
inventory_schema.add_field('instancedCount', label='Count (Instanced)', width=2)
inventory_schema.add_field('shelvedCount', label='Count (Shelved)', width=2)
inventory_schema.add_filter('active_household_inventories')
inventory_schema.add_filter('npc_sim_inventories')
inventory_schema.add_filter('on_lot_object_inventories')
inventory_schema.add_filter('off_lot_object_inventories')
with inventory_schema.add_view_cheat('objects.focus_camera_on_object', label='Focus On Selected Object') as (cheat):
    cheat.add_token_param('objId')
with inventory_schema.add_has_many('instanced_contents', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('stackId', label='Stack ID')
    sub_schema.add_field('definition', label='Definition', width=3)
    sub_schema.add_field('objectCount', label='Object Count')
    sub_schema.add_field('isHidden', label='Is Hidden')
with inventory_schema.add_has_many('shelved_contents', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('definition', label='Definition', width=3)
    sub_schema.add_field('objectCount', label='Object Count')

@GsiHandler('inventories', inventory_schema)
def generate_inventories_data--- This code section failed: ---

 L.  39         0  LOAD_GLOBAL              parse_filter_to_list
                2  LOAD_FAST                'filter'
                4  CALL_FUNCTION_1       1  '1 positional argument'
                6  STORE_FAST               'filter_list'

 L.  40         8  LOAD_GLOBAL              services
               10  LOAD_METHOD              get_zone
               12  LOAD_FAST                'zone_id'
               14  CALL_METHOD_1         1  '1 positional argument'
               16  STORE_FAST               'zone'

 L.  41        18  BUILD_LIST_0          0 
               20  STORE_FAST               'all_object_data'

 L.  43        22  LOAD_GLOBAL              services
               24  LOAD_METHOD              active_household
               26  CALL_METHOD_0         0  '0 positional arguments'
               28  STORE_DEREF              'active_household'

 L.  44        30  LOAD_GLOBAL              services
               32  LOAD_METHOD              definition_manager
               34  CALL_METHOD_0         0  '0 positional arguments'
               36  STORE_FAST               'def_manager'

 L.  46        38  LOAD_CLOSURE             'active_household'
               40  BUILD_TUPLE_1         1 
               42  LOAD_CODE                <code_object _active_household_sim>
               44  LOAD_STR                 'generate_inventories_data.<locals>._active_household_sim'
               46  MAKE_FUNCTION_8          'closure'
               48  STORE_FAST               '_active_household_sim'

 L.  51        50  LOAD_CLOSURE             'active_household'
               52  BUILD_TUPLE_1         1 
               54  LOAD_CODE                <code_object _npc_sim>
               56  LOAD_STR                 'generate_inventories_data.<locals>._npc_sim'
               58  MAKE_FUNCTION_8          'closure'
               60  STORE_FAST               '_npc_sim'

 L.  56        62  LOAD_FAST                'zone'
               64  LOAD_ATTR                object_manager
               66  LOAD_CONST               None
               68  COMPARE_OP               is
               70  POP_JUMP_IF_FALSE    76  'to 76'

 L.  57        72  LOAD_FAST                'all_object_data'
               74  RETURN_VALUE     
             76_0  COME_FROM            70  '70'

 L.  58     76_78  SETUP_LOOP          462  'to 462'
               80  LOAD_GLOBAL              list
               82  LOAD_GLOBAL              itertools
               84  LOAD_METHOD              chain
               86  LOAD_FAST                'zone'
               88  LOAD_ATTR                object_manager
               90  LOAD_ATTR                objects

 L.  59        92  LOAD_FAST                'zone'
               94  LOAD_ATTR                inventory_manager
               96  LOAD_ATTR                objects
               98  CALL_METHOD_2         2  '2 positional arguments'
              100  CALL_FUNCTION_1       1  '1 positional argument'
              102  GET_ITER         
            104_0  COME_FROM           232  '232'
            104_1  COME_FROM           228  '228'
            104_2  COME_FROM           224  '224'
          104_106  FOR_ITER            460  'to 460'
              108  STORE_FAST               'cur_obj'

 L.  60       110  LOAD_FAST                'cur_obj'
              112  LOAD_ATTR                inventory_component
              114  STORE_FAST               'inventory'

 L.  61       116  LOAD_FAST                'inventory'
              118  LOAD_CONST               None
              120  COMPARE_OP               is
              122  POP_JUMP_IF_FALSE   126  'to 126'

 L.  62       124  CONTINUE            104  'to 104'
            126_0  COME_FROM           122  '122'

 L.  64       126  LOAD_GLOBAL              hasattr
              128  LOAD_FAST                'cur_obj'
              130  LOAD_STR                 'is_on_active_lot'
              132  CALL_FUNCTION_2       2  '2 positional arguments'
              134  POP_JUMP_IF_FALSE   144  'to 144'
              136  LOAD_FAST                'cur_obj'
              138  LOAD_METHOD              is_on_active_lot
              140  CALL_METHOD_0         0  '0 positional arguments'
              142  JUMP_FORWARD        146  'to 146'
            144_0  COME_FROM           134  '134'
              144  LOAD_CONST               False
            146_0  COME_FROM           142  '142'
              146  STORE_FAST               'on_active_lot'

 L.  65       148  LOAD_FAST                'cur_obj'
              150  LOAD_ATTR                is_sim
              152  STORE_FAST               'is_sim'

 L.  67       154  LOAD_FAST                'filter_list'
              156  LOAD_CONST               None
              158  COMPARE_OP               is
              160  POP_JUMP_IF_TRUE    234  'to 234'

 L.  68       162  LOAD_STR                 'active_household_inventories'
              164  LOAD_FAST                'filter_list'
              166  COMPARE_OP               in
              168  POP_JUMP_IF_FALSE   182  'to 182'
              170  LOAD_FAST                'is_sim'
              172  POP_JUMP_IF_FALSE   182  'to 182'
              174  LOAD_FAST                '_active_household_sim'
              176  LOAD_FAST                'cur_obj'
              178  CALL_FUNCTION_1       1  '1 positional argument'
              180  POP_JUMP_IF_TRUE    234  'to 234'
            182_0  COME_FROM           172  '172'
            182_1  COME_FROM           168  '168'

 L.  69       182  LOAD_STR                 'npc_sim_inventories'
              184  LOAD_FAST                'filter_list'
              186  COMPARE_OP               in
              188  POP_JUMP_IF_FALSE   202  'to 202'
              190  LOAD_FAST                'is_sim'
              192  POP_JUMP_IF_FALSE   202  'to 202'
              194  LOAD_FAST                '_npc_sim'
              196  LOAD_FAST                'cur_obj'
              198  CALL_FUNCTION_1       1  '1 positional argument'
              200  POP_JUMP_IF_TRUE    234  'to 234'
            202_0  COME_FROM           192  '192'
            202_1  COME_FROM           188  '188'

 L.  70       202  LOAD_STR                 'on_lot_object_inventories'
              204  LOAD_FAST                'filter_list'
              206  COMPARE_OP               in
              208  POP_JUMP_IF_FALSE   218  'to 218'
              210  LOAD_FAST                'is_sim'
              212  POP_JUMP_IF_TRUE    218  'to 218'
              214  LOAD_FAST                'on_active_lot'
              216  POP_JUMP_IF_TRUE    234  'to 234'
            218_0  COME_FROM           212  '212'
            218_1  COME_FROM           208  '208'

 L.  71       218  LOAD_STR                 'off_lot_object_inventories'
              220  LOAD_FAST                'filter_list'
              222  COMPARE_OP               in
              224  POP_JUMP_IF_FALSE   104  'to 104'
              226  LOAD_FAST                'is_sim'
              228  POP_JUMP_IF_TRUE    104  'to 104'
              230  LOAD_FAST                'on_active_lot'
              232  POP_JUMP_IF_TRUE    104  'to 104'
            234_0  COME_FROM           216  '216'
            234_1  COME_FROM           200  '200'
            234_2  COME_FROM           180  '180'
            234_3  COME_FROM           160  '160'

 L.  74       234  LOAD_GLOBAL              hex
              236  LOAD_FAST                'cur_obj'
              238  LOAD_ATTR                id
              240  CALL_FUNCTION_1       1  '1 positional argument'

 L.  75       242  LOAD_GLOBAL              gsi_handlers
              244  LOAD_ATTR                gsi_utils
              246  LOAD_METHOD              format_object_name
              248  LOAD_FAST                'cur_obj'
              250  CALL_METHOD_1         1  '1 positional argument'

 L.  76       252  LOAD_GLOBAL              str
              254  LOAD_GLOBAL              len
              256  LOAD_FAST                'inventory'
              258  CALL_FUNCTION_1       1  '1 positional argument'
              260  CALL_FUNCTION_1       1  '1 positional argument'
              262  LOAD_CONST               ('objId', 'inventoryOwner', 'instancedCount')
              264  BUILD_CONST_KEY_MAP_3     3 
              266  STORE_FAST               'obj_entry'

 L.  78       268  LOAD_FAST                'inventory'
          270_272  POP_JUMP_IF_FALSE   356  'to 356'

 L.  79       274  BUILD_LIST_0          0 
              276  STORE_FAST               'instanced_contents'

 L.  80       278  SETUP_LOOP          348  'to 348'
              280  LOAD_FAST                'inventory'
              282  GET_ITER         
              284  FOR_ITER            346  'to 346'
              286  STORE_FAST               'item'

 L.  81       288  LOAD_FAST                'item'
              290  LOAD_ATTR                inventoryitem_component
              292  STORE_FAST               'item_component'

 L.  82       294  LOAD_FAST                'instanced_contents'
              296  LOAD_METHOD              append

 L.  83       298  LOAD_GLOBAL              str
              300  LOAD_FAST                'item_component'
              302  LOAD_METHOD              get_stack_id
              304  CALL_METHOD_0         0  '0 positional arguments'
              306  CALL_FUNCTION_1       1  '1 positional argument'

 L.  84       308  LOAD_GLOBAL              str
              310  LOAD_FAST                'item'
              312  LOAD_ATTR                definition
              314  CALL_FUNCTION_1       1  '1 positional argument'

 L.  85       316  LOAD_GLOBAL              str
              318  LOAD_FAST                'item_component'
              320  LOAD_METHOD              stack_count
              322  CALL_METHOD_0         0  '0 positional arguments'
              324  CALL_FUNCTION_1       1  '1 positional argument'

 L.  86       326  LOAD_GLOBAL              str
              328  LOAD_FAST                'item_component'
              330  LOAD_ATTR                is_hidden
              332  CALL_FUNCTION_1       1  '1 positional argument'
              334  LOAD_CONST               ('stackId', 'definition', 'objectCount', 'isHidden')
              336  BUILD_CONST_KEY_MAP_4     4 
              338  CALL_METHOD_1         1  '1 positional argument'
              340  POP_TOP          
          342_344  JUMP_BACK           284  'to 284'
              346  POP_BLOCK        
            348_0  COME_FROM_LOOP      278  '278'

 L.  88       348  LOAD_FAST                'instanced_contents'
              350  LOAD_FAST                'obj_entry'
              352  LOAD_STR                 'instanced_contents'
              354  STORE_SUBSCR     
            356_0  COME_FROM           270  '270'

 L.  90       356  LOAD_FAST                'is_sim'
          358_360  POP_JUMP_IF_FALSE   448  'to 448'

 L.  91       362  LOAD_GLOBAL              str
              364  LOAD_FAST                'inventory'
              366  LOAD_METHOD              get_shelved_object_count
              368  CALL_METHOD_0         0  '0 positional arguments'
              370  CALL_FUNCTION_1       1  '1 positional argument'
              372  LOAD_FAST                'obj_entry'
              374  LOAD_STR                 'shelvedCount'
              376  STORE_SUBSCR     

 L.  92       378  BUILD_LIST_0          0 
              380  STORE_FAST               'shelved_contents'

 L.  93       382  SETUP_LOOP          440  'to 440'
              384  LOAD_FAST                'inventory'
              386  LOAD_METHOD              get_shelved_object_data
              388  CALL_METHOD_0         0  '0 positional arguments'
              390  GET_ITER         
              392  FOR_ITER            438  'to 438'
              394  STORE_FAST               'shelved'

 L.  94       396  LOAD_FAST                'shelved_contents'
              398  LOAD_METHOD              append

 L.  95       400  LOAD_GLOBAL              str
              402  LOAD_FAST                'def_manager'
              404  LOAD_METHOD              get
              406  LOAD_FAST                'shelved'
              408  LOAD_STR                 'guid'
              410  BINARY_SUBSCR    
              412  CALL_METHOD_1         1  '1 positional argument'
              414  CALL_FUNCTION_1       1  '1 positional argument'

 L.  96       416  LOAD_GLOBAL              str
              418  LOAD_FAST                'shelved'
              420  LOAD_STR                 'objectCount'
              422  BINARY_SUBSCR    
              424  CALL_FUNCTION_1       1  '1 positional argument'
              426  LOAD_CONST               ('definition', 'objectCount')
              428  BUILD_CONST_KEY_MAP_2     2 
              430  CALL_METHOD_1         1  '1 positional argument'
              432  POP_TOP          
          434_436  JUMP_BACK           392  'to 392'
              438  POP_BLOCK        
            440_0  COME_FROM_LOOP      382  '382'

 L.  98       440  LOAD_FAST                'shelved_contents'
              442  LOAD_FAST                'obj_entry'
              444  LOAD_STR                 'shelved_contents'
              446  STORE_SUBSCR     
            448_0  COME_FROM           358  '358'

 L. 100       448  LOAD_FAST                'all_object_data'
              450  LOAD_METHOD              append
              452  LOAD_FAST                'obj_entry'
              454  CALL_METHOD_1         1  '1 positional argument'
              456  POP_TOP          
              458  JUMP_BACK           104  'to 104'
              460  POP_BLOCK        
            462_0  COME_FROM_LOOP       76  '76'

 L. 101       462  LOAD_FAST                'all_object_data'
              464  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `POP_BLOCK' instruction at offset 460