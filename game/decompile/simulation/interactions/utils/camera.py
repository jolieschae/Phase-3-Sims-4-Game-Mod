# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\camera.py
# Compiled at: 2021-05-06 20:19:49
# Size of source mod 2**32: 6819 bytes
from camera import focus_on_sim, focus_on_object, shake_camera, focus_on_object_from_position, focus_on_lot, walls_up_override, focus_on_position
from interactions import ParticipantType
from interactions.utils.interaction_elements import XevtTriggeredElement
from objects.components.types import CAMERA_VIEW_COMPONENT
from sims4.tuning.tunable import TunableEnumEntry, Tunable, AutoFactoryInit, HasTunableFactory, HasTunableSingletonFactory, OptionalTunable, TunableRange, TunableRealSecond, TunablePackSafeReference
import services, sims4

class CameraFocusElement(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'description':'\n            Focus the camera on the specified participant.\n            ', 
     'participant':TunableEnumEntry(description='\n            The participant of this interaction to focus the camera on.\n            \n            Should be some kind of object or Sim.  Can also be set to Lot\n            to do a thumbnail-style view of the lot.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'follow':Tunable(description='\n            Whether or not the camera should stick to the focused participant.\n            ',
       tunable_type=bool,
       default=False), 
     'time_to_position':TunableRealSecond(description='\n            The amount of time given for the camera to move into position.\n            \n            Only applicable when participant type is Lot\n            ',
       default=1.0), 
     'sim_filter':OptionalTunable(description='\n            If enabled, this sim filter will be used as the camera subject \n            instead of the participant.\n            ',
       tunable=TunablePackSafeReference(description='\n                The filter used to find the desired Sim.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER))))}

    def _do_behavior--- This code section failed: ---

 L.  63         0  LOAD_CONST               None
                2  STORE_FAST               'subject'

 L.  66         4  LOAD_FAST                'self'
                6  LOAD_ATTR                sim_filter
                8  LOAD_CONST               None
               10  COMPARE_OP               is-not
               12  POP_JUMP_IF_FALSE    76  'to 76'

 L.  67        14  SETUP_LOOP          102  'to 102'
               16  LOAD_GLOBAL              services
               18  LOAD_METHOD              sim_info_manager
               20  CALL_METHOD_0         0  '0 positional arguments'
               22  LOAD_METHOD              instanced_sims_gen
               24  CALL_METHOD_0         0  '0 positional arguments'
               26  GET_ITER         
             28_0  COME_FROM            62  '62'
               28  FOR_ITER             72  'to 72'
               30  STORE_FAST               'sim'

 L.  68        32  LOAD_GLOBAL              services
               34  LOAD_METHOD              sim_filter_service
               36  CALL_METHOD_0         0  '0 positional arguments'
               38  LOAD_ATTR                does_sim_match_filter
               40  LOAD_FAST                'sim'
               42  LOAD_ATTR                id

 L.  69        44  LOAD_FAST                'self'
               46  LOAD_ATTR                sim_filter

 L.  70        48  LOAD_LAMBDA              '<code_object <lambda>>'
               50  LOAD_STR                 'CameraFocusElement._do_behavior.<locals>.<lambda>'
               52  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
               54  LOAD_CONST               ('sim_filter', 'gsi_source_fn')
               56  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
               58  STORE_FAST               'matched'

 L.  71        60  LOAD_FAST                'matched'
               62  POP_JUMP_IF_FALSE    28  'to 28'

 L.  72        64  LOAD_FAST                'sim'
               66  STORE_FAST               'subject'

 L.  73        68  BREAK_LOOP       
               70  JUMP_BACK            28  'to 28'
               72  POP_BLOCK        
               74  JUMP_FORWARD        102  'to 102'
             76_0  COME_FROM            12  '12'

 L.  75        76  LOAD_FAST                'self'
               78  LOAD_ATTR                interaction
               80  LOAD_METHOD              get_participant
               82  LOAD_FAST                'self'
               84  LOAD_ATTR                participant
               86  CALL_METHOD_1         1  '1 positional argument'
               88  STORE_FAST               'subject'

 L.  76        90  LOAD_FAST                'subject'
               92  LOAD_CONST               None
               94  COMPARE_OP               is
               96  POP_JUMP_IF_FALSE   102  'to 102'

 L.  77        98  LOAD_CONST               None
              100  RETURN_VALUE     
            102_0  COME_FROM            96  '96'
            102_1  COME_FROM            74  '74'
            102_2  COME_FROM_LOOP       14  '14'

 L.  79       102  LOAD_FAST                'self'
              104  LOAD_ATTR                participant
              106  LOAD_GLOBAL              ParticipantType
              108  LOAD_ATTR                Lot
              110  COMPARE_OP               ==
              112  POP_JUMP_IF_FALSE   130  'to 130'

 L.  81       114  LOAD_GLOBAL              focus_on_lot
              116  LOAD_FAST                'self'
              118  LOAD_ATTR                time_to_position
              120  LOAD_CONST               ('lerp_time',)
              122  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              124  POP_TOP          

 L.  82       126  LOAD_CONST               None
              128  RETURN_VALUE     
            130_0  COME_FROM           112  '112'

 L.  84       130  LOAD_FAST                'subject'
              132  LOAD_METHOD              has_component
              134  LOAD_GLOBAL              CAMERA_VIEW_COMPONENT
              136  CALL_METHOD_1         1  '1 positional argument'
              138  POP_JUMP_IF_FALSE   162  'to 162'

 L.  85       140  LOAD_GLOBAL              focus_on_object_from_position
              142  LOAD_FAST                'subject'
              144  LOAD_ATTR                position

 L.  86       146  LOAD_FAST                'subject'
              148  LOAD_METHOD              get_camera_position
              150  CALL_METHOD_0         0  '0 positional arguments'
              152  LOAD_CONST               ('obj_position', 'camera_position')
              154  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              156  POP_TOP          

 L.  87       158  LOAD_CONST               None
              160  RETURN_VALUE     
            162_0  COME_FROM           138  '138'

 L.  89       162  LOAD_FAST                'subject'
              164  LOAD_ATTR                is_sim
              166  POP_JUMP_IF_FALSE   188  'to 188'

 L.  90       168  LOAD_GLOBAL              focus_on_sim
              170  LOAD_FAST                'subject'
              172  LOAD_FAST                'self'
              174  LOAD_ATTR                follow
              176  LOAD_FAST                'subject'
              178  LOAD_ATTR                client
              180  LOAD_CONST               ('sim', 'follow', 'client')
              182  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              184  POP_TOP          
              186  JUMP_FORWARD        234  'to 234'
            188_0  COME_FROM           166  '166'

 L.  91       188  LOAD_FAST                'subject'
              190  LOAD_METHOD              is_in_inventory
              192  CALL_METHOD_0         0  '0 positional arguments'
              194  POP_JUMP_IF_FALSE   220  'to 220'

 L.  92       196  LOAD_FAST                'subject'
              198  LOAD_ATTR                inventoryitem_component
              200  LOAD_ATTR                last_inventory_owner
              202  STORE_FAST               'inventory_owner'

 L.  93       204  LOAD_GLOBAL              focus_on_object
              206  LOAD_FAST                'inventory_owner'
              208  LOAD_FAST                'self'
              210  LOAD_ATTR                follow
              212  LOAD_CONST               ('object', 'follow')
              214  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              216  POP_TOP          
              218  JUMP_FORWARD        234  'to 234'
            220_0  COME_FROM           194  '194'

 L.  95       220  LOAD_GLOBAL              focus_on_object
              222  LOAD_FAST                'subject'
              224  LOAD_FAST                'self'
              226  LOAD_ATTR                follow
              228  LOAD_CONST               ('object', 'follow')
              230  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              232  POP_TOP          
            234_0  COME_FROM           218  '218'
            234_1  COME_FROM           186  '186'

Parse error at or near `COME_FROM_LOOP' instruction at offset 102_2


class SetWallsUpOverrideElement(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'enable': Tunable(description='\n            Set to True to enable the override.  False to disable it.\n            \n            A user moving the camera manually will also cancel the override.\n            ',
                 tunable_type=bool,
                 default=True)}

    def _do_behavior(self):
        walls_up_override(walls_up=(self.enable))


class TunableCameraShake(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'duration':TunableRange(description='\n            Length of time this effect should occur, in seconds.\n            ',
       tunable_type=float,
       default=1.0,
       minimum=0.0), 
     'frequency':OptionalTunable(description='\n            The times per second that the effect should occur.\n            \n            Default value is 1.0\n            ',
       tunable=TunableRange(float, 1.0, minimum=0.0),
       disabled_name='use_default',
       enabled_name='specify'), 
     'amplitude':OptionalTunable(description='\n            Strength of the shake, in Sim meters.\n            \n            Default value is 1.0\n            ',
       tunable=TunableRange(float, 1.0, minimum=0.0),
       disabled_name='use_default',
       enabled_name='specify'), 
     'octaves':OptionalTunable(description='\n            Number of octaves for the shake.\n\n            Default value is 1\n            ',
       tunable=TunableRange(int, 1, minimum=0),
       disabled_name='use_default',
       enabled_name='specify'), 
     'fade_multiplier':OptionalTunable(description='\n            Adjusts the wave function, this can be set above 1.0 to introduce\n            a plateau for the shake effect.\n\n            Default value is 1.0\n            ',
       tunable=TunableRange(float, 1.0, minimum=1.0),
       disabled_name='use_default',
       enabled_name='specify')}

    def shake_camera(self):
        shake_camera((self.duration), frequency=(self.frequency),
          amplitude=(self.amplitude),
          octaves=(self.octaves),
          fade_multiplier=(self.fade_multiplier))