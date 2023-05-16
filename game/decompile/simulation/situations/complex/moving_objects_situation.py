# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\moving_objects_situation.py
# Compiled at: 2018-04-19 16:36:23
# Size of source mod 2**32: 13438 bytes
from _sims4_collections import frozendict
from element_utils import build_element, CleanupType
from elements import SoftSleepElement
from event_testing.resolver import GlobalResolver, SingleSimResolver, SingleActorAndObjectResolver
from event_testing.tests import TunableTestSet
from interactions import ParticipantType
from interactions.interaction_finisher import FinishingType
from objects.object_creation import ObjectCreationOp
from objects.placement.placement_helper import _PlacementStrategyLocation
from sims4 import random
from sims4.resources import Types
from sims4.tuning.tunable import TunableList, TunableTuple, TunableSimMinute, TunableSet, OptionalTunable, TunableReference
from sims4.tuning.tunable_base import GroupNames
from situations.situation import Situation
from situations.situation_complex import SituationComplexCommon, CommonSituationState, SituationStateData
from tag import TunableTags
from tunable_multiplier import TunableMultiplier
from vfx import PlayEffect
import clock, services

class _PreparationState(CommonSituationState):
    FACTORY_TUNABLES = {'creation_ops':TunableList(tunable=ObjectCreationOp.TunableFactory(description='\n                The operation that will create the objects.\n                ',
       locked_args={'destroy_on_placement_failure': True})), 
     'locked_args':{'job_and_role_changes':frozendict(), 
      'allow_join_situation':False, 
      'time_out':None}}

    def __init__(self, *args, creation_ops=(), **kwargs):
        (super().__init__)(*args, **kwargs)
        self.creation_ops = creation_ops

    def on_activate(self, reader=None):
        super().on_activate(reader=reader)
        resolver = self.owner._get_placement_resolver()
        for operation in self.creation_ops:
            operation.apply_to_resolver(resolver)

        self.owner.on_objects_ready()


class _WaitingToMoveState(CommonSituationState):
    FACTORY_TUNABLES = {'locked_args': {'job_and_role_changes':frozendict(), 
                     'allow_join_situation':False}}

    def timer_expired(self):
        self.owner.on_ready_to_move()


OBJECT_TOKEN = 'object_id'

class MovingObjectsSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'_preparation_state':_PreparationState.TunableFactory(tuning_group=GroupNames.STATE), 
     '_waiting_to_move_state':_WaitingToMoveState.TunableFactory(tuning_group=GroupNames.STATE), 
     '_tests_to_continue':TunableTestSet(description='\n            A list of tests that must pass in order to continue the situation\n            after the tuned duration for the waiting state has elapsed.\n            ',
       tuning_group=GroupNames.STATE), 
     'starting_requirements':TunableTestSet(description='\n            A list of tests that must pass in order for the situation\n            to start.\n            ',
       tuning_group=GroupNames.SITUATION), 
     'object_tags':TunableTags(description='\n            Tags used to find objects which will move about.\n            ',
       tuning_group=GroupNames.SITUATION), 
     'placement_strategy_locations':TunableList(description='\n            A list of weighted location strategies.\n            ',
       tunable=TunableTuple(weight=TunableMultiplier.TunableFactory(description='\n                    The weight of this strategy relative to other locations.\n                    '),
       placement_strategy=_PlacementStrategyLocation.TunableFactory(description='\n                    The placement strategy for the object.\n                    ')),
       minlength=1,
       tuning_group=GroupNames.SITUATION), 
     'fade':OptionalTunable(description='\n            If enabled, the objects will fade-in/fade-out as opposed to\n            immediately moving to their location.\n            ',
       tunable=TunableTuple(out_time=TunableSimMinute(description='\n                    Time over which the time will fade out.\n                    ',
       default=1),
       in_time=TunableSimMinute(description='\n                    Time over which the time will fade in.\n                    ',
       default=1)),
       enabled_by_default=True,
       tuning_group=GroupNames.SITUATION), 
     'vfx_on_move':OptionalTunable(description='\n            If tuned, apply this one-shot vfx on the moving object when it\n            is about to move.\n            ',
       tunable=PlayEffect.TunableFactory(),
       tuning_group=GroupNames.SITUATION), 
     'situation_end_loots_to_apply_on_objects':TunableSet(description='\n            The loots to apply on the tagged objects when the situation ends \n            or is destroyed.\n            \n            E.g. use this to reset objects to a specific state after \n            the situation is over.\n            \n            The loot will be processed with the active sim as the actor,\n            and the object as the target.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(Types.ACTION)),
       pack_safe=True),
       tuning_group=GroupNames.SITUATION)}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        reader = self._seed.custom_init_params_reader
        if reader is None:
            self._target_id = self._seed.extra_kwargs.get('default_target_id', None)
        else:
            self._target_id = reader.read_uint64(OBJECT_TOKEN, None)

    @classmethod
    def _states(cls):
        return (
         SituationStateData(0, _PreparationState, factory=(cls._preparation_state)),
         SituationStateData(1, _WaitingToMoveState, factory=(cls._waiting_to_move_state)))

    @classmethod
    def default_job(cls):
        pass

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return []

    @classmethod
    def situation_meets_starting_requirements(cls, **kwargs):
        if not cls.starting_requirements:
            return True
        else:
            resolver = SingleSimResolver(services.active_sim_info())
            return cls.starting_requirements.run_tests(resolver) or False
        return True

    def _save_custom_situation(self, writer):
        super()._save_custom_situation(writer)
        if self._target_id is not None:
            writer.write_uint64(OBJECT_TOKEN, self._target_id)

    def start_situation(self):
        super().start_situation()
        self._change_state(self._preparation_state())

    def load_situation(self):
        if not self.situation_meets_starting_requirements():
            return False
        return super().load_situation()

    def on_objects_ready(self):
        self._change_state(self._waiting_to_move_state())

    def on_ready_to_move(self):
        if self._tests_to_continue.run_tests(GlobalResolver()):
            self._move_objects()
            self._change_state(self._waiting_to_move_state())
        else:
            self._self_destruct()

    def _get_placement_resolver(self):
        additional_participants = {}
        if self._target_id is not None:
            target = services.object_manager().get(self._target_id)
            additional_participants[ParticipantType.Object] = (
             target,)
            if target is not None:
                if target.is_sim:
                    additional_participants[ParticipantType.TargetSim] = (
                     target.sim_info,)
        return SingleSimResolver((services.active_sim_info()), additional_participants=additional_participants)

    def _destroy(self):
        objects_of_interest = services.object_manager().get_objects_matching_tags((self.object_tags), match_any=True)
        if not objects_of_interest:
            return
        active_sim_info = services.active_sim_info()
        for obj in objects_of_interest:
            resolver = SingleActorAndObjectResolver(active_sim_info, obj, self)
            for loot in self.situation_end_loots_to_apply_on_objects:
                loot.apply_to_resolver(resolver)

        super()._destroy()

    def _move_objects--- This code section failed: ---

 L. 303         0  LOAD_GLOBAL              services
                2  LOAD_METHOD              object_manager
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  LOAD_ATTR                get_objects_matching_tags
                8  LOAD_DEREF               'self'
               10  LOAD_ATTR                object_tags
               12  LOAD_CONST               True
               14  LOAD_CONST               ('match_any',)
               16  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
               18  STORE_FAST               'objects_to_move'

 L. 304        20  LOAD_FAST                'objects_to_move'
               22  POP_JUMP_IF_TRUE     28  'to 28'

 L. 305        24  LOAD_CONST               None
               26  RETURN_VALUE     
             28_0  COME_FROM            22  '22'

 L. 307        28  LOAD_DEREF               'self'
               30  LOAD_METHOD              _get_placement_resolver
               32  CALL_METHOD_0         0  '0 positional arguments'
               34  STORE_DEREF              'resolver'

 L. 308        36  LOAD_CLOSURE             'resolver'
               38  BUILD_TUPLE_1         1 
               40  LOAD_LISTCOMP            '<code_object <listcomp>>'
               42  LOAD_STR                 'MovingObjectsSituation._move_objects.<locals>.<listcomp>'
               44  MAKE_FUNCTION_8          'closure'
               46  LOAD_DEREF               'self'
               48  LOAD_ATTR                placement_strategy_locations
               50  GET_ITER         
               52  CALL_FUNCTION_1       1  '1 positional argument'
               54  STORE_FAST               'choices'

 L. 309        56  LOAD_GLOBAL              random
               58  LOAD_METHOD              weighted_random_item
               60  LOAD_FAST                'choices'
               62  CALL_METHOD_1         1  '1 positional argument'
               64  STORE_DEREF              'chosen_strategy'

 L. 311        66  LOAD_DEREF               'self'
               68  LOAD_ATTR                fade
               70  LOAD_CONST               None
               72  COMPARE_OP               is-not
               74  STORE_FAST               'do_fade'

 L. 313        76  BUILD_LIST_0          0 
               78  STORE_FAST               'out_sequence'

 L. 314        80  BUILD_LIST_0          0 
               82  STORE_FAST               'moves'

 L. 315        84  BUILD_LIST_0          0 
               86  STORE_FAST               'in_sequence'

 L. 318        88  SETUP_LOOP          226  'to 226'
               90  LOAD_FAST                'objects_to_move'
               92  GET_ITER         
             94_0  COME_FROM           198  '198'
               94  FOR_ITER            224  'to 224'
               96  STORE_FAST               'object_to_move'

 L. 321        98  LOAD_FAST                'object_to_move'
              100  LOAD_ATTR                cancel_interactions_running_on_object
              102  LOAD_GLOBAL              FinishingType
              104  LOAD_ATTR                OBJECT_CHANGED
              106  LOAD_STR                 'Object changing location.'
              108  LOAD_CONST               ('cancel_reason_msg',)
              110  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              112  POP_TOP          

 L. 323       114  LOAD_DEREF               'self'
              116  LOAD_ATTR                vfx_on_move
              118  LOAD_CONST               None
              120  COMPARE_OP               is-not
              122  POP_JUMP_IF_FALSE   146  'to 146'

 L. 324       124  LOAD_FAST                'out_sequence'
              126  LOAD_METHOD              append
              128  LOAD_FAST                'object_to_move'
              130  BUILD_TUPLE_1         1 
              132  LOAD_CLOSURE             'self'
              134  BUILD_TUPLE_1         1 
              136  LOAD_LAMBDA              '<code_object <lambda>>'
              138  LOAD_STR                 'MovingObjectsSituation._move_objects.<locals>.<lambda>'
              140  MAKE_FUNCTION_9          'default, closure'
              142  CALL_METHOD_1         1  '1 positional argument'
              144  POP_TOP          
            146_0  COME_FROM           122  '122'

 L. 326       146  LOAD_FAST                'do_fade'
              148  POP_JUMP_IF_FALSE   172  'to 172'

 L. 327       150  LOAD_FAST                'out_sequence'
              152  LOAD_METHOD              append
              154  LOAD_FAST                'object_to_move'
              156  BUILD_TUPLE_1         1 
              158  LOAD_CLOSURE             'self'
              160  BUILD_TUPLE_1         1 
              162  LOAD_LAMBDA              '<code_object <lambda>>'
              164  LOAD_STR                 'MovingObjectsSituation._move_objects.<locals>.<lambda>'
              166  MAKE_FUNCTION_9          'default, closure'
              168  CALL_METHOD_1         1  '1 positional argument'
              170  POP_TOP          
            172_0  COME_FROM           148  '148'

 L. 329       172  LOAD_FAST                'moves'
              174  LOAD_METHOD              append
              176  LOAD_FAST                'object_to_move'
              178  BUILD_TUPLE_1         1 
              180  LOAD_CLOSURE             'chosen_strategy'
              182  LOAD_CLOSURE             'resolver'
              184  BUILD_TUPLE_2         2 
              186  LOAD_LAMBDA              '<code_object <lambda>>'
              188  LOAD_STR                 'MovingObjectsSituation._move_objects.<locals>.<lambda>'
              190  MAKE_FUNCTION_9          'default, closure'
              192  CALL_METHOD_1         1  '1 positional argument'
              194  POP_TOP          

 L. 331       196  LOAD_FAST                'do_fade'
              198  POP_JUMP_IF_FALSE    94  'to 94'

 L. 332       200  LOAD_FAST                'in_sequence'
              202  LOAD_METHOD              append
              204  LOAD_FAST                'object_to_move'
              206  BUILD_TUPLE_1         1 
              208  LOAD_CLOSURE             'self'
              210  BUILD_TUPLE_1         1 
              212  LOAD_LAMBDA              '<code_object <lambda>>'
              214  LOAD_STR                 'MovingObjectsSituation._move_objects.<locals>.<lambda>'
              216  MAKE_FUNCTION_9          'default, closure'
              218  CALL_METHOD_1         1  '1 positional argument'
              220  POP_TOP          
              222  JUMP_BACK            94  'to 94'
              224  POP_BLOCK        
            226_0  COME_FROM_LOOP       88  '88'

 L. 335       226  BUILD_LIST_0          0 
              228  STORE_FAST               'sequence'

 L. 337       230  LOAD_FAST                'out_sequence'
          232_234  POP_JUMP_IF_FALSE   270  'to 270'

 L. 338       236  LOAD_FAST                'sequence'
              238  LOAD_METHOD              append
              240  LOAD_FAST                'out_sequence'
              242  CALL_METHOD_1         1  '1 positional argument'
              244  POP_TOP          

 L. 340       246  LOAD_FAST                'sequence'
              248  LOAD_METHOD              append
              250  LOAD_GLOBAL              SoftSleepElement
              252  LOAD_GLOBAL              clock
              254  LOAD_METHOD              interval_in_sim_minutes
              256  LOAD_DEREF               'self'
              258  LOAD_ATTR                fade
              260  LOAD_ATTR                out_time
              262  CALL_METHOD_1         1  '1 positional argument'
              264  CALL_FUNCTION_1       1  '1 positional argument'
              266  CALL_METHOD_1         1  '1 positional argument'
              268  POP_TOP          
            270_0  COME_FROM           232  '232'

 L. 342       270  LOAD_FAST                'sequence'
              272  LOAD_METHOD              append
              274  LOAD_FAST                'moves'
              276  CALL_METHOD_1         1  '1 positional argument'
              278  POP_TOP          

 L. 344       280  LOAD_FAST                'in_sequence'
          282_284  POP_JUMP_IF_FALSE   296  'to 296'

 L. 345       286  LOAD_FAST                'sequence'
              288  LOAD_METHOD              append
              290  LOAD_FAST                'in_sequence'
              292  CALL_METHOD_1         1  '1 positional argument'
              294  POP_TOP          
            296_0  COME_FROM           282  '282'

 L. 347       296  LOAD_GLOBAL              build_element
              298  LOAD_FAST                'sequence'
              300  LOAD_GLOBAL              CleanupType
              302  LOAD_ATTR                RunAll
              304  LOAD_CONST               ('critical',)
              306  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              308  STORE_FAST               'element'

 L. 349       310  LOAD_GLOBAL              services
              312  LOAD_METHOD              time_service
              314  CALL_METHOD_0         0  '0 positional arguments'
              316  LOAD_ATTR                sim_timeline
              318  LOAD_METHOD              schedule
              320  LOAD_FAST                'element'
              322  CALL_METHOD_1         1  '1 positional argument'
              324  POP_TOP          

Parse error at or near `MAKE_FUNCTION_9' instruction at offset 190