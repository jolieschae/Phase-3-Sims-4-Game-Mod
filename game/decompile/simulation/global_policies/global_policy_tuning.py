# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\global_policies\global_policy_tuning.py
# Compiled at: 2019-04-26 20:11:59
# Size of source mod 2**32: 8678 bytes
from date_and_time import TimeSpan
from display_snippet_tuning import DisplaySnippet
from elements import SleepElement
from event_testing.resolver import SingleSimResolver
from event_testing.test_events import TestEvent
from global_policies.global_policy_effects import GlobalPolicyEffectVariants
from global_policies.global_policy_enums import GlobalPolicyProgressEnum, GlobalPolicyTokenType
from interactions.utils.loot import LootActions
from sims4.localization import TunableLocalizedStringFactory, LocalizationHelperTuning
from sims4.tuning.tunable import TunableList, TunableRange
import services, sims4
logger = sims4.log.Logger('Global Policy Tuning', default_owner='shipark')

class GlobalPolicy(DisplaySnippet):
    GLOBAL_POLICY_TOKEN_NON_ACTIVE = TunableLocalizedStringFactory(description='\n        Display string that appears when trying to use a Global Policy Token\n        referencing a non-active Global Policy.\n        ')
    INSTANCE_TUNABLES = {'decay_days':TunableRange(description='\n            The number of days it will take for the global policy to revert to\n            not-complete. Decay begins when the policy is completed.\n            ',
       tunable_type=int,
       default=5,
       minimum=0), 
     'progress_initial_value':TunableRange(description='\n            The initial value of global policy progress. Progress begins when\n            the policy is first set to in-progress.\n            ',
       tunable_type=int,
       default=0,
       minimum=0), 
     'progress_max_value':TunableRange(description='\n            The max value of global policy progress. Once the policy progress\n            reaches the max threshold, global policy state becomes complete.\n            ',
       tunable_type=int,
       default=100,
       minimum=1), 
     'loot_on_decay':TunableList(description='\n            A list of loot actions that will be run when the policy decays.\n            ',
       tunable=LootActions.TunableReference(description='\n                The loot action will target the active Sim.\n                ')), 
     'loot_on_complete':TunableList(description='\n            A list of loot actions that will be run when the policy is complete.\n            ',
       tunable=LootActions.TunableReference(description='\n                The loot action will target the active Sim.\n                ')), 
     'global_policy_effects':TunableList(description='\n            Actions to apply when the global policy is enacted.\n            ',
       tunable=GlobalPolicyEffectVariants(description='\n                The action to apply.\n                '))}

    @classmethod
    def _verify_tuning_callback(cls):
        if cls.progress_max_value < cls.progress_initial_value:
            logger.error('Global Policy {} has a max value less than the initial value. This is not allowed.', cls)

    def __init__(self, progress_initial_value=None, **kwargs):
        (super().__init__)(**kwargs)
        self._progress_state = GlobalPolicyProgressEnum.NOT_STARTED
        self._progress_value = 0
        self.decay_handler = None
        self.end_time_from_load = 0

    @property
    def progress_state(self):
        return self._progress_state

    @property
    def progress_value(self):
        return self._progress_value

    def pre_load(self, global_policy_data):
        self.set_progress_state((GlobalPolicyProgressEnum(global_policy_data.progress_state)), from_load=True)
        self.set_progress_value((global_policy_data.progress_value), from_load=True)
        if global_policy_data.decay_days != 0:
            self.end_time_from_load = global_policy_data.decay_days

    def set_progress_state(self, progress_enum, from_load=False):
        old_state = self._progress_state
        self._progress_state = progress_enum
        if old_state != self._progress_state:
            if not from_load:
                services.get_event_manager().process_event((TestEvent.GlobalPolicyProgress), custom_keys=(type(self), self))

    def set_progress_value(self, new_value, from_load=False):
        self._progress_value = new_value
        if not from_load:
            self._process_new_value(new_value)
        return self.progress_state

    def _process_new_value--- This code section failed: ---

 L. 154         0  LOAD_FAST                'new_value'
                2  LOAD_FAST                'self'
                4  LOAD_ATTR                progress_initial_value
                6  COMPARE_OP               <=
                8  POP_JUMP_IF_FALSE    70  'to 70'
               10  LOAD_FAST                'self'
               12  LOAD_ATTR                progress_state
               14  LOAD_GLOBAL              GlobalPolicyProgressEnum
               16  LOAD_ATTR                NOT_STARTED
               18  COMPARE_OP               !=
               20  POP_JUMP_IF_FALSE    70  'to 70'

 L. 155        22  LOAD_FAST                'self'
               24  LOAD_METHOD              set_progress_state
               26  LOAD_GLOBAL              GlobalPolicyProgressEnum
               28  LOAD_ATTR                NOT_STARTED
               30  CALL_METHOD_1         1  '1 positional argument'
               32  POP_TOP          

 L. 156        34  LOAD_CONST               None
               36  LOAD_FAST                'self'
               38  STORE_ATTR               decay_handler

 L. 157        40  SETUP_LOOP          158  'to 158'
               42  LOAD_FAST                'self'
               44  LOAD_ATTR                global_policy_effects
               46  GET_ITER         
               48  FOR_ITER             66  'to 66'
               50  STORE_FAST               'effect'

 L. 158        52  LOAD_FAST                'effect'
               54  LOAD_METHOD              turn_off
               56  LOAD_FAST                'self'
               58  LOAD_ATTR                guid64
               60  CALL_METHOD_1         1  '1 positional argument'
               62  POP_TOP          
               64  JUMP_BACK            48  'to 48'
               66  POP_BLOCK        
               68  JUMP_FORWARD        158  'to 158'
             70_0  COME_FROM            20  '20'
             70_1  COME_FROM             8  '8'

 L. 159        70  LOAD_FAST                'new_value'
               72  LOAD_FAST                'self'
               74  LOAD_ATTR                progress_max_value
               76  COMPARE_OP               >=
               78  POP_JUMP_IF_FALSE   134  'to 134'
               80  LOAD_FAST                'self'
               82  LOAD_ATTR                progress_state
               84  LOAD_GLOBAL              GlobalPolicyProgressEnum
               86  LOAD_ATTR                COMPLETE
               88  COMPARE_OP               !=
               90  POP_JUMP_IF_FALSE   134  'to 134'

 L. 160        92  LOAD_FAST                'self'
               94  LOAD_METHOD              set_progress_state
               96  LOAD_GLOBAL              GlobalPolicyProgressEnum
               98  LOAD_ATTR                COMPLETE
              100  CALL_METHOD_1         1  '1 positional argument'
              102  POP_TOP          

 L. 161       104  SETUP_LOOP          158  'to 158'
              106  LOAD_FAST                'self'
              108  LOAD_ATTR                global_policy_effects
              110  GET_ITER         
              112  FOR_ITER            130  'to 130'
              114  STORE_FAST               'effect'

 L. 162       116  LOAD_FAST                'effect'
              118  LOAD_METHOD              turn_on
              120  LOAD_FAST                'self'
              122  LOAD_ATTR                guid64
              124  CALL_METHOD_1         1  '1 positional argument'
              126  POP_TOP          
              128  JUMP_BACK           112  'to 112'
              130  POP_BLOCK        
              132  JUMP_FORWARD        158  'to 158'
            134_0  COME_FROM            90  '90'
            134_1  COME_FROM            78  '78'

 L. 163       134  LOAD_FAST                'self'
              136  LOAD_ATTR                progress_state
              138  LOAD_GLOBAL              GlobalPolicyProgressEnum
              140  LOAD_ATTR                IN_PROGRESS
              142  COMPARE_OP               !=
              144  POP_JUMP_IF_FALSE   158  'to 158'

 L. 164       146  LOAD_FAST                'self'
              148  LOAD_METHOD              set_progress_state
              150  LOAD_GLOBAL              GlobalPolicyProgressEnum
              152  LOAD_ATTR                IN_PROGRESS
              154  CALL_METHOD_1         1  '1 positional argument'
              156  POP_TOP          
            158_0  COME_FROM           144  '144'
            158_1  COME_FROM           132  '132'
            158_2  COME_FROM_LOOP      104  '104'
            158_3  COME_FROM            68  '68'
            158_4  COME_FROM_LOOP       40  '40'

