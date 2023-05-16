# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\tutorials\tutorial_tip.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 38440 bytes
from autonomy.autonomy_request import AutonomyDistanceEstimationBehavior, AutonomyPostureBehavior
from buffs.tunable import TunableBuffReference
from distributor.system import Distributor
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.resolver import DoubleSimResolver
from interactions import priority
from interactions.aop import AffordanceObjectPair
from interactions.context import InteractionContext, InteractionBucketType
from sims.household_enums import HouseholdChangeOrigin
from sims4.localization import TunableLocalizedStringFactory, TunableLocalizedString
from sims4.tuning.tunable import TunableList, TunableReference, TunableTuple, Tunable, TunableEnumEntry, TunableSet, OptionalTunable, TunableRange, TunableResourceKey, TunableVariant, TunablePercent, TunableHouseDescription, TunablePackSafeReference, TunableEnumSet
from sims4.tuning.tunable_base import ExportModes
from tunable_time import TunableTimeOfDay
from snippets import TunableAffordanceFilterSnippet
from ui.ui_tuning import TunableUiMessage
from tutorials.tutorial_tip_enums import TutorialTipGameState, TutorialTipUiElement, TutorialTipGroupRequirementType, TutorialTipDisplayOption, TutorialTipActorOption, TutorialTipTestSpecificityOption, TutorialMode, TutorialTipSubtitleDisplayLocation
import autonomy, distributor.ops, enum, event_testing, services, sims4.localization, sims4.resources, sims4.tuning.instances, tutorials.tutorial
GROUP_NAME_DISPLAY_CRITERIA = 'Display Criteria'
GROUP_NAME_ACTIONS = 'Tip Actions'
GROUP_NAME_SATISFY = 'Satisfy Criteria'

