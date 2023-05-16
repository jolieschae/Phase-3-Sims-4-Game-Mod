# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gameplay_scenarios\scenario_tracker.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 23428 bytes
import alarms, clock, distributor, services, sims4, telemetry_helper
from distributor.ops import GenericProtocolBufferOp
from distributor.shared_messages import IconInfoData, create_icon_info_msg
from distributor.system import Distributor
from distributor.rollback import ProtocolBufferRollback
from event_testing.resolver import SingleSimResolver
from households.household_tracker import HouseholdTracker
from situations.situation_types import SituationGoalDisplayType
from gameplay_scenarios.scenario_phase import PhaseEndingReason
from protocolbuffers import Situations_pb2, UI_pb2
from protocolbuffers.DistributorOps_pb2 import Operation
from sims.sim_info_lod import SimInfoLODLevel
from sims4.resources import get_protobuff_for_key
from sims4.utils import classproperty
from ui.ui_utils import UIUtils
logger = sims4.log.Logger('Gameplay Scenario Tracker', default_owner='jmorrow')
TELEMETRY_GROUP_SCENARIOS = 'SCEN'
TELEMETRY_HOOK_SCENARIO_COMPLETE = 'ENDD'
TELEMETRY_HOOK_GOAL_COMPLETE = 'GOAL'
TELEMETRY_HOOK_PHASE_END = 'PHAS'
TELEMETRY_ATTRIBUTE_SCENARIO_GUID = 'scid'
TELEMETRY_ATTRIBUTE_SCENARIO_INSTANCE_ID = 'usid'
TELEMETRY_ATTRIBUTE_GOAL_GUID = 'goid'
TELEMETRY_ATTRIBUTE_END_GOAL_GUID = 'edid'
TELEMETRY_ATTRIBUTE_PHASE_GUID = 'phas'
TELEMETRY_ATTRIBUTE_PHASE_TERMINATOR = 'term'
TELEMETRY_ATTRIBUTE_PHASE_OUTPUT = 'phou'
TELEMETRY_ATTRIBUTE_PHASE_STEP = 'phst'
TELEMETRY_ATTRIBUTE_PHASE_END_REASON = 'pher'
writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_SCENARIOS)
with sims4.reload.protected(globals()):
    _show_hidden_goals = False