Parse error at or near `COME_FROM_LOOP' instruction at offset 158_2

    def apply_policy_loot_to_active_sim(self, loot_list, resolver=None):
        if resolver is None:
            resolver = SingleSimResolver(services.active_sim_info())
        for loot_action in loot_list:
            loot_action.apply_to_resolver(resolver)

    def decay_policy(self, timeline):
        yield timeline.run_child(SleepElement(TimeSpan.ZERO))
        services.global_policy_service().set_global_policy_progress(self, self.progress_initial_value)
        self.decay_handler = None
        self.apply_policy_loot_to_active_sim(self.loot_on_decay)

    @classmethod
    def get_non_active_display(cls, token_data):
        if token_data.token_property == GlobalPolicyTokenType.NAME:
            return LocalizationHelperTuning.get_raw_text(token_data.global_policy.display_name())
        if token_data.token_property == GlobalPolicyTokenType.PROGRESS:
            return LocalizationHelperTuning.get_raw_text(cls.GLOBAL_POLICY_TOKEN_NON_ACTIVE())
        logger.error('Invalid Global Policy Property {} tuned on the Global Policy token.'.format(token_data.property))

    def get_active_policy_display(self, token_data):
        if token_data.token_property == GlobalPolicyTokenType.NAME:
            return LocalizationHelperTuning.get_raw_text(self.display_name())
        if token_data.token_property == GlobalPolicyTokenType.PROGRESS:
            progress_percentage_str = str(int(round(float(self.progress_value) / float(self.progress_max_value), 2) * 100))
            return LocalizationHelperTuning.get_raw_text(progress_percentage_str)
        logger.error('Invalid Global Policy Property {} tuned on the Global Policy token.'.format(token_data.property))