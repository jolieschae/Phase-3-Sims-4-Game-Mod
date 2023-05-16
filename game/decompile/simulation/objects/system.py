# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\system.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 21496 bytes
from objects.gallery_tuning import ContentSource
from objects.object_enums import ResetReason
from objects.persistence_groups import PersistenceGroups
from sims4.tuning.tunable import Tunable
from sims4.utils import exception_protected
import build_buy, services, sims4, sims4.log
LOG_CHANNEL = 'Objects'
logger = sims4.log.Logger(LOG_CHANNEL)
production_logger = sims4.log.ProductionLogger(LOG_CHANNEL)

class SystemTuning:
    build_buy_lockout_duration = Tunable(int, 5, description='Number of seconds an object should stay locked for after it is manipulated in Build/Buy.')


@exception_protected
def c_api_get_object_definition(obj_id, zone_id):
    obj = find_object(obj_id)
    if obj is None:
        return
    return obj.definition.id


@exception_protected
def c_api_get_object_def_state(obj_id, zone_id):
    obj = find_object(obj_id)
    if obj is None:
        return
    return obj.state_index


def c_api_get_object_attributes(obj_id, zone_id):
    obj = find_object(obj_id)
    if obj is None:
        return
    return (
     obj.definition.id, obj.state_index, obj.transform, obj.routing_surface)


def create_script_object(definition_or_id, obj_state=0, **kwargs):
    from objects.definition import Definition
    if isinstance(definition_or_id, Definition):
        definition = definition_or_id
    else:
        definition = services.definition_manager().get(definition_or_id, obj_state=obj_state)
        if definition is None:
            logger.error('Unable to create a script object for definition id: {0}', definition_or_id)
            return
    return (definition.instantiate)(obj_state=obj_state, **kwargs)


@exception_protected
def c_api_create_object(zone_id, def_id, obj_id, obj_state, loc_type, content_source=ContentSource.DEFAULT):
    return create_object(def_id, obj_id=obj_id, obj_state=obj_state, loc_type=loc_type, content_source=content_source)


@exception_protected
def c_api_set_part_owner(zone_id, part_owner_id, part_id):
    part_owner = find_object(part_owner_id)
    part = find_object(part_id)
    if part_owner is None or part is None:
        return False
    part.part_owner = part_owner
    return True


@exception_protected
def c_api_start_delaying_posture_graph_adds():
    pass


@exception_protected
def c_api_stop_delaying_posture_graph_adds():
    pass