class TutorialTipTuning:
    FTUE_TUNABLES = TunableTuple(description='\n        Tunables relating to the FTUE tutorial mode.\n        ',
      start_house_description=TunableHouseDescription(description='\n            A reference to the HouseDescription resource to load into in FTUE\n            '),
      ftue_aspiration_category=TunablePackSafeReference(description='\n            A reference to an aspiration category which is used in cas for the ftue flow\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION_CATEGORY))),
      disable_ui_elements=TunableList(description='\n            Disable one or more UI elements during a phase of the tutorial, denoted by\n            the starting and ending tips.\n            ',
      tunable=TunableTuple(description='\n                Defines a set of UI elements to be disabled during a range of tips.\n                ',
      start_tip=TunablePackSafeReference(description='\n                    When this tip becomes active or is satisfied, the target elements\n                    will become disabled.\n                    ',
      manager=(services.get_instance_manager(sims4.resources.Types.TUTORIAL_TIP))),
      end_tip=TunablePackSafeReference(description='\n                    When this tip becomes active or is satisfied, the target elements\n                    will become re-enabled.\n                    ',
      manager=(services.get_instance_manager(sims4.resources.Types.TUTORIAL_TIP))),
      reason=TunableLocalizedString(description='\n                    The reason the element has been disabled, usually displayed as a tooltip.\n                    '),
      elements=TunableEnumSet(description='\n                    List of UI elements to disable.  Note that not all elements can be disabled.\n                    ',
      enum_type=TutorialTipUiElement),
      export_class_name='TutorialTipDisableUiElements')),
      export_modes=(
     ExportModes.ClientBinary,),
      export_class_name='FtueDataTuple')


class TunableTutorialTipDisplay(TunableTuple):

    def __init__(self, **kwargs):
        (super().__init__)(cancelable=Tunable(description='\n                If this tutorial tip can be canceled.\n                ',
  tunable_type=bool,
  default=True), 
         text=TunableLocalizedStringFactory(description="\n                The text for this tip.\n                Token {0} is the active sim. i.e. {0.SimFirstName}\n                Token {1.String} is a 'wildcard' string to be used for things\n                like aspiration names or buff names during the tutorial.\n                Not used when display type is INDICATOR_ARROW.\n                ",
  allow_none=True), 
         action_text=TunableLocalizedStringFactory(description="\n                The action the user must make for this tip to satisfy.\n                Token {0} is the active sim. i.e. {0.SimFirstName}\n                Token {1.String} is a 'wildcard' string to be used for things\n                like aspiration names or buff names during the tutorial.\n                ",
  allow_none=True), 
         timeout=TunableRange(description='\n                How long, in seconds, until this tutorial tip times out.\n                ',
  tunable_type=int,
  default=1,
  minimum=1), 
         ui_element=TunableEnumEntry(description='\n                The UI element associated with this tutorial tip.\n                ',
  tunable_type=TutorialTipUiElement,
  default=(TutorialTipUiElement.UI_INVALID)), 
         is_modal=Tunable(description='\n                Enable if this tip should be modal.\n                Disable, if not.\n                ',
  tunable_type=bool,
  default=False), 
         icon=TunableResourceKey(description='\n                The icon to be displayed in a modal tutorial tip.\n                If Is Modal is disabled, this field can be ignored.\n                ',
  resource_types=(sims4.resources.CompoundTypes.IMAGE),
  default=None,
  allow_none=True), 
         icon_console=TunableResourceKey(description='\n                The icon to be displayed in a modal tutorial tip on console.\n                If unset, will fall back to Icon.\n                If Is Modal is disabled, this field can be ignored.\n                ',
  resource_types=(sims4.resources.CompoundTypes.IMAGE),
  default=None,
  allow_none=True,
  display_name='Icon (Console)',
  export_modes=(ExportModes.ClientBinary)), 
         title=TunableLocalizedString(description='\n                The title of this tutorial tip.\n                Not used when display type is INDICATOR_ARROW.\n                ',
  allow_none=True), 
         pagination_label=TunableLocalizedString(description='\n                The label of what page this tutorial tip is in within the\n                tutorial tip group.\n                Not used when display type is INDICATOR_ARROW.\n                ',
  allow_none=True), 
         display_type_option=TunableEnumEntry(description='\n                The display type of this tutorial tip.\n                ',
  tunable_type=TutorialTipDisplayOption,
  default=(TutorialTipDisplayOption.STANDARD)), **kwargs)


class TutorialTipGroup(metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.TUTORIAL_TIP)):
    INSTANCE_TUNABLES = {'tips':TunableList(description='\n            The tips that are associated with this tip group.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.TUTORIAL_TIP)),
       class_restrictions='TutorialTip',
       export_modes=(ExportModes.ClientBinary))), 
     'group_requirement':TunableEnumEntry(description='\n            The requirement for completing this tip group. ANY means any of the\n            tips in this group need to be completed for the group to be\n            considered complete. ALL means all of the tips in this group need\n            to be completed for the group to be considered complete.\n            ',
       tunable_type=TutorialTipGroupRequirementType,
       default=TutorialTipGroupRequirementType.ALL,
       export_modes=ExportModes.ClientBinary)}

    def __init__(self):
        raise NotImplementedError