class ScenarioTracker(HouseholdTracker):

    def __init__(self, household, *args, **kwargs):
        self._household = household
        self._active_scenario = None
        self.outcome_celebration_alarm_handle = None
        self._current_phase_index = 0

    @classproperty
    def _tracker_lod_threshold(cls):
        return SimInfoLODLevel.FULL

    def household_lod_cleanup(self):
        if self._active_scenario is not None:
            self._active_scenario.reset_scenario_data()

    @property
    def household(self):
        return self._household

    @property
    def active_scenario(self):
        return self._active_scenario

    def get_role_id_for_sim_for_active_scenario(self, sim_id):
        if self._active_scenario is None:
            return
        return self._active_scenario.get_role_id_for_sim(sim_id)

    def get_role_for_sim_for_active_scenario(self, sim_id):
        if self._active_scenario is None:
            return
        return self._active_scenario.get_role_for_sim(sim_id)

    def start_scenario(self, scenario_type, logger=None):
        if self._active_scenario is not None:
            if logger is not None:
                logger('Cannot start scenario when another scenario is already active on the household. The active scenario must be canceled first.')
            return
        self._active_scenario = scenario_type(self)
        self._active_scenario.start_scenario()
        self.send_goal_update_op_to_client()
        if logger is not None:
            logger('Successfully started scenario.')

    def send_goal_completed_telemetry(self, goal):
        if self._active_scenario is None:
            return
        with telemetry_helper.begin_hook(writer, TELEMETRY_HOOK_GOAL_COMPLETE) as (hook):
            hook.write_int(TELEMETRY_ATTRIBUTE_SCENARIO_GUID, self._active_scenario.guid64)
            hook.write_int(TELEMETRY_ATTRIBUTE_SCENARIO_INSTANCE_ID, self._active_scenario.instance_id)
            hook.write_int(TELEMETRY_ATTRIBUTE_GOAL_GUID, goal.guid64)
            active_phase_id = self._active_scenario.current_phase_id
            if active_phase_id is not None:
                hook.write_int(TELEMETRY_ATTRIBUTE_PHASE_GUID, active_phase_id)
                hook.write_int(TELEMETRY_ATTRIBUTE_PHASE_STEP, self._current_phase_index)

    def send_phase_finished_telemetry(self, phase, reason, end_description):
        with telemetry_helper.begin_hook(writer, TELEMETRY_HOOK_PHASE_END) as (hook):
            hook.write_int(TELEMETRY_ATTRIBUTE_SCENARIO_GUID, self._active_scenario.guid64)
            hook.write_int(TELEMETRY_ATTRIBUTE_SCENARIO_INSTANCE_ID, self._active_scenario.instance_id)
            hook.write_int(TELEMETRY_ATTRIBUTE_PHASE_GUID, phase.guid64)
            hook.write_int(TELEMETRY_ATTRIBUTE_PHASE_END_REASON, reason)
            hook.write_int(TELEMETRY_ATTRIBUTE_PHASE_STEP, self._current_phase_index)
            if reason == PhaseEndingReason.TERMINATED:
                hook.write_string(TELEMETRY_ATTRIBUTE_PHASE_TERMINATOR, end_description)
            else:
                hook.write_string(TELEMETRY_ATTRIBUTE_PHASE_OUTPUT, end_description)

    def on_goal_completed(self, goal, is_completed):
        if not is_completed:
            return
        if self.outcome_celebration_alarm_handle is not None:
            return
        self.end_scenario(goal)

    def on_phase_finished(self, phase, reason, end_description):
        self.send_phase_finished_telemetry(phase, reason, end_description)
        self._current_phase_index += 1

    def end_scenario(self, goal=None, last_phase=None, outcome=None):
        if goal is not None:
            if goal.is_visible:
                sim_info = next(iter(self._active_scenario.household), None)
                slam = self._active_scenario.screen_slam_scenario_completed
                if slam is not None:
                    slam.send_screen_slam_message(sim_info, self._active_scenario.scenario_name)
        self.send_scenario_end_op_to_client()
        self.outcome_celebration_alarm_handle = alarms.add_alarm_real_time(self, clock.interval_in_real_seconds(1.0), lambda _: self._celebrate_outcome(outcome))
        with telemetry_helper.begin_hook(writer, TELEMETRY_HOOK_SCENARIO_COMPLETE) as (hook):
            hook.write_int(TELEMETRY_ATTRIBUTE_SCENARIO_GUID, self._active_scenario.guid64)
            hook.write_int(TELEMETRY_ATTRIBUTE_SCENARIO_INSTANCE_ID, self._active_scenario.instance_id)
            if goal is not None:
                hook.write_int(TELEMETRY_ATTRIBUTE_END_GOAL_GUID, goal.guid64)
            if last_phase is not None:
                hook.write_int(TELEMETRY_ATTRIBUTE_PHASE_GUID, last_phase.guid64)
                hook.write_int(TELEMETRY_ATTRIBUTE_PHASE_STEP, self._current_phase_index - 1)

    def cancel_scenario(self, logger=None):
        if self._active_scenario is None:
            if logger is not None:
                logger('Household does not have an active scenario.')
            return
        self._active_scenario.end_scenario(None, None, True)
        self._active_scenario = None
        if logger is not None:
            logger('Successfully removed scenario.')

    def force_complete_goal(self, goal_id: int):
        for goal in self._active_scenario.active_goals_gen():
            if goal.id == goal_id:
                goal.force_complete()
                return

    def on_household_member_instanced(self, sim_info):
        if self._active_scenario is not None:
            scenario_role = self.get_role_for_sim_for_active_scenario(sim_info.sim_id)
            if scenario_role is not None:
                role_traits = self._active_scenario.get_role_traits_for_role_id(scenario_role.guid64)
                if role_traits is not None:
                    for role_trait in role_traits:
                        sim_info.add_trait(role_trait)

    def on_household_member_deinstanced(self, sim_info):
        if self._active_scenario is not None:
            self.remove_role_traits(sim_info)

    def remove_role_traits(self, sim_info):
        scenario_role = self.get_role_for_sim_for_active_scenario(sim_info.sim_id)
        if scenario_role is not None:
            role_traits = self._active_scenario.get_role_traits_for_role_id(scenario_role.guid64)
            if role_traits is not None:
                for role_trait in role_traits:
                    sim_info.remove_trait(role_trait)

    def on_household_member_removed(self, sim_info):
        if self._active_scenario is not None:
            self._active_scenario.on_household_member_removed(sim_info)

    def on_hit_their_marks(self):
        if not self._household.is_active_household or self._active_scenario is None:
            return
        if not self._active_scenario.has_started:
            self._active_scenario.start_scenario()
        else:
            self._active_scenario.validate_sim_infos()
            self._active_scenario.setup_goals()
        if self._active_scenario is not None:
            self.send_goal_update_op_to_client()

    def on_zone_unload(self):
        if not self._household.is_active_household:
            return
        if self._active_scenario is not None:
            self._active_scenario.clean_up_goals()

    def send_scenario_end_op_to_client(self):
        msg = Situations_pb2.ScenarioEnded()
        msg.scenario_id = self._active_scenario.guid64
        op = distributor.ops.ScenarioEndOp(msg)
        Distributor.instance().add_op_with_no_owner(op)

    def send_goal_update_op_to_client(self, completed_goal=None):
        if self.outcome_celebration_alarm_handle is not None:
            return
        msg = Situations_pb2.ScenarioGoalsUpdate()
        msg.scenario_id = self._active_scenario.guid64
        msg.instance_id = self._active_scenario.instance_id
        if self._active_scenario.starting_phase is None:
            for goal, goal_tuning in self._active_scenario.active_goals_and_tuning_gen():
                if not goal.is_visible:
                    if not _show_hidden_goals:
                        continue
                with ProtocolBufferRollback(msg.goal_groups) as (goal_group_msg):
                    header_icon = goal_tuning.outcome_header_icon
                    goal_group_msg.header_icon = create_icon_info_msg(IconInfoData(icon_resource=header_icon))
                    goal_group_msg.header_name = goal_tuning.goal_title_text
                    has_visible_sub_goals = False
                    if goal.sub_goals:
                        for sub_goal in goal.sub_goals:
                            if sub_goal.is_visible or _show_hidden_goals:
                                if sub_goal.display_data is not None:
                                    has_visible_sub_goals = True
                                    with ProtocolBufferRollback(goal_group_msg.goals) as (goal_msg):
                                        sub_goal.build_goal_message(goal_msg)

                    if not has_visible_sub_goals:
                        with ProtocolBufferRollback(goal_group_msg.goals) as (goal_msg):
                            goal.build_goal_message(goal_msg)

        else:
            if self._active_scenario._active_phase is None:
                return
            with ProtocolBufferRollback(msg.goal_groups) as (goal_group_msg):
                goal_group_msg.header_icon = create_icon_info_msg(IconInfoData())
                goal_group_msg.header_name = self._active_scenario._active_phase.phase_objective
                for index, goal_sequence in enumerate(self._active_scenario._active_phase.goals):
                    most_recent_visible, is_mandatory = self._active_scenario._last_completed_visible_goal_for_sequence.get(index, (None,
                                                                                                                                    None))
                    for goal in goal_sequence.goal_sequence:
                        active_goal_tuple = next(filter((lambda active_goal: goal.goal.situation_goal.guid64 == active_goal.situation_goal.guid64), self._active_scenario._active_goals), None)
                        if active_goal_tuple is not None:
                            if _show_hidden_goals or (active_goal_tuple.scenario_goal.hidden or active_goal_tuple.situation_goal).is_visible:
                                most_recent_visible = active_goal_tuple.situation_goal
                                is_mandatory = active_goal_tuple.scenario_goal.mandatory
                            break

                    if most_recent_visible is not None:
                        with ProtocolBufferRollback(goal_group_msg.goals) as (goal_msg):
                            most_recent_visible.build_goal_message(goal_msg)
                            goal_msg.is_mandatory = is_mandatory

        if completed_goal is not None:
            msg.completed_goal_id = completed_goal.id
        op = distributor.ops.ScenarioGoalsUpdateOp(msg)
        Distributor.instance().add_op_with_no_owner(op)

    def _celebrate_outcome(self, outcome, *args):
        self.outcome_celebration_alarm_handle = None
        scenario = self._active_scenario
        self._active_scenario.clean_up_goals()
        self._active_scenario = None
        if len(tuple(scenario.household.can_live_alone_info_gen())) <= 0:
            return
        outcome_distributor_op = None
        push_outcome_loot = False
        if outcome:
            outcome_info = Situations_pb2.ScenarioOutcomeData()
            outcome_info.scenario_name = scenario.scenario_name
            outcome_info.outcome_title = outcome.outcome_title_text
            outcome_info.outcome_description = outcome.outcome_description_text
            outcome_info.next_steps_description = outcome.outcome_next_steps_text
            if outcome.outcome_icon:
                outcome_info.outcome_icon = get_protobuff_for_key(outcome.outcome_icon)
            else:
                if scenario.icon:
                    outcome_info.outcome_icon = get_protobuff_for_key(scenario.icon)
            if outcome.outcome_reward_icon:
                outcome_info.reward_icon = get_protobuff_for_key(outcome.outcome_reward_icon)
                outcome_info.reward_tooltip = outcome.outcome_reward_icon_tooltip
            if outcome.outcome_bonus_reward_icon:
                outcome_info.bonus_icon = get_protobuff_for_key(outcome.outcome_bonus_reward_icon)
                outcome_info.bonus_tooltip = outcome.outcome_bonus_reward_icon_tooltip
            outcome_info.household_id = scenario.household.id
            outcome_distributor_op = GenericProtocolBufferOp(Operation.SCENARIO_OUTCOME_DATA, outcome_info)
        else:
            outcome_info = UI_pb2.DynamicSignView()
            outcome_info.sign_type = UIUtils.DynamicSignType.DYNAMIC_SIGN_TYPE_SCENARIO
            outcome_info.name = scenario.scenario_name
            outcome_info.time_spent = scenario.sim_time_lapsed.in_minutes()
            outcome_info.household_id = scenario.household.id
            if scenario.outcome_screen_background_image is not None:
                outcome_info.background_image = sims4.resources.get_protobuff_for_key(scenario.outcome_screen_background_image)
            for active_goal, tuned_goal_tuple in scenario.active_goals_and_tuning_gen():
                if not active_goal.is_completed:
                    continue
                push_outcome_loot = push_outcome_loot or active_goal.is_visible
                with ProtocolBufferRollback(outcome_info.activities) as (activity_msg):
                    activity_msg.name = tuned_goal_tuple.goal_title_text
                    activity_msg.description = tuned_goal_tuple.goal_description_text
                    activity_msg.icon = create_icon_info_msg(IconInfoData(active_goal.display_icon))

            outcome_distributor_op = GenericProtocolBufferOp(Operation.DYNAMIC_SIGN_VIEW, outcome_info)
        active_sim_info = services.active_sim_info()
        loot = scenario.loot_on_scenario_end
        if push_outcome_loot:
            if loot.household_loot_on_successful_completion:
                if active_sim_info is not None:
                    resolver = SingleSimResolver(active_sim_info)
                    for action in loot.household_loot_on_successful_completion:
                        action.apply_to_resolver(resolver)

        if outcome_distributor_op:
            Distributor.instance().add_op(active_sim_info, outcome_distributor_op)

    def load_data(self, household_proto):
        snippet_manager = services.get_instance_manager(sims4.resources.Types.SNIPPET)
        scenario_data = household_proto.scenario_data
        created_scenario_type = snippet_manager.get(scenario_data.scenario_id, None)
        gameplay_scenario_data = household_proto.gameplay_data.gameplay_scenario_tracker.active_scenario_data
        persisted_scenario_type = snippet_manager.get(gameplay_scenario_data.scenario_guid, None)
        if created_scenario_type is None:
            if persisted_scenario_type is None:
                return
        elif created_scenario_type is not None and persisted_scenario_type is None:
            self._active_scenario = created_scenario_type(self)
            self._active_scenario.load_household_data(scenario_data, gameplay_scenario_data, scenario_started_before=False)
        else:
            if created_scenario_type is None or created_scenario_type is persisted_scenario_type:
                self._active_scenario = persisted_scenario_type(self)
                self._active_scenario.load_household_data(scenario_data, gameplay_scenario_data, scenario_started_before=True)
            else:
                logger.error('The scenario in the HouseholdData ({}) is different from the Scenario in the GameplayHouseholdData ({}). This is not expected and behavior is undefined!', created_scenario_type, persisted_scenario_type)

    def save_data(self, household_proto):
        if self._active_scenario is None:
            return
        self._active_scenario.save(household_proto)