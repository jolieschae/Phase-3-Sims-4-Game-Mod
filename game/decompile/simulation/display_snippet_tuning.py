# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\display_snippet_tuning.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 20532 bytes
from collections import namedtuple
from event_testing.resolver import InteractionResolver
from event_testing.tests import TunableTestSetWithTooltip
from interactions import ParticipantTypeSim
from interactions.base.picker_interaction import PickerSuperInteraction
from interactions.utils.display_mixin import get_display_mixin
from interactions.utils.localization_tokens import LocalizationTokens
from interactions.utils.loot import LootActions
from interactions.utils.tunable import TunableContinuation
from sims.university.university_scholarship_tuning import ScholarshipMaintenaceType, ScholarshipEvaluationType, MeritEvaluation
from sims4.localization import TunableLocalizedString, TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableEnumFlags, TunableList, TunableTuple, TunableReference, Tunable, TunableRange, TunableVariant, OptionalTunable, AutoFactoryInit, HasTunableSingletonFactory
from sims4.tuning.tunable_base import GroupNames, ExportModes
from sims4.utils import flexmethod
from singletons import DEFAULT
from ui.ui_dialog_picker import TunablePickerDialogVariant, ObjectPickerTuningFlags, BasePickerRow
import enum, event_testing, services, sims4.tuning
logger = sims4.log.Logger('Display Snippet', default_owner='shipark')
SnippetDisplayMixin = get_display_mixin(use_string_tokens=True, has_description=True, has_icon=True, has_tooltip=True, enabled_by_default=True,
  has_secondary_icon=True,
  export_modes=(ExportModes.All))

