# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\aspirations\timed_aspiration_loot_op.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 7573 bytes
import enum, services, sims4, random
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunablePackSafeReference, TunableVariant, HasTunableSingletonFactory, AutoFactoryInit, Tunable, TunableList, TunableReference, TunableRange, TunableEnumEntry
from protocolbuffers import Sims_pb2
logger = sims4.log.Logger('Aspirations', default_owner='yecao')

class AddObjectiveActionType(enum.Int):
    INITIAL_ADD = 0
    OBJECTIVE_UPDATE = 1


class _AddObjectiveList(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'objectives':TunableList(description='\n            A list of objectives that can be added to the Timed Aspiration.\n            ',
       tunable=TunableReference(description='\n                    An objective to add.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.OBJECTIVE)),
       pack_safe=True)), 
     'number_to_add':TunableRange(description='\n            Number of objectives that will be added to Timed Aspiration, \n            objectives will be selected randomly from the list.\n            ',
       tunable_type=int,
       default=1,
       minimum=1), 
     'replace_completed_objective':Tunable(description='\n            The newly added objectives will replace completed objectives if checked.\n            Note: only objectives that are added to sim by AddObjective loot or at runtime can be replaced,\n                  Any objectives that are directly tuned to aspiration will not be changed.\n            ',
       tunable_type=bool,
       default=False), 
     'add_objective_action_type':TunableEnumEntry(description='\n            Action type for the add operation. \n            Choose InitialAdd if we want the objectives to be added to the TimedAspiration immediately \n            at the start of the timed aspiration.\n            Choose ObjectiveUpdate if the objective is added from completion loot of the previous objective \n            and needed to wait for the completion animation to be finished.\n            ',
       tunable_type=AddObjectiveActionType,
       default=AddObjectiveActionType.OBJECTIVE_UPDATE)}

    def __call__--- This code section failed: ---

 L.  69         0  LOAD_FAST                'self'
                2  LOAD_ATTR                objectives
                4  POP_JUMP_IF_TRUE     10  'to 10'

 L.  70         6  LOAD_CONST               None
                8  RETURN_VALUE     
             10_0  COME_FROM             4  '4'

 L.  71        10  LOAD_FAST                'subject'
               12  LOAD_ATTR                aspiration_tracker
               14  LOAD_METHOD              get_timed_aspiration_data
               16  LOAD_FAST                'source_op'
               18  LOAD_ATTR                aspiration
               20  CALL_METHOD_1         1  '1 positional argument'
               22  STORE_FAST               'timed_aspiration_data'

 L.  72        24  LOAD_FAST                'timed_aspiration_data'
               26  LOAD_CONST               None
               28  COMPARE_OP               is
               30  POP_JUMP_IF_FALSE    52  'to 52'

 L.  73        32  LOAD_GLOBAL              logger
               34  LOAD_METHOD              error
               36  LOAD_STR                 '{} does not have timed aspiration: {}. Sim should have the timed aspiration first to add more objectives on that aspiration.'

 L.  74        38  LOAD_FAST                'subject'
               40  LOAD_FAST                'source_op'
               42  LOAD_ATTR                aspiration
               44  CALL_METHOD_3         3  '3 positional arguments'
               46  POP_TOP          

 L.  75        48  LOAD_CONST               None
               50  RETURN_VALUE     
             52_0  COME_FROM            30  '30'

 L.  77        52  LOAD_FAST                'subject'
               54  LOAD_ATTR                aspiration_tracker
               56  LOAD_METHOD              get_objectives
               58  LOAD_FAST                'source_op'
               60  LOAD_ATTR                aspiration
               62  CALL_METHOD_1         1  '1 positional argument'
               64  STORE_FAST               'current_objectives'

 L.  78        66  LOAD_GLOBAL              list
               68  LOAD_FAST                'self'
               70  LOAD_ATTR                objectives
               72  CALL_FUNCTION_1       1  '1 positional argument'
               74  STORE_FAST               'new_objectives_list'

 L.  79        76  LOAD_GLOBAL              random
               78  LOAD_METHOD              shuffle
               80  LOAD_FAST                'new_objectives_list'
               82  CALL_METHOD_1         1  '1 positional argument'
               84  POP_TOP          

 L.  80        86  BUILD_LIST_0          0 
               88  STORE_FAST               'objectives_to_add'

 L.  83        90  SETUP_LOOP          150  'to 150'
             92_0  COME_FROM           142  '142'
               92  LOAD_GLOBAL              len
               94  LOAD_FAST                'objectives_to_add'
               96  CALL_FUNCTION_1       1  '1 positional argument'
               98  LOAD_FAST                'self'
              100  LOAD_ATTR                number_to_add
              102  COMPARE_OP               <
              104  POP_JUMP_IF_FALSE   148  'to 148'

 L.  84       106  LOAD_FAST                'new_objectives_list'
              108  LOAD_CONST               -1
              110  BINARY_SUBSCR    
              112  LOAD_FAST                'current_objectives'
              114  COMPARE_OP               not-in
              116  POP_JUMP_IF_FALSE   132  'to 132'

 L.  85       118  LOAD_FAST                'objectives_to_add'
              120  LOAD_METHOD              append
              122  LOAD_FAST                'new_objectives_list'
              124  LOAD_CONST               -1
              126  BINARY_SUBSCR    
              128  CALL_METHOD_1         1  '1 positional argument'
              130  POP_TOP          
            132_0  COME_FROM           116  '116'

 L.  86       132  LOAD_FAST                'new_objectives_list'
              134  LOAD_METHOD              pop
              136  CALL_METHOD_0         0  '0 positional arguments'
              138  POP_TOP          

 L.  87       140  LOAD_FAST                'new_objectives_list'
              142  POP_JUMP_IF_TRUE     92  'to 92'

 L.  88       144  BREAK_LOOP       
              146  JUMP_BACK            92  'to 92'
            148_0  COME_FROM           104  '104'
              148  POP_BLOCK        
            150_0  COME_FROM_LOOP       90  '90'

 L.  89       150  LOAD_FAST                'subject'
              152  LOAD_ATTR                aspiration_tracker
              154  LOAD_ATTR                register_additional_objectives
              156  LOAD_FAST                'source_op'
              158  LOAD_ATTR                aspiration
              160  LOAD_FAST                'objectives_to_add'
              162  LOAD_FAST                'self'
              164  LOAD_ATTR                replace_completed_objective
              166  LOAD_CONST               ('replace_completed_objective',)
              168  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              170  STORE_FAST               'new_objectives'

 L.  90       172  LOAD_LISTCOMP            '<code_object <listcomp>>'
              174  LOAD_STR                 '_AddObjectiveList.__call__.<locals>.<listcomp>'
              176  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              178  LOAD_FAST                'new_objectives'
              180  GET_ITER         
              182  CALL_FUNCTION_1       1  '1 positional argument'
              184  STORE_FAST               'tests'

 L.  91       186  LOAD_GLOBAL              services
              188  LOAD_METHOD              get_event_manager
              190  CALL_METHOD_0         0  '0 positional arguments'
              192  LOAD_METHOD              register_tests
              194  LOAD_FAST                'source_op'
              196  LOAD_ATTR                aspiration
              198  LOAD_FAST                'tests'
              200  CALL_METHOD_2         2  '2 positional arguments'
              202  POP_TOP          

 L.  94       204  LOAD_FAST                'subject'
              206  LOAD_ATTR                aspiration_tracker
              208  LOAD_METHOD              process_test_events_for_aspiration
              210  LOAD_FAST                'source_op'
              212  LOAD_ATTR                aspiration
              214  CALL_METHOD_1         1  '1 positional argument'
              216  POP_TOP          

 L.  95       218  LOAD_FAST                'self'
              220  LOAD_ATTR                add_objective_action_type
              222  LOAD_GLOBAL              AddObjectiveActionType
              224  LOAD_ATTR                INITIAL_ADD
              226  COMPARE_OP               ==
              228  POP_JUMP_IF_FALSE   246  'to 246'

 L.  96       230  LOAD_FAST                'timed_aspiration_data'
              232  LOAD_METHOD              send_timed_aspiration_to_client
              234  LOAD_GLOBAL              Sims_pb2
              236  LOAD_ATTR                TimedAspirationUpdate
              238  LOAD_ATTR                ADD
              240  CALL_METHOD_1         1  '1 positional argument'
              242  POP_TOP          
              244  JUMP_FORWARD        260  'to 260'
            246_0  COME_FROM           228  '228'

 L.  98       246  LOAD_FAST                'timed_aspiration_data'
              248  LOAD_METHOD              send_timed_aspiration_to_client
              250  LOAD_GLOBAL              Sims_pb2
              252  LOAD_ATTR                TimedAspirationUpdate
              254  LOAD_ATTR                OBJECTIVE_UPDATE
              256  CALL_METHOD_1         1  '1 positional argument'
              258  POP_TOP          
            260_0  COME_FROM           244  '244'

