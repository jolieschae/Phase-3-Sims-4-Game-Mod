# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\__init__.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 39942 bytes
import collections, weakref
from alarms import add_alarm
from native.animation import get_mirrored_joint_name_hash
from native.animation.arb import ClipEventType, ArbEventData
from objects import VisibilityState, MaterialState
from objects.components.censor_grid_component import CensorState
from objects.system import create_prop, create_object, create_prop_with_footprint
from sims4.repr_utils import standard_angle_repr
from singletons import DEFAULT
from uid import unique_id, UniqueIdGenerator
import audio, clock, native.animation.arb, services, sims4.hash_util, sims4.log, vfx
logger = sims4.log.Logger('Animation')
ClipEventType = native.animation.arb.ClipEventType
with sims4.reload.protected(globals()):
    GLOBAL_SINGLE_PART_CONDITION_CACHE = {}
    GLOBAL_MULTI_PART_CONDITION_CACHE = {}

def get_animation_object_by_id(obj_id, allow_obj=True, allow_prop=True):
    zone = services.current_zone()
    if allow_obj:
        obj = zone.find_object(obj_id)
        if obj is not None:
            return obj
    if allow_prop:
        obj = zone.prop_manager.get(obj_id)
        if obj is not None:
            return obj
    if allow_obj:
        if allow_prop:
            logger.warn('Animation object not found in prop or object manager: 0x{:016x}', obj_id)


def get_event_handler_error_for_missing_object(name, object_id):
    if object_id:
        return '{} (id: 0x{:016x}) not found in object manager. It was probably deleted.'.format(name, object_id)
    return "Missing {0}. Either the {0}'s namespace wasn't set in Maya, wasn't found in the namespace map, or wasn't set as an actor on the ASM.".format(name, object_id)


def get_animation_object_for_event(event_data, attr_name, error_name, asms=None, **kwargs):
    obj_id = event_data.event_data[attr_name]
    if obj_id == 0:
        asm_names = ', '.join(set((asm.name for asm in asms)))
        clip_name = event_data.event_data.get('clip_name', 'unknown clip')
        logger.warn('\n            ANIMATION: The game is unable to resolve the {} ({}) \n            variable of {} event {}. The specific clip is {}, \n            and is found in one of these ASMs:\n             {}\n             \n            Please check the clip event data in Sage first. If everything looks\n            correct, check it out in Maya before asking Tech Design whether or\n            not all the actors are properly set. That should be verifiable by\n            looking at the GSI animation archive.\n            ', attr_name, error_name, ClipEventType(event_data.event_type).name, event_data.event_id, clip_name, asm_names)
        error = get_event_handler_error_for_missing_object(error_name, obj_id)
        return (error, None)
    obj = get_animation_object_by_id(obj_id, **kwargs)
    if obj is None:
        error = get_event_handler_error_for_missing_object(error_name, obj_id)
        return (error, None)
    return (
     None, obj)


class EventHandle:

    def __init__(self, manager, tag=None):
        self._manager_ref = weakref.ref(manager)
        self._tag = tag

    @property
    def _manager(self):
        if self._manager_ref is not None:
            return self._manager_ref()

    @property
    def tag(self):
        return self._tag

    def release(self):
        if self._manager is not None:
            self._manager._release_handle(self)

    def __hash__(self):
        if self.tag is not None:
            return hash(self.tag)
        return super().__hash__()

    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        if self.tag is not None:
            if self.tag == other.tag:
                return True
        return self is other


UserDataKey = collections.namedtuple('UserDataKey', ['event_type', 'actor_id', 'id'])

