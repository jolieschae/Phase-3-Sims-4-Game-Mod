# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gameplay_scenarios\scenario.py
# Compiled at: 2023-01-31 21:21:57
# Size of source mod 2**32: 76210 bytes
import itertools, assertions, event_testing, services, sims4, uid
from cas.cas_tuning import CASContextCriterionList
from collections import namedtuple
from date_and_time import TimeSpan
from distributor.rollback import ProtocolBufferRollback
from event_testing import test_events
from event_testing.resolver import SingleSimResolver, DoubleSimResolver, GlobalResolver
from filters.tunable import TunableSimFilter
from gameplay_scenarios.scenario_enums import ScenarioDifficultyCategory, ScenarioEntryMethod, ScenarioProperties, ScenarioCategory, ScenarioTheme
from gameplay_scenarios.scenario_outcomes import ScenarioOutcome, ScenarioPhaseLoot
from gameplay_scenarios.scenario_phase import ScenarioPhase, TerminatorHandler, run_scenario_test, PhaseEndingReason
from gameplay_scenarios.scenario_profiling import record_scenario_profile_metrics, should_record_scenario_profile_metrics, scenario_profile_on_phase_end
from gameplay_scenarios.scenario_tests_set import TunableScenarioBreakTest
from interactions.utils.death import DeathType
from interactions.utils.tunable_icon import TunableIcon
from playstyles.playstyle_enums import Playstyle
from relationships.relationship_enums import RelationshipType
from sims4 import math
from sims4.localization import TunableLocalizedString
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableFactory, TunableList, TunableTuple, TunableReference, TunablePackSafeReference, TunableInterval, OptionalTunable, TunableResourceKey, Tunable, TunableMapping, TunableEnumFlags, TunableEnumEntry, HasTunableReference
from sims4.tuning.tunable_base import ExportModes, GroupNames
from situations.situation_serialization import GoalSeedling
from ui.screen_slam import TunableScreenSlamSnippet
from ui.ui_utils import hide_selected_notifications
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet
logger = sims4.log.Logger('Gameplay Scenarios', default_owner='jmorrow')
with sims4.reload.protected(globals()):
    scenario_profiles = None

