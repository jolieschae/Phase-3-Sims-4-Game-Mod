# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\idle_component.py
# Compiled at: 2020-07-22 16:11:31
# Size of source mod 2**32: 13977 bytes
import animation.asm, caches, distributor.ops, element_utils, services, sims4
from animation import AnimationContext
from animation.animation_utils import flush_all_animations
from collections import defaultdict
from distributor.system import Distributor
from element_utils import build_critical_section_with_finally, build_element
from objects.components import Component, types, componentmethod_with_fallback, componentmethod
from sims4.tuning.tunable import HasTunableFactory, TunableMapping, TunableReference, OptionalTunable, Tunable, AutoFactoryInit
from sims4.callback_utils import CallableList
from singletons import DEFAULT
from weakref import WeakKeyDictionary
logger = sims4.log.Logger('IdleComponent', default_owner='rmccord')

class IdleComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=types.IDLE_COMPONENT):
    FACTORY_TUNABLES = {'idle_animation_map':TunableMapping(description='\n            The animations that the attached object can play.\n            ',
       key_type=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
       class_restrictions='ObjectStateValue'),
       value_type=TunableReference(description='\n                The animation to play when the object is in the specified state.\n                If you want the object to stop playing idles, you must tune an\n                animation element corresponding to an ASM state that requests a\n                stop on the object.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.ANIMATION)),
       class_restrictions='ObjectAnimationElement')), 
     'client_suppressed_state':OptionalTunable(description='\n            If enabled, set this object state whenever a client suppression is \n            triggered.\n            For example, when the retail system replaces an object when sold\n            all of its distributables are suppressed so we should stop all\n            animation, vfx, etc. \n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
       class_restrictions='ObjectStateValue')), 
     'parent_name':OptionalTunable(description='\n            If enabled, when the object is parented, its parent will be set as\n            this actor in whatever ASM is playing.\n            ',
       tunable=Tunable(tunable_type=str,
       default=None))}

    def __init__(self, owner, *args, **kwargs):
        (super().__init__)(owner, *args, **kwargs)
        self._asm_registry = WeakKeyDictionary()
        self._animation_context = AnimationContext()
        self._animation_context.add_ref(self)
        self._idle_animation_element = None
        self._current_idle_state_value = None
        self._component_suppressed = False
        self._wakeable_element = None
        self._scheduled_after_callbacks = defaultdict(CallableList)

    def get_asm(self, asm_key, actor_name, setup_asm_func=None, use_cache=True, animation_context=DEFAULT, cache_key=DEFAULT, **kwargs):
        if animation_context is DEFAULT:
            animation_context = self._animation_context
        else:
            if use_cache:
                asm_dict = self._asm_registry.setdefault(animation_context, {})
                asm = None
                if asm_key in asm_dict:
                    asm = asm_dict[asm_key]
                    if asm.current_state == 'exit':
                        asm = None
                if asm is None:
                    asm = animation.asm.create_asm(asm_key, context=animation_context)
                asm_dict[asm_key] = asm
            else:
                asm = animation.asm.create_asm(asm_key, context=animation_context)
            asm.set_actor(actor_name, self.owner)
            if self.parent_name is not None:
                parent = self.owner.parent
                if parent is not None:
                    asm.add_potentially_virtual_actor(actor_name, self.owner, self.parent_name, parent)
            if setup_asm_func is not None:
                result = setup_asm_func(asm)
                if not result:
                    logger.warn("Couldn't setup idle asm {} for {}. {}", asm, self.owner, result)
                    return
        return asm

    @componentmethod
    def get_idle_animation_context(self):
        return self._animation_context

    def add_scheduled_after_callback(self, state, func):
        self._scheduled_after_callbacks[state].register(func)

    def remove_scheduled_after_callback(self, state, func):
        self._scheduled_after_callbacks[state].unregister(func)

    def _refresh_active_idle(self):
        if self._current_idle_state_value is not None:
            if self._idle_animation_element is not None:
                self._trigger_idle_animation(self._current_idle_state_value.state, self._current_idle_state_value, False)

    def _stop_wakeable(self):
        if self._wakeable_element is not None:
            self._wakeable_element.trigger_soft_stop()
            self._wakeable_element = None

    def on_removed_from_inventory(self):
        self._refresh_active_idle()

    def on_state_changed(self, state, old_value, new_value, from_init):
        if not self._trigger_idle_animation(state, new_value, from_init):
            if new_value.anim_overrides is not None:
                if old_value != new_value:
                    self._refresh_active_idle()

    def _trigger_idle_animation--- This code section failed: ---

 L. 193         0  LOAD_DEREF               'self'
                2  LOAD_ATTR                _component_suppressed
                4  POP_JUMP_IF_FALSE    10  'to 10'

 L. 194         6  LOAD_CONST               None
                8  RETURN_VALUE     
             10_0  COME_FROM             4  '4'

 L. 196        10  LOAD_DEREF               'new_value'
               12  LOAD_DEREF               'self'
               14  LOAD_ATTR                idle_animation_map
               16  COMPARE_OP               in
               18  POP_JUMP_IF_FALSE   178  'to 178'

 L. 201        20  LOAD_GLOBAL              services
               22  LOAD_METHOD              current_zone
               24  CALL_METHOD_0         0  '0 positional arguments'
               26  STORE_FAST               'current_zone'

 L. 202        28  LOAD_FAST                'current_zone'
               30  LOAD_CONST               None
               32  COMPARE_OP               is
               34  POP_JUMP_IF_TRUE     46  'to 46'
               36  LOAD_FAST                'from_init'
               38  POP_JUMP_IF_FALSE    50  'to 50'
               40  LOAD_FAST                'current_zone'
               42  LOAD_ATTR                is_zone_loading
               44  POP_JUMP_IF_FALSE    50  'to 50'
             46_0  COME_FROM            34  '34'

 L. 203        46  LOAD_CONST               False
               48  RETURN_VALUE     
             50_0  COME_FROM            44  '44'
             50_1  COME_FROM            38  '38'

 L. 204        50  LOAD_DEREF               'self'
               52  LOAD_ATTR                idle_animation_map
               54  LOAD_DEREF               'new_value'
               56  BINARY_SUBSCR    
               58  STORE_FAST               'new_animation'

 L. 205        60  LOAD_DEREF               'self'
               62  LOAD_METHOD              _stop_animation_element
               64  CALL_METHOD_0         0  '0 positional arguments'
               66  POP_TOP          

 L. 206        68  LOAD_DEREF               'new_value'
               70  LOAD_DEREF               'self'
               72  STORE_ATTR               _current_idle_state_value

 L. 207        74  LOAD_FAST                'new_animation'
               76  LOAD_CONST               None
               78  COMPARE_OP               is-not
               80  POP_JUMP_IF_FALSE   178  'to 178'

 L. 208        82  LOAD_CONST               ()
               84  STORE_FAST               'sequence'

 L. 209        86  LOAD_FAST                'new_animation'
               88  LOAD_ATTR                repeat
               90  POP_JUMP_IF_FALSE   108  'to 108'

 L. 212        92  LOAD_GLOBAL              element_utils
               94  LOAD_METHOD              soft_sleep_forever
               96  CALL_METHOD_0         0  '0 positional arguments'
               98  LOAD_DEREF               'self'
              100  STORE_ATTR               _wakeable_element

 L. 213       102  LOAD_DEREF               'self'
              104  LOAD_ATTR                _wakeable_element
              106  STORE_FAST               'sequence'
            108_0  COME_FROM            90  '90'

 L. 214       108  LOAD_FAST                'new_animation'
              110  LOAD_DEREF               'self'
              112  LOAD_ATTR                owner
              114  LOAD_FAST                'sequence'
              116  LOAD_CONST               ('sequence',)
              118  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              120  STORE_FAST               'animation_element'

 L. 215       122  LOAD_GLOBAL              build_element
              124  LOAD_FAST                'animation_element'

 L. 216       126  LOAD_GLOBAL              flush_all_animations
              128  BUILD_TUPLE_2         2 
              130  CALL_FUNCTION_1       1  '1 positional argument'
              132  STORE_FAST               'core_idle_animation_element'

 L. 217       134  LOAD_GLOBAL              build_critical_section_with_finally
              136  LOAD_FAST                'core_idle_animation_element'

 L. 218       138  LOAD_CLOSURE             'new_value'
              140  LOAD_CLOSURE             'self'
              142  BUILD_TUPLE_2         2 
              144  LOAD_LAMBDA              '<code_object <lambda>>'
              146  LOAD_STR                 'IdleComponent._trigger_idle_animation.<locals>.<lambda>'
              148  MAKE_FUNCTION_8          'closure'
              150  CALL_FUNCTION_2       2  '2 positional arguments'
              152  LOAD_DEREF               'self'
              154  STORE_ATTR               _idle_animation_element

 L. 219       156  LOAD_GLOBAL              services
              158  LOAD_METHOD              time_service
              160  CALL_METHOD_0         0  '0 positional arguments'
              162  LOAD_ATTR                sim_timeline
              164  LOAD_METHOD              schedule
              166  LOAD_DEREF               'self'
              168  LOAD_ATTR                _idle_animation_element
              170  CALL_METHOD_1         1  '1 positional argument'
              172  POP_TOP          

 L. 220       174  LOAD_CONST               True
              176  RETURN_VALUE     
            178_0  COME_FROM            80  '80'
            178_1  COME_FROM            18  '18'

 L. 221       178  LOAD_CONST               False
              180  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `RETURN_VALUE' instruction at offset 180

    @componentmethod_with_fallback((lambda *_, **__: None))
    def on_client_suppressor_added(self):
        if self.client_suppressed_state is not None:
            self.owner.set_state(self.client_suppressed_state.state, self.client_suppressed_state)
        self._component_suppressed = True

    @componentmethod_with_fallback((lambda *_, **__: None))
    def on_client_suppressor_removed(self, supressors_active):
        if supressors_active:
            return
        self._component_suppressed = False
        if self.client_suppressed_state is not None:
            if self._current_idle_state_value is not None:
                self.owner.set_state(self._current_idle_state_value.state, self._current_idle_state_value)

    def component_reset(self, _):
        self._stop_animation_element(hard_stop=True)

    def post_component_reset(self):
        self.reapply_idle_state()

    def reapply_idle_state(self):
        for current_value in self.idle_animation_map:
            if self.owner.state_value_active(current_value):
                self._trigger_idle_animation(current_value.state, current_value, False)
                return

    def _stop_animation_element(self, hard_stop=False):
        self._stop_wakeable()
        if self._idle_animation_element is not None:
            if hard_stop:
                self._idle_animation_element.trigger_hard_stop()
            else:
                self._idle_animation_element.trigger_soft_stop()
            self._idle_animation_element = None
        self._current_idle_state_value = None

    def on_remove_from_client(self, *_, **__):
        zone = services.current_zone()
        if zone is not None:
            if zone.is_in_build_buy:
                try:
                    reset_op = distributor.ops.ResetObject(self.owner.id)
                    dist = Distributor.instance()
                    dist.add_op(self.owner, reset_op)
                except:
                    logger.exception('Exception thrown sending reset op for {}', self)

    def on_remove(self, *_, **__):
        if self._animation_context is not None:
            self._animation_context.release_ref(self)
            self._animation_context = None
        self._stop_animation_element(hard_stop=True)