class DisplaySnippet(SnippetDisplayMixin, metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    pass


class ScholarshipAmountEnum(enum.Int, export=False):
    FIXED_AMOUNT = 0
    EVALUATION_TYPE = 1


class Scholarship(DisplaySnippet):

    @classmethod
    def _verify_tuning_callback(cls):
        if not cls._display_data.instance_display_name:
            logger.error("Scholarships require a display name, but scholarship ({})'s display name has a None value.", str(cls))
        else:
            if not cls._display_data.instance_display_description:
                logger.error("Scholarships require a display description, but scholarship ({})'s display description has a None value.", str(cls))
            cls._display_data.instance_display_icon or logger.error("Scholarships require a display icon, but scholarship ({})'s display icon has a None value.", str(cls))

    INSTANCE_TUNABLES = {'evaluation_type':ScholarshipEvaluationType.TunableFactory(description='\n            The evaluation type used by this scholarship.\n            '), 
     'maintenance_type':ScholarshipMaintenaceType.TunableFactory(description='\n            The maintenance requirement of this scholarship.\n            '), 
     'amount':TunableVariant(description='\n            If fixed_amount, use the tuned value when receiving the scholarship.\n            If evaluation_type, use the evaluation type to determine what the value of \n            the scholarship should be. \n            ',
       fixed_amount=TunableTuple(amount=TunableRange(description='\n                    The amount of money to award a Sim if they receive this scholarship.\n                    ',
       tunable_type=int,
       default=50,
       minimum=1),
       locked_args={'amount_enum': ScholarshipAmountEnum.FIXED_AMOUNT}),
       evaluation_type=TunableTuple(locked_args={'amount_enum': ScholarshipAmountEnum.EVALUATION_TYPE}))}

    @classmethod
    def verify_tuning_callback(cls):
        if cls.amount.amount_enum == ScholarshipAmountEnum.EVALUATION_TYPE:
            if not isinstance(cls.evaluation_type, MeritEvaluation):
                logger.error('Scholarship ({}) specified its value to be determined                    by use-evaluation-type, but evaluation type ({}) does not support                    dynamic value generation.', cls, cls.evaluation_type)

    @classmethod
    def get_value(cls, sim_info):
        if cls.amount.amount_enum == ScholarshipAmountEnum.FIXED_AMOUNT:
            return cls.amount.amount
        return cls.evaluation_type.get_value(sim_info)


class Organization(DisplaySnippet):
    INSTANCE_TUNABLES = {'progress_statistic':TunableReference(description='\n            The Ranked Statistic represents Organization Progress.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC),
       class_restrictions='RankedStatistic',
       export_modes=ExportModes.All), 
     'hidden':Tunable(description='\n            If True, then the organization is hidden from the organization panel.\n            ',
       tunable_type=bool,
       default=False,
       export_modes=ExportModes.All), 
     'organization_task_data':TunableList(description='\n            List of possible tested organization tasks that can be offered to \n            active organization members.\n            ',
       tunable=TunableTuple(description='\n                Tuple of test and aspirations that is run on activating\n                organization tasks.\n                ',
       tests=event_testing.tests.TunableTestSet(description='\n                   Tests run when the task is activated. If tests do not pass,\n                   the tasks are not considered for assignment.\n                   '),
       organization_task=TunableReference(description='\n                    An aspiration to use for task completion.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION)),
       class_restrictions='AspirationOrganizationTask'))), 
     'organization_filter':TunableReference(description="\n            Terms to add a member to the Organization's membership list.\n            ",
       manager=services.get_instance_manager(sims4.resources.Types.SIM_FILTER),
       class_restrictions=('TunableSimFilter', )), 
     'no_events_are_scheduled_string':OptionalTunable(description='\n            If enabled and the organization has no scheduled events, this text\n            will be displayed in the org panel background.\n            ',
       tunable=TunableLocalizedString(description='\n                The string to show in the organization panel if there are no scheduled\n                events.\n                '))}


snippet_override_data = namedtuple('SnippetDisplayData', ('display_name', 'display_description',
                                                          'display_tooltip', 'display_icon'))

class _DisplaySnippetTextOverrides(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'display_name_override':OptionalTunable(description='\n            If enabled, the localized name override for each display snippet in \n            the list. \n            ',
       tunable=TunableLocalizedStringFactory(description='\n                The localized name override for each display snippet in \n                the list. \n                ')), 
     'display_description_override':OptionalTunable(description='\n            If enabled, the localized description override for each display \n            snippet in the list. \n            ',
       tunable=TunableLocalizedStringFactory(description='\n                The localized description override for each display snippet in \n                the list. \n                ')), 
     'display_tooltip_override':OptionalTunable(description='\n            If enabled, the localized tooltip override for each display \n            snippet in the list. \n            ',
       tunable=TunableLocalizedStringFactory(description='\n               The localized tooltip override for each display snippet in the \n               list. \n               '))}

    def __call__(self, original_snippet):
        name = self.display_name_override if self.display_name_override is not None else original_snippet.display_name
        description = self.display_description_override if self.display_description_override is not None else original_snippet.display_description
        tooltip = self.display_tooltip_override if self.display_tooltip_override is not None else original_snippet.display_tooltip
        return snippet_override_data(display_name=name, display_description=description,
          display_tooltip=tooltip,
          display_icon=(original_snippet.display_icon))


class _PickerDisplaySnippet(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'display_snippet':TunableReference(description='\n            A display snippet that holds the display data that will\n            populate the row in the picker.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SNIPPET),
       class_restrictions='DisplaySnippet',
       allow_none=False), 
     'loot_on_selected':TunableList(description='\n            A list of loot actions that will be applied to the subject Sim.\n            ',
       tunable=LootActions.TunableReference(description='\n                A loot action applied to the subject Sim.\n                ')), 
     'tests':TunableTestSetWithTooltip(description='\n            Test set that must pass for this snippet to be available.\n            NOTE: A tooltip test result will take priority over any\n            instance display tooltip tuned in the display snippet.\n            \n            ID of the snippet will be the PickedItemID participant\n            '), 
     'display_snippet_text_tokens':LocalizationTokens.TunableFactory(description='\n            Localization tokens passed into the display snippet text fields.\n            These will be appended to the list of tokens when evaluating \n            strings for this snippet. \n            ',
       tuning_group=GroupNames.PICKERTUNING)}

    def test(self, resolver):
        return self.tests.run_tests(resolver, search_for_tooltip=True)


class DisplaySnippetPickerSuperInteraction(PickerSuperInteraction):
    INSTANCE_TUNABLES = {'picker_dialog':TunablePickerDialogVariant(description='\n            The item picker dialog.\n            ',
       available_picker_flags=ObjectPickerTuningFlags.ITEM,
       tuning_group=GroupNames.PICKERTUNING), 
     'subject':TunableEnumFlags(description="\n            To whom 'loot on selected' should be applied.\n            ",
       enum_type=ParticipantTypeSim,
       default=ParticipantTypeSim.Actor,
       tuning_group=GroupNames.PICKERTUNING), 
     'display_snippets':TunableList(description='\n            The list of display snippets available to select and paired loot actions\n            that will run if selected.\n            ',
       tunable=_PickerDisplaySnippet.TunableFactory(description='\n                Display snippet available to select.\n                '),
       tuning_group=GroupNames.PICKERTUNING), 
     'display_snippet_text_tokens':LocalizationTokens.TunableFactory(description='\n            Localization tokens passed into the display snippet text fields.\n            \n            When acting on the individual items within the snippet list, the \n            following text tokens will be appended to this list of tokens (in \n            order):\n            0: snippet instance display name\n            1: snippet instance display description\n            2: snippet instance display tooltip\n            3: tokens tuned alongside individual snippets within the snippet list\n            ',
       tuning_group=GroupNames.PICKERTUNING), 
     'display_snippet_text_overrides':OptionalTunable(description='\n            If enabled, display snippet text overrides for all snippets \n            to be displayed in the picker. \n            \n            Can be used together with the display snippet text tokens to \n            act as text wrappers around the existing snippet display data.\n            ',
       tunable=_DisplaySnippetTextOverrides.TunableFactory(description='\n                Display snippet text overrides for all snippets to be displayed\n                in the picker. \n            \n                Can be used together with the display snippet text tokens to \n                act as text wrappers around the existing snippet display data.\n                '),
       tuning_group=GroupNames.PICKERTUNING), 
     'continuations':TunableList(description='\n            List of continuations to push when a snippet is selected.\n            \n            ID of the snippet will be the PickedItemID participant in the \n            continuation.\n            ',
       tunable=TunableContinuation(),
       tuning_group=GroupNames.PICKERTUNING), 
     'run_continuations_on_no_selection':Tunable(description='\n            Checked, runs continuations regardless if anything is selected.\n            Unchecked, continuations are only run if something is selected.\n            ',
       tunable_type=bool,
       default=True,
       tuning_group=GroupNames.PICKERTUNING)}

    @classmethod
    def has_valid_choice(cls, target, context, **kwargs):
        snippet_count = 0
        for _ in (cls.picker_rows_gen)(target, context, **kwargs):
            snippet_count += 1
            if snippet_count >= cls.picker_dialog.min_selectable:
                return True

        return False

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog((self.sim), target_sim=(self.sim))
        return True
        if False:
            yield None

    @flexmethod
    def picker_rows_gen--- This code section failed: ---

 L. 375         0  LOAD_FAST                'inst'
                2  LOAD_CONST               None
                4  COMPARE_OP               is-not
                6  POP_JUMP_IF_FALSE    12  'to 12'
                8  LOAD_FAST                'inst'
               10  JUMP_FORWARD         14  'to 14'
             12_0  COME_FROM             6  '6'
               12  LOAD_FAST                'cls'
             14_0  COME_FROM            10  '10'
               14  STORE_FAST               'inst_or_cls'

 L. 376        16  LOAD_FAST                'target'
               18  LOAD_GLOBAL              DEFAULT
               20  COMPARE_OP               is-not
               22  POP_JUMP_IF_FALSE    28  'to 28'
               24  LOAD_FAST                'target'
               26  JUMP_FORWARD         32  'to 32'
             28_0  COME_FROM            22  '22'
               28  LOAD_FAST                'inst'
               30  LOAD_ATTR                target
             32_0  COME_FROM            26  '26'
               32  STORE_FAST               'target'

 L. 377        34  LOAD_FAST                'context'
               36  LOAD_GLOBAL              DEFAULT
               38  COMPARE_OP               is-not
               40  POP_JUMP_IF_FALSE    46  'to 46'
               42  LOAD_FAST                'context'
               44  JUMP_FORWARD         50  'to 50'
             46_0  COME_FROM            40  '40'
               46  LOAD_FAST                'inst'
               48  LOAD_ATTR                context
             50_0  COME_FROM            44  '44'
               50  STORE_FAST               'context'

 L. 378        52  LOAD_GLOBAL              InteractionResolver
               54  LOAD_FAST                'cls'
               56  LOAD_FAST                'inst'
               58  LOAD_FAST                'target'
               60  LOAD_FAST                'context'
               62  LOAD_CONST               ('target', 'context')
               64  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
               66  STORE_FAST               'resolver'

 L. 380        68  LOAD_FAST                'inst_or_cls'
               70  LOAD_ATTR                display_snippet_text_tokens
               72  LOAD_METHOD              get_tokens
               74  LOAD_FAST                'resolver'
               76  CALL_METHOD_1         1  '1 positional argument'
               78  STORE_FAST               'general_tokens'

 L. 381        80  LOAD_FAST                'inst_or_cls'
               82  LOAD_ATTR                display_snippet_text_overrides
               84  STORE_FAST               'overrides'

 L. 383        86  LOAD_CONST               0
               88  STORE_FAST               'index'

 L. 384     90_92  SETUP_LOOP          410  'to 410'
               94  LOAD_FAST                'inst_or_cls'
               96  LOAD_ATTR                display_snippets
               98  GET_ITER         
          100_102  FOR_ITER            408  'to 408'
              104  STORE_FAST               'display_snippet_data'

 L. 385       106  LOAD_FAST                'display_snippet_data'
              108  LOAD_ATTR                display_snippet
              110  STORE_FAST               'display_snippet'

 L. 388       112  LOAD_GLOBAL              InteractionResolver
              114  LOAD_FAST                'cls'
              116  LOAD_FAST                'inst'
              118  LOAD_FAST                'target'
              120  LOAD_FAST                'context'
              122  LOAD_FAST                'display_snippet'
              124  LOAD_ATTR                guid64
              126  BUILD_SET_1           1 
              128  LOAD_CONST               ('target', 'context', 'picked_item_ids')
              130  CALL_FUNCTION_KW_5     5  '5 total positional and keyword args'
              132  STORE_FAST               'resolver'

 L. 389       134  LOAD_FAST                'display_snippet_data'
              136  LOAD_METHOD              test
              138  LOAD_FAST                'resolver'
              140  CALL_METHOD_1         1  '1 positional argument'
              142  STORE_FAST               'test_result'

 L. 390       144  LOAD_FAST                'test_result'
              146  LOAD_ATTR                result
              148  STORE_FAST               'is_enable'

 L. 391       150  LOAD_FAST                'is_enable'
              152  POP_JUMP_IF_TRUE    166  'to 166'
              154  LOAD_FAST                'test_result'
              156  LOAD_ATTR                tooltip
              158  LOAD_CONST               None
              160  COMPARE_OP               is-not
          162_164  POP_JUMP_IF_FALSE   398  'to 398'
            166_0  COME_FROM           152  '152'

 L. 395       166  LOAD_FAST                'display_snippet'
              168  LOAD_ATTR                display_name
              170  LOAD_CONST               None
              172  COMPARE_OP               is-not
              174  POP_JUMP_IF_FALSE   186  'to 186'
              176  LOAD_FAST                'display_snippet'
              178  LOAD_ATTR                display_name
              180  LOAD_FAST                'general_tokens'
              182  CALL_FUNCTION_EX      0  'positional arguments only'
              184  JUMP_FORWARD        188  'to 188'
            186_0  COME_FROM           174  '174'
              186  LOAD_CONST               None
            188_0  COME_FROM           184  '184'

 L. 397       188  LOAD_FAST                'display_snippet'
              190  LOAD_ATTR                display_description
              192  LOAD_CONST               None
              194  COMPARE_OP               is-not
              196  POP_JUMP_IF_FALSE   208  'to 208'
              198  LOAD_FAST                'display_snippet'
              200  LOAD_ATTR                display_description
              202  LOAD_FAST                'general_tokens'
              204  CALL_FUNCTION_EX      0  'positional arguments only'
              206  JUMP_FORWARD        210  'to 210'
            208_0  COME_FROM           196  '196'
              208  LOAD_CONST               None
            210_0  COME_FROM           206  '206'

 L. 399       210  LOAD_FAST                'display_snippet'
              212  LOAD_ATTR                display_tooltip
              214  LOAD_CONST               None
              216  COMPARE_OP               is-not
              218  POP_JUMP_IF_FALSE   230  'to 230'
              220  LOAD_FAST                'display_snippet'
              222  LOAD_ATTR                display_tooltip
              224  LOAD_FAST                'general_tokens'
              226  CALL_FUNCTION_EX      0  'positional arguments only'
              228  JUMP_FORWARD        232  'to 232'
            230_0  COME_FROM           218  '218'
              230  LOAD_CONST               None
            232_0  COME_FROM           228  '228'
              232  BUILD_TUPLE_3         3 
              234  STORE_FAST               'snippet_default_tokens'

 L. 401       236  LOAD_FAST                'display_snippet_data'
              238  LOAD_ATTR                display_snippet_text_tokens
              240  LOAD_METHOD              get_tokens
              242  LOAD_FAST                'resolver'
              244  CALL_METHOD_1         1  '1 positional argument'
              246  STORE_FAST               'snippet_additional_tokens'

 L. 402       248  LOAD_FAST                'general_tokens'
              250  LOAD_FAST                'snippet_default_tokens'
              252  BINARY_ADD       
              254  LOAD_FAST                'snippet_additional_tokens'
              256  BINARY_ADD       
              258  STORE_DEREF              'tokens'

 L. 405       260  LOAD_FAST                'overrides'
              262  LOAD_CONST               None
              264  COMPARE_OP               is-not
          266_268  POP_JUMP_IF_FALSE   280  'to 280'

 L. 406       270  LOAD_FAST                'overrides'
              272  LOAD_FAST                'display_snippet_data'
              274  LOAD_ATTR                display_snippet
              276  CALL_FUNCTION_1       1  '1 positional argument'
              278  STORE_FAST               'display_snippet'
            280_0  COME_FROM           266  '266'

 L. 409       280  LOAD_FAST                'test_result'
              282  LOAD_ATTR                tooltip
              284  LOAD_CONST               None
              286  COMPARE_OP               is
          288_290  POP_JUMP_IF_FALSE   296  'to 296'
              292  LOAD_CONST               None
              294  JUMP_FORWARD        314  'to 314'
            296_0  COME_FROM           288  '288'
              296  LOAD_FAST                'test_result'
              298  LOAD_ATTR                tooltip
              300  LOAD_CONST               ('tooltip',)
              302  BUILD_CONST_KEY_MAP_1     1 
              304  LOAD_CLOSURE             'tokens'
              306  BUILD_TUPLE_1         1 
              308  LOAD_LAMBDA              '<code_object <lambda>>'
              310  LOAD_STR                 'DisplaySnippetPickerSuperInteraction.picker_rows_gen.<locals>.<lambda>'
              312  MAKE_FUNCTION_10         'keyword-only, closure'
            314_0  COME_FROM           294  '294'
              314  STORE_FAST               'tooltip'

 L. 410       316  LOAD_FAST                'tooltip'
          318_320  POP_JUMP_IF_TRUE    358  'to 358'

 L. 411       322  LOAD_FAST                'display_snippet'
              324  LOAD_ATTR                display_tooltip
              326  LOAD_CONST               None
              328  COMPARE_OP               is
          330_332  POP_JUMP_IF_FALSE   338  'to 338'
              334  LOAD_CONST               None
              336  JUMP_FORWARD        356  'to 356'
            338_0  COME_FROM           330  '330'
              338  LOAD_FAST                'display_snippet'
              340  LOAD_ATTR                display_tooltip
              342  LOAD_CONST               ('tooltip',)
              344  BUILD_CONST_KEY_MAP_1     1 
              346  LOAD_CLOSURE             'tokens'
              348  BUILD_TUPLE_1         1 
              350  LOAD_LAMBDA              '<code_object <lambda>>'
              352  LOAD_STR                 'DisplaySnippetPickerSuperInteraction.picker_rows_gen.<locals>.<lambda>'
              354  MAKE_FUNCTION_10         'keyword-only, closure'
            356_0  COME_FROM           336  '336'
              356  STORE_FAST               'tooltip'
            358_0  COME_FROM           318  '318'

 L. 412       358  LOAD_GLOBAL              BasePickerRow
              360  LOAD_FAST                'is_enable'

 L. 413       362  LOAD_FAST                'display_snippet'
              364  LOAD_ATTR                display_name
              366  LOAD_DEREF               'tokens'
              368  CALL_FUNCTION_EX      0  'positional arguments only'

 L. 414       370  LOAD_FAST                'display_snippet'
              372  LOAD_ATTR                display_icon

 L. 415       374  LOAD_FAST                'index'

 L. 416       376  LOAD_FAST                'display_snippet'
              378  LOAD_ATTR                display_description
              380  LOAD_DEREF               'tokens'
              382  CALL_FUNCTION_EX      0  'positional arguments only'

 L. 417       384  LOAD_FAST                'tooltip'
              386  LOAD_CONST               ('is_enable', 'name', 'icon', 'tag', 'row_description', 'row_tooltip')
              388  CALL_FUNCTION_KW_6     6  '6 total positional and keyword args'
              390  STORE_FAST               'row'

 L. 418       392  LOAD_FAST                'row'
              394  YIELD_VALUE      
              396  POP_TOP          
            398_0  COME_FROM           162  '162'

 L. 419       398  LOAD_FAST                'index'
              400  LOAD_CONST               1
              402  INPLACE_ADD      
              404  STORE_FAST               'index'
              406  JUMP_BACK           100  'to 100'
              408  POP_BLOCK        
            410_0  COME_FROM_LOOP       90  '90'

Parse error at or near `COME_FROM' instruction at offset 314_0

    def _on_display_snippet_selected(self, picked_choice, **kwargs):
        resolver = (self.get_resolver)(**kwargs)
        for loot_on_selected in self.display_snippets[picked_choice].loot_on_selected:
            loot_on_selected.apply_to_resolver(resolver)

    def on_choice_selected(self, picked_choice, **kwargs):
        if picked_choice is None:
            if self.run_continuations_on_no_selection:
                for continuation in self.continuations:
                    self.push_tunable_continuation(continuation)

            return
        display_snippet = self.display_snippets[picked_choice].display_snippet
        picked_item_set = {display_snippet.guid64}
        self._on_display_snippet_selected(picked_choice, picked_item_ids=picked_item_set)
        for continuation in self.continuations:
            self.push_tunable_continuation(continuation, picked_item_ids=picked_item_set)