Parse error at or near `POP_BLOCK' instruction at offset 148


class _TimedAspirationActivate(HasTunableSingletonFactory, AutoFactoryInit):

    def __call__(self, subject, target, source_op):
        subject.aspiration_tracker.activate_timed_aspiration(source_op.aspiration)


class _TimedAspirationDeactivate(HasTunableSingletonFactory, AutoFactoryInit):

    def __call__(self, subject, target, source_op):
        subject.aspiration_tracker.deactivate_timed_aspiration(source_op.aspiration)


class TimedAspirationLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'aspiration':TunablePackSafeReference(description='\n            The timed aspiration we will do the loot op on. Only sim with active LOD will be able to\n            do the operations.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION),
       class_restrictions='TimedAspiration'), 
     'operation':TunableVariant(description='\n            Timed aspiration related operations to perform.\n            ',
       timed_aspiration_activate=_TimedAspirationActivate.TunableFactory,
       timed_aspiration_deactivate=_TimedAspirationDeactivate.TunableFactory,
       add_objective_list=_AddObjectiveList.TunableFactory,
       default='timed_aspiration_activate')}

    def __init__(self, operation, aspiration, **kwargs):
        (super().__init__)(**kwargs)
        self.aspiration = aspiration
        self.operation = operation

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if self.aspiration is None:
            logger.error('Aspiration is not specified in TimedAspirationLootOp.')
            return
        if subject is None:
            logger.error('Timed Aspiration loot found None owner sim. subject {}. Loot: {}', (self.subject),
              self, owner='yecao')
            return
        if subject.aspiration_tracker is None:
            logger.error('Aspiration tracker is not found for subject {}, aspiration tracker is only on sim with active LOD', subject, owner='yecao')
            return
        self.operation(subject, target, source_op=self)