def create_object--- This code section failed: ---

 L. 136         0  LOAD_CONST               0
                2  LOAD_CONST               ('BaseObject',)
                4  IMPORT_NAME_ATTR         objects.base_object
                6  IMPORT_FROM              BaseObject
                8  STORE_FAST               'BaseObject'
               10  POP_TOP          

 L. 137        12  LOAD_CONST               0
               14  LOAD_CONST               ('ItemLocation',)
               16  IMPORT_NAME_ATTR         objects.object_enums
               18  IMPORT_FROM              ItemLocation
               20  STORE_FAST               'ItemLocation'
               22  POP_TOP          

 L. 138        24  LOAD_CONST               False
               26  STORE_FAST               'added_to_object_manager'

 L. 139        28  LOAD_CONST               None
               30  STORE_FAST               'obj'

 L. 141        32  LOAD_FAST                'loc_type'
               34  LOAD_CONST               None
               36  COMPARE_OP               is
               38  POP_JUMP_IF_FALSE    46  'to 46'

 L. 142        40  LOAD_FAST                'ItemLocation'
               42  LOAD_ATTR                ON_LOT
               44  STORE_FAST               'loc_type'
             46_0  COME_FROM            38  '38'

 L. 144     46_48  SETUP_FINALLY       452  'to 452'

 L. 145        50  LOAD_CONST               0
               52  LOAD_CONST               ('Definition',)
               54  IMPORT_NAME_ATTR         objects.definition
               56  IMPORT_FROM              Definition
               58  STORE_FAST               'Definition'
               60  POP_TOP          

 L. 146        62  LOAD_GLOBAL              isinstance
               64  LOAD_FAST                'definition_or_id'
               66  LOAD_FAST                'Definition'
               68  CALL_FUNCTION_2       2  '2 positional arguments'
               70  POP_JUMP_IF_FALSE   102  'to 102'

 L. 147        72  LOAD_GLOBAL              build_buy
               74  LOAD_METHOD              get_vetted_object_defn_guid
               76  LOAD_FAST                'obj_id'
               78  LOAD_FAST                'definition_or_id'
               80  LOAD_ATTR                id
               82  CALL_METHOD_2         2  '2 positional arguments'
               84  STORE_FAST               'fallback_definition_id'

 L. 148        86  LOAD_FAST                'fallback_definition_id'
               88  LOAD_FAST                'definition_or_id'
               90  LOAD_ATTR                id
               92  COMPARE_OP               !=
               94  POP_JUMP_IF_FALSE   114  'to 114'

 L. 149        96  LOAD_FAST                'fallback_definition_id'
               98  STORE_FAST               'definition_or_id'
              100  JUMP_FORWARD        114  'to 114'
            102_0  COME_FROM            70  '70'

 L. 151       102  LOAD_GLOBAL              build_buy
              104  LOAD_METHOD              get_vetted_object_defn_guid
              106  LOAD_FAST                'obj_id'
              108  LOAD_FAST                'definition_or_id'
              110  CALL_METHOD_2         2  '2 positional arguments'
              112  STORE_FAST               'definition_or_id'
            114_0  COME_FROM           100  '100'
            114_1  COME_FROM            94  '94'

 L. 153       114  LOAD_FAST                'definition_or_id'
              116  LOAD_CONST               None
              118  COMPARE_OP               is
              120  POP_JUMP_IF_FALSE   126  'to 126'

 L. 156       122  LOAD_CONST               None
              124  RETURN_VALUE     
            126_0  COME_FROM           120  '120'

 L. 158       126  LOAD_GLOBAL              create_script_object
              128  LOAD_FAST                'definition_or_id'
              130  BUILD_TUPLE_1         1 
              132  LOAD_FAST                'kwargs'
              134  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
              136  STORE_FAST               'obj'

 L. 160       138  LOAD_FAST                'obj'
              140  LOAD_CONST               None
              142  COMPARE_OP               is
              144  POP_JUMP_IF_FALSE   150  'to 150'

 L. 161       146  LOAD_CONST               None
              148  RETURN_VALUE     
            150_0  COME_FROM           144  '144'

 L. 163       150  LOAD_GLOBAL              isinstance
              152  LOAD_FAST                'obj'
              154  LOAD_FAST                'BaseObject'
              156  CALL_FUNCTION_2       2  '2 positional arguments'
              158  POP_JUMP_IF_TRUE    180  'to 180'

 L. 164       160  LOAD_GLOBAL              logger
              162  LOAD_METHOD              error
              164  LOAD_STR                 'Type {0} is not a valid managed object.  It is not a subclass of BaseObject.'
              166  LOAD_GLOBAL              type
              168  LOAD_FAST                'obj'
              170  CALL_FUNCTION_1       1  '1 positional argument'
              172  CALL_METHOD_2         2  '2 positional arguments'
              174  POP_TOP          

 L. 165       176  LOAD_CONST               None
              178  RETURN_VALUE     
            180_0  COME_FROM           158  '158'

 L. 167       180  LOAD_FAST                'init'
              182  LOAD_CONST               None
              184  COMPARE_OP               is-not
              186  POP_JUMP_IF_FALSE   196  'to 196'

 L. 168       188  LOAD_FAST                'init'
              190  LOAD_FAST                'obj'
              192  CALL_FUNCTION_1       1  '1 positional argument'
              194  POP_TOP          
            196_0  COME_FROM           186  '186'

 L. 170       196  LOAD_FAST                'loc_type'
              198  LOAD_FAST                'ItemLocation'
              200  LOAD_ATTR                FROM_WORLD_FILE
              202  COMPARE_OP               ==
              204  POP_JUMP_IF_TRUE    216  'to 216'
              206  LOAD_FAST                'loc_type'
              208  LOAD_FAST                'ItemLocation'
              210  LOAD_ATTR                FROM_CONDITIONAL_LAYER
              212  COMPARE_OP               ==
              214  POP_JUMP_IF_FALSE   224  'to 224'
            216_0  COME_FROM           204  '204'

 L. 171       216  LOAD_GLOBAL              PersistenceGroups
              218  LOAD_ATTR                IN_OPEN_STREET
              220  LOAD_FAST                'obj'
              222  STORE_ATTR               persistence_group
            224_0  COME_FROM           214  '214'

 L. 173       224  LOAD_FAST                'loc_type'
              226  LOAD_CONST               None
              228  COMPARE_OP               is-not
              230  POP_JUMP_IF_FALSE   240  'to 240'
              232  LOAD_FAST                'ItemLocation'
              234  LOAD_FAST                'loc_type'
              236  CALL_FUNCTION_1       1  '1 positional argument'
              238  JUMP_FORWARD        244  'to 244'
            240_0  COME_FROM           230  '230'
              240  LOAD_FAST                'ItemLocation'
              242  LOAD_ATTR                INVALID_LOCATION
            244_0  COME_FROM           238  '238'
              244  LOAD_FAST                'obj'
              246  STORE_ATTR               item_location

 L. 174       248  LOAD_FAST                'obj_id'
              250  LOAD_FAST                'obj'
              252  STORE_ATTR               id

 L. 175       254  LOAD_FAST                'content_source'
              256  LOAD_FAST                'obj'
              258  STORE_ATTR               content_source

 L. 178       260  LOAD_FAST                'disable_object_commodity_callbacks'
          262_264  POP_JUMP_IF_TRUE    278  'to 278'
              266  LOAD_GLOBAL              services
              268  LOAD_METHOD              current_zone
              270  CALL_METHOD_0         0  '0 positional arguments'
              272  LOAD_ATTR                suppress_object_commodity_callbacks
          274_276  POP_JUMP_IF_FALSE   296  'to 296'
            278_0  COME_FROM           262  '262'

 L. 179       278  LOAD_FAST                'obj'
              280  LOAD_ATTR                is_sim
          282_284  POP_JUMP_IF_TRUE    296  'to 296'

 L. 184       286  LOAD_FAST                'obj'
              288  LOAD_METHOD              set_statistics_callback_alarm_calculation_supression
              290  LOAD_CONST               True
              292  CALL_METHOD_1         1  '1 positional argument'
              294  POP_TOP          
            296_0  COME_FROM           282  '282'
            296_1  COME_FROM           274  '274'

 L. 186       296  LOAD_FAST                'loc_type'
              298  LOAD_FAST                'ItemLocation'
              300  LOAD_ATTR                ON_LOT
              302  COMPARE_OP               ==
          304_306  POP_JUMP_IF_TRUE    356  'to 356'

 L. 187       308  LOAD_FAST                'loc_type'
              310  LOAD_FAST                'ItemLocation'
              312  LOAD_ATTR                FROM_WORLD_FILE
              314  COMPARE_OP               ==
          316_318  POP_JUMP_IF_TRUE    356  'to 356'

 L. 188       320  LOAD_FAST                'loc_type'
              322  LOAD_FAST                'ItemLocation'
              324  LOAD_ATTR                FROM_OPEN_STREET
              326  COMPARE_OP               ==
          328_330  POP_JUMP_IF_TRUE    356  'to 356'

 L. 189       332  LOAD_FAST                'loc_type'
              334  LOAD_FAST                'ItemLocation'
              336  LOAD_ATTR                HOUSEHOLD_INVENTORY
              338  COMPARE_OP               ==
          340_342  POP_JUMP_IF_TRUE    356  'to 356'

 L. 190       344  LOAD_FAST                'loc_type'
              346  LOAD_FAST                'ItemLocation'
              348  LOAD_ATTR                FROM_CONDITIONAL_LAYER
              350  COMPARE_OP               ==
          352_354  POP_JUMP_IF_FALSE   370  'to 370'
            356_0  COME_FROM           340  '340'
            356_1  COME_FROM           328  '328'
            356_2  COME_FROM           316  '316'
            356_3  COME_FROM           304  '304'

 L. 191       356  LOAD_FAST                'obj'
              358  LOAD_ATTR                object_manager_for_create
              360  LOAD_METHOD              add
              362  LOAD_FAST                'obj'
              364  CALL_METHOD_1         1  '1 positional argument'
              366  POP_TOP          
              368  JUMP_FORWARD        426  'to 426'
            370_0  COME_FROM           352  '352'

 L. 192       370  LOAD_FAST                'loc_type'
              372  LOAD_FAST                'ItemLocation'
              374  LOAD_ATTR                SIM_INVENTORY
              376  COMPARE_OP               ==
          378_380  POP_JUMP_IF_TRUE    394  'to 394'
              382  LOAD_FAST                'loc_type'
              384  LOAD_FAST                'ItemLocation'
              386  LOAD_ATTR                OBJECT_INVENTORY
              388  COMPARE_OP               ==
          390_392  POP_JUMP_IF_FALSE   412  'to 412'
            394_0  COME_FROM           378  '378'

 L. 193       394  LOAD_GLOBAL              services
              396  LOAD_METHOD              current_zone
              398  CALL_METHOD_0         0  '0 positional arguments'
              400  LOAD_ATTR                inventory_manager
              402  LOAD_METHOD              add
              404  LOAD_FAST                'obj'
              406  CALL_METHOD_1         1  '1 positional argument'
              408  POP_TOP          
              410  JUMP_FORWARD        426  'to 426'
            412_0  COME_FROM           390  '390'

 L. 195       412  LOAD_GLOBAL              logger
              414  LOAD_ATTR                error
              416  LOAD_STR                 'Unsupported loc_type passed to create_script_object.  We likely need to update this code path.'
              418  LOAD_STR                 'mduke'
              420  LOAD_CONST               ('owner',)
              422  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              424  POP_TOP          
            426_0  COME_FROM           410  '410'
            426_1  COME_FROM           368  '368'

 L. 196       426  LOAD_CONST               True
              428  STORE_FAST               'added_to_object_manager'

 L. 198       430  LOAD_FAST                'post_add'
              432  LOAD_CONST               None
              434  COMPARE_OP               is-not
          436_438  POP_JUMP_IF_FALSE   448  'to 448'

 L. 199       440  LOAD_FAST                'post_add'
              442  LOAD_FAST                'obj'
              444  CALL_FUNCTION_1       1  '1 positional argument'
              446  POP_TOP          
            448_0  COME_FROM           436  '436'

 L. 201       448  LOAD_FAST                'obj'
              450  RETURN_VALUE     
            452_0  COME_FROM_FINALLY    46  '46'

 L. 203       452  LOAD_FAST                'added_to_object_manager'
          454_456  POP_JUMP_IF_TRUE    486  'to 486'
              458  LOAD_FAST                'obj'
              460  LOAD_CONST               None
              462  COMPARE_OP               is-not
          464_466  POP_JUMP_IF_FALSE   486  'to 486'

 L. 205       468  LOAD_CONST               0
              470  LOAD_CONST               None
              472  IMPORT_NAME              _weakrefutils
              474  STORE_FAST               '_weakrefutils'

 L. 206       476  LOAD_FAST                '_weakrefutils'
              478  LOAD_METHOD              clear_weak_refs
              480  LOAD_FAST                'obj'
              482  CALL_METHOD_1         1  '1 positional argument'
              484  POP_TOP          
            486_0  COME_FROM           464  '464'
            486_1  COME_FROM           454  '454'
              486  END_FINALLY      

