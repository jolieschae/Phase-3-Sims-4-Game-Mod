# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\guidance\guidance_tip.py
# Compiled at: 2022-10-05 14:14:58
# Size of source mod 2**32: 22781 bytes
from distributor.system import Distributor
from sims4.localization import TunableLocalizedStringFactory, TunableLocalizedString
from sims4.tuning.tunable import TunableList, TunableReference, TunableTuple, Tunable, TunableEnumEntry, OptionalTunable, TunableRange, HasTunableReference, TunableResourceKey, TunableVariant, TunablePackSafeReference
from sims4.tuning.tunable_hash import TunableStringHash64
from sims4.tuning.tunable_base import ExportModes
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from ui.ui_tuning import TunableUiMessage
from guidance.guidance_tip_enums import GuidanceTipPlatformFilter, GuidanceTipGameState, GuidanceTipGroupConditionType, GuidanceTipRuleBoolen, GuidanceTipMode, GuidanceTipOptionType
from tutorials.tutorial_tip_enums import TutorialTipUiElement
import distributor.ops, enum, services, sims4.localization, sims4.resources, sims4.tuning.instances

class GuidanceTipUiMessage(TunableTuple):

    def __init__(self, **kwargs):
        (super().__init__)(ui_message_cmn=OptionalTunable(description='\n                Sends a message to the UI for a guidance tip.\n                ',
  display_name='UI Message Common',
  tunable=(TunableUiMessage()),
  tuning_group=GROUP_NAME_ACTIONS,
  export_modes=(ExportModes.ClientBinary)), 
         ui_message_ps4=OptionalTunable(description='\n                If set, overrides the ui_message_cmn to be specific to the PS4 platform\n                ',
  display_name='UI Message PS4 override',
  tunable=(TunableUiMessage()),
  tuning_group=GROUP_NAME_ACTIONS,
  export_modes=(ExportModes.ClientBinary)), 
         ui_message_xb1=OptionalTunable(description='\n                If set, overrides the ui_message_cmn to be specific to the XB1 platform\n                ',
  display_name='UI Message XboxOne override',
  tunable=(TunableUiMessage()),
  tuning_group=GROUP_NAME_ACTIONS,
  export_modes=(ExportModes.ClientBinary)), **kwargs)


class GuidanceTipAction(TunableVariant):

    def __init__(self, **kwargs):
        (super().__init__)(ui_message=GuidanceTipUiMessage(description='\n                Sends a message to the UI when this action is executed.\n                ',
  export_modes=(ExportModes.ClientBinary)), 
         activate_guidance_item=TunablePackSafeReference(description='\n                Guidance Item to activate after this action is executed.\n                ',
  manager=(services.get_instance_manager(sims4.resources.Types.GUIDANCE_TIP)),
  class_restrictions='GuidanceTip',
  export_modes=(ExportModes.ClientBinary)), 
         tutorial_tip_group=TunablePackSafeReference(description='\n                Tutorial tip group to show when this this action is executed.\n                ',
  manager=(services.get_instance_manager(sims4.resources.Types.TUTORIAL_TIP)),
  class_restrictions='TutorialTipGroup',
  export_modes=(ExportModes.ClientBinary)), 
         satisfy_item=TunablePackSafeReference(description='\n                Guidance item to satisfy when this this action is executed.\n                ',
  manager=(services.get_instance_manager(sims4.resources.Types.GUIDANCE_TIP)),
  class_restrictions='GuidanceTip',
  export_modes=(ExportModes.ClientBinary)), 
         unsatisfy_item=TunablePackSafeReference(description='\n                Guidance item to unsatisfy when this this action is executed.\n                ',
  manager=(services.get_instance_manager(sims4.resources.Types.GUIDANCE_TIP)),
  class_restrictions='GuidanceTip',
  export_modes=(ExportModes.ClientBinary)), 
         satisfy_guidance_item_group=TunablePackSafeReference(description='\n                Guidance item group to satisfy when this this action is executed.\n                ',
  manager=(services.get_instance_manager(sims4.resources.Types.GUIDANCE_TIP)),
  class_restrictions='GuidanceTipGroup',
  export_modes=(ExportModes.ClientBinary)), 
         unsatisfy_guidance_item_group=TunablePackSafeReference(description='\n                Guidance item group to unsatisfy when this this action is executed.\n                ',
  manager=(services.get_instance_manager(sims4.resources.Types.GUIDANCE_TIP)),
  class_restrictions='GuidanceTipGroup',
  export_modes=(ExportModes.ClientBinary)), **kwargs)