class TunableTutorialTipUiMessage(TunableTuple):

    def __init__(self, **kwargs):
        (super().__init__)(ui_message_cmn=OptionalTunable(description='\n                Sends a message to the UI for a tutorial tip.\n                ',
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


class TutorialTip(metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.TUTORIAL_TIP)):
    INSTANCE_TUNABLES = {'required_tip_groups':TunableList(description='\n            The Tip Groups that must be complete for this tip to be valid.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.TUTORIAL_TIP)),
       class_restrictions='TutorialTipGroup'),
       tuning_group=GROUP_NAME_DISPLAY_CRITERIA,
       export_modes=ExportModes.ClientBinary), 
     'required_ui_list':TunableList(description='\n            The UI elements that are required to be present in order for this\n            tutorial tip to be valid.\n            ',
       tunable=TunableEnumEntry(tunable_type=TutorialTipUiElement,
       default=(TutorialTipUiElement.UI_INVALID)),
       tuning_group=GROUP_NAME_DISPLAY_CRITERIA,
       export_modes=ExportModes.ClientBinary), 
     'required_ui_hidden_list':TunableList(description='\n            The UI elements that are required to NOT be present in order for this\n            tutorial tip to be valid.\n            ',
       tunable=TunableEnumEntry(tunable_type=TutorialTipUiElement,
       default=(TutorialTipUiElement.UI_INVALID)),
       tuning_group=GROUP_NAME_DISPLAY_CRITERIA,
       export_modes=ExportModes.ClientBinary), 
     'required_game_state':TunableEnumEntry(description='\n            The state the game must be in for this tutorial tip to be valid.\n            ',
       tunable_type=TutorialTipGameState,
       default=TutorialTipGameState.GAMESTATE_NONE,
       tuning_group=GROUP_NAME_DISPLAY_CRITERIA,
       export_modes=ExportModes.ClientBinary), 
     'required_tips_not_satisfied':TunableList(description='\n            This is a list of tips that must be un-satisfied in order for this\n            tip to activate. If any tip in this list is satisfied, this tip will\n            not activate.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.TUTORIAL_TIP)),
       class_restrictions='TutorialTip'),
       tuning_group=GROUP_NAME_DISPLAY_CRITERIA,
       export_modes=ExportModes.ClientBinary), 
     'required_active_tip_groups':TunableList(description='\n            The Tip Groups that must be requested for this tip to be valid.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.TUTORIAL_TIP)),
       class_restrictions='TutorialTipGroup'),
       tuning_group=GROUP_NAME_DISPLAY_CRITERIA,
       export_modes=ExportModes.ClientBinary), 
     'platform_filter':TunableEnumEntry(description='\n            The platforms on which this tutorial tip is shown.\n            ',
       tunable_type=tutorials.tutorial.TutorialPlatformFilter,
       default=tutorials.tutorial.TutorialPlatformFilter.ALL_PLATFORMS,
       tuning_group=GROUP_NAME_DISPLAY_CRITERIA,
       export_modes=ExportModes.ClientBinary), 
     'required_tutorial_mode':TunableEnumEntry(description='\n            What mode this tutorial tip should be restricted to.\n            STANDARD allows this tip to be in the original / standard tutorial mode.\n            FTUE allows this tip to be in the FTUE tutorial mode.\n            DISABLED means this tip is valid in any mode.\n            ',
       tunable_type=TutorialMode,
       default=TutorialMode.STANDARD,
       tuning_group=GROUP_NAME_DISPLAY_CRITERIA,
       export_modes=ExportModes.ClientBinary), 
     'display':TunableTutorialTipDisplay(description='\n            This display information for this tutorial tip.\n            ',
       tuning_group=GROUP_NAME_ACTIONS,
       export_modes=ExportModes.ClientBinary), 
     'display_narration':OptionalTunable(description='\n            Optionally play narration voice-over and display subtitles.\n            ',
       tunable=TunableTuple(voiceover_audio=TunableResourceKey(description='\n                    Narration audio to play.\n                    ',
       default=None,
       allow_none=True,
       resource_types=(
      sims4.resources.Types.PROPX,)),
       voiceover_audio_ps4=TunableResourceKey(description='\n                    Narration audio to play specific to PS4.\n                    ',
       default=None,
       allow_none=True,
       resource_types=(
      sims4.resources.Types.PROPX,)),
       voiceover_audio_xb1=TunableResourceKey(description='\n                    Narration audio to play specific to XB1.\n                    ',
       default=None,
       allow_none=True,
       resource_types=(
      sims4.resources.Types.PROPX,)),
       subtitle_text=TunableLocalizedString(description='\n                    Subtitles to display while audio narration is playing.\n                    '),
       subtitle_display_location=TunableVariant(description='\n                    What area on the screen the subtitles should appear.\n                    Top    - Use the generic top-of-screen position.\n                    Bottom - Use the generic bottom-of-screen position.\n                    Custom - Specify a custom position in terms of % vertically.\n                    ',
       location=TunableEnumEntry(description='\n                        Semantic location (UX-defined) for where the subtitles should appear.\n                        ',
       tunable_type=TutorialTipSubtitleDisplayLocation,
       default=(TutorialTipSubtitleDisplayLocation.BOTTOM)),
       custom=TunablePercent(description='\n                        Vertical position for the subtitles, expressed as a\n                        percentage of the height of the screen.\n                        ',
       default=90),
       default='location'),
       satisfy_when_voiceover_finished=Tunable(description='\n                    If set, the tutorial tip will be marked as satisfied when the\n                    voiceover completes or is interrupted.\n                    ',
       tunable_type=bool,
       default=False),
       delay_satisfaction_until_voiceover_finished=Tunable(description='\n                    If set, the tutorial tip will not be marked satisfied until after\n                    the voiceover completes, preventing the voiceover from being\n                    interrupted by external satisfaction.\n                    ',
       tunable_type=bool,
       default=False),
       keep_subtitle_visible_until_satisfaction=Tunable(description='\n                    If set, the subtitle will remain visible until the tutorial tip is\n                    marked as satisfied, even though the voiceover may have finished.\n                    ',
       tunable_type=bool,
       default=False),
       export_class_name='TutorialTipNarrationDisplay'),
       tuning_group=GROUP_NAME_ACTIONS,
       export_modes=ExportModes.ClientBinary), 
     'activation_ui_message':TunableTutorialTipUiMessage(description='\n            Sends a message to the UI when this tip is activated.\n            ',
       tuning_group=GROUP_NAME_ACTIONS,
       export_modes=ExportModes.ClientBinary), 
     'deactivation_ui_message':TunableTutorialTipUiMessage(description='\n            Sends a message to the UI when this tip is deactivated.\n            ',
       tuning_group=GROUP_NAME_ACTIONS,
       export_modes=ExportModes.ClientBinary), 
     'buffs':TunableList(description='\n            Buffs that will be applied at the start of this tutorial tip.\n            ',
       tunable=TunableBuffReference(),
       tuning_group=GROUP_NAME_ACTIONS), 
     'buffs_removed_on_deactivate':Tunable(description='\n            If enabled, this tip will remove those buffs on deactivate.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GROUP_NAME_ACTIONS), 
     'commodities_to_solve':TunableSet(description="\n            A set of commodities we will attempt to solve. This will result in\n            the Sim's interaction queue being filled with various interactions.\n            ",
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC))),
       tuning_group=GROUP_NAME_ACTIONS), 
     'gameplay_loots':OptionalTunable(description='\n            Loots that will be given at the start of this tip.\n            Actor is is the sim specified by Sim Actor.\n            Target is the sim specified by Sim Target.\n            ',
       tunable=TunableList(tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', ),
       pack_safe=True)),
       tuning_group=GROUP_NAME_ACTIONS), 
     'restricted_affordances':OptionalTunable(description='\n            If enabled, use the filter to determine which affordances are allowed.\n            ',
       tunable=TunableTuple(visible_affordances=TunableAffordanceFilterSnippet(description='\n                    The filter of affordances that are visible.\n                    '),
       tooltip=OptionalTunable(description='\n                    Tooltip when interaction is disabled by tutorial restrictions\n                    If not specified, will use the default in the tutorial service\n                    tuning.\n                    ',
       tunable=(sims4.localization.TunableLocalizedStringFactory())),
       enabled_affordances=TunableAffordanceFilterSnippet(description='\n                    The filter of visible affordances that are enabled.\n                    ')),
       tuning_group=GROUP_NAME_ACTIONS), 
     'call_to_actions':OptionalTunable(description='\n            Call to actions that should persist for the duration of this tip.\n            ',
       tunable=TunableList(tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.CALL_TO_ACTION)),
       pack_safe=True)),
       tuning_group=GROUP_NAME_ACTIONS), 
     'end_drama_node':Tunable(description='\n            If enabled, this tip will end the tutorial drama node.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GROUP_NAME_ACTIONS), 
     'sim_actor':TunableEnumEntry(description="\n            The entity who will be the actor sim for loot, and will\n            receive the items that aren't specified via loots.\n            \n            If there is no Tutorial Drama Node active, actor will be active\n            sim\n            ",
       tunable_type=TutorialTipActorOption,
       default=TutorialTipActorOption.ACTIVE_SIM,
       tuning_group=GROUP_NAME_ACTIONS), 
     'sim_target':TunableEnumEntry(description='\n            The entity who will be the target sim for loot\n            \n            If there is no Tutorial Drama Node active, target sim will be active\n            sim.\n            ',
       tunable_type=TutorialTipActorOption,
       default=TutorialTipActorOption.ACTIVE_SIM,
       tuning_group=GROUP_NAME_ACTIONS), 
     'add_target_to_actor_household':Tunable(description='\n            If enabled, target sim will be added to active sim household.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GROUP_NAME_ACTIONS), 
     'make_housemate_unselectable':Tunable(description='\n            If enabled, housemate will be unselectable for the duration of the\n            tooltip.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GROUP_NAME_ACTIONS), 
     'timeout_satisfies':Tunable(description='\n            If enabled, this tip is satisfied when the timeout is reached.\n            If disabled, this tip will not satisfy when the timeout is reached.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GROUP_NAME_SATISFY,
       export_modes=ExportModes.ClientBinary), 
     'gameplay_test':OptionalTunable(description='\n            Tests that, if passed, will satisfy this tutorial tip.\n            Only one test needs to pass to satisfy. These are intended for tips\n            where the satisfy message should be tested and sent at a later time.\n            ',
       tunable=tutorials.tutorial.TunableTutorialTestVariant(),
       tuning_group=GROUP_NAME_SATISFY,
       export_modes=ExportModes.All), 
     'sim_tested':TunableEnumEntry(description='\n            The entity who must fulfill the test events.\n            \n            If there is no Tutorial Drama Node, player sim and housemate sim will be active\n            sim.\n            ',
       tunable_type=TutorialTipTestSpecificityOption,
       default=TutorialTipTestSpecificityOption.UNSPECIFIED,
       tuning_group=GROUP_NAME_SATISFY), 
     'time_of_day':OptionalTunable(description='\n            If specified, tutorialtip will be satisfied once the time passes \n            the specified time.\n            ',
       tunable=TunableTimeOfDay(),
       tuning_group=GROUP_NAME_SATISFY), 
     'gameplay_immediate_test':OptionalTunable(description='\n            Tests that, if passed, will satisfy this tutorial tip.\n            Only one test needs to pass to satisfy. These are intended for tips\n            where the satisfy message should be tested and sent back immediately.\n            ',
       tunable=tutorials.tutorial.TunableTutorialTestVariant(),
       tuning_group=GROUP_NAME_SATISFY,
       export_modes=ExportModes.All), 
     'satisfy_on_active_sim_change':Tunable(description='\n            If enabled, this tip is satisfied when the active sim changes\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GROUP_NAME_SATISFY,
       export_modes=ExportModes.All), 
     'satisfy_on_activate':Tunable(description="\n            If enabled, this tip is satisfied immediately when all of it's\n            preconditions have been met.\n            ",
       tunable_type=bool,
       default=False,
       tuning_group=GROUP_NAME_SATISFY,
       export_modes=ExportModes.ClientBinary), 
     'tutorial_group_to_complete_on_skip':TunableReference(description='\n            The tutorial group who will have all tutorial tips within it\n            completed when the button to skip all is pressed from this tip.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.TUTORIAL_TIP),
       class_restrictions='TutorialTipGroup',
       export_modes=ExportModes.ClientBinary)}

    def __init__(self):
        raise NotImplementedError

    @classmethod
    def activate(cls):
        tutorial_service = services.get_tutorial_service()
        client = services.client_manager().get_first_client()
        actor_sim_info = client.active_sim.sim_info
        target_sim_info = actor_sim_info
        housemate_sim_info = None
        tutorial_drama_node = None
        drama_scheduler = services.drama_scheduler_service()
        if drama_scheduler is not None:
            drama_nodes = drama_scheduler.get_running_nodes_by_drama_node_type(DramaNodeType.TUTORIAL)
            if drama_nodes:
                tutorial_drama_node = drama_nodes[0]
                housemate_sim_info = tutorial_drama_node.get_housemate_sim_info()
                player_sim_info = tutorial_drama_node.get_player_sim_info()
                if cls.sim_actor == TutorialTipActorOption.PLAYER_SIM:
                    actor_sim_info = player_sim_info
                else:
                    if cls.sim_actor == TutorialTipActorOption.HOUSEMATE_SIM:
                        actor_sim_info = housemate_sim_info
                    elif cls.sim_target == TutorialTipActorOption.PLAYER_SIM:
                        target_sim_info = player_sim_info
                    else:
                        if cls.sim_target == TutorialTipActorOption.HOUSEMATE_SIM:
                            target_sim_info = housemate_sim_info
        if cls.gameplay_immediate_test is not None:
            resolver = event_testing.resolver.SingleSimResolver(actor_sim_info)
            if resolver(cls.gameplay_immediate_test):
                cls.satisfy()
            else:
                return
        for buff_ref in cls.buffs:
            actor_sim_info.add_buff_from_op((buff_ref.buff_type), buff_reason=(buff_ref.buff_reason))

        if cls.gameplay_test is not None:
            services.get_event_manager().register_tests(cls, [cls.gameplay_test])
        if cls.satisfy_on_active_sim_change:
            client = services.client_manager().get_first_client()
            if client is not None:
                client.register_active_sim_changed(cls._on_active_sim_change)
        if cls.commodities_to_solve:
            actor_sim = actor_sim_info.get_sim_instance()
            if actor_sim is not None:
                context = InteractionContext(actor_sim, (InteractionContext.SOURCE_SCRIPT_WITH_USER_INTENT), (priority.Priority.High),
                  bucket=(InteractionBucketType.DEFAULT))
                for commodity in cls.commodities_to_solve:
                    if not actor_sim.queue.can_queue_visible_interaction():
                        break
                    autonomy_request = autonomy.autonomy_request.AutonomyRequest(actor_sim, autonomy_mode=(autonomy.autonomy_modes.FullAutonomy), commodity_list=(
                     commodity,),
                      context=context,
                      consider_scores_of_zero=True,
                      posture_behavior=(AutonomyPostureBehavior.IGNORE_SI_STATE),
                      distance_estimation_behavior=(AutonomyDistanceEstimationBehavior.ALLOW_UNREACHABLE_LOCATIONS),
                      allow_opportunity_cost=False,
                      autonomy_mode_label_override='Tutorial')
                    selected_interaction = services.autonomy_service().find_best_action(autonomy_request)
                    AffordanceObjectPair.execute_interaction(selected_interaction)

        if cls.gameplay_loots:
            resolver = DoubleSimResolver(actor_sim_info, target_sim_info)
            for loot_action in cls.gameplay_loots:
                loot_action.apply_to_resolver(resolver)

        if cls.restricted_affordances is not None:
            if tutorial_service is not None:
                tutorial_service.set_restricted_affordances(cls.restricted_affordances.visible_affordances, cls.restricted_affordances.tooltip, cls.restricted_affordances.enabled_affordances)
        if cls.call_to_actions is not None:
            call_to_action_service = services.call_to_action_service()
            for call_to_action_fact in cls.call_to_actions:
                call_to_action_service.begin(call_to_action_fact, None)

        if cls.add_target_to_actor_household:
            household_manager = services.household_manager()
            household_manager.switch_sim_household(target_sim_info, reason=(HouseholdChangeOrigin.TUTORIAL))
        if cls.make_housemate_unselectable:
            if tutorial_service is not None:
                tutorial_service.set_unselectable_sim(housemate_sim_info)
        if cls.end_drama_node:
            if tutorial_drama_node is not None:
                tutorial_drama_node.end()
        if cls.time_of_day is not None:
            if tutorial_service is not None:
                tutorial_service.add_tutorial_alarm(cls, lambda _: cls.satisfy(), cls.time_of_day)

    @classmethod
    def _on_active_sim_change(cls, old_sim, new_sim):
        cls.satisfy()

    @classmethod
    def handle_event(cls, sim_info, event, resolver):
        if cls.gameplay_test is not None:
            if resolver(cls.gameplay_test):
                if cls.sim_tested != TutorialTipTestSpecificityOption.UNSPECIFIED:
                    client = services.client_manager().get_first_client()
                    test_sim_info = client.active_sim.sim_info
                    drama_scheduler = services.drama_scheduler_service()
                    if drama_scheduler is not None:
                        drama_nodes = drama_scheduler.get_running_nodes_by_drama_node_type(DramaNodeType.TUTORIAL)
                        if drama_nodes:
                            drama_node = drama_nodes[0]
                            if cls.sim_tested == TutorialTipTestSpecificityOption.PLAYER_SIM:
                                test_sim_info = drama_node.get_player_sim_info()
                            else:
                                if cls.sim_tested == TutorialTipTestSpecificityOption.HOUSEMATE_SIM:
                                    test_sim_info = drama_node.get_housemate_sim_info()
                    if test_sim_info is not sim_info:
                        return
                cls.satisfy()

    @classmethod
    def satisfy(cls):
        op = distributor.ops.SetTutorialTipSatisfy(cls.guid64)
        distributor_instance = Distributor.instance()
        distributor_instance.add_op_with_no_owner(op)

    @classmethod
    def deactivate(cls):
        tutorial_service = services.get_tutorial_service()
        client = services.client_manager().get_first_client()
        if cls.gameplay_test is not None:
            services.get_event_manager().unregister_tests(cls, (cls.gameplay_test,))
        elif cls.satisfy_on_active_sim_change:
            if client is not None:
                client.unregister_active_sim_changed(cls._on_active_sim_change)
            elif cls.restricted_affordances is not None and tutorial_service is not None:
                tutorial_service.clear_restricted_affordances()
            if cls.call_to_actions is not None:
                call_to_action_service = services.call_to_action_service()
                for call_to_action_fact in cls.call_to_actions:
                    call_to_action_service.end(call_to_action_fact)

            if cls.buffs_removed_on_deactivate:
                actor_sim_info = None
                if client is not None:
                    actor_sim_info = client.active_sim.sim_info
                drama_scheduler = services.drama_scheduler_service()
                if drama_scheduler is not None:
                    drama_nodes = drama_scheduler.get_running_nodes_by_drama_node_type(DramaNodeType.TUTORIAL)
                    if drama_nodes:
                        tutorial_drama_node = drama_nodes[0]
                        if cls.sim_actor == TutorialTipActorOption.PLAYER_SIM:
                            actor_sim_info = tutorial_drama_node.get_player_sim_info()
        elif cls.sim_actor == TutorialTipActorOption.HOUSEMATE_SIM:
            actor_sim_info = tutorial_drama_node.get_housemate_sim_info()
        if actor_sim_info is not None:
            for buff_ref in cls.buffs:
                actor_sim_info.remove_buff_by_type(buff_ref.buff_type)

        if cls.time_of_day is not None:
            if tutorial_service is not None:
                tutorial_service.remove_tutorial_alarm(cls)
        if cls.make_housemate_unselectable:
            if tutorial_service is not None:
                tutorial_service.set_unselectable_sim(None)