Parse error at or near `JUMP_FORWARD' instruction at offset 368


def _get_id_for_obj_or_id(obj_or_id):
    from objects.base_object import BaseObject
    if isinstance(obj_or_id, BaseObject):
        return obj_or_id.id
    return int(obj_or_id)


def _get_obj_for_obj_or_id(obj_or_id):
    from objects.base_object import BaseObject
    if not isinstance(obj_or_id, BaseObject):
        obj = services.object_manager().get(obj_or_id)
        if obj is None:
            logger.error('Could not find the target id {} for a RequiredTargetParam in the object manager.', obj_or_id)
        return obj
    return obj_or_id


@exception_protected
def c_api_destroy_object(zone_id, obj_or_id):
    obj = _get_obj_for_obj_or_id(obj_or_id)
    if obj is not None:
        return obj.destroy(source=obj, cause='Destruction request from C.')
    return False


@exception_protected
def c_api_reset_object(zone_id, obj_or_id):
    return reset_object(obj_or_id, expected=True, cause='Build/Buy')


def reset_object(obj_or_id, expected, cause=None):
    obj = _get_obj_for_obj_or_id(obj_or_id)
    if obj is not None:
        obj.reset(ResetReason.RESET_EXPECTED if expected else ResetReason.RESET_ON_ERROR, None, cause)
        return True
    return False


def remove_object_from_client(obj_or_id, **kwargs):
    obj = _get_obj_for_obj_or_id(obj_or_id)
    manager = obj.manager
    if obj.id in manager:
        (manager.remove_from_client)(obj, **kwargs)
        return True
    return False


def create_prop(definition_or_id, is_basic=False, **kwargs):
    from objects.prop_object import BasicPropObject, PropObject
    cls_override = BasicPropObject if is_basic else PropObject
    return create_object(definition_or_id, cls_override=cls_override, **kwargs)


def create_prop_with_footprint(definition_or_id, **kwargs):
    from objects.prop_object import PropObjectWithFootprint
    return create_object(definition_or_id, cls_override=PropObjectWithFootprint, **kwargs)


@exception_protected
def c_api_find_object(obj_id, zone_id):
    return find_object(obj_id)


def find_object(obj_id, **kwargs):
    return (services.current_zone().find_object)(obj_id, **kwargs)


@exception_protected
def c_api_get_objects(zone_id):
    return get_objects()


def get_objects():
    return services.object_manager().get_all()


@exception_protected
def c_api_set_object_state_index(obj_id, state_index, zone_id):
    obj = find_object(obj_id)
    obj.set_object_def_state_index(state_index)


@exception_protected(default_return=False)
def c_api_set_build_buy_lockout(zone_id, obj_or_id, lockout_state, permanent_lock=False):
    obj = _get_obj_for_obj_or_id(obj_or_id)
    if obj is not None:
        obj.set_build_buy_lockout_state(False, None)
        return True
        obj.set_build_buy_lockout_state(lockout_state, SystemTuning.build_buy_lockout_duration)
        return True
    return False


@exception_protected(default_return=(-1))
def c_api_set_parent_object(obj_id, parent_id, transform, joint_name, slot_hash, zone_id):
    set_parent_object(obj_id, parent_id, transform, joint_name, slot_hash)


@exception_protected
def c_api_get_buildbuy_use_flags(zone_id, object_id):
    obj = find_object(object_id)
    return obj.build_buy_use_flags


@exception_protected
def c_api_set_buildbuy_use_flags(zone_id, object_id, build_buy_use_flags):
    obj = find_object(object_id)
    if obj is not None:
        obj.build_buy_use_flags = build_buy_use_flags
        return True
    return False


def set_parent_object(obj_id, parent_id, transform=sims4.math.Transform.IDENTITY(), joint_name=None, slot_hash=0):
    obj = find_object(obj_id)
    parent_obj = find_object(parent_id)
    obj.set_parent(parent_obj, transform, joint_name_or_hash=joint_name, slot_hash=slot_hash)


@exception_protected(default_return=(-1))
def c_api_clear_parent_object(obj_id, transform, zone_id, surface):
    obj = find_object(obj_id)
    obj.clear_parent(transform, surface)


@exception_protected
def c_api_get_parent(obj_id, zone_id):
    obj = find_object(obj_id, include_props=True)
    if obj is not None:
        return obj.get_parent()


@exception_protected(default_return=0)
def c_api_get_slot_hash(obj_id, zone_id):
    obj = find_object(obj_id, include_props=True)
    if obj is not None:
        return obj.bone_name_hash
    return 0


@exception_protected(default_return=0)
def c_api_set_slot_hash(obj_id, zone_id, slot_hash):
    obj = find_object(obj_id)
    if obj is not None:
        obj.slot_hash = slot_hash


@exception_protected(default_return=(iter(())))
def c_api_get_all_children_gen(obj_id):
    obj = find_object(obj_id)
    if obj is not None:
        try:
            yield from obj.get_all_children_gen()
        except AttributeError:
            pass

    if False:
        yield None


@exception_protected(default_return=True)
def c_api_clear_default_children(obj_id):
    obj = find_object(obj_id, include_props=True)
    if obj is not None:
        try:
            obj.clear_default_children()
            return True
        except AttributeError:
            logger.error('Trying to clear children, but obj({}) does not support functionality', obj)

    return False


@sims4.utils.exception_protected
def c_api_set_modular_pieces(obj_id, piece_ids):
    obj = find_object(obj_id)
    if obj is None:
        return
    from objects.modular.sectional_sofa_tuning import SectionalSofaTuning
    if not isinstance(obj, SectionalSofaTuning.SECTIONAL_SOFA_OBJECT_DEF.cls):
        logger.error('Attempting to set modular pieces on something that is not modular! {}', obj, owner='jdimailig')
        return
    obj.set_modular_pieces(piece_ids)


@sims4.utils.exception_protected
def c_api_get_modular_pieces(obj_id):
    obj = find_object(obj_id)
    if obj is None:
        return ()
    from objects.modular.sectional_sofa_tuning import SectionalSofaTuning
    if not isinstance(obj, SectionalSofaTuning.SECTIONAL_SOFA_OBJECT_DEF.cls):
        logger.error('Attempting to get modular pieces on something that is not modular! {}', obj, owner='jdimailig')
        return ()
    return tuple((piece.id for piece in obj.sofa_pieces))


@sims4.utils.exception_protected
def c_api_clear_modular_pieces(obj_id):
    obj = find_object(obj_id)
    if obj is None:
        return
    from objects.modular.sectional_sofa_tuning import SectionalSofaTuning
    if not isinstance(obj, SectionalSofaTuning.SECTIONAL_SOFA_OBJECT_DEF.cls):
        logger.error('Attempting to clear modular pieces on something that is not modular! {}', obj, owner='jdimailig')
        return
    obj.clear_modular_pieces()


@sims4.utils.exception_protected
def c_api_get_modular_owners():
    modular_owners = []
    from objects.modular.sectional_sofa_tuning import SectionalSofaTuning
    for obj in get_objects():
        if isinstance(obj, SectionalSofaTuning.SECTIONAL_SOFA_OBJECT_DEF.cls):
            modular_owners.append(obj.id)

    return tuple(modular_owners)