class GuidanceTipActionGroup(TunableTuple):

    def __init__(self, **kwargs):
        (super().__init__)(actions_on_activate=TunableList(description='\n                The Actions which will be performed when this option is activated.\n                ',
  tunable=(GuidanceTipAction()),
  export_modes=(ExportModes.ClientBinary)), 
         actions_on_success=TunableList(description='\n                The Actions which will be performed when a success is received by the running activate actions.\n                ',
  tunable=(GuidanceTipAction()),
  export_modes=(ExportModes.ClientBinary)), 
         actions_on_cancel=TunableList(description='\n                The Actions which will be performed when a cancel is received by the running activate actions.\n                ',
  tunable=(GuidanceTipAction()),
  export_modes=(ExportModes.ClientBinary)), 
         satisfy_on_activate=Tunable(description='\n                If enabled, the guidance item is satisfied when the actions are run.\n                ',
  tunable_type=bool,
  default=False,
  export_modes=(ExportModes.ClientBinary)), 
         satisfy_on_action_success=Tunable(description='\n                If enabled, the guidance item is satisfied when a success is received by the actions.\n                ',
  tunable_type=bool,
  default=True,
  export_modes=(ExportModes.ClientBinary)), 
         satisfy_on_action_cancel=Tunable(description='\n                If enabled, the guidance item is satisfied when a cancel is received by the actions.\n                ',
  tunable_type=bool,
  default=False,
  export_modes=(ExportModes.ClientBinary)), **kwargs)


class GuidanceTipCriterion(TunableVariant):

    def __init__(self, **kwargs):
        (super().__init__)(boolean=TunableEnumEntry(description='\n                Always or never\n                ',
  tunable_type=GuidanceTipRuleBoolen,
  default=(GuidanceTipRuleBoolen.ALWAYS)), 
         platform_filter=TunableEnumEntry(description='\n                The platforms on which this criterion is valid\n                ',
  tunable_type=GuidanceTipPlatformFilter,
  default=(GuidanceTipPlatformFilter.ALL_PLATFORMS)), 
         guidance_mode=TunableEnumEntry(description='\n                The guidance mode on which this criterion is valid\n                STANDARD allows this tip to be in the original / standard guidance mode.\n                DISABLED means this criterion is valid in any mode.\n                ',
  tunable_type=GuidanceTipMode,
  default=(GuidanceTipMode.STANDARD)), 
         game_state=TunableEnumEntry(description='\n                The game state the client must be in for this criterion to be valid.\n                ',
  tunable_type=GuidanceTipGameState,
  default=(GuidanceTipGameState.GAMESTATE_NONE)), 
         guidance_tip_group_satisfied=TunableList(description='\n                The Tip Groups that must be complete for this criteron to be valid.\n                ',
  tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.GUIDANCE_TIP)),
  class_restrictions='GuidanceTipGroup')), 
         guidance_tips_satisfied=TunableList(description='\n                A list of guidance tips that must be satisfied in order for this\n                criteron to activate. If any tip in this list is not satisfied, this criteron will\n                not activate.\n                ',
  tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.GUIDANCE_TIP)),
  class_restrictions='GuidanceTip')), 
         ui_element_visible=TunableList(description='\n                The UI elements that are required to be visible in order for this criteron to be valid.\n                ',
  tunable=TunableEnumEntry(tunable_type=TutorialTipUiElement,
  default=(TutorialTipUiElement.UI_INVALID))), 
         first_time_player=Tunable(description='\n                The player must be a first time player for this criteron to be valid.\n                ',
  tunable_type=bool,
  default=True), 
         feature_parameter=TunableStringHash64(description='\n                Checks the feature parameter value is present for this criteron to be valid.\n                ',
  default='',
  export_to_binary=True), **kwargs)


