# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\fishing\aquarium_object.py
# Compiled at: 2018-02-28 16:55:27
# Size of source mod 2**32: 6387 bytes
import collections
from sims4 import hash_util
import broadcasters.environment_score, objects.game_object, sims4.tuning.tunable, sims4.tuning.tunable_base, vfx

class Aquarium(objects.game_object.GameObject):
    VFX_SLOT_NAME = '_FX_fish_'
    INSTANCE_TUNABLES = {'fish_vfx_prefix': sims4.tuning.tunable.Tunable(description='\n            prefix gets added to beginning of every effect. This way we can\n            swap out effects if we need to for different aquariums.\n            i.e. if the effect on the fish is "trout_vfx" and we put "ep04" here, it will\n            change it to "ep04_trout_vfx". This will apply to every fish object\n            in this aquarium.\n            ',
                          tunable_type=str,
                          default=None,
                          tuning_group=(sims4.tuning.tunable_base.GroupNames.FISHING))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._fish_vfx_handles = []

    def on_object_added_to_inventory(self, obj):
        for _ in range(obj.stack_count()):
            self._add_fish_effect(obj)

        self.add_dynamic_component(objects.components.types.ENVIRONMENT_SCORE_COMPONENT)

    def on_object_removed_from_inventory(self, obj):
        for _ in range(obj.stack_count()):
            self._remove_fish_effect(obj.id)

        if len(self.inventory_component) == 0:
            self._fish_vfx_handles.clear()
            self.remove_component(objects.components.types.ENVIRONMENT_SCORE_COMPONENT)

    def on_object_stack_id_updated--- This code section failed: ---

 L.  69         0  SETUP_LOOP           64  'to 64'
                2  LOAD_GLOBAL              enumerate
                4  LOAD_FAST                'self'
                6  LOAD_ATTR                _fish_vfx_handles
                8  CALL_FUNCTION_1       1  '1 positional argument'
               10  GET_ITER         
             12_0  COME_FROM            38  '38'
             12_1  COME_FROM            26  '26'
               12  FOR_ITER             62  'to 62'
               14  UNPACK_SEQUENCE_2     2 
               16  STORE_FAST               'i'
               18  STORE_FAST               'fish_vfx_handle'

 L.  70        20  LOAD_FAST                'fish_vfx_handle'
               22  LOAD_CONST               None
               24  COMPARE_OP               is-not
               26  POP_JUMP_IF_FALSE    12  'to 12'
               28  LOAD_FAST                'fish_vfx_handle'
               30  LOAD_CONST               0
               32  BINARY_SUBSCR    
               34  LOAD_FAST                'old_obj_id'
               36  COMPARE_OP               ==
               38  POP_JUMP_IF_FALSE    12  'to 12'

 L.  71        40  LOAD_FAST                'obj'
               42  LOAD_ATTR                id
               44  LOAD_FAST                'fish_vfx_handle'
               46  LOAD_CONST               1
               48  BINARY_SUBSCR    
               50  BUILD_TUPLE_2         2 
               52  LOAD_FAST                'self'
               54  LOAD_ATTR                _fish_vfx_handles
               56  LOAD_FAST                'i'
               58  STORE_SUBSCR     
               60  JUMP_BACK            12  'to 12'
               62  POP_BLOCK        
             64_0  COME_FROM_LOOP        0  '0'

 L.  74        64  LOAD_FAST                'obj'
               66  LOAD_METHOD              stack_count
               68  CALL_METHOD_0         0  '0 positional arguments'
               70  LOAD_FAST                'old_stack_count'
               72  BINARY_SUBTRACT  
               74  STORE_FAST               'stack_delta'

 L.  75        76  LOAD_FAST                'stack_delta'
               78  LOAD_CONST               0
               80  COMPARE_OP               >
               82  POP_JUMP_IF_FALSE   114  'to 114'

 L.  77        84  SETUP_LOOP          154  'to 154'
               86  LOAD_GLOBAL              range
               88  LOAD_FAST                'stack_delta'
               90  CALL_FUNCTION_1       1  '1 positional argument'
               92  GET_ITER         
               94  FOR_ITER            110  'to 110'
               96  STORE_FAST               '_'

 L.  78        98  LOAD_FAST                'self'
              100  LOAD_METHOD              _add_fish_effect
              102  LOAD_FAST                'obj'
              104  CALL_METHOD_1         1  '1 positional argument'
              106  POP_TOP          
              108  JUMP_BACK            94  'to 94'
              110  POP_BLOCK        
              112  JUMP_FORWARD        154  'to 154'
            114_0  COME_FROM            82  '82'

 L.  79       114  LOAD_FAST                'stack_delta'
              116  LOAD_CONST               0
              118  COMPARE_OP               <
              120  POP_JUMP_IF_FALSE   154  'to 154'

 L.  81       122  SETUP_LOOP          154  'to 154'
              124  LOAD_GLOBAL              range
              126  LOAD_FAST                'stack_delta'
              128  UNARY_NEGATIVE   
              130  CALL_FUNCTION_1       1  '1 positional argument'
              132  GET_ITER         
              134  FOR_ITER            152  'to 152'
              136  STORE_FAST               '_'

 L.  82       138  LOAD_FAST                'self'
              140  LOAD_METHOD              _remove_fish_effect
              142  LOAD_FAST                'obj'
              144  LOAD_ATTR                id
              146  CALL_METHOD_1         1  '1 positional argument'
              148  POP_TOP          
              150  JUMP_BACK           134  'to 134'
              152  POP_BLOCK        
            154_0  COME_FROM_LOOP      122  '122'
            154_1  COME_FROM           120  '120'
            154_2  COME_FROM           112  '112'
            154_3  COME_FROM_LOOP       84  '84'

Parse error at or near `COME_FROM' instruction at offset 154_2

    def get_environment_score(self, sim, ignore_disabled_state=False):
        if len(self.inventory_component) > 0:
            total_mood_scores = collections.Counter()
            total_positive_score = 0
            total_negative_score = 0
            total_contributions = []
            for fish in self.inventory_component:
                mood_scores, negative_score, positive_score, contributions = fish.get_environment_score(sim=sim, ignore_disabled_state=ignore_disabled_state)
                total_mood_scores.update(mood_scores)
                total_positive_score += positive_score
                total_negative_score += negative_score
                total_contributions.extend(contributions)

            return (total_mood_scores, total_negative_score, total_positive_score, total_contributions)
        return broadcasters.environment_score.environment_score_component.EnvironmentScoreComponent.ENVIRONMENT_SCORE_ZERO

    def _add_fish_effect(self, fish):
        if None in self._fish_vfx_handles:
            index = self._fish_vfx_handles.index(None)
        else:
            index = len(self._fish_vfx_handles)
            self._fish_vfx_handles.append(None)
        vfx_data = fish.inventory_to_fish_vfx.get(self.inventory_component.inventory_type, None)
        if vfx_data is not None:
            vfx_index = index + 1
            if self.fish_vfx_prefix is not None:
                vfx_name = '{}_{}_{}'.format(self.fish_vfx_prefix, vfx_data.vfx_name, vfx_index)
            else:
                vfx_name = '{}_{}'.format(vfx_data.vfx_name, vfx_index)
            vfx_slot_name = '{}{}'.format(vfx_data.vfx_base_bone_name, vfx_index)
        else:
            vfx_name = fish.fishbowl_vfx
            vfx_slot_name = self.VFX_SLOT_NAME
        vfx_slot = hash_util.hash32(vfx_slot_name)
        play_effect_handle = vfx.PlayEffect(self, vfx_name, joint_name=vfx_slot)
        play_effect_handle.start()
        self._fish_vfx_handles[index] = (
         fish.id, play_effect_handle)

    def _remove_fish_effect(self, fish_obj_id):
        for i, fish_vfx_handle in enumerate(self._fish_vfx_handles):
            if fish_vfx_handle is not None and fish_vfx_handle[0] == fish_obj_id:
                fish_vfx_handle[1].stop()
                self._fish_vfx_handles[i] = None
                break