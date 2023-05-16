# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\bucks\bucks_handlers.py
# Compiled at: 2020-06-04 21:30:23
# Size of source mod 2**32: 6660 bytes
from bucks.bucks_enums import BucksType, BucksTrackerType
from bucks.bucks_utils import BucksUtils
from gsi_handlers.gameplay_archiver import GameplayArchiver
from gsi_handlers.gsi_utils import parse_filter_to_list
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
import services, sims4.log
logger = sims4.log.Logger('GSI/Bucks')
bucks_perks = GsiGridSchema(label='Bucks Perks', sim_specific=True)
bucks_perks.add_field('sim_id', label='simID', hidden=True)
bucks_perks.add_field('name', label='Name', type=(GsiFieldVisualizers.STRING))
bucks_perks.add_field('bucks_type', label='bucksType', type=(GsiFieldVisualizers.STRING))
bucks_perks.add_field('bucks_type_value', label='bucksTypeValue', type=(GsiFieldVisualizers.STRING), hidden=True)
bucks_perks.add_field('bucks_tracker_name', label='Bucks Tracker Name', type=(GsiFieldVisualizers.STRING))
bucks_perks.add_field('is_unlocked', label='isUnlocked', type=(GsiFieldVisualizers.STRING))
for bucks_type in BucksType:
    bucks_perks.add_filter(str(bucks_type))

bucks_perks.add_filter('Unlocked Only')
with bucks_perks.add_view_cheat('bucks.unlock_perk', label='Unlock Perk', dbl_click=True, refresh_view=False) as (cheat):
    cheat.add_token_param('name')
    cheat.add_static_param(True)
    cheat.add_token_param('bucks_type_value')
    cheat.add_token_param('sim_id')
bucks = GsiGridSchema(label='Bucks', sim_specific=True)
bucks.add_field('bucks_type', label='bucksType', type=(GsiFieldVisualizers.STRING))
bucks.add_field('bucks_tracker_type', label='Bucks Tracker Type', type=(GsiFieldVisualizers.STRING))
bucks.add_field('bucks_amount', label='bucksAmount', type=(GsiFieldVisualizers.INT))
bucksLog = GsiGridSchema(label='Bucks Log', sim_specific=True)
bucksLog.add_field('sim_id', label='simID', type=(GsiFieldVisualizers.INT), hidden=True)
bucksLog.add_field('bucks_type', label='bucksType', type=(GsiFieldVisualizers.STRING))
bucksLog.add_field('bucks_tracker_type', label='bucksTrackerType', type=(GsiFieldVisualizers.STRING))
bucksLog.add_field('bucks_start_amount', label='bucksStartAmount', type=(GsiFieldVisualizers.INT))
bucksLog.add_field('bucks_change_amount', label='bucksChange', type=(GsiFieldVisualizers.INT))
bucksLog.add_field('bucks_final_amount', label='bucksFinalAmount', type=(GsiFieldVisualizers.INT))

@GsiHandler('bucks_perks', bucks_perks)
def generate_bucks_perks_view(sim_id: int=None, filter=None):
    filter_list = parse_filter_to_list(filter)
    bucks_perks_data = []
    perks_instance_manager = services.get_instance_manager(sims4.resources.Types.BUCKS_PERK)
    previous_bucks_type = None
    for perk in perks_instance_manager.types.values():
        if perk.associated_bucks_type != previous_bucks_type:
            perk_specific_bucks_tracker = BucksUtils.get_tracker_for_bucks_type(perk.associated_bucks_type, sim_id)
            previous_bucks_type = perk.associated_bucks_type
        if filter_list is not None:
            if 'Unlocked Only' in filter_list and not perk_specific_bucks_tracker is None:
                if not perk_specific_bucks_tracker.is_perk_unlocked(perk):
                    continue
                if len(filter_list) > 1:
                    if str(perk.associated_bucks_type) not in filter_list:
                        continue
                    else:
                        if str(perk.associated_bucks_type) not in filter_list:
                            continue
            bucks_perks_data.append({'sim_id':str(sim_id), 
             'name':perk.__name__, 
             'bucks_type':str(perk.associated_bucks_type), 
             'bucks_type_value':int(perk.associated_bucks_type), 
             'bucks_tracker_name':str(perk_specific_bucks_tracker), 
             'is_unlocked':perk_specific_bucks_tracker.is_perk_unlocked(perk) if perk_specific_bucks_tracker is not None else False})

    return bucks_perks_data