class GuidanceTipRuleCriterionList(TunableList):

    def __init__(self, **kwargs):
        (super().__init__)(tunable=TunableTuple(criterion=GuidanceTipCriterion(description='\n                    A rule which can be tested against.\n                    ',
                    export_modes=(ExportModes.ClientBinary)),
                    exclude_if_matched=Tunable(description='\n                    When set will NOT the result of the criterion.\n                    ',
                    tunable_type=bool,
                    default=False,
                    export_modes=(ExportModes.ClientBinary)),
                    export_class_name='GuidanceTipRuleCriterionListEntry'), **kwargs)


class GuidanceTipRuleCriteriaGroupList(TunableList):

    def __init__(self, **kwargs):
        (super().__init__)(tunable=TunableTuple(description='\n                Defines groups of rules which are tested against to see if this \n                rule set should be considered activated.\n                ',
                    children_condition=TunableEnumEntry(description='\n                    The conditional logic applied to the criteria in this rule group.\n                    AND means all of the rules in this group need to return "true" \n                    for the group to be considered complete.\n                    OR means any of the rules in this group can return "true" \n                    for the group value to be considered true.\n                    ',
                    tunable_type=GuidanceTipGroupConditionType,
                    default=(GuidanceTipGroupConditionType.AND)),
                    parent_condition=TunableEnumEntry(description='\n                    The conditional logic applied to the group when comparing against \n                    other rule groups in this set.\n                    ',
                    tunable_type=GuidanceTipGroupConditionType,
                    default=(GuidanceTipGroupConditionType.AND)),
                    criteria=GuidanceTipRuleCriterionList(description='\n                    The criterion items to be matched.\n                    '),
                    export_class_name='GuidanceTipRuleCriteriaGroupListEntry'), **kwargs)


class GuidanceTipOption(TunableTuple):

    def __init__(self, **kwargs):
        super().__init__(display_rules=GuidanceTipRuleCriteriaGroupList(description='\n            The rules which must be satisfied for this option to be shown or disabled, or empty for always show.\n            ',
          export_modes=(ExportModes.ClientBinary)),
          display_rules_disable_option=Tunable(description='\n            When enabled, if the display rules fail the option will be shown in the UI but will be disabled with a tooltip.\n            ',
          tunable_type=bool,
          default=False,
          export_modes=(ExportModes.ClientBinary)),
          display_type=TunableEnumEntry(description='\n            The option layout display type.\n            ',
          tunable_type=GuidanceTipOptionType,
          default=(GuidanceTipOptionType.STANDARD),
          export_modes=(ExportModes.ClientBinary)),
          text=TunableLocalizedStringFactory(description='\n            The text to display for this option.\n            ',
          allow_none=True,
          export_modes=(ExportModes.ClientBinary)),
          icon=TunableResourceKey(description='\n            The icon to be displayed for this option if the display type allows icons.\n            ',
          resource_types=(sims4.resources.CompoundTypes.IMAGE),
          default=None,
          allow_none=True,
          export_modes=(ExportModes.ClientBinary)),
          tooltip=TunableLocalizedStringFactory(description='\n            The tooltip to display for this option button.\n            ',
          allow_none=True,
          export_modes=(ExportModes.ClientBinary)),
          suppress_hide_on_activate=Tunable(description='\n            If enabled, the ui will not be hidden when the action is activated.\n            ',
          tunable_type=bool,
          default=False,
          export_modes=(ExportModes.ClientBinary)),
          actions=GuidanceTipActionGroup(description='\n            The actions and satisfaction rules for when this option is selected.\n            ',
          export_modes=(ExportModes.ClientBinary)))


class GuidanceTipGroup(metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.GUIDANCE_TIP)):
    INSTANCE_TUNABLES = {'items':TunableList(description='\n            The items that are associated with this group.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.GUIDANCE_TIP)),
       class_restrictions='GuidanceTip',
       export_modes=(ExportModes.ClientBinary))), 
     'group_condition':TunableEnumEntry(description='\n            The condition for completing this tip group. OR means any of the\n            items in this group need to be completed for the group to be\n            considered complete. AND means all of the items in this group need\n            to be completed for the group to be considered complete.\n            ',
       tunable_type=GuidanceTipGroupConditionType,
       default=GuidanceTipGroupConditionType.AND,
       export_modes=ExportModes.ClientBinary)}

    def __init__(self):
        raise NotImplementedError


