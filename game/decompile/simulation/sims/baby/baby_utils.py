# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\baby\baby_utils.py
# Compiled at: 2016-10-06 15:13:48
# Size of source mod 2**32: 6997 bytes
from build_buy import find_objects_in_household_inventory, remove_object_from_household_inventory, object_exists_in_household_inventory
from objects import HiddenReasonFlag
from objects.object_enums import ResetReason
from objects.system import create_object
from sims.baby.baby_tuning import BabyTuning
import services, sims4.log
logger = sims4.log.Logger('Baby')

def assign_bassinet_for_baby(sim_info):
    object_manager = services.object_manager()
    for bassinet in (object_manager.get_objects_of_type_gen)(*BabyTuning.BABY_BASSINET_DEFINITION_MAP.values()):
        if not bassinet.transient:
            set_baby_sim_info_with_switch_id(bassinet, sim_info)
            bassinet.destroy(source=sim_info, cause='Assigned bassinet for baby.')
            return True

    return False


def assign_to_bassinet(sim_info):
    if object_exists_in_household_inventory(sim_info.id, sim_info.household_id):
        return
    bassinet = services.object_manager().get(sim_info.sim_id)
    if bassinet is None:
        if assign_bassinet_for_baby(sim_info):
            return
        create_and_place_baby(sim_info)


def create_and_place_baby(sim_info, position=None, routing_surface=None, **kwargs):
    bassinet = create_object((BabyTuning.get_default_definition(sim_info)), obj_id=(sim_info.sim_id))
    (bassinet.set_sim_info)(sim_info, **kwargs)
    bassinet.place_in_good_location(position=position, routing_surface=routing_surface)
    sim_info.suppress_aging()


def remove_stale_babies--- This code section failed: ---

 L.  80         0  LOAD_FAST                'household'
                2  LOAD_GLOBAL              services
                4  LOAD_METHOD              active_household
                6  CALL_METHOD_0         0  '0 positional arguments'
                8  COMPARE_OP               is
               10  POP_JUMP_IF_FALSE    98  'to 98'

 L.  81        12  SETUP_LOOP           98  'to 98'
               14  LOAD_GLOBAL              find_objects_in_household_inventory
               16  LOAD_GLOBAL              tuple
               18  LOAD_GENEXPR             '<code_object <genexpr>>'
               20  LOAD_STR                 'remove_stale_babies.<locals>.<genexpr>'
               22  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
               24  LOAD_GLOBAL              BabyTuning
               26  LOAD_ATTR                BABY_BASSINET_DEFINITION_MAP
               28  GET_ITER         
               30  CALL_FUNCTION_1       1  '1 positional argument'
               32  CALL_FUNCTION_1       1  '1 positional argument'
               34  LOAD_FAST                'household'
               36  LOAD_ATTR                id
               38  CALL_FUNCTION_2       2  '2 positional arguments'
               40  GET_ITER         
             42_0  COME_FROM            82  '82'
               42  FOR_ITER             96  'to 96'
               44  STORE_FAST               'obj_id'

 L.  82        46  LOAD_GLOBAL              services
               48  LOAD_METHOD              sim_info_manager
               50  CALL_METHOD_0         0  '0 positional arguments'
               52  LOAD_METHOD              get
               54  LOAD_FAST                'obj_id'
               56  CALL_METHOD_1         1  '1 positional argument'
               58  STORE_FAST               'sim_info'

 L.  83        60  LOAD_FAST                'sim_info'
               62  LOAD_CONST               None
               64  COMPARE_OP               is
               66  POP_JUMP_IF_TRUE     84  'to 84'
               68  LOAD_FAST                'sim_info'
               70  LOAD_ATTR                household
               72  LOAD_FAST                'household'
               74  COMPARE_OP               is-not
               76  POP_JUMP_IF_TRUE     84  'to 84'
               78  LOAD_FAST                'sim_info'
               80  LOAD_ATTR                is_baby
               82  POP_JUMP_IF_TRUE     42  'to 42'
             84_0  COME_FROM            76  '76'
             84_1  COME_FROM            66  '66'

 L.  84        84  LOAD_GLOBAL              remove_object_from_household_inventory
               86  LOAD_FAST                'obj_id'
               88  LOAD_FAST                'household'
               90  CALL_FUNCTION_2       2  '2 positional arguments'
               92  POP_TOP          
               94  JUMP_BACK            42  'to 42'
               96  POP_BLOCK        
             98_0  COME_FROM_LOOP       12  '12'
             98_1  COME_FROM            10  '10'

Parse error at or near `COME_FROM' instruction at offset 84_1


def replace_bassinet(sim_info, bassinet=None, safe_destroy=False):
    bassinet = bassinet if bassinet is not None else services.object_manager().get(sim_info.sim_id)
    if bassinet is not None:
        empty_bassinet = create_object(BabyTuning.get_corresponding_definition(bassinet.definition))
        empty_bassinet.location = bassinet.location
        if safe_destroy:
            bassinet.make_transient()
        else:
            bassinet.reset(ResetReason.RESET_EXPECTED, None, 'Replacing Bassinet with child')
            bassinet.destroy(source=sim_info, cause='Replaced bassinet with empty version')
        return empty_bassinet


def run_baby_spawn_behavior(sim_info):
    sim_info.set_zone_on_spawn()
    if sim_info.is_baby:
        assign_to_bassinet(sim_info)
    else:
        replace_bassinet(sim_info)
    return True


def set_baby_sim_info_with_switch_id(bassinet, sim_info, **kwargs):
    if bassinet.id != sim_info.sim_id:
        new_bassinet = None
        try:
            try:
                bassinet_definition = BabyTuning.get_corresponding_definition(bassinet.definition)
                new_bassinet = create_object(bassinet_definition, obj_id=(sim_info.sim_id))
                (new_bassinet.set_sim_info)(sim_info, **kwargs)
                new_bassinet.location = bassinet.location
            except:
                logger.exception('{} fail to set sim_info {}', bassinet, sim_info)
                if new_bassinet is not None:
                    new_bassinet.destroy(source=sim_info, cause='Failed to set sim_info on bassinet')

        finally:
            sim_info.suppress_aging()
            bassinet.hide(HiddenReasonFlag.REPLACEMENT)

        return new_bassinet