@GsiHandler('bucks', bucks)
def generate_bucks_view(sim_id: int=None):
    bucks_data = []
    for bucks in BucksType:
        specific_bucks_tracker = BucksUtils.get_tracker_for_bucks_type(bucks, sim_id)
        bucks_amount = None
        if specific_bucks_tracker is not None:
            bucks_amount = specific_bucks_tracker.get_bucks_amount_for_type(bucks)
        bucks_tracker_type = BucksUtils.BUCK_TYPE_TO_TRACKER_MAP.get(bucks)
        if bucks_tracker_type == BucksTrackerType.HOUSEHOLD or bucks_tracker_type == BucksTrackerType.SIM:
            bucks_data.append({'bucks_type':str(bucks), 
             'bucks_tracker_type':str(bucks_tracker_type), 
             'bucks_amount':bucks_amount})

    return bucks_data


archiver = GameplayArchiver('bucks_log', bucksLog)

def add_bucks_data--- This code section failed: ---

 L. 115         0  LOAD_FAST                'bucks_final_amount'
                2  LOAD_FAST                'bucks_change_amount'
                4  BINARY_SUBTRACT  
                6  STORE_FAST               'bucks_start_amount'

 L. 116         8  LOAD_GLOBAL              BucksUtils
               10  LOAD_ATTR                BUCK_TYPE_TO_TRACKER_MAP
               12  LOAD_METHOD              get
               14  LOAD_FAST                'bucks_type'
               16  CALL_METHOD_1         1  '1 positional argument'
               18  STORE_FAST               'bucks_tracker_type'

 L. 117        20  LOAD_FAST                'bucks_tracker_type'
               22  LOAD_GLOBAL              BucksTrackerType
               24  LOAD_ATTR                HOUSEHOLD
               26  COMPARE_OP               ==
               28  POP_JUMP_IF_FALSE    64  'to 64'

 L. 118        30  SETUP_LOOP           92  'to 92'
               32  LOAD_FAST                'bucks_tracker_owner'
               34  GET_ITER         
               36  FOR_ITER             60  'to 60'
               38  STORE_FAST               'sim'

 L. 119        40  LOAD_GLOBAL              _assign_bucks_data
               42  LOAD_FAST                'sim'
               44  LOAD_FAST                'bucks_type'
               46  LOAD_FAST                'bucks_tracker_type'
               48  LOAD_FAST                'bucks_start_amount'
               50  LOAD_FAST                'bucks_change_amount'

 L. 120        52  LOAD_FAST                'bucks_final_amount'
               54  CALL_FUNCTION_6       6  '6 positional arguments'
               56  POP_TOP          
               58  JUMP_BACK            36  'to 36'
               60  POP_BLOCK        
               62  JUMP_FORWARD         92  'to 92'
             64_0  COME_FROM            28  '28'

 L. 122        64  LOAD_FAST                'bucks_tracker_type'
               66  LOAD_GLOBAL              BucksTrackerType
               68  LOAD_ATTR                SIM
               70  COMPARE_OP               ==
               72  POP_JUMP_IF_FALSE    92  'to 92'

 L. 123        74  LOAD_GLOBAL              _assign_bucks_data
               76  LOAD_FAST                'bucks_tracker_owner'
               78  LOAD_FAST                'bucks_type'
               80  LOAD_FAST                'bucks_tracker_type'
               82  LOAD_FAST                'bucks_start_amount'
               84  LOAD_FAST                'bucks_change_amount'

 L. 124        86  LOAD_FAST                'bucks_final_amount'
               88  CALL_FUNCTION_6       6  '6 positional arguments'
               90  POP_TOP          
             92_0  COME_FROM            72  '72'
             92_1  COME_FROM            62  '62'
             92_2  COME_FROM_LOOP       30  '30'

Parse error at or near `COME_FROM' instruction at offset 92_1


def _assign_bucks_data(sim, bucks_type, bucks_tracker_type, bucks_start_amount, bucks_change_amount, bucks_final_amount):
    entry = {}
    entry['sim_id'] = sim.id
    entry['bucks_type'] = str(bucks_type)
    entry['bucks_tracker_type'] = str(bucks_tracker_type)
    entry['bucks_start_amount'] = bucks_start_amount
    entry['bucks_change_amount'] = bucks_change_amount
    entry['bucks_final_amount'] = bucks_final_amount
    archiver.archive(data=entry, object_id=(sim.id))