class ScenarioTag(metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    INSTANCE_TUNABLES = {'name':TunableLocalizedString(description='\n            Name of the scenario type to display in the UI.\n            ',
       export_modes=ExportModes.ClientBinary), 
     'theme':TunableEnumEntry(description='\n            The theme identifier for this tag.\n            ',
       tunable_type=ScenarioTheme,
       default=ScenarioTheme.INVALID,
       invalid_enums=(
      ScenarioTheme.INVALID,),
       export_modes=ExportModes.ClientBinary)}


class ScenarioRole(HasTunableReference, metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    INSTANCE_TUNABLES = {'criteria': TunableList(description='\n            Data about CAS criteria that constrains sims with this Scenario Role.\n            \n            Each entry contains a list of criteria associated with a Loc String.\n            ',
                   tunable=TunableTuple(description='\n                A set of criteria associated with a Loc String, which will be\n                displayed in the CAS as a household requirement.\n                ',
                   criteria_list=CASContextCriterionList(description='\n                    A list of criteria that define restrictions on sims in scenarios\n                    with this role.\n                    '),
                   household_requirement_text=TunableLocalizedString(description='\n                    The text that will display as the player-facing\n                    household requirement associated with this Criteria List.\n                    '),
                   export_class_name='TunableScenarioRoleCriteria',
                   export_modes=(ExportModes.ClientBinary)))}


ActiveGoal = namedtuple('ActiveGoal', ['situation_goal', 'scenario_goal'])
LastVisibleGoal = namedtuple('LastVisibleGoal', ['goal', 'is_mandatory'])

class Scenario(metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    SCENARIO_CATEGORIES = TunableMapping(description='\n        A mapping from category to category data.\n        ',
      key_type=TunableEnumEntry(description='\n            The scenario category.\n            ',
      tunable_type=ScenarioCategory,
      default=(ScenarioCategory.INVALID),
      invalid_enums=(
     ScenarioCategory.INVALID,)),
      value_type=TunableTuple(description='\n            Data associated with the scenario category.\n            ',
      category_name=TunableLocalizedString(description='\n                The player facing name for this scenario category.\n                '),
      category_description=TunableLocalizedString(description='\n                The player facing description for this scenario category.\n                '),
      export_class_name='CategoryDataTuple'),
      export_modes=(
     ExportModes.ClientBinary,),
      tuple_name='CategoryData')
    SCENARIO_DIFFICULTY_CATEGORIES = TunableMapping(description='\n        A mapping from difficulty category to difficulty data.\n        ',
      key_type=TunableEnumEntry(description='\n            The difficulty category.\n            ',
      tunable_type=ScenarioDifficultyCategory,
      default=(ScenarioDifficultyCategory.INVALID),
      invalid_enums=(
     ScenarioDifficultyCategory.INVALID,)),
      value_type=TunableTuple(description='\n            Data associated with the difficulty category.\n            ',
      player_facing_name=TunableLocalizedString(description='\n                The player facing name for this difficulty category.\n                '),
      export_class_name='DifficultyCategoryDataTuple'),
      export_modes=(
     ExportModes.ClientBinary,),
      tuple_name='DifficultyCategoryData')
    RECOMMENDED_SCENARIOS = TunableTuple(description='\n        Data associated with scenarios recommended to players.\n        ',
      recommended_scenarios_no_playstyle=TunableList(description="\n            A list of scenarios recommended for new players for whom we don't have\n            playstyle data yet.\n            ",
      tunable=TunableReference(description='\n                A scenario.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
      class_restrictions=('Scenario', ))),
      recommended_scenarios_for_playstyles=TunableMapping(description='\n            A mapping from playstyle to list of scenarios recommended for that playstyle.\n            ',
      key_name='playstyle',
      key_type=TunableEnumEntry(description='\n                A playstyle.\n                ',
      tunable_type=Playstyle,
      default=(Playstyle.INVALID),
      invalid_enums=(
     Playstyle.INVALID,)),
      value_name='recommended_scenarios',
      value_type=TunableList(description='\n                A list of scenarios recommended for players that match this playstyle.\n                ',
      tunable=TunableReference(description='\n                    A scenario.\n                    ',
      manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
      class_restrictions=('Scenario', ))),
      tuple_name='PlaystyleRecommendedScenariosData',
      export_modes=(ExportModes.ClientBinary)),
      export_modes=(
     ExportModes.ClientBinary,),
      export_class_name='RecommendedScenariosData')

    @classmethod
    def _verify_tuning_callback(cls):

        def traverse_validate_base(phase, phases):
            phase_to_check = phase.phase_fallback_output.output.next_phase
            if phase_to_check is not None:
                if phase_to_check in phases:
                    if len(phase.phase_outputs) == 0:
                        logger.error('A loop detected in scenario phase graph. Next default phase:{} of phase:{} is already                             a previous phase. Consider changing it or adding an alternative next phase.'.format(phase_to_check, phase))
                        return False
            phase_outputs = phase.phase_outputs
            if len(phase_outputs) == 1:
                fallback_output = phase.phase_fallback_output.output
                first_output = phase_outputs[0].output.output
                if first_output.next_phase is not None:
                    if fallback_output.next_phase is None:
                        if fallback_output.scenario_outcome is None:
                            if first_output.next_phase in phases:
                                logger.error('A loop detected in scenario phase graph. Only next phase:{} of phase:{} is already                                 a previous phase. Consider changing it or adding an alternative next phase.'.format(first_output.next_phase, phase))
                                return False
            return True

        def traverse_validate(phase, phases):
            if not traverse_validate_base(phase, phases):
                return
            phases.add(phase)
            for phase_output in phase.phase_outputs:
                next_phase = phase_output.output.output.next_phase
                if next_phase is not None:
                    traverse_validate(next_phase, phases)

            next_phase = phase.phase_fallback_output.output.next_phase
            if next_phase is not None:
                traverse_validate(next_phase, phases)
            phases.remove(phase)

        phases = set()
        if cls.starting_phase is not None:
            traverse_validate(cls.starting_phase, phases)

    INSTANCE_TUNABLES = {'compatibility_with_scenario_entry_method':TunableEnumFlags(description='\n            A set of values that defines which entry methods are compatible with this scenario.\n            \n            For example, if only NEW_HOUSEHOLDS is tuned, then this scenario\n            is only compatible with new households and cannot be applied to\n            an existing household. \n            ',
       enum_type=ScenarioEntryMethod,
       export_modes=ExportModes.All), 
     'category':TunableEnumEntry(description='\n            A value that defines which category this scenario falls under.\n\n            This category maps to a user-facing name that can be defined in \n            the gameplay_scenarios.scenario module tuning.\n            ',
       tunable_type=ScenarioCategory,
       default=ScenarioCategory.INVALID,
       invalid_enums=(
      ScenarioCategory.INVALID,),
       export_modes=ExportModes.ClientBinary), 
     'difficulty':TunableEnumEntry(description='\n            A value that defines how difficult the scenario is estimated to be.\n            \n            This difficulty maps to a user-facing name that can be defined in \n            the gameplay_scenarios.scenario module tuning.\n            ',
       tunable_type=ScenarioDifficultyCategory,
       default=ScenarioDifficultyCategory.INVALID,
       invalid_enums=(
      ScenarioDifficultyCategory.INVALID,),
       export_modes=ExportModes.ClientBinary), 
     'scenario_name':TunableLocalizedString(description='\n            A string that will be used in UI to display the name of the scenario.\n            ',
       export_modes=ExportModes.All,
       tuning_group=GroupNames.UI), 
     'scenario_description':TunableLocalizedString(description='\n            A string that will be used in UI to display the description of the scenario.\n            ',
       export_modes=ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'tagline_text':TunableLocalizedString(description='\n            A string to show a brief description of the scenario in the scenario list.\n            ',
       export_modes=ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'scenario_tags':TunableList(description='\n            A list of tags associated with this scenario that will be used in the\n            UI to filter scenarios.\n            ',
       tunable=TunableReference(description='\n                A scenario tag.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
       class_restrictions=('ScenarioTag', )),
       export_modes=ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'icon':TunableResourceKey(description=',\n            If enabled, an icon to be displayed in the scenario browsing UI.\n            ',
       allow_none=True,
       export_modes=ExportModes.ClientBinary,
       resource_types=sims4.resources.CompoundTypes.IMAGE,
       tuning_group=GroupNames.UI), 
     'reward_icon':TunableResourceKey(description=',\n            If enabled, an icon of the default reward given to players to displayed\n            in the scenario browsing UI, details panel and outcome ui.\n            ',
       allow_none=True,
       export_modes=ExportModes.All,
       resource_types=sims4.resources.CompoundTypes.IMAGE,
       tuning_group=GroupNames.UI), 
     'reward_text':TunableLocalizedString(description=',\n            If enabled, the name of the reward players will be given upon completing\n            the scenario which is shown in the browsing UI, details panel and outcome ui.\n            ',
       allow_none=True,
       export_modes=ExportModes.All,
       tuning_group=GroupNames.UI), 
     'scenario_start_notification':TunableUiDialogNotificationSnippet(description='\n            Provides access to the TNS data to allow injection of the scenario name.\n            '), 
     'scenario_role_data':TunableList(description='\n            A list of data about scenario roles for this scenario.\n            ',
       tunable=TunableTuple(role=TunableReference(description='\n                    The scenario role.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
       class_restrictions=('ScenarioRole', )),
       sim_count=TunableInterval(description='\n                    The minimum (inclusive) and maximum (inclusive) number of\n                    sims in the household that may have this role.\n                    ',
       tunable_type=int,
       default_lower=1,
       default_upper=1,
       minimum=0,
       maximum=8,
       export_class_name='ScenarioRoleTunableInterval'),
       role_traits=TunableList(description='\n                    A list of all role traits for this specific scenario role. These traits will be re-added to a sim \n                    with this scenario role every time that sim is instanced and removed every time that sim \n                    is de-instanced.\n                    ',
       tunable=TunableReference(description='\n                        This should only be used for Traits that do not add commodities, as these traits will be \n                        re-added every time the sim is instanced.\n                        ',
       manager=(services.get_instance_manager(sims4.resources.Types.TRAIT))),
       export_modes=(ExportModes.ServerXML)),
       export_class_name='TunableScenarioRoleData',
       export_modes=(ExportModes.ClientBinary),
       tuning_group=(GroupNames.UI))), 
     'relationship_requirements':TunableList(description='\n            Constraints on how sims with different roles must be related.\n            ',
       tunable=TunableTuple(description='\n                Data about how two sims with specific roles must be related.\n                ',
       subject_role=TunableReference(description='\n                    One role in the relationship.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
       class_restrictions=('ScenarioRole', )),
       target_role=TunableReference(description='\n                    The other role in the relationship.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
       class_restrictions=('ScenarioRole', )),
       relationship_type=TunableEnumEntry(description='\n                    The type of relationship between a subject sim and\n                    a target sim.\n                    \n                    A value of NONE indicates no familial relationship.\n                    \n                    Relationships are directed from sims with the Subject Role to\n                    sims with the Target Role. For example, if this is tuned to\n                    PARENT, then any sims with the Target Role will be\n                    the parents of any sims with the Subject Role.\n                    ',
       tunable_type=RelationshipType,
       default=(RelationshipType.NONE)),
       household_requirement_text=TunableLocalizedString(description='\n                    The text that will display for this requirement.\n                    '),
       export_class_name='TunableRelationshipRequirement',
       export_modes=(ExportModes.ClientBinary),
       tuning_group=(GroupNames.UI))), 
     'screen_slam_scenario_completed':OptionalTunable(description='\n            If enabled, trigger this Screen Slam when the scenario is completed.\n            ',
       tunable=TunableScreenSlamSnippet(description='\n                A Screen Slam to show when the scenario is completed.\n                \n                Localization Tokens: Scenario Name - {0.String}.\n                '),
       tuning_group=GroupNames.UI), 
     'starting_phase':ScenarioPhase.TunablePackSafeReference(description='\n            A reference to the first phase of the scenario.\n            If empty, scenario will be executed with scenario goals instead of phase goals,\n            according to scenario versions v1 and v2.\n            ',
       allow_none=True,
       export_modes=ExportModes.ClientBinary), 
     'terminators':TunableList(description='\n            List of Terminators.\n            If any terminator test is triggered, the current scenario will be terminated.\n            ',
       tunable=TunableTuple(description='\n                Data containing termination condition and associated scenario outcome. \n                ',
       scenario_outcome=ScenarioOutcome.TunablePackSafeReference(description='\n                    The scenario outcome that will happen if termination conditions are met.\n                    '),
       termination_condition=TunableScenarioBreakTest.TunableFactory(description='\n                    Test to determine if the terminator is triggered.\n                    '),
       terminator_description_text=TunableLocalizedString(description='\n                    Description text for terminator (only for debug purposes).\n                    '))), 
     'outcome_on_cancel':ScenarioOutcome.TunableReference(description='\n            The scenario outcome that will be executed when player manually cancels the scenario.\n            ',
       pack_safe=True,
       allow_none=True), 
     'outcome_on_validation_failed':ScenarioOutcome.TunableReference(description='\n            The scenario outcome that will be executed if for any reason the \n            sources needed for scenario cannot be validated.\n            i.e when npc sim is not alive anymore.\n            ',
       pack_safe=True,
       allow_none=True), 
     'loot_on_end':ScenarioPhaseLoot.TunableFactory(description='\n            The loots that will be applied when scenario ends no matter of the outcome.\n            This is a good place to clean up the temp buff/traits/items that are added only for the scenario.\n            '), 
     'scenario_npc_sims':TunableList(description='\n            A list of sim filters. Sim_infos of satisfying the conditions will be stored in the scenario\n            and used for referencing non household sims in loots and tests inside the scenario.\n            If sim_info satisfying filters does not exist a new one will be created.\n            ',
       tunable=TunableTuple(description='\n                Data containing the sim_filter to reference non household sims.\n                ',
       sim_filter=TunableReference(description='\n                    A sim filter to reference non household sims.\n                    If sim_info satisfying filter does not exist a new one will be created.           \n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER)),
       class_restrictions=TunableSimFilter),
       invalidation_trait=TunableReference(description='\n                    Trait used to invalidate the NPC associated to the scenario when the scenario is finished/reset.\n                    ',
       allow_none=True,
       manager=(services.get_instance_manager(sims4.resources.Types.TRAIT))),
       export_class_name='TunableScenarioNpcSims',
       export_modes=(ExportModes.ClientBinary))), 
     'goals':TunableList(description='\n            A list of SituationGoals that track on any household with this\n            scenario. These act as the end conditions for the scenario. If any\n            goal is achieved, the scenario will end.\n            This is only relevant for scenario versions v1 and v2.\n            Should be empty for v3 and start_phase should be filled instead.\n            ',
       tunable=TunableTuple(description='\n                Data containing the SituationGoal and any additional data about that goal specific to the scenario.\n                ',
       situation_goal=TunablePackSafeReference(description='\n                    A SituationGoal.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_GOAL))),
       goal_description_text=TunableLocalizedString(description='\n                    The text that will display for this goal in the load dialog\n                    and scenario outcome screen.\n                    '),
       goal_title_text=TunableLocalizedString(description='\n                    The title for this goal. This is shown in the scenario outcome screen\n                    and also in the ScenarioLivePanel.\n                    '),
       outcome_header_icon=TunableIcon(description='\n                    The icon that sits next to the header text for each goal\n                    in the ScenarioLivePanel.\n                    ',
       export_modes=(ExportModes.ServerXML),
       allow_none=True),
       required_pack=TunableEnumEntry(description='\n                    The pack that the goal may require.\n                    ',
       tunable_type=(sims4.common.Pack),
       default=(sims4.common.Pack.BASE_GAME),
       export_modes=(ExportModes.All)),
       visible_in_load_dialog=Tunable(description='\n                    If checked, the goal text will be visible in the scenario\n                    load dialog. If unchecked, the goal text will not be\n                    visible in the scenario load dialog.\n                    \n                    This will not affect whether or not the description text\n                    is shown in the outcome screen.\n                    ',
       tunable_type=bool,
       default=True),
       export_class_name='TunableScenarioGoalData',
       export_modes=(ExportModes.ClientBinary))), 
     'household_money':sims4.tuning.tunable.Tunable(description='\n            The starting money of the pre-made household. Can be overridden using a Loot Action in Live Mode.\n            Needed to allow the player to be able to purchase a lot in the Neighborhood Edit mode.\n            ',
       tunable_type=int,
       default=20000,
       export_modes=ExportModes.ClientBinary), 
     'loot_on_scenario_start':TunableMapping(key_name='Enum Entry',
       key_type=TunableEnumEntry(description='\n                How the household enters the scenario\n                ',
       tunable_type=ScenarioEntryMethod,
       default=(ScenarioEntryMethod.NEW_HOUSEHOLD)),
       value_name='Loots',
       value_type=TunableTuple(description='\n                A list of loot actions to apply to the household with this scenario.\n                These are applied only when the scenario starts (the first time a\n                household is loaded with the scenario).\n                ',
       household_loot=TunableList(description='\n                    Loot that will apply once to an arbitrary sim in the household.\n                    \n                    Useful for applying loot to the household as a whole. For example,\n                    this can be used to set the household funds at the start of the\n                    scenario.\n                    ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', ))),
       rel_loot=TunableList(description='\n                    Loot that will apply to each pair of sims in the household.\n                    \n                    Useful for setting up relationships at the start of the\n                    scenario.\n                    \n                    Subject and targets should be Actor and TargetSim, respectively.\n                    ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', ))))), 
     'loot_on_scenario_end':TunableTuple(description='\n            Loot that applies when the scenario ends.\n            ',
       household_loot_on_successful_completion=TunableList(description='\n                Loot that applies to an arbitrary sim in the household if the scenario\n                ends successfully, meaning the scenario ended because a non-hidden\n                goal was achieved.\n                ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', )))), 
     'outcome_screen_background_image':OptionalTunable(description=',\n            The background image for the outcome screen when the scenario ends.\n            ',
       tunable=TunableResourceKey(resource_types=(sims4.resources.CompoundTypes.IMAGE)),
       tuning_group=GroupNames.UI), 
     'ui_sort_order':sims4.tuning.tunable.Tunable(description='\n            Order in which the scenario will appear in the scenario list dialog.\n            Scenarios sort from lowest to highest.\n            ',
       tunable_type=int,
       default=0,
       export_modes=ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'compatible_premade_household_templates':TunableList(description='\n            The Premade Households that are compatible with this scenario. \n            NOTE: only the first one in the list will be selected for this scenario \n            (in the future the player will have a choice of which one to pick from).\n            ',
       tunable=TunableResourceKey(description='\n                The Household file to use.\n                ',
       default=None,
       resource_types=(
      sims4.resources.Types.HOUSEHOLD_BINARY,),
       export_modes=(ExportModes.ClientBinary))), 
     'properties':TunableEnumFlags(description='\n            A set of properties related to this scenario.\n            ',
       enum_type=ScenarioProperties,
       export_modes=ExportModes.All)}

    def __init__(self, scenario_tracker, **kwargs):
        (super().__init__)(**kwargs)
        self._has_started = False
        self._active_goals = []
        self._triggered_phases_guid64 = set()
        self._skipped_phases_guid64 = set()
        self._last_completed_visible_goal_for_sequence = {}
        self._active_phase = None
        self._terminator_handlers = []
        self._last_phase_outputs = {}
        self._scenario_tracker = scenario_tracker
        self._goal_id_gen = uid.UniqueIdGenerator(1)
        self._role_id_to_role_traits = {}
        self._sim_id_to_role_id_map = {}
        self._role_id_to_sim_info_map = {}
        self._sim_time_lapsed = None
        self._sim_time_marker = None
        self._instance_id = 0
        self._scenario_entry_method = None
        for role_data in self.scenario_role_data:
            self._role_id_to_role_traits[role_data.role.guid64] = role_data.role_traits

        self._sim_filter_id_to_sim_info_map = {}
        self._loaded_sim_filter_id_to_sim_info_id_map = {}
        self._completed_goal_infos = {}
        self._terminated_phase_infos = {}

    @property
    def household(self):
        return self._scenario_tracker.household

    def reset_scenario_data(self):
        self._has_started = False
        self._role_id_to_role_traits = {}
        self._role_id_to_sim_info_map = {}
        self._sim_id_to_role_id_map = {}
        self._sim_time_lapsed = None
        self._sim_time_marker = None
        self._active_goals = []
        self._triggered_phases_guid64 = set()
        self._terminator_handlers = []
        self._last_phase_outputs = {}
        self._last_completed_visible_goal_for_sequence = {}
        self._sim_filter_id_to_sim_info_map = {}
        self._loaded_sim_filter_id_to_sim_info_id_map = {}
        self._completed_goal_infos = {}
        self._terminated_phase_infos = {}

    def sims_of_interest_gen(self, roles=None):
        if not roles:
            yield from (sim_info.get_sim_instance() for sim_info in self._scenario_tracker.household if sim_info.is_instanced())
        else:
            for role in roles:
                if role.guid64 not in self._role_id_to_sim_info_map:
                    continue
                sim_infos = self._role_id_to_sim_info_map[role.guid64]
                for sim_info in sim_infos:
                    sim = sim_info.get_sim_instance()
                    if sim is not None:
                        yield sim

    def sim_infos_of_interest_gen(self, roles=None):
        if not roles:
            yield from self._scenario_tracker.household
        else:
            for role in roles:
                if role is None:
                    continue
                if role.guid64 not in self._role_id_to_sim_info_map:
                    continue
                yield from self._role_id_to_sim_info_map[role.guid64]

        if False:
            yield None

    def on_household_member_removed(self, sim_info):
        self._sim_id_to_role_id_map.pop(sim_info.id, None)
        for _, sim_infos in self._role_id_to_sim_info_map.items():
            if sim_info in sim_infos:
                sim_infos.remove(sim_info)

    def get_role_traits_for_role_id(self, role_id):
        return self._role_id_to_role_traits.get(role_id, None)

    def get_role_id_for_sim(self, sim_id):
        return self._sim_id_to_role_id_map.get(sim_id, None)

    def get_role_for_sim(self, sim_id):
        return services.snippet_manager().get(self._sim_id_to_role_id_map.get(sim_id, 0))

    def active_goals_gen(self):
        for active_goal, _ in self._active_goals:
            yield active_goal

    def active_goals_and_tuning_gen(self):
        yield from self._active_goals
        if False:
            yield None

    def is_goal_completed(self, goal_guid64):
        return goal_guid64 in self._completed_goal_infos

    def get_goal_completion_time(self, goal_guid64):
        return self._completed_goal_infos.get(goal_guid64)

    @property
    def triggered_phases_guids(self):
        return self._triggered_phases_guid64

    def get_sim_info_from_sim_filter(self, sim_filter):
        if sim_filter.guid64 in self._sim_filter_id_to_sim_info_map:
            return self._sim_filter_id_to_sim_info_map[sim_filter.guid64]
        for scenario_npc in self.scenario_npc_sims:
            if scenario_npc.sim_filter.guid64 == sim_filter.guid64:
                filter_results = services.sim_filter_service().submit_matching_filter(sim_filter=sim_filter,
                  allow_yielding=False,
                  conform_if_constraints_fail=False)
                if len(filter_results) > 0:
                    self._sim_filter_id_to_sim_info_map[sim_filter.guid64] = filter_results[0].sim_info
                    return self._sim_filter_id_to_sim_info_map[sim_filter.guid64]

    @property
    def has_started(self):
        return self._has_started

    def start_scenario(self):
        self._sim_time_lapsed = TimeSpan(0)
        self._sim_time_marker = services.time_service().sim_now
        if self.starting_phase is None:
            self.start_scenario_without_phase()
        else:
            self.run_sim_filters_for_scenario_npcs()
            self.register_scenario_terminators()
            self.start_phase(self.starting_phase(scenario=self))
        self._has_started = True
        dialog = self.scenario_start_notification(services.active_sim_info())
        dialog.show_dialog(additional_tokens=(self.scenario_name,))

    def start_scenario_without_phase(self):
        loot_tuple = self.loot_on_scenario_start.get(ScenarioEntryMethod(self._scenario_entry_method))
        if loot_tuple is not None:
            with hide_selected_notifications():
                if loot_tuple.household_loot:
                    sim = next(iter(self._scenario_tracker.household), None)
                    if sim is None:
                        logger.error('Household is empty while trying to start scenario!')
                    else:
                        resolver = SingleSimResolver(sim)
                        for action in loot_tuple.household_loot:
                            action.apply_to_resolver(resolver)

                if loot_tuple.rel_loot:
                    for sim_info_a, sim_info_b in itertools.combinations(self._scenario_tracker.household, 2):
                        resolver = DoubleSimResolver(sim_info_a, sim_info_b)
                        for action in loot_tuple.rel_loot:
                            action.apply_to_resolver(resolver)

        self._active_goals = [ActiveGoal(goal_tuple.situation_goal(goal_id=(self._goal_id_gen()), scenario=self), goal_tuple) for goal_tuple in self.goals if goal_tuple.situation_goal is not None]
        self.setup_goals()

    def start_phase(self, phase, run_pretests=True):
        if phase.guid64 in self._triggered_phases_guid64:
            for goal_sequence_tuple in phase.goals:
                for goal_tuple in goal_sequence_tuple.goal_sequence:
                    goal_id = goal_tuple.goal.situation_goal.guid64
                    if goal_id in self._completed_goal_infos:
                        del self._completed_goal_infos[goal_id]

        else:
            self._triggered_phases_guid64.add(phase.guid64)
            services.get_event_manager().process_event((test_events.TestEvent.ScenarioPhaseTriggered), None,
              phase=phase)
            self._last_completed_visible_goal_for_sequence = {}
            if not run_pretests or phase.run_pre_tests():
                self._active_phase = phase
                self.apply_loot(phase.intro_loot.loots)
                self.set_active_goals_on_phase_start(phase)
                self.setup_goals()
                phase.on_start()
                self._scenario_tracker.send_goal_update_op_to_client()
            else:
                phase.choose_output_and_progress(PhaseEndingReason.SKIPPED)
                self._skipped_phases_guid64.add(phase.guid64)

    def reset_active_phase(self):
        self.start_phase(self._active_phase, False)

    def reset_goal(self, situation_goal_guid64):
        for active_goal in self._active_goals:
            if active_goal.situation_goal.guid64 == situation_goal_guid64:
                active_goal.situation_goal.reset_count()
                break
        else:
            return False

        self._scenario_tracker.send_goal_update_op_to_client()
        return True

    def __str__(self):
        return self.__class__.__name__

    def on_phase_ended(self, reason, end_description):
        if reason == PhaseEndingReason.TERMINATED:
            termination_time = services.time_service().sim_now.absolute_ticks()
            self._terminated_phase_infos[self._active_phase.guid64] = termination_time
        self._scenario_tracker.on_phase_finished(self._active_phase, reason, end_description)
        if scenario_profiles is not None:
            self.update_scenario_profile_on_phase_end()
        self._active_phase = None

    def update(self):
        if scenario_profiles is not None:
            self.update_scenario_profile()

    def update_scenario_profile(self):
        scenario_record_name = str(self)
        record = scenario_profiles.get(scenario_record_name)
        if record is None:
            record = dict()
            scenario_profiles[scenario_record_name] = record
        if should_record_scenario_profile_metrics(record, self._active_phase):
            record_scenario_profile_metrics(record, self._active_phase, math.ceil(get_sim_debt_time()))

    def update_scenario_profile_on_phase_end(self):
        scenario_record_name = str(self)
        record = scenario_profiles.get(scenario_record_name)
        if record is not None:
            scenario_profile_on_phase_end(record, self._active_phase, get_sim_debt_time())

    def on_phase_output_triggered(self, output_key, next_phase):
        output_time = services.time_service().sim_now.absolute_ticks()
        next_phase_name = next_phase.__name__ if next_phase is not None else 'None'
        self._last_phase_outputs[self._active_phase.guid64] = (output_key, next_phase_name, output_time)

    def get_phase_last_output_info(self, phase_guid64):
        return self._last_phase_outputs.get(phase_guid64)

    def set_active_goals_on_phase_start(self, phase):
        self.clean_up_goals()
        self._active_goals.clear()
        for goal_tuple in phase.goals:
            self.activate_goal(self.generate_active_goal_tuple_from_sequence(goal_tuple.goal_sequence, 0))

    def generate_active_goal_tuple_from_sequence(self, goal_sequence, index):
        if index < len(goal_sequence):
            phase_goal = goal_sequence[index].goal
            return ActiveGoal(phase_goal.situation_goal(goal_id=(self._goal_id_gen()), scenario=self), phase_goal)
        return

    def setup_goals(self):
        for goal in self.active_goals_gen():
            self.setup_goal(goal, reevaluate=False)

        for goal in self.active_goals_gen():
            if not goal.should_reevaluate_on_load:
                continue
            goal.reevaluate_goal_completion()

    def setup_goal(self, goal, reevaluate=True):
        goal.setup()
        goal.register_for_on_goal_completed_callback(self._on_goal_completed)
        if reevaluate:
            if goal.should_reevaluate_on_load:
                goal.reevaluate_goal_completion()

    def clean_up_goals(self):
        for goal in self.active_goals_gen():
            goal.decommision()

    def on_goal_sequence_reset(self, goal_sequence, sequence_index):
        for goal_tuple in goal_sequence:
            active_goal = self.get_active_goal_from_scenario_goal(goal_tuple.goal)
            goal_id = goal_tuple.goal.situation_goal.guid64
            if active_goal is not None:
                self._active_goals.remove(active_goal)
            elif goal_id in self._completed_goal_infos:
                del self._completed_goal_infos[goal_id]

        self._last_completed_visible_goal_for_sequence.pop(sequence_index)
        self.activate_goal(self.generate_active_goal_tuple_from_sequence(goal_sequence, 0))
        self.setup_goal(self._active_goals[-1].situation_goal)

    def get_active_goal_from_scenario_goal(self, scenario_goal):
        for active_goal in self._active_goals:
            if active_goal.scenario_goal is scenario_goal:
                return active_goal

    def register_scenario_terminators(self):
        for terminator in self.terminators:
            self._terminator_handlers.append(TerminatorHandler(self, terminator, self.on_terminator_triggered))
            services.get_event_manager().register_tests(self._terminator_handlers[-1], (terminator.termination_condition.scenario_test.test,))

    def unregister_scenario_terminators(self):
        for terminator_handler in self._terminator_handlers:
            services.get_event_manager().unregister_tests(terminator_handler, (terminator_handler.terminator.termination_condition.scenario_test.test,))

        self._terminator_handlers.clear()

    def on_terminator_triggered(self, terminator):
        last_phase = self._active_phase
        self._active_phase.on_terminator_triggered(terminator)
        self.end_scenario(terminator.scenario_outcome, last_phase)

    def run_sim_filters_for_scenario_npcs(self):
        for sim_filter_tuple in self.scenario_npc_sims:
            filter_results = services.sim_filter_service().submit_matching_filter(sim_filter=(sim_filter_tuple.sim_filter), allow_yielding=False, conform_if_constraints_fail=True)
            for result in filter_results:
                self._sim_filter_id_to_sim_info_map[sim_filter_tuple.sim_filter.guid64] = result.sim_info

    def end_scenario(self, outcome, last_phase, cancelled=False):
        scenario_outcome = outcome if not cancelled else self.outcome_on_cancel
        if scenario_outcome is not None:
            self.apply_outcome(scenario_outcome)
        self.apply_loot(self.loot_on_end.loots)
        if not cancelled:
            self._scenario_tracker.end_scenario(last_phase=last_phase, outcome=scenario_outcome)
        self.unregister_scenario_terminators()
        self.clean_up_goals()
        for sim_info in self.household:
            self._scenario_tracker.remove_role_traits(sim_info)

    def apply_loot(self, loots):

        def apply_double_sim_loot(sim_info, sim_info_2):
            resolver = DoubleSimResolver(sim_info, sim_info_2)
            resolver.set_additional_metric_key_data(self._active_phase)
            loot_tuple.scenario_loot.loot_action.apply_to_resolver(resolver)

        def check_and_apply_single_or_double_sim_loot(sim_info, loot_tuple):
            secondary_actor_role = loot_tuple.scenario_loot.secondary_actor_role
            secondary_actor_sim_filter = loot_tuple.scenario_loot.secondary_actor_sim_filter
            if secondary_actor_role is not None:
                for sim_info_2 in self.sim_infos_of_interest_gen([secondary_actor_role]):
                    apply_double_sim_loot(sim_info, sim_info_2)

            else:
                if secondary_actor_sim_filter is not None:
                    sim_info_2 = self.get_sim_info_from_sim_filter(secondary_actor_sim_filter)
                    if sim_info_2 is not None:
                        apply_double_sim_loot(sim_info, sim_info_2)
                    else:
                        logger.error('No sim satisfying secondary_actor_sim_filter conditions is found.')
                else:
                    resolver = event_testing.resolver.DataResolver(sim_info=sim_info, additional_metric_key_data=(self._active_phase))
                    loot_tuple.scenario_loot.loot_action.apply_to_resolver(resolver)

        for loot_tuple in loots:
            actor_role = loot_tuple.scenario_loot.actor_role
            actor_sim_filter = loot_tuple.scenario_loot.actor_sim_filter
            if actor_role is not None:
                for sim_info in self.sim_infos_of_interest_gen([actor_role]):
                    check_and_apply_single_or_double_sim_loot(sim_info, loot_tuple)

            elif actor_sim_filter is not None:
                sim_info = self.get_sim_info_from_sim_filter(actor_sim_filter)
                if sim_info is not None:
                    check_and_apply_single_or_double_sim_loot(sim_info, loot_tuple)
                else:
                    logger.error('No sim satisfying actor_sim_filter conditions is found.')
            else:
                loot_tuple.scenario_loot.loot_action.apply_to_resolver(GlobalResolver(additional_metric_key_data=(self._active_phase)))

    def apply_outcome(self, outcome):
        tests_passed = True
        for test_tuple in outcome.tests.scenario_tests:
            if not run_scenario_test(test_tuple.scenario_test, self, self._active_phase):
                tests_passed = False
                break

        if tests_passed:
            self.apply_loot(outcome.scenario_outcome_loot.loots)

    def save(self, household_proto):
        household_scenario_data_msg = household_proto.scenario_data
        gameplay_scenario_data_msg = household_proto.gameplay_data.gameplay_scenario_tracker.active_scenario_data
        household_scenario_data_msg.scenario_id = self.guid64
        household_scenario_data_msg.instance_id = self.instance_id
        for sim_id, role_id in self._sim_id_to_role_id_map.items():
            with ProtocolBufferRollback(household_scenario_data_msg.sim_role_pairs) as (sim_role_pair):
                sim_role_pair.sim_id = sim_id
                sim_role_pair.role_id = role_id

        household_scenario_data_msg.scenario_entry_method = self._scenario_entry_method
        if self._has_started:
            gameplay_scenario_data_msg.scenario_guid = self.guid64
            gameplay_scenario_data_msg.sim_time_lapsed = self.sim_time_lapsed.in_ticks()
            for active_goal in self.active_goals_gen():
                with ProtocolBufferRollback(gameplay_scenario_data_msg.active_goals) as (goal_proto):
                    goal_seed = active_goal.create_seedling()
                    goal_seed.finalize_creation_for_save()
                    goal_seed.serialize_to_proto(goal_proto.goal_data)

            if self.starting_phase is not None:
                self.save_phase_related_data(gameplay_scenario_data_msg)

    def save_phase_related_data(self, gameplay_scenario_data_msg):
        gameplay_scenario_data_msg.active_phase_guid = self._active_phase.guid64
        gameplay_scenario_data_msg.triggered_phases.extend(self._triggered_phases_guid64)
        gameplay_scenario_data_msg.skipped_phases.extend(self._skipped_phases_guid64)
        for sequence_index, last_visible_goal in self._last_completed_visible_goal_for_sequence.items():
            with ProtocolBufferRollback(gameplay_scenario_data_msg.last_completed_goal_sequence_pair) as (completed_goal_sequence_pair_proto):
                goal_seed = last_visible_goal.goal.create_seedling()
                goal_seed.finalize_creation_for_save()
                goal_seed.serialize_to_proto(completed_goal_sequence_pair_proto.completed_goal.goal_data)
                completed_goal_sequence_pair_proto.sequence_index = sequence_index
                completed_goal_sequence_pair_proto.is_mandatory = last_visible_goal.is_mandatory

        for phase_guid64, output_info in self._last_phase_outputs.items():
            output_key, next_phase, output_time = output_info
            with ProtocolBufferRollback(gameplay_scenario_data_msg.last_phase_outputs) as (phase_output_info):
                phase_output_info.phase_guid64 = phase_guid64
                phase_output_info.output_key = output_key
                phase_output_info.next_phase = next_phase
                phase_output_info.output_time = output_time

        for sim_filter_id, sim_info in self._sim_filter_id_to_sim_info_map.items():
            with ProtocolBufferRollback(gameplay_scenario_data_msg.sim_filter_sim_info_pair) as (sim_filter_sim_info_pair):
                sim_filter_sim_info_pair.sim_filter_id = sim_filter_id
                sim_filter_sim_info_pair.sim_info_id = sim_info.id

        for goal_guid64, completion_time in self._completed_goal_infos.items():
            with ProtocolBufferRollback(gameplay_scenario_data_msg.completed_goal_infos) as (completed_goal_info):
                completed_goal_info.goal_guid64 = goal_guid64
                completed_goal_info.completion_time = completion_time

        for phase_guid64, termination_time in self._terminated_phase_infos.items():
            with ProtocolBufferRollback(gameplay_scenario_data_msg.terminated_phase_infos) as (terminated_phase_info):
                terminated_phase_info.phase_guid64 = phase_guid64
                terminated_phase_info.termination_time = termination_time

    def load_household_data(self, scenario_data_msg, gameplay_scenario_data_msg, scenario_started_before=False):
        self._has_started = scenario_started_before
        self._instance_id = scenario_data_msg.instance_id
        sim_info_manager = services.sim_info_manager()
        for pair_proto in scenario_data_msg.sim_role_pairs:
            sim_info = sim_info_manager.get(pair_proto.sim_id)
            if sim_info is None:
                continue
            self._sim_id_to_role_id_map[pair_proto.sim_id] = pair_proto.role_id
            if pair_proto.role_id in self._role_id_to_sim_info_map:
                self._role_id_to_sim_info_map[pair_proto.role_id].append(sim_info)
            else:
                self._role_id_to_sim_info_map[pair_proto.role_id] = [
                 sim_info]

        self._sim_time_lapsed = TimeSpan(gameplay_scenario_data_msg.sim_time_lapsed)
        self._sim_time_marker = services.time_service().sim_now if self.household.is_active_household else None
        self._scenario_entry_method = scenario_data_msg.scenario_entry_method

        def to_goal(goal_seed):
            return goal_seed.goal_type(goal_id=(self._goal_id_gen()), count=(goal_seed.count),
              reader=(goal_seed.reader),
              completed_time=(goal_seed.completed_time),
              scenario=self,
              sub_goals=[to_goal(sub_goal_seed) for sub_goal_seed in goal_seed.sub_goal_seeds])

        if self._has_started:
            phase_id = gameplay_scenario_data_msg.active_phase_guid
            phase = self.get_phase_with_id(phase_id)
            if phase is None:
                self.load_data_without_phase(gameplay_scenario_data_msg, to_goal)
            else:
                self.load_data_with_phase(phase, gameplay_scenario_data_msg, to_goal)

    def load_data_without_phase(self, gameplay_scenario_data_msg, to_goal):
        for goal_proto in gameplay_scenario_data_msg.active_goals:
            goal_seed = GoalSeedling.deserialize_from_proto(goal_proto.goal_data)
            if goal_seed is None:
                continue
            goal_guid64_to_load = goal_seed.goal_type.guid64
            for goal_tuning in self.goals:
                if goal_tuning.situation_goal.guid64 == goal_guid64_to_load:
                    goal = to_goal(goal_seed)
                    self._active_goals.append(ActiveGoal(goal, goal_tuning))
                    break

        goal_ids = [situation_goal.guid64 for situation_goal in self.active_goals_gen()]
        for goal_tuning in self.goals:
            if goal_tuning.situation_goal is not None and goal_tuning.situation_goal.guid64 not in goal_ids:
                goal = goal_tuning.situation_goal(goal_id=(self._goal_id_gen()), scenario=self)
                self._active_goals.append(ActiveGoal(goal, goal_tuning))

    def load_data_with_phase(self, phase, gameplay_scenario_data_msg, to_goal):
        self.register_scenario_terminators()
        self._active_phase = phase(scenario=self)
        self._active_phase.on_load()
        for completed_goal_info in gameplay_scenario_data_msg.completed_goal_infos:
            self._completed_goal_infos[completed_goal_info.goal_guid64] = completed_goal_info.completion_time

        for goal_proto in gameplay_scenario_data_msg.active_goals:
            goal_seed = GoalSeedling.deserialize_from_proto(goal_proto.goal_data)
            if goal_seed is None:
                continue
            goal_guid64_to_load = goal_seed.goal_type.guid64
            for goal_sequence_tuple in phase.goals:
                for goal_tuple in goal_sequence_tuple.goal_sequence:
                    if goal_tuple.goal.situation_goal.guid64 == goal_guid64_to_load:
                        goal = to_goal(goal_seed)
                        self.activate_goal(ActiveGoal(goal, goal_tuple.goal))
                        break
                else:
                    continue

                break

        self._triggered_phases_guid64 = set(gameplay_scenario_data_msg.triggered_phases)
        self._skipped_phases_guid64 = set(gameplay_scenario_data_msg.skipped_phases)
        active_goal_ids = [situation_goal.guid64 for situation_goal in self.active_goals_gen()]
        for goal_sequence_tuple in phase.goals:
            new_goal_candidate = None
            for goal_tuple in goal_sequence_tuple.goal_sequence:
                goal_id = goal_tuple.goal.situation_goal.guid64
                if goal_id in active_goal_ids:
                    new_goal_candidate = None
                    break
                elif self.is_goal_completed(goal_id):
                    new_goal_candidate = None
                elif new_goal_candidate is None and goal_id not in active_goal_ids:
                    new_goal_candidate = self.is_goal_completed(goal_id) or goal_tuple

            if new_goal_candidate is not None:
                goal = new_goal_candidate.goal.situation_goal(goal_id=(self._goal_id_gen()), scenario=self)
                self.activate_goal(ActiveGoal(goal, new_goal_candidate.goal))

        for completed_goal_sequence_pair_proto in gameplay_scenario_data_msg.last_completed_goal_sequence_pair:
            goal_seed = GoalSeedling.deserialize_from_proto(completed_goal_sequence_pair_proto.completed_goal.goal_data)
            if goal_seed is None:
                continue
            goal = to_goal(goal_seed)
            self._last_completed_visible_goal_for_sequence[completed_goal_sequence_pair_proto.sequence_index] = LastVisibleGoal(goal, completed_goal_sequence_pair_proto.is_mandatory)

        for pair_proto in gameplay_scenario_data_msg.sim_filter_sim_info_pair:
            self._loaded_sim_filter_id_to_sim_info_id_map[pair_proto.sim_filter_id] = pair_proto.sim_info_id

        for phase_output_info in gameplay_scenario_data_msg.last_phase_outputs:
            self._last_phase_outputs[phase_output_info.phase_guid64] = (phase_output_info.output_key,
             phase_output_info.next_phase,
             phase_output_info.output_time)

        for terminated_phase_info in gameplay_scenario_data_msg.terminated_phase_infos:
            self._terminated_phase_infos[terminated_phase_info.phase_guid64] = terminated_phase_info.termination_time

    def activate_goal(self, active_goal):
        self._active_goals.append(active_goal)
        self.apply_loot(active_goal.scenario_goal.loot_on_instantiate)

    def validate_sim_infos--- This code section failed: ---

 L.1450         0  LOAD_GLOBAL              services
                2  LOAD_METHOD              sim_info_manager
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  STORE_FAST               'sim_info_manager'

 L.1451         8  SETUP_LOOP          106  'to 106'
               10  LOAD_FAST                'self'
               12  LOAD_ATTR                _loaded_sim_filter_id_to_sim_info_id_map
               14  LOAD_METHOD              items
               16  CALL_METHOD_0         0  '0 positional arguments'
               18  GET_ITER         
               20  FOR_ITER            104  'to 104'
               22  UNPACK_SEQUENCE_2     2 
               24  STORE_FAST               'sim_filter_id'
               26  STORE_FAST               'sim_info_id'

 L.1452        28  LOAD_FAST                'sim_info_manager'
               30  LOAD_METHOD              get
               32  LOAD_FAST                'sim_info_id'
               34  CALL_METHOD_1         1  '1 positional argument'
               36  STORE_FAST               'sim_info'

 L.1453        38  LOAD_FAST                'sim_info'
               40  LOAD_CONST               None
               42  COMPARE_OP               is
               44  POP_JUMP_IF_TRUE     74  'to 74'
               46  LOAD_FAST                'sim_info'
               48  LOAD_ATTR                can_instantiate_sim
               50  POP_JUMP_IF_FALSE    74  'to 74'

 L.1454        52  LOAD_FAST                'sim_info'
               54  LOAD_ATTR                death_type
               56  LOAD_CONST               None
               58  COMPARE_OP               is-not
               60  POP_JUMP_IF_FALSE    92  'to 92'
               62  LOAD_FAST                'sim_info'
               64  LOAD_ATTR                death_type
               66  LOAD_GLOBAL              DeathType
               68  LOAD_ATTR                NONE
               70  COMPARE_OP               !=
               72  POP_JUMP_IF_FALSE    92  'to 92'
             74_0  COME_FROM            50  '50'
             74_1  COME_FROM            44  '44'

 L.1455        74  LOAD_FAST                'self'
               76  LOAD_METHOD              end_scenario
               78  LOAD_FAST                'self'
               80  LOAD_ATTR                outcome_on_validation_failed
               82  LOAD_FAST                'self'
               84  LOAD_ATTR                _active_phase
               86  CALL_METHOD_2         2  '2 positional arguments'
               88  POP_TOP          

 L.1456        90  BREAK_LOOP       
             92_0  COME_FROM            72  '72'
             92_1  COME_FROM            60  '60'

 L.1457        92  LOAD_FAST                'sim_info'
               94  LOAD_FAST                'self'
               96  LOAD_ATTR                _sim_filter_id_to_sim_info_map
               98  LOAD_FAST                'sim_filter_id'
              100  STORE_SUBSCR     
              102  JUMP_BACK            20  'to 20'
              104  POP_BLOCK        
            106_0  COME_FROM_LOOP        8  '8'

Parse error at or near `JUMP_BACK' instruction at offset 102

    def get_phase_with_id(self, phase_id):
        if self.starting_phase is not None:
            return find_phase_with_id(self.starting_phase, phase_id)

    def get_all_phases(self):

        def traverse_next_phases(phase, phases):
            if phase in phases:
                return
            phases.add(phase)
            for phase_output in phase.phase_outputs:
                if phase_output.output.output.next_phase is not None:
                    traverse_next_phases(phase_output.output.output.next_phase, phases)

            if phase.phase_fallback_output.output.next_phase is not None:
                traverse_next_phases(phase.phase_fallback_output.output.next_phase, phases)

        all_phases = set()
        if self.starting_phase is not None:
            traverse_next_phases(self.starting_phase, all_phases)
        return all_phases

    @property
    def sim_time_lapsed(self):
        if self._sim_time_marker is None:
            return self._sim_time_lapsed
        delta_time_span = services.time_service().sim_now - self._sim_time_marker
        return self._sim_time_lapsed + delta_time_span

    def _on_goal_completed(self, goal, is_completed):
        completed_goal = goal if is_completed else None
        if self.starting_phase is None:
            self._scenario_tracker.send_goal_update_op_to_client(completed_goal=completed_goal)
            self._scenario_tracker.on_goal_completed(goal, is_completed)
        else:
            if is_completed and self._active_phase is not None:
                self.update_goal_sequences_on_complete(goal)
                self._scenario_tracker.send_goal_update_op_to_client(completed_goal=completed_goal)
                completed_goal.decommision()
                services.get_event_manager().process_event((test_events.TestEvent.ScenarioGoalCompleted), None, situation_goal=completed_goal)
                if not self.is_there_mandatory_active_goals():
                    if self._active_phase is not None:
                        self._active_phase.choose_output_and_progress(PhaseEndingReason.COMPLETE)
            else:
                self._scenario_tracker.send_goal_update_op_to_client(completed_goal=completed_goal)

    def update_goal_sequences_on_complete(self, completed_goal):
        completed_goal.unregister_for_on_goal_completed_callback(self._on_goal_completed)
        if self._active_phase is None:
            return
        next_goal_in_sequence_found = False
        for sequence_index, goal_tuple in enumerate(self._active_phase.goals):
            if next_goal_in_sequence_found:
                break
            for index, phase_goal in enumerate(goal_tuple.goal_sequence):
                if phase_goal.goal.situation_goal.guid64 == completed_goal.guid64:
                    if completed_goal.is_visible:
                        self._last_completed_visible_goal_for_sequence[sequence_index] = LastVisibleGoal(completed_goal, phase_goal.goal.mandatory)
                    if len(goal_tuple.goal_sequence) > index + 1:
                        goal_to_add = self.generate_active_goal_tuple_from_sequence(goal_tuple.goal_sequence, index + 1)
                        self.activate_goal(goal_to_add)
                        self.setup_goal(self._active_goals[-1].situation_goal)
                        next_goal_in_sequence_found = True
                    break

        found_in_active_goals = False
        for active_goal in self._active_goals:
            if active_goal.situation_goal.id == completed_goal.id:
                self.apply_loot(active_goal.scenario_goal.goal_loot)
                found_in_active_goals = True
                completion_time = services.time_service().sim_now.absolute_ticks()
                self._completed_goal_infos[active_goal.situation_goal.guid64] = completion_time
                break

        if found_in_active_goals:
            self._active_goals.remove(active_goal)

    def is_there_mandatory_active_goals(self):
        for active_goal in self._active_goals:
            if active_goal.scenario_goal.mandatory:
                return True

        return False

    def is_phase_active(self, phase_guid64):
        return self.current_phase_id == phase_guid64

    def is_phase_triggered(self, phase_guid64):
        return phase_guid64 in self._triggered_phases_guid64

    def is_phase_skipped(self, phase_guid64):
        return phase_guid64 in self._skipped_phases_guid64

    def is_phase_terminated(self, phase_guid64):
        return phase_guid64 in self._terminated_phase_infos

    def get_phase_termination_time(self, phase_guid64):
        return self._terminated_phase_infos.get(phase_guid64)

    @property
    def instance_id(self):
        return self._instance_id

    @property
    def current_phase(self):
        return self._active_phase

    @property
    def current_phase_id(self):
        if self._active_phase:
            return self._active_phase.guid64


@assertions.not_recursive
def find_phase_with_id(phase, phase_guid64):
    if phase.guid64 == phase_guid64:
        return phase
    for phase_output in phase.phase_outputs:
        if phase_output.output.output.next_phase is not None:
            found_phase = find_phase_with_id(phase_output.output.output.next_phase, phase_guid64)
            if found_phase is not None:
                return found_phase

    if phase.phase_fallback_output.output.next_phase is not None:
        found_phase = find_phase_with_id(phase.phase_fallback_output.output.next_phase, phase_guid64)
        if found_phase is not None:
            return found_phase


def get_sim_debt_time():
    time_service = services.time_service()
    if time_service:
        return time_service.get_simulator_debt()
    return 0