GROUP_NAME_REQUIREMENTS = 'Activation Requirements'
GROUP_NAME_DISPLAY = 'Display'
GROUP_NAME_ACTIONS = 'Tip Actions'
GROUP_NAME_TIMEOUT = 'Timeout'

class GuidanceTip(HasTunableReference, metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.GUIDANCE_TIP)):
    INSTANCE_TUNABLES = {'activation_rules':GuidanceTipRuleCriteriaGroupList(description='\n            The rules which must be satisfied for this tip to be considered as active.\n            ',
       tuning_group=GROUP_NAME_REQUIREMENTS,
       export_modes=ExportModes.ClientBinary), 
     'auto_select_on_activate':Tunable(description='\n            If enabled, the guidance item will not display any UI and will automatically\n            select and run the actions on the first option as soon as it activates.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GROUP_NAME_DISPLAY,
       export_modes=ExportModes.ClientBinary), 
     'relaunch_rules':GuidanceTipRuleCriteriaGroupList(description='\n            The rules which must be satisfied for this tip to be allowed to be relaunched.\n            ',
       tuning_group=GROUP_NAME_REQUIREMENTS,
       export_modes=ExportModes.ClientBinary), 
     'title':TunableLocalizedStringFactory(description='\n            The title to be displayed in the guidance item UI.\n            ',
       allow_none=True,
       tuning_group=GROUP_NAME_DISPLAY,
       export_modes=ExportModes.ClientBinary), 
     'text':TunableLocalizedStringFactory(description='\n            The text to be displayed in the guidance item UI.\n            ',
       allow_none=True,
       tuning_group=GROUP_NAME_DISPLAY,
       export_modes=ExportModes.ClientBinary), 
     'icon':TunableResourceKey(description='\n            The icon to be displayed on the guidance item UI.\n            ',
       resource_types=sims4.resources.CompoundTypes.IMAGE,
       default=None,
       allow_none=True,
       tuning_group=GROUP_NAME_DISPLAY,
       export_modes=ExportModes.ClientBinary), 
     'options':TunableList(description='\n            The question options displayed in the UI for this tip\n            ',
       tunable=GuidanceTipOption(),
       tuning_group=GROUP_NAME_DISPLAY,
       export_modes=ExportModes.ClientBinary), 
     'timeout':TunableRange(description='\n            How long, in seconds, until this tip times out, or 0 for no timeout.\n            ',
       tunable_type=int,
       default=0,
       minimum=0,
       tuning_group=GROUP_NAME_TIMEOUT,
       export_modes=ExportModes.ClientBinary), 
     'satisfy_on_timeout':Tunable(description='\n            If enabled, the guidance item is satisfied when the timeout occurs.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GROUP_NAME_TIMEOUT,
       export_modes=ExportModes.ClientBinary), 
     'relaunch_text':TunableLocalizedStringFactory(description='\n            The text to display for this item in the relaunch menu\n            ',
       allow_none=True,
       export_modes=ExportModes.ClientBinary), 
     'guidance_group_to_unsatisfy_on_relaunch':TunableReference(description='\n            The guidance item group which will ne unsatisfied when this item is relaunched\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.GUIDANCE_TIP),
       class_restrictions='GuidanceTipGroup',
       allow_none=True,
       export_modes=ExportModes.ClientBinary), 
     'priority':Tunable(description='\n            The order the items are shown when multiple items could activate at the same time.\n            Higher values will be selected first. Items with equal values will be selected in an undefined order.\n            ',
       tunable_type=int,
       default=0,
       tuning_group=GROUP_NAME_TIMEOUT,
       export_modes=ExportModes.ClientBinary), 
     'relaunch_item_sort_order':Tunable(description='\n            The order the items are shown in the relaunch menu.\n            Higher values will be first. Items with equal values will be displayed in an undefined order.\n            ',
       tunable_type=int,
       default=0,
       export_modes=ExportModes.ClientBinary)}

    def __init__(self):
        raise NotImplementedError

    @classmethod
    def activate(cls):
        pass

    @classmethod
    def satisfy(cls):
        pass

    @classmethod
    def deactivate(cls):
        pass