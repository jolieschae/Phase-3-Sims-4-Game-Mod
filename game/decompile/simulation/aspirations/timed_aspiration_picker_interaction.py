# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\aspirations\timed_aspiration_picker_interaction.py
# Compiled at: 2018-06-05 13:58:30
# Size of source mod 2**32: 4304 bytes
from event_testing.resolver import SingleSimResolver
from event_testing.tests import TunableTestSetWithTooltip
from interactions import ParticipantType
from interactions.base.picker_interaction import PickerSuperInteraction
from interactions.utils.loot import LootActions
from interactions.utils.tunable import TunableContinuation
from sims4.tuning.tunable import TunableList, TunableTuple, TunableReference
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
from ui.ui_dialog_picker import UiItemPicker, BasePickerRow
import services, sims4.resources

class TimedAspirationPickerInteraction(PickerSuperInteraction):
    INSTANCE_TUNABLES = {'picker_dialog':UiItemPicker.TunableFactory(description='\n            The timed aspiration picker dialog.\n            ',
       tuning_group=GroupNames.PICKERTUNING), 
     'timed_aspirations':TunableList(description='\n            The list of timed aspirations available to select.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION)),
       class_restrictions='TimedAspiration',
       pack_safe=True),
       unique_entries=True,
       tuning_group=GroupNames.PICKERTUNING), 
     'actor_continuation':TunableContinuation(description='\n            If specified, a continuation to push on the actor when a picker \n            selection has been made.\n            ',
       locked_args={'actor': ParticipantType.Actor},
       tuning_group=GroupNames.PICKERTUNING), 
     'loot_on_picker_selection':TunableList(description="\n            Loot that will be applied to the Sim if an aspiration is selected.\n            It will not be applied if the user doesn't select an aspiration.\n            ",
       tunable=LootActions.TunableReference(),
       tuning_group=GroupNames.PICKERTUNING)}

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog((self.sim), target_sim=(self.sim))
        return True
        if False:
            yield None

    @flexmethod
    def picker_rows_gen--- This code section failed: ---

 L.  67         0  LOAD_FAST                'inst'
                2  LOAD_CONST               None
                4  COMPARE_OP               is-not
                6  POP_JUMP_IF_FALSE    12  'to 12'
                8  LOAD_FAST                'inst'
               10  JUMP_FORWARD         14  'to 14'
             12_0  COME_FROM             6  '6'
               12  LOAD_FAST                'cls'
             14_0  COME_FROM            10  '10'
               14  STORE_DEREF              'inst_or_cls'

 L.  69        16  LOAD_GLOBAL              SingleSimResolver
               18  LOAD_FAST                'target'
               20  LOAD_ATTR                sim_info
               22  CALL_FUNCTION_1       1  '1 positional argument'
               24  STORE_FAST               'resolver'

 L.  70        26  SETUP_LOOP          158  'to 158'
               28  LOAD_DEREF               'inst_or_cls'
               30  LOAD_ATTR                timed_aspirations
               32  GET_ITER         
             34_0  COME_FROM            72  '72'
               34  FOR_ITER            156  'to 156'
               36  STORE_FAST               'timed_aspiration'

 L.  71        38  LOAD_FAST                'timed_aspiration'
               40  LOAD_ATTR                tests
               42  LOAD_ATTR                run_tests
               44  LOAD_FAST                'resolver'
               46  LOAD_CONST               True
               48  LOAD_CONST               ('search_for_tooltip',)
               50  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
               52  STORE_FAST               'test_result'

 L.  72        54  LOAD_FAST                'test_result'
               56  LOAD_ATTR                result
               58  STORE_FAST               'is_enable'

 L.  76        60  LOAD_FAST                'is_enable'
               62  POP_JUMP_IF_TRUE     74  'to 74'
               64  LOAD_FAST                'test_result'
               66  LOAD_ATTR                tooltip
               68  LOAD_CONST               None
               70  COMPARE_OP               is-not
               72  POP_JUMP_IF_FALSE    34  'to 34'
             74_0  COME_FROM            62  '62'

 L.  77        74  LOAD_FAST                'test_result'
               76  LOAD_ATTR                tooltip
               78  LOAD_CONST               None
               80  COMPARE_OP               is-not
               82  POP_JUMP_IF_FALSE   106  'to 106'

 L.  78        84  LOAD_FAST                'test_result'
               86  LOAD_ATTR                tooltip
               88  LOAD_CONST               ('tooltip',)
               90  BUILD_CONST_KEY_MAP_1     1 
               92  LOAD_CLOSURE             'inst_or_cls'
               94  BUILD_TUPLE_1         1 
               96  LOAD_LAMBDA              '<code_object <lambda>>'
               98  LOAD_STR                 'TimedAspirationPickerInteraction.picker_rows_gen.<locals>.<lambda>'
              100  MAKE_FUNCTION_10         'keyword-only, closure'
              102  STORE_FAST               'row_tooltip'
              104  JUMP_FORWARD        110  'to 110'
            106_0  COME_FROM            82  '82'

 L.  81       106  LOAD_CONST               None
              108  STORE_FAST               'row_tooltip'
            110_0  COME_FROM           104  '104'

 L.  82       110  LOAD_GLOBAL              BasePickerRow
              112  LOAD_FAST                'is_enable'

 L.  83       114  LOAD_DEREF               'inst_or_cls'
              116  LOAD_METHOD              create_localized_string
              118  LOAD_FAST                'timed_aspiration'
              120  LOAD_ATTR                display_name
              122  CALL_METHOD_1         1  '1 positional argument'

 L.  84       124  LOAD_FAST                'timed_aspiration'
              126  LOAD_ATTR                display_icon

 L.  85       128  LOAD_DEREF               'inst_or_cls'
              130  LOAD_METHOD              create_localized_string
              132  LOAD_FAST                'timed_aspiration'
              134  LOAD_ATTR                display_description
              136  CALL_METHOD_1         1  '1 positional argument'

 L.  86       138  LOAD_FAST                'row_tooltip'

 L.  87       140  LOAD_FAST                'timed_aspiration'
              142  LOAD_CONST               ('is_enable', 'name', 'icon', 'row_description', 'row_tooltip', 'tag')
              144  CALL_FUNCTION_KW_6     6  '6 total positional and keyword args'
              146  STORE_FAST               'row'

 L.  88       148  LOAD_FAST                'row'
              150  YIELD_VALUE      
              152  POP_TOP          
              154  JUMP_BACK            34  'to 34'
              156  POP_BLOCK        
            158_0  COME_FROM_LOOP       26  '26'

Parse error at or near `STORE_FAST' instruction at offset 102

    def on_choice_selected(self, choice_tag, **kwargs):
        if choice_tag is None:
            return
        self.target.aspiration_tracker.activate_timed_aspiration(choice_tag)
        resolver = self.get_resolver()
        for loot_action in self.loot_on_picker_selection:
            loot_action.apply_to_resolver(resolver)

        if self.actor_continuation:
            self.push_tunable_continuation(self.actor_continuation)