@unique_id('_context_uid')
class AnimationContext:
    _get_next_asm_event_uid = UniqueIdGenerator()
    _CENSOR_MAPPING = {native.animation.arb.CENSOREVENT_STATE_OFF: CensorState.OFF, 
     native.animation.arb.CENSOREVENT_STATE_TORSO: CensorState.TORSO, 
     native.animation.arb.CENSOREVENT_STATE_TORSOPELVIS: CensorState.TORSO_PELVIS, 
     native.animation.arb.CENSOREVENT_STATE_PELVIS: CensorState.PELVIS, 
     native.animation.arb.CENSOREVENT_STATE_TODDLERPELVIS: CensorState.TODDLER_PELVIS, 
     native.animation.arb.CENSOREVENT_STATE_FULLBODY: CensorState.FULLBODY, 
     native.animation.arb.CENSOREVENT_STATE_RHAND: CensorState.RHAND, 
     native.animation.arb.CENSOREVENT_STATE_LHAND: CensorState.LHAND}

    def __init__(self, *args, is_throwaway=False, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._user_data = {}
        self._props = {}
        self._placeholders = {}
        self._posture_owners = None if is_throwaway else set()
        self._vfx_overrides = None
        self._sound_overrides = None
        self._custom_event_handlers = {}
        self._event_handlers = {}
        self._asms = []
        self._alarm_handles = []
        self.include_object_children_in_fade = False
        if not is_throwaway:
            self.reset_for_new_interaction()
        self.apply_carry_interaction_mask = []
        self._ref_count = []

    def __repr__(self):
        kwargs = {}
        if self._props:
            kwargs['props'] = list(sorted(self._props))
        if self._placeholders:
            kwargs['placeholders'] = list(sorted((str(e) for e in self._placeholders.values())))
        if self._asms:
            kwargs['asms'] = list(sorted({e.name for e in self._asms}))
        if self._ref_count:
            kwargs['refs'] = self._ref_count
        return standard_angle_repr(self, request_id=self.request_id, **kwargs)

    def add_asm(self, asm):
        self._asms.append(asm)

    def get_asms_gen(self):
        return iter(self._asms)

    @property
    def user_data(self):
        return self._user_data

    def add_posture_owner(self, posture):
        if self._posture_owners is not None:
            self._posture_owners.add(posture)
            self.add_ref(posture)

    def remove_posture_owner(self, posture):
        if self._posture_owners is not None:
            self._posture_owners.discard(posture)
            self.release_ref(posture)
            if not self._posture_owners:
                if self._ref_count:
                    logger.error('{} release all the postures but still have {} ref count. This is invalid.', self, self._ref_count)

    def reset_for_new_interaction(self):
        self._vfx_overrides = None
        self._sound_overrides = None
        self._alarm_handles = [alarm_handle for alarm_handle in self._alarm_handles if alarm_handle is not None]
        self._custom_event_handlers = {}
        self._event_handlers = {}
        self.register_event_handler(self._event_handler_effect_start, ClipEventType.Effect)
        self.register_event_handler(self._event_handler_effect_stop, ClipEventType.StopEffect)
        self.register_event_handler(self._event_handler_sound_start, ClipEventType.ServerSoundStart)
        self.register_event_handler(self._event_handler_sound_stop, ClipEventType.ServerSoundStop)
        self.register_event_handler(self._event_handler_censor_grid, ClipEventType.Censor)
        self.register_event_handler(self._event_handler_material_state, ClipEventType.MaterialState)
        self.register_event_handler(self._event_handler_geometry_state, ClipEventType.GeometryState)
        self.register_event_handler(self._event_handler_fade_object, ClipEventType.FadeObject)

    def get_placeholder_objects(self):
        return tuple((reservation_and_object[1] for reservation_and_object in self._placeholders.values()))

    def _reset_throwaway_context(self):
        self._stop()
        self.reset_for_new_interaction()
        del self._asms[:]

    def add_ref(self, tag):
        self._ref_count.append(tag)

    def release_ref(self, tag):
        if tag in self._ref_count:
            self._ref_count.remove(tag)
        else:
            logger.error('Unexpected tag in release_ref: {} (remaining refs: {})', tag, self._ref_count)
        if not self._ref_count:
            self._stop()

    def release_alarms(self):
        for alarm_handle in self._alarm_handles:
            if alarm_handle is not None:
                alarm_handle.cancel()

        self._alarm_handles.clear()

    def _all_props_gen(self, held_only):
        for name, prop in self._props.items():
            if prop.id not in prop.manager:
                continue
            if held_only:
                parent = prop.parent
                if not (parent is None or parent.is_sim):
                    continue
            yield name

    def destroy_all_props(self, held_only=False):
        names = []
        for name in self._all_props_gen(held_only):
            names.append(name)

        for name in names:
            prop_manager = services.prop_manager()
            prop_manager.destroy_prop((self._props.pop(name)), source=self, cause='Animation destroying all props.')

    def set_all_prop_visibility(self, visible, held_only=False):
        for name in self._all_props_gen(held_only):
            self._props[name].visibility = VisibilityState(visible)

    def _stop(self):
        for key in self._user_data:
            data = self._user_data[key]
            if hasattr(data, 'stop'):
                if key.event_type == ClipEventType.Effect:
                    data.stop(immediate=False)
                else:
                    data.stop()
            if key.event_type == ClipEventType.Censor:
                censor_object = get_animation_object_by_id(key.actor_id)
                if censor_object is not None:
                    censor_object.censorgrid_component.remove_censor(data)

        self._user_data.clear()
        self.destroy_all_props()
        self.clear_reserved_slots()
        self.release_alarms()
        self._event_handlers.clear()

    @property
    def request_id(self):
        return self._context_uid

    def _override_prop_states(self, actor, prop, states):
        if actor is None or actor.state_component is None:
            return
        if prop is None or prop.state_component is None:
            return
        for state in states:
            state_value = actor.get_state(state)
            if state_value is not None:
                prop.set_state(state, state_value)

    def _get_prop(self, asm, prop_name, definition_id):
        props = self._props
        prop = props.get(prop_name)
        from_actor, states_to_override = asm.get_prop_state_override(prop_name)
        if not definition_id:
            self._override_prop_states(from_actor, prop, states_to_override)
            return prop
        if prop is not None:
            if prop.definition.id != definition_id:
                asm.set_actor(prop_name, None)
                prop.destroy(source=self, cause='Replacing prop.')
                del props[prop_name]
                prop = None
        elif prop is None:
            share_key = asm.get_prop_share_key(prop_name)
            if share_key is None:
                prop = create_prop(definition_id)
            else:
                prop_manager = services.prop_manager()
                prop = prop_manager.create_shared_prop(share_key, definition_id)
            if prop is not None:
                props[prop_name] = prop
            else:
                logger.error("{}: Failed to create prop '{}' with definition id {:#x}", asm.name, prop_name, definition_id)
        if prop is not None:
            asm.set_prop_state_values(prop_name, prop)
            self._override_prop_states(from_actor, prop, states_to_override)
            asm.set_prop_as_asm_actor(prop_name, prop)
            asm.apply_special_case_overrides(prop_name, prop)
        return prop

    def clear_reserved_slots(self):
        for slot_manifest_entry, placeholder_info in list(self._placeholders.items()):
            reservation_handler, placeholder_obj = placeholder_info
            logger.debug('Slot Reservation: Release: {} for {}', placeholder_obj, slot_manifest_entry)
            reservation_handler.end_reservation()
            placeholder_obj.destroy(source=self, cause='Clearing reserved slots')

        self._placeholders.clear()

    @staticmethod
    def init_placeholder_obj(obj):
        obj.visibility = VisibilityState(False)

    def update_reserved_slots(self, slot_manifest_entry, reserve_sim, objects_to_ignore=DEFAULT):
        runtime_slot = slot_manifest_entry.runtime_slot
        if runtime_slot is None:
            raise RuntimeError('Attempt to reserve slots without a valid runtime slot: {}'.format(slot_manifest_entry))
        if slot_manifest_entry.actor in runtime_slot.children or slot_manifest_entry in self._placeholders:
            return sims4.utils.Result.TRUE
        definition = slot_manifest_entry.actor.definition
        result = sims4.utils.Result.TRUE

        def post_add(obj):
            nonlocal result
            try:
                try:
                    result = runtime_slot.is_valid_for_placement(obj=obj, objects_to_ignore=objects_to_ignore)
                    if result:
                        runtime_slot.add_child(obj)
                        reservation_handler = obj.get_reservation_handler(reserve_sim)
                        reservation_handler.begin_reservation()
                        self._placeholders[slot_manifest_entry] = (
                         reservation_handler, obj)
                        logger.debug('Slot Reservation: Reserve: {} for {}', obj, slot_manifest_entry)
                except:
                    logger.exception('Exception reserving slot: {} for {}', obj, slot_manifest_entry)
                    result = sims4.utils.Result(False, 'Exception reserving slot.')

            finally:
                if not result:
                    logger.debug('Slot Reservation: Fail:    {} for {} - {}', obj, slot_manifest_entry, result)
                    obj.destroy(source=self, cause='updating reserved slots')

        create_prop_with_footprint(definition, init=(self.init_placeholder_obj), post_add=post_add)
        return result

    def register_event_handler(self, callback, handler_type=ClipEventType.Script, handler_id=None, tag=None):
        handle = EventHandle(self, tag=tag)
        for existing_handle in list(self._event_handlers):
            if existing_handle == handle:
                existing_handle.release()

        uid = AnimationContext._get_next_asm_event_uid()
        self._event_handlers[handle] = (uid, callback, handler_type, handler_id)
        return handle

    def register_custom_event_handler(self, callback, actor, time, allow_stub_creation=False, optional=False):
        handler_id = services.current_zone().arb_accumulator_service.claim_xevt_id()
        handle = EventHandle(self)
        uid = AnimationContext._get_next_asm_event_uid()
        self._custom_event_handlers[handle] = (uid, callback, handler_id, actor.id if actor is not None else None, time, allow_stub_creation, optional)
        return handle

    def _release_handle(self, handle):
        if handle in self._event_handlers:
            del self._event_handlers[handle]
        if handle in self._custom_event_handlers:
            del self._custom_event_handlers[handle]

    def _pre_request(self, asm, arb, state):
        arb.add_request_info(self, asm, state)
        for uid, callback, event_type, event_id in self._event_handlers.values():
            if not hasattr(arb, '_context_uids'):
                arb._context_uids = set()
            if uid not in arb._context_uids:
                arb.register_event_handler(callback, event_type, event_id)
                arb._context_uids.add(uid)

        props = asm.get_props_in_traversal(asm.current_state, state)
        for prop_name, definition_id in props.items():
            prop = self._get_prop(asm, prop_name, definition_id)
            if prop is not None:
                asm.set_actor(prop_name, prop) or logger.warn('{}: Failed to set actor: {} to {}', asm, prop_name, prop)

        self._vfx_overrides = asm.vfx_overrides
        self._sound_overrides = asm.sound_overrides
        for actor_name in self.apply_carry_interaction_mask:
            asm._set_actor_trackmask_override(actor_name, 50000, 'Trackmask_CarryInteraction')

    def _post_request--- This code section failed: ---

 L. 565         0  LOAD_CONST               None
                2  STORE_FAST               'asm_actors'

 L. 566       4_6  SETUP_LOOP          366  'to 366'
                8  LOAD_FAST                'self'
               10  LOAD_ATTR                _custom_event_handlers
               12  LOAD_METHOD              values
               14  CALL_METHOD_0         0  '0 positional arguments'
               16  GET_ITER         
             18_0  COME_FROM           234  '234'
            18_20  FOR_ITER            364  'to 364'
               22  UNPACK_SEQUENCE_7     7 
               24  STORE_FAST               'uid'
               26  STORE_DEREF              'callback'
               28  STORE_FAST               'event_id'
               30  STORE_FAST               'actor_id'
               32  STORE_FAST               'time'
               34  STORE_FAST               'allow_stub_creation'
               36  STORE_FAST               'optional'

 L. 568        38  LOAD_FAST                'actor_id'
               40  LOAD_CONST               None
               42  COMPARE_OP               is-not
               44  POP_JUMP_IF_FALSE    92  'to 92'

 L. 569        46  LOAD_FAST                'arb'
               48  LOAD_METHOD              _actors
               50  CALL_METHOD_0         0  '0 positional arguments'
               52  STORE_FAST               'actors'

 L. 570        54  LOAD_FAST                'actors'
               56  POP_JUMP_IF_FALSE    92  'to 92'

 L. 571        58  LOAD_FAST                'actor_id'
               60  LOAD_FAST                'actors'
               62  COMPARE_OP               not-in
               64  POP_JUMP_IF_FALSE    92  'to 92'

 L. 572        66  LOAD_FAST                'optional'
               68  POP_JUMP_IF_FALSE    72  'to 72'

 L. 573        70  CONTINUE             18  'to 18'
             72_0  COME_FROM            68  '68'

 L. 574        72  LOAD_GLOBAL              logger
               74  LOAD_METHOD              error
               76  LOAD_STR                 "Failed to schedule custom x-event {} from {} on {} which didn't have the requested actor: {}, callback: {}"
               78  LOAD_FAST                'event_id'
               80  LOAD_FAST                'asm'
               82  LOAD_FAST                'arb'
               84  LOAD_FAST                'actor_id'
               86  LOAD_DEREF               'callback'
               88  CALL_METHOD_6         6  '6 positional arguments'
               90  POP_TOP          
             92_0  COME_FROM            64  '64'
             92_1  COME_FROM            56  '56'
             92_2  COME_FROM            44  '44'

 L. 576        92  LOAD_CONST               False
               94  STORE_FAST               'scheduled_event'

 L. 577        96  LOAD_FAST                'actor_id'
               98  LOAD_CONST               None
              100  COMPARE_OP               is
              102  POP_JUMP_IF_FALSE   152  'to 152'

 L. 579       104  LOAD_FAST                'arb'
              106  LOAD_METHOD              _actors
              108  CALL_METHOD_0         0  '0 positional arguments'
              110  STORE_FAST               'actors'

 L. 580       112  LOAD_FAST                'actors'
              114  POP_JUMP_IF_FALSE   170  'to 170'

 L. 581       116  SETUP_LOOP          170  'to 170'
              118  LOAD_FAST                'actors'
              120  GET_ITER         
            122_0  COME_FROM           138  '138'
              122  FOR_ITER            148  'to 148'
              124  STORE_FAST               'arb_actor_id'

 L. 582       126  LOAD_FAST                'arb'
              128  LOAD_METHOD              add_custom_event
              130  LOAD_FAST                'arb_actor_id'
              132  LOAD_FAST                'time'
              134  LOAD_FAST                'event_id'
              136  CALL_METHOD_3         3  '3 positional arguments'
              138  POP_JUMP_IF_FALSE   122  'to 122'

 L. 583       140  LOAD_CONST               True
              142  STORE_FAST               'scheduled_event'

 L. 584       144  BREAK_LOOP       
              146  JUMP_BACK           122  'to 122'
              148  POP_BLOCK        
              150  JUMP_FORWARD        170  'to 170'
            152_0  COME_FROM           102  '102'

 L. 586       152  LOAD_FAST                'arb'
              154  LOAD_METHOD              add_custom_event
              156  LOAD_FAST                'actor_id'
              158  LOAD_FAST                'time'
              160  LOAD_FAST                'event_id'
              162  CALL_METHOD_3         3  '3 positional arguments'
              164  POP_JUMP_IF_FALSE   170  'to 170'

 L. 587       166  LOAD_CONST               True
              168  STORE_FAST               'scheduled_event'
            170_0  COME_FROM           164  '164'
            170_1  COME_FROM           150  '150'
            170_2  COME_FROM_LOOP      116  '116'
            170_3  COME_FROM           114  '114'

 L. 589       170  LOAD_FAST                'scheduled_event'
              172  POP_JUMP_IF_FALSE   232  'to 232'

 L. 590       174  LOAD_GLOBAL              hasattr
              176  LOAD_FAST                'arb'
              178  LOAD_STR                 '_context_uids'
              180  CALL_FUNCTION_2       2  '2 positional arguments'
              182  POP_JUMP_IF_TRUE    192  'to 192'

 L. 591       184  LOAD_GLOBAL              set
              186  CALL_FUNCTION_0       0  '0 positional arguments'
              188  LOAD_FAST                'arb'
              190  STORE_ATTR               _context_uids
            192_0  COME_FROM           182  '182'

 L. 592       192  LOAD_FAST                'uid'
              194  LOAD_FAST                'arb'
              196  LOAD_ATTR                _context_uids
              198  COMPARE_OP               not-in
              200  POP_JUMP_IF_FALSE   230  'to 230'

 L. 593       202  LOAD_FAST                'arb'
              204  LOAD_METHOD              register_event_handler
              206  LOAD_DEREF               'callback'
              208  LOAD_GLOBAL              ClipEventType
              210  LOAD_ATTR                Script
              212  LOAD_FAST                'event_id'
              214  CALL_METHOD_3         3  '3 positional arguments'
              216  POP_TOP          

 L. 594       218  LOAD_FAST                'arb'
              220  LOAD_ATTR                _context_uids
              222  LOAD_METHOD              add
              224  LOAD_FAST                'uid'
              226  CALL_METHOD_1         1  '1 positional argument'
              228  POP_TOP          
            230_0  COME_FROM           200  '200'
              230  JUMP_BACK            18  'to 18'
            232_0  COME_FROM           172  '172'

 L. 595       232  LOAD_FAST                'allow_stub_creation'
              234  POP_JUMP_IF_FALSE    18  'to 18'

 L. 600       236  LOAD_FAST                'asm_actors'
              238  LOAD_CONST               None
              240  COMPARE_OP               is
          242_244  POP_JUMP_IF_FALSE   258  'to 258'
              246  LOAD_GLOBAL              list
              248  LOAD_FAST                'asm'
              250  LOAD_METHOD              actors_gen
              252  CALL_METHOD_0         0  '0 positional arguments'
              254  CALL_FUNCTION_1       1  '1 positional argument'
              256  JUMP_FORWARD        260  'to 260'
            258_0  COME_FROM           242  '242'
              258  LOAD_FAST                'asm_actors'
            260_0  COME_FROM           256  '256'
              260  STORE_FAST               'asm_actors'

 L. 601       262  SETUP_LOOP          362  'to 362'
              264  LOAD_FAST                'asm_actors'
              266  GET_ITER         
            268_0  COME_FROM           280  '280'
              268  FOR_ITER            360  'to 360'
              270  STORE_FAST               'actor'

 L. 602       272  LOAD_FAST                'actor'
              274  LOAD_ATTR                id
              276  LOAD_FAST                'actor_id'
              278  COMPARE_OP               ==
          280_282  POP_JUMP_IF_FALSE   268  'to 268'

 L. 603       284  LOAD_FAST                'actor_id'
              286  BUILD_SET_1           1 
              288  STORE_FAST               'actors'

 L. 604       290  BUILD_MAP_0           0 
              292  STORE_FAST               'event_data'

 L. 605       294  LOAD_GLOBAL              ArbEventData
              296  LOAD_GLOBAL              ClipEventType
              298  LOAD_ATTR                Script
              300  LOAD_FAST                'event_id'
              302  LOAD_FAST                'event_data'
              304  LOAD_FAST                'actors'
              306  CALL_FUNCTION_4       4  '4 positional arguments'
              308  STORE_DEREF              'data'

 L. 606       310  LOAD_CLOSURE             'callback'
              312  LOAD_CLOSURE             'data'
              314  BUILD_TUPLE_2         2 
              316  LOAD_CODE                <code_object custom_event_alarm_callback>
              318  LOAD_STR                 'AnimationContext._post_request.<locals>.custom_event_alarm_callback'
              320  MAKE_FUNCTION_8          'closure'
              322  STORE_FAST               'custom_event_alarm_callback'

 L. 608       324  LOAD_GLOBAL              add_alarm
              326  LOAD_FAST                'self'
              328  LOAD_GLOBAL              clock
              330  LOAD_METHOD              interval_in_sim_minutes
              332  LOAD_FAST                'time'
              334  CALL_METHOD_1         1  '1 positional argument'
              336  LOAD_FAST                'custom_event_alarm_callback'
              338  CALL_FUNCTION_3       3  '3 positional arguments'
              340  STORE_FAST               'alarm_handle'

 L. 609       342  LOAD_FAST                'self'
              344  LOAD_ATTR                _alarm_handles
              346  LOAD_METHOD              append
              348  LOAD_FAST                'alarm_handle'
              350  CALL_METHOD_1         1  '1 positional argument'
              352  POP_TOP          

 L. 610       354  BREAK_LOOP       
          356_358  JUMP_BACK           268  'to 268'
              360  POP_BLOCK        
            362_0  COME_FROM_LOOP      262  '262'
              362  JUMP_BACK            18  'to 18'
              364  POP_BLOCK        
            366_0  COME_FROM_LOOP        4  '4'

 L. 612       366  SETUP_LOOP          394  'to 394'
              368  LOAD_FAST                'self'
              370  LOAD_ATTR                apply_carry_interaction_mask
              372  GET_ITER         
              374  FOR_ITER            392  'to 392'
              376  STORE_FAST               'actor_name'

 L. 613       378  LOAD_FAST                'asm'
              380  LOAD_METHOD              _clear_actor_trackmask_override
              382  LOAD_FAST                'actor_name'
              384  CALL_METHOD_1         1  '1 positional argument'
              386  POP_TOP          
          388_390  JUMP_BACK           374  'to 374'
              392  POP_BLOCK        
            394_0  COME_FROM_LOOP      366  '366'

 L. 618       394  BUILD_MAP_0           0 
              396  LOAD_FAST                'self'
              398  STORE_ATTR               _custom_event_handlers

Parse error at or near `LOAD_FAST' instruction at offset 170

    def _event_handler_discard_prop(self, event_data):
        request_id = event_data.event_data['request_id']
        if request_id != self.request_id:
            return
        prop_id = event_data.event_data['prop_actor_id']
        self.destroy_prop_from_id(prop_id)

    def destroy_prop_from_actor_id(self, prop_id):
        props = self._props
        for prop_name, prop in props.items():
            if prop.id == prop_id:
                prop_manager = services.prop_manager()
                prop_manager.destroy_prop(prop, source=self, cause='Discarding props.')
                del props[prop_name]
                return

    def _event_handler_effect_start(self, event_data):
        request_id = event_data.event_data['request_id']
        if request_id != self.request_id:
            return
        early_out, effect_parent_obj = get_animation_object_for_event(event_data,
          'effect_parent_id', 'parent', asms=(self._asms))
        if early_out is not None:
            return
        target_parent_id = event_data.event_data['effect_target_parent_id']
        if target_parent_id == 0:
            target_parent_obj = None
        else:
            early_out, target_parent_obj = get_animation_object_for_event(event_data,
              'effect_target_parent_id', 'parent', asms=(self._asms))
            if early_out is not None:
                return
            else:
                event_actor_id = event_data.event_data['event_actor_id']
                effect_actor_id = event_data.event_data['effect_actor_id']
                effect_name = None
                target_joint_offset = None
                callback_event_id = None
                mirrored_effect_name = None
                effect_joint_name_hash = event_data.event_data['effect_joint_name_hash']
                target_joint_name_hash = event_data.event_data['effect_target_joint_name_hash']
                if self._vfx_overrides and effect_actor_id in self._vfx_overrides:
                    effect_overrides = self._vfx_overrides[effect_actor_id]
                    if effect_overrides.effect is not None:
                        effect_name = effect_overrides.effect
                    if effect_overrides.effect_joint is not None:
                        effect_joint_name_hash = effect_overrides.effect_joint
                    if effect_overrides.target_joint is not None:
                        target_joint_name_hash = effect_overrides.target_joint
                    if effect_overrides.target_joint_offset is not None:
                        target_joint_offset = effect_overrides.target_joint_offset()
                    if effect_overrides.callback_event_id is not None:
                        callback_event_id = effect_overrides.callback_event_id
                    if effect_overrides.mirrored_effect is not None:
                        mirrored_effect_name = effect_overrides.mirrored_effect
                else:
                    effect_name = event_data.event_data['effect_name']
            key = UserDataKeyClipEventType.Effectevent_actor_ideffect_actor_id
            if key in self._user_data:
                self._user_data[key].stop()
                del self._user_data[key]
            mirrored = event_data.event_data['clip_is_mirrored']
            if mirrored:
                if mirrored_effect_name is not None:
                    effect_name = mirrored_effect_name
                    mirrored = False
            if not effect_name:
                return
            if mirrored:
                try:
                    if effect_parent_obj is not None:
                        effect_joint_name_hash = get_mirrored_joint_name_hash(effect_parent_obj.rig, effect_joint_name_hash)
                    if target_parent_obj is not None:
                        target_joint_name_hash = get_mirrored_joint_name_hash(target_parent_obj.rig, target_joint_name_hash)
                except Exception as e:
                    try:
                        logger.error('Failed to look up mirrored joint name...\nException: {}\nEventData: {}', e, event_data.event_data)
                    finally:
                        e = None
                        del e

            effect = vfx.PlayEffect(effect_parent_obj,
              effect_name,
              effect_joint_name_hash,
              target_parent_id,
              target_joint_name_hash,
              target_joint_offset=target_joint_offset,
              callback_event_id=callback_event_id,
              mirror_effect=mirrored)
            self._user_data[key] = effect
            effect.start()

    def _event_handler_effect_stop(self, event_data):
        request_id = event_data.event_data['request_id']
        if request_id != self.request_id:
            return
        event_actor_id = event_data.event_data['event_actor_id']
        effect_actor_id = event_data.event_data['effect_actor_id']
        key = UserDataKeyClipEventType.Effectevent_actor_ideffect_actor_id
        if key in self._user_data:
            self._user_data[key].stop(immediate=(event_data.event_data['effect_hard_stop']))
            del self._user_data[key]

    def _event_handler_sound_start(self, event_data):
        request_id = event_data.event_data['request_id']
        if request_id != self.request_id:
            return
        early_out, obj = get_animation_object_for_event(event_data,
          'target_actor_id', 'parent', asms=(self._asms))
        if early_out is not None:
            return
        sound_name = event_data.event_data['sound_name']
        sound_id = sims4.hash_util.hash64(sound_name)
        sound_id_overridden = False
        if self._sound_overrides:
            if sound_id in self._sound_overrides:
                sound_id = self._sound_overrides[sound_id]
                sound_id_overridden = True
        key = UserDataKeyClipEventType.ServerSoundStartobj.idsound_name
        if key in self._user_data:
            self._user_data[key].stop()
            del self._user_data[key]
        if sound_id is None:
            return
        is_vox = sound_name.startswith('vo')
        if is_vox:
            sound = sound_id_overridden or audio.primitive.PlaySound(obj, sound_id, is_vox=is_vox)
        else:
            if not sound_id_overridden:
                sound = audio.primitive.PlaySound(obj, sound_id, sound_name=sound_name)
            else:
                sound = audio.primitive.PlaySound(obj, sound_id)
        self._user_data[key] = sound
        sound.start()

    def _event_handler_sound_stop(self, event_data):
        request_id = event_data.event_data['request_id']
        if request_id != self.request_id:
            return
        sound_parent_id = event_data.event_data['target_actor_id']
        sound_name = event_data.event_data['sound_name']
        key = UserDataKeyClipEventType.ServerSoundStartsound_parent_idsound_name
        if key in self._user_data:
            self._user_data[key].stop()
            del self._user_data[key]

    def _event_handler_censor_grid(self, event_data):
        request_id = event_data.event_data['request_id']
        if request_id != self.request_id:
            return
        event_actor_id = event_data.event_data['event_actor_id']
        censor_state = event_data.event_data['censor_state']
        key = UserDataKeyClipEventType.Censorevent_actor_idNone
        censor_state = self._CENSOR_MAPPING[censor_state]
        actor = get_animation_object_by_id(event_actor_id)
        if key in self._user_data:
            actor.censorgrid_component.remove_censor(self._user_data[key])
            del self._user_data[key]
        if censor_state != CensorState.OFF:
            self._user_data[key] = actor.censorgrid_component.add_censor(censor_state)

    def _event_handler_material_state(self, event_data):
        request_id = event_data.event_data['request_id']
        if request_id != self.request_id:
            return
        target_actor_id = event_data.event_data['target_actor_id']
        material_state = event_data.event_data['material_state_name']
        target = get_animation_object_by_id(target_actor_id)
        if target is None:
            logger.error('Failed to handle material state clip event in ASMs: {}, Clip: {} because Target is None. Target ID: {}, Material State: {}', (self._asms), (event_data.event_data.get('clip_name', 'unknown clip')), target_actor_id, material_state, owner='shouse')
            return
        material_state = MaterialState(material_state)
        target.material_state = material_state

    def _event_handler_geometry_state(self, event_data):
        request_id = event_data.event_data['request_id']
        if request_id != self.request_id:
            return
        target_actor_id = event_data.event_data['target_actor_id']
        geometry_state = event_data.event_data['geometry_state_name']
        target = get_animation_object_by_id(target_actor_id)
        if target is None:
            logger.error('Failed to handle geometry state clip event in ASMs: {}, Clip: {} because Target is None. Target ID: {}, Geometry State: {}', (self._asms), (event_data.event_data.get('clip_name', 'unknown clip')), target_actor_id, geometry_state, owner='rmccord')
            return
        target.geometry_state = geometry_state

    def _event_handler_fade_object(self, event_data):
        request_id = event_data.event_data['request_id']
        if request_id != self.request_id:
            return
        target_actor_id = event_data.event_data['target_actor_id']
        opacity = event_data.event_data['target_opacity']
        duration = event_data.event_data['duration']
        target = get_animation_object_by_id(target_actor_id)
        target.fade_opacity(opacity, duration)
        if self.include_object_children_in_fade:
            for obj in target.children_recursive_gen():
                obj.fade_opacity(opacity, duration)

    def add_user_data_from_anim_context(self, anim_context):
        self._user_data.update(anim_context.user_data)


_GLOBAL_ANIMATION_CONTEXT_SINGLETON = AnimationContext(is_throwaway=True)

def get_throwaway_animation_context():
    _GLOBAL_ANIMATION_CONTEXT_SINGLETON._reset_throwaway_context()
    return _GLOBAL_ANIMATION_CONTEXT_SINGLETON