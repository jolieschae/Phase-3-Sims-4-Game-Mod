# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\developmental_milestones\developmental_milestone_tracker.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 57635 bytes
import enum, game_services, services, sims4, telemetry_helper, uid
from build_buy import get_object_catalog_name
from collections import defaultdict
from developmental_milestones.developmental_milestone import DevelopmentalMilestone
from developmental_milestones.developmental_milestone_enums import DevelopmentalMilestoneStates, MilestoneDataClass
from distributor.ops import GenericProtocolBufferOp
from distributor.rollback import ProtocolBufferRollback
from distributor.system import Distributor
from element_utils import build_element
from event_testing.resolver import SingleSimResolver, DataResolver
from event_testing.test_events import TestEvent
from interactions.utils.death import DeathTracker
from objects import ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED
from protocolbuffers import GameplaySaveData_pb2, Localization_pb2, Sims_pb2
from protocolbuffers.DistributorOps_pb2 import Operation
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_info_tracker import SimInfoTracker
from sims4.common import Pack
from sims4.utils import classproperty
from situations.situation_serialization import GoalSeedling
from zone_types import ZoneState
TELEMETRY_GROUP_MILESTONES = 'MILE'
TELEMETRY_HOOK_MILESTONE_START = 'STRT'
TELEMETRY_HOOK_MILESTONE_END = 'ENDD'
TELEMETRY_FIELD_MILESTONE_ID = 'mile'
TELEMETRY_FIELD_MILESTONE_CONTEXT = 'ctxt'
milestones_telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_MILESTONES)
logger = sims4.log.Logger('DevelopmentalMilestones', default_owner='shipark')

class MilestoneTelemetryContext(enum.Int, export=False):
    NONE = 0
    NEW_SIM = 1
    GOAL = 2
    LOOT = 3
    AGE_UP = 4
    LOD_UP = 5
    CHEAT = 6
    REPEAT = 7


class PreviousGoalData:

    def __init__(self, goal, new_in_ui, age_completed):
        self.goal = goal
        self.age_completed = age_completed
        self.new_in_ui = new_in_ui


class DevelopmentalMilestoneData:

    def __init__(self):
        self.milestone = None
        self.state = DevelopmentalMilestoneStates.ACTIVE
        self.age_completed = None
        self.new_in_ui = False
        self.goal = None
        self._previous_goals = {}

    @property
    def previous_goals(self):
        return self._previous_goals

    def add_previous_goal_entry(self, goal_id, previous_goal_data):
        self._previous_goals[goal_id] = previous_goal_data

    def store_previous_data(self):
        if self.goal is None:
            logger.error('Attemping to store previous goal data from repeatable milestone {}, but no goal exists.', self.milestone)
            return
        previous_data = PreviousGoalData(self.goal, self.new_in_ui, self.age_completed)
        self.add_previous_goal_entry(self.goal.id, previous_data)

    def mark_as_viewed_in_ui(self, goal_id=None):
        if goal_id is None:
            self.new_in_ui = False
            return
        if goal_id == self.goal.id:
            self.new_in_ui = False
            return
        previous_goal_data = self._previous_goals.get(goal_id, None)
        if previous_goal_data is None:
            logger.error('Attempting to mark milestone {} as seen, but the goal id is not tracked in any iteration of the milestone.', self.milestone)
            return
        previous_goal_data.new_in_ui = False

    def get_unlock_function(self, sim_info):
        developmental_milestone_tracker = sim_info.developmental_milestone_tracker
        if developmental_milestone_tracker is None:
            logger.error('Attempting to unlock a milestone on a sim {} without a developmental milestone tracker.', sim_info)
            return
        return developmental_milestone_tracker.unlock_milestone

    def __repr__(self):
        return 'DevelopmentalMilestoneData(Milestone: {}, State: {}, Goal: {}'.format(self.milestone, self.state, self.goal)


class HadChildDevelopmentalMilestoneData(DevelopmentalMilestoneData):

    def __init__(self):
        super().__init__()
        self._sim_info = None
        self._offspring_infos = []
        self._evaluation_counter = 0
        self._pregnancy_unlock_queued = False
        self.milestone = None

    def handle_event(self, sim_info, event, resolver):
        if event == TestEvent.OffspringCreated:
            offspring_infos = resolver.event_kwargs.get('offspring_infos')
            if not offspring_infos:
                logger.error('Attempting to unlock a birth milestone for sim {} but the offspring kwarg is not                              provided.', self._sim_info)
                return
            self._offspring_infos = offspring_infos
            self._evaluation_counter = len(offspring_infos)
            self._run_pregnancy_evaluations()

    def _run_pregnancy_evaluations(self):
        self.pregnancy_unlock_queued = True
        developmental_milestone_tracker = self._sim_info.developmental_milestone_tracker
        if developmental_milestone_tracker is None:
            logger.error('Attempting to unlock a milestone on a sim {} without a developmental milestone tracker.', self._sim_info)
            return
        for offspring_info in self._offspring_infos:
            developmental_milestone_tracker.add_milestone_evaluation(self.milestone, self._sim_info, offspring_info.id)

        developmental_milestone_tracker.process_evaluation(self.milestone)

    def _setup_unlock(self, milestone, telemetry_context, **kwargs):
        if self._pregnancy_unlock_queued:
            return
        self.milestone = milestone
        self._pregnancy_unlock_queued = True
        services.get_event_manager().register_single_event(self, TestEvent.OffspringCreated)

    def get_unlock_function(self, sim_info):
        if not services.current_zone().have_households_and_sim_infos_loaded:
            return super().get_unlock_function(sim_info)
        self._sim_info = sim_info
        if self._evaluation_counter == 0:
            return self._setup_unlock
        self._evaluation_counter -= 1
        return super().get_unlock_function(sim_info)


class _ReevaluationAction:

    def __init__(self, milestone, subject_sim, target_sim_id):
        self.milestone = milestone
        self.subject_sim = subject_sim
        self.target_sim_id = target_sim_id


class DevelopmentalMilestoneTracker(SimInfoTracker):

    def __init__(self, sim_info):
        self._sim_info = sim_info
        self._goal_id_generator = uid.UniqueIdGenerator(1)
        self._active_milestones_data = {}
        self._archived_milestones_data = {}
        self._active_goal_map = {}
        self._developmental_milestone_proto = None
        self._initial_loot_applied = False
        self._milestone_evaluations = defaultdict(list)
        self._setup_delayed_goals = False

    @classproperty
    def required_packs(cls):
        return (Pack.EP13,)

    def start_milestone_tracker(self):
        if self._sim_info.is_npc:
            return
        else:
            is_instanced = self._sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED)
            zone_is_running = services.current_zone().is_zone_running
            if is_instanced:
                if self._setup_delayed_goals:
                    self.setup_goals()
            self._activate_available_milestones(telemetry_context=(MilestoneTelemetryContext.NEW_SIM), activate_goals=is_instanced)
            if not self._initial_loot_applied:
                if is_instanced:
                    if zone_is_running:
                        self._apply_retroactive_milestones_from_gameplay()
                    else:
                        self._apply_initial_loot()
                        services.current_zone().register_callback(ZoneState.RUNNING, self._shutdown_retroactive_only_milestones)
            zone_is_running or services.current_zone().register_callback(ZoneState.RUNNING, self.send_all_milestones_update_to_client)

    def clean_up(self):
        self._active_milestones_data.clear()
        self._archived_milestones_data.clear()
        self._active_goal_map.clear()
        self._milestone_evaluations.clear()

    def add_milestone_evaluation(self, milestone, subject_sim, target_sim_id):
        reevaluation_action = _ReevaluationAction(milestone, subject_sim, target_sim_id)
        if milestone in self._milestone_evaluations:
            self._milestone_evaluations[milestone].append(reevaluation_action)
        else:
            self._milestone_evaluations[milestone] = [
             reevaluation_action]

    def process_evaluation(self, milestone):
        if len(self._milestone_evaluations) == 0 or milestone not in self._milestone_evaluations:
            if self._initial_loot_applied:
                self.send_all_milestones_update_to_client()
            return
        action = self._milestone_evaluations[milestone].pop(0)
        goal = self.get_active_milestone_goal(action.milestone)
        if goal is None:
            self._milestone_evaluations[milestone].append(action)
            logger.info('{} for {} is not in the ACTIVE state.', action.milestone, action.subject_sim)
            return
        resolver = DataResolver(sim_info=(action.subject_sim), event_kwargs={'target_sim_id':action.target_sim_id, 
         'bypass_pretest':True})
        goal.reevaluate_goal_completion(resolver=resolver)
        if len(self._milestone_evaluations[milestone]) == 0:
            del self._milestone_evaluations[milestone]

    @property
    def active_milestones(self):
        return self._active_milestones_data.values()

    def is_milestone_valid_for_sim(self, milestone):
        if self._sim_info.age not in milestone.ages:
            return False
        return True

    def is_milestone_available(self, milestone, allow_retroactive_only=False):
        if self.is_milestone_valid_for_sim(milestone):
            if milestone.retroactive_only:
                if self._initial_loot_applied:
                    return False
        elif milestone.retroactive_only:
            return allow_retroactive_only or False
        if milestone.prerequisite_milestones:
            for prerequisite_milestone in milestone.prerequisite_milestones:
                if not self.is_milestone_unlocked(prerequisite_milestone):
                    return False

        return True

    def get_milestone_state(self, milestone):
        milestone_data = self._active_milestones_data.get(milestone)
        if milestone_data is None:
            milestone_data = self._archived_milestones_data.get(milestone)
        if milestone_data is None:
            return DevelopmentalMilestoneStates.LOCKED
        return milestone_data.state

    def is_milestone_locked(self, milestone):
        return self.get_milestone_state(milestone) == DevelopmentalMilestoneStates.LOCKED

    def is_milestone_active(self, milestone):
        return self.get_milestone_state(milestone) == DevelopmentalMilestoneStates.ACTIVE

    def is_milestone_unlocked(self, milestone):
        return self.get_milestone_state(milestone) == DevelopmentalMilestoneStates.UNLOCKED

    def is_milestone_tracked(self, milestone):
        milestone_data = self._active_milestones_data.get(milestone)
        return milestone_data is not None

    def get_active_milestone_goal(self, milestone):
        milestone_data = self._active_milestones_data.get(milestone)
        if milestone_data is not None:
            if milestone_data.state == DevelopmentalMilestoneStates.ACTIVE:
                return milestone_data.goal

    def get_milestone_goals(self, milestone, milestone_state=DevelopmentalMilestoneStates.UNLOCKED):
        milestone_data = self._active_milestones_data.get(milestone)
        goals = []
        if milestone_data is None:
            return goals
        if milestone.repeatable:
            for _, previous_data in milestone_data.previous_goals.items():
                goals.append(previous_data.goal)

        if milestone_data.state == milestone_state:
            goals.append(milestone_data.goal)
        return goals

    def any_previous_goal_completed(self, milestone):
        if not milestone.repeatable:
            return False
        milestone_data = self._active_milestones_data.get(milestone)
        if milestone_data is None:
            return False
        return len(milestone_data.previous_goals) > 0

    def is_milestone_visible(self, milestone, resolver):
        if self.is_milestone_unlocked(milestone):
            return True
        if milestone.is_primary_milestone is not None:
            if milestone.is_primary_milestone.tests.run_tests(resolver):
                return True
        if self.any_previous_goal_completed(milestone):
            return True
        return False

    def is_milestone_completed(self, milestone_data):
        if milestone_data.milestone.repeatable:
            return len(milestone_data.previous_goals) > 0
        return milestone_data.state == DevelopmentalMilestoneStates.UNLOCKED

    def get_all_completed_milestones(self):
        completed_milestones = [milestone for milestone, milestone_data in self._active_milestones_data.items() if self.is_milestone_completed(milestone_data)]
        completed_milestones.extend(self._archived_milestones_data)
        return completed_milestones

    def create_milestone(self, milestone, send_ui_update=False):
        milestone_data = self._get_data_class(milestone)()
        milestone_data.milestone = milestone
        milestone_data.state = DevelopmentalMilestoneStates.LOCKED
        milestone_data.new_in_ui = True
        milestone_data.goal = None
        if self.is_milestone_valid_for_sim(milestone):
            self._active_milestones_data[milestone] = milestone_data
        else:
            self._archived_milestones_data[milestone] = milestone_data
        if send_ui_update:
            self.try_send_milestone_update_to_client(milestone_data)
        return milestone_data

    def activate_milestone(self, milestone, telemetry_context, from_repeat=False, send_ui_update=True, activate_goals=True):
        if not self.is_milestone_valid_for_sim(milestone):
            logger.error('activate_milestone() called for milestone {}, which is not valid for sim {}.', milestone, self._sim_info)
            return
        else:
            if milestone.retroactive_only:
                if self._initial_loot_applied:
                    if milestone not in self._milestone_evaluations:
                        return
            milestone_data = self._active_milestones_data.get(milestone)
            if milestone_data is None:
                milestone_data = self.create_milestone(milestone)
            milestone_data.state = DevelopmentalMilestoneStates.ACTIVE
            if from_repeat:
                milestone_data.store_previous_data()
                milestone_data.age_completed = None
                milestone_data.new_in_ui = True
            commodity_to_add = milestone.commodity
            if commodity_to_add is not None:
                self._sim_info.commodity_tracker.add_statistic(commodity_to_add)
            if milestone.goal is not None:
                goal = milestone.goal(sim_info=(self._sim_info), goal_id=(self._goal_id_generator()))
                milestone_data.goal = goal
                self._active_goal_map[goal] = milestone
                if activate_goals:
                    goal.setup()
                    goal.on_goal_offered()
                    goal.register_for_on_goal_completed_callback(self.on_goal_completed)
        if send_ui_update:
            self.try_send_milestone_update_to_client(milestone_data)
            for previous_goal_data in milestone_data.previous_goals.values():
                self.try_send_milestone_update_to_client(milestone_data, previous_goal_data.goal.id)

        if telemetry_context is not MilestoneTelemetryContext.NONE:
            with telemetry_helper.begin_hook(milestones_telemetry_writer, TELEMETRY_HOOK_MILESTONE_START, sim_info=(self._sim_info)) as (hook):
                hook.write_guid(TELEMETRY_FIELD_MILESTONE_ID, milestone.guid64)
                hook.write_int(TELEMETRY_FIELD_MILESTONE_CONTEXT, telemetry_context)
        logger.info('activate_milestone(): milestone {} activated.', milestone)
        if milestone.repeatable:
            self.process_evaluation(milestone)

    def unlock_milestone(self, milestone, telemetry_context, send_ui_update=True):
        if not self.is_milestone_valid_for_sim(milestone):
            logger.error('unlock_milestone() called for milestone {}, which is not valid for sim {}.', milestone, self._sim_info)
            return
        milestone_data = self._active_milestones_data.get(milestone)
        if milestone_data is None:
            logger.error('unlock_milestone() called for milestone {}, which does not have milestone_data.', milestone)
            return
        if milestone_data == DevelopmentalMilestoneStates.UNLOCKED:
            logger.error('Trying to unlock milestone {}, but it is already unlocked.', milestone)
            return
        milestone_data.state = DevelopmentalMilestoneStates.UNLOCKED
        milestone_data.age_completed = self._sim_info.age
        milestone_data.new_in_ui = True
        self._shutdown_milestone(milestone_data)
        resolver = SingleSimResolver(self._sim_info)
        for loot in milestone.loot:
            loot.apply_to_resolver(resolver)

        if send_ui_update:
            self.try_send_milestone_update_to_client(milestone_data)
        if telemetry_context is not MilestoneTelemetryContext.NONE:
            with telemetry_helper.begin_hook(milestones_telemetry_writer, TELEMETRY_HOOK_MILESTONE_END, sim_info=(self._sim_info)) as (hook):
                hook.write_guid(TELEMETRY_FIELD_MILESTONE_ID, milestone.guid64)
                hook.write_int(TELEMETRY_FIELD_MILESTONE_CONTEXT, telemetry_context)
        logger.info('unlock_milestone(): milestone {} unlocked.', milestone)
        self._activate_available_milestones(telemetry_context=telemetry_context, send_ui_update=send_ui_update)
        if milestone.repeatable:
            activate_fn = lambda _: self.activate_milestone(milestone, telemetry_context=(MilestoneTelemetryContext.REPEAT),
              from_repeat=True,
              send_ui_update=False)
            element = build_element([activate_fn])
            services.time_service().sim_timeline.schedule(element)

    def remove_milestone(self, milestone):
        milestone_data = self._active_milestones_data.get(milestone)
        if milestone_data is None:
            logger.error('remove_milestone() called for milestone {}, which does not have milestone_data.', milestone)
            return
        self._shutdown_milestone(milestone_data)
        if self.is_milestone_completed(milestone_data):
            self._archived_milestones_data[milestone] = milestone_data
        del self._active_milestones_data[milestone]
        if milestone_data.goal is not None:
            if milestone_data.goal not in self._active_goal_map:
                logger.error('Milestone {} is being removed from active data without having registered a goal with the active goal map. This is unexpected.', milestone)
                return
            del self._active_goal_map[milestone_data.goal]

    def mark_milestone_as_viewed(self, milestone, goal_id=None):
        milestone_data = self._active_milestones_data.get(milestone)
        if milestone_data is None:
            logger.error('mark_milestone_as_viewed() called for milestone {}, which does not have milestone_data.', milestone)
            return
        milestone_data.mark_as_viewed_in_ui(goal_id)
        self.try_send_milestone_update_to_client(milestone_data, goal_id)

    def recursively_unlock_prerequisites(self, milestone, telemetry_context):
        for prerequisite_milestone in milestone.prerequisite_milestones:
            if not self.is_milestone_unlocked(prerequisite_milestone):
                self.recursively_unlock_prerequisites(prerequisite_milestone, telemetry_context=telemetry_context)
                if not self.is_milestone_active(prerequisite_milestone):
                    self.activate_milestone(prerequisite_milestone, telemetry_context=telemetry_context)
                self.unlock_milestone(prerequisite_milestone, telemetry_context=telemetry_context)

    def setup_goals(self):
        for milestone, milestone_data in self._active_milestones_data.items():
            if milestone_data.state == DevelopmentalMilestoneStates.ACTIVE:
                goal = milestone_data.goal
                if goal is not None and goal.guid == milestone.goal.guid:
                    goal.setup()
                else:
                    if goal is not None:
                        goal.decommision()
                    if self._active_goal_map.get(goal):
                        del self._active_goal_map[goal]
                    goal = milestone.goal(sim_info=(self._sim_info), goal_id=(self._goal_id_generator()))
                    milestone_data.goal = goal
                    self._active_goal_map[goal] = milestone
                    goal.setup()
                    goal.on_goal_offered()
                goal.register_for_on_goal_completed_callback(self.on_goal_completed)

        self._setup_delayed_goals = False

    @classproperty
    def _tracker_lod_threshold(cls):
        return SimInfoLODLevel.FULL

    def _apply_initial_loot(self, from_gameplay=False):
        resolver = SingleSimResolver(self._sim_info)
        for loot_entry in DevelopmentalMilestone.RETROACTIVE_MILESTONES:
            loot_entry.apply_to_resolver(resolver)

        if not from_gameplay:
            self._initial_loot_applied = True

    def _activate_available_milestones(self, telemetry_context, send_ui_update=False, activate_goals=True):
        if self._sim_info.lod < self._tracker_lod_threshold:
            return
        allow_retroactive_only = not self._initial_loot_applied
        for milestone in DevelopmentalMilestone.age_milestones_gen(self._sim_info.age):
            if self.is_milestone_locked(milestone):
                if self.is_milestone_available(milestone, allow_retroactive_only=allow_retroactive_only):
                    self.activate_milestone(milestone, telemetry_context=telemetry_context, send_ui_update=send_ui_update, activate_goals=activate_goals)
                elif self.is_milestone_tracked(milestone) or self.is_milestone_valid_for_sim(milestone) and milestone.is_primary_milestone is not None:
                    self.create_milestone(milestone, send_ui_update=send_ui_update)

    def _remove_all_milestones(self):
        to_remove = [milestone for milestone in self._active_milestones_data.keys()]
        for milestone in to_remove:
            self.remove_milestone(milestone)

        self.send_all_milestones_update_to_client()

    def _remove_inappropriate_milestones(self):
        to_remove = []
        for milestone, milestone_data in self._active_milestones_data.items():
            if not self.is_milestone_valid_for_sim(milestone):
                to_remove.append(milestone_data)

        if to_remove:
            for milestone_data in to_remove:
                self.remove_milestone(milestone_data.milestone)

            self.send_all_milestones_update_to_client()

    def _grant_retroactive_fake_milestones(self, telemetry_context):
        milestones_unlocked = False
        current_age_percentage = self._sim_info.age_progress_percentage
        for milestone in DevelopmentalMilestone.age_milestones_gen(self._sim_info.age):
            if self.is_milestone_unlocked(milestone) or milestone.treat_unlocked_at_age_percentage is not None and current_age_percentage >= milestone.treat_unlocked_at_age_percentage:
                if not self.is_milestone_active(milestone):
                    self.activate_milestone(milestone, telemetry_context=telemetry_context, send_ui_update=False)
                self.unlock_milestone(milestone, telemetry_context=telemetry_context, send_ui_update=False)
                milestones_unlocked = True

        if milestones_unlocked:
            self.send_all_milestones_update_to_client()

    def _shutdown_milestone(self, milestone_data):
        if milestone_data.goal is not None:
            milestone_data.goal.decommision()
        commodity_to_remove = milestone_data.milestone.commodity
        if commodity_to_remove is not None:
            self._sim_info.commodity_tracker.remove_statistic(commodity_to_remove)

    def _shutdown_retroactive_only_milestones(self):
        retroactive_only_milestones_data = [milestone_data for milestone_data in self._active_milestones_data.values() if milestone_data.milestone.retroactive_only if milestone_data.milestone not in self._milestone_evaluations]
        for milestone_data in retroactive_only_milestones_data:
            if milestone_data.state == DevelopmentalMilestoneStates.UNLOCKED:
                self._shutdown_milestone(milestone_data)
            else:
                self.remove_milestone(milestone_data.milestone)

    @staticmethod
    def _get_data_class(milestone):
        data_class_enum = DevelopmentalMilestone.DEVELOPMENTAL_MILESTONE_UNLOCK_OVERRIDES.get(milestone)
        if data_class_enum == MilestoneDataClass.HAD_CHILD:
            return HadChildDevelopmentalMilestoneData
        return DevelopmentalMilestoneData

    def on_age_stage_change(self):
        self._remove_inappropriate_milestones()
        self._activate_available_milestones(telemetry_context=(MilestoneTelemetryContext.AGE_UP))
        self.send_all_milestones_update_to_client()

    def on_goal_completed(self, goal, is_completed):
        if not is_completed:
            return
        milestone = self._active_goal_map.get(goal)
        if milestone is None:
            logger.error('on_goal_completed() called for goal {}, which is not in the goal_map.', goal)
            return
        unlock_function = self._active_milestones_data.get(milestone).get_unlock_function(self._sim_info)
        if unlock_function is None:
            logger.error("No unlock function for this milestone {}'s data class was provided.", milestone)
            return
        unlock_function(milestone, telemetry_context=(MilestoneTelemetryContext.GOAL))

    def _apply_retroactive_milestones_from_gameplay(self):
        self._apply_initial_loot(from_gameplay=True)

        def _post_retroactive_actions(*_):
            self._initial_loot_applied = True
            self._shutdown_retroactive_only_milestones()
            self.send_all_milestones_update_to_client()

        element = build_element([_post_retroactive_actions])
        services.time_service().sim_timeline.schedule(element)

    def on_lod_update(self, old_lod, new_lod):
        if new_lod < self._tracker_lod_threshold:
            self._remove_all_milestones()
        else:
            if old_lod < self._tracker_lod_threshold:
                self._grant_retroactive_fake_milestones(telemetry_context=(MilestoneTelemetryContext.LOD_UP))
                self._activate_available_milestones(telemetry_context=(MilestoneTelemetryContext.LOD_UP))
                if services.current_zone().have_households_and_sim_infos_loaded:
                    self._apply_retroactive_milestones_from_gameplay()

    def on_zone_load(self):
        if self._sim_info.is_npc:
            return
        self.load_milestones_info_from_proto()
        services.current_zone().register_callback(ZoneState.ALL_SIMS_SPAWNED, self.start_milestone_tracker)

    def on_zone_unload(self):
        if not self._sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED):
            return
        else:
            return game_services.service_manager.is_traveling or None
        self._developmental_milestone_proto = GameplaySaveData_pb2.DevelopmentalMilestoneTrackerData()
        self.save_milestones_info_to_proto((self._developmental_milestone_proto), copy_existing=False)
        self.clean_up()

    def cache_milestones_proto(self, milestone_tracker_proto, skip_load=False):
        if skip_load:
            return
        if self._sim_info.developmental_milestone_tracker is None:
            return
        self._developmental_milestone_proto = GameplaySaveData_pb2.DevelopmentalMilestoneTrackerData()
        self._developmental_milestone_proto.CopyFrom(milestone_tracker_proto)

    def _load_milestone_data_from_proto(self, msg, milestone_data, reassociate_goal=True):
        milestone = milestone_data.milestone
        milestone_data.state = DevelopmentalMilestoneStates(msg.state)
        milestone_data.new_in_ui = msg.new_in_ui
        if msg.HasField('age_completed'):
            milestone_data.age_completed = msg.age_completed
        if msg.HasField('goal_data'):
            goal_seed = GoalSeedling.deserialize_from_proto(msg.goal_data)
            if goal_seed is not None:
                goal = goal_seed.goal_type(sim_info=(self._sim_info), goal_id=(self._goal_id_generator()),
                  count=(goal_seed.count),
                  reader=(goal_seed.reader),
                  locked=(goal_seed.locked),
                  completed_time=(goal_seed.completed_time))
                milestone_data.goal = goal
                if reassociate_goal:
                    self._active_goal_map[goal] = milestone
        for previous_goal_msg in msg.previous_goals:
            if not previous_goal_msg.HasField('age_completed'):
                logger.info('Trying to load previous milestone data with no completed age value for DEVELOPMENTAL_MILESTONE : {}', milestone)
                continue
            goal_seed = GoalSeedling.deserialize_from_proto(previous_goal_msg.goal_data)
            if goal_seed is not None:
                goal = goal_seed.goal_type(sim_info=(self._sim_info), goal_id=(self._goal_id_generator()),
                  count=(goal_seed.count),
                  reader=(goal_seed.reader),
                  locked=(goal_seed.locked),
                  completed_time=(goal_seed.completed_time))
                previous_goal_data = PreviousGoalData(goal, previous_goal_msg.new_in_ui, previous_goal_msg.age_completed)
                milestone_data.add_previous_goal_entry(goal.id, previous_goal_data)

        logger.info('Milestone {} loaded for Sim {}. State = {}', milestone, self._sim_info, milestone_data.state)

    def load_milestones_info_from_proto(self):
        if self._developmental_milestone_proto is None:
            return
        self._setup_delayed_goals = True
        self._initial_loot_applied = self._developmental_milestone_proto.initial_loot_applied
        milestone_manager = services.get_instance_manager(sims4.resources.Types.DEVELOPMENTAL_MILESTONE)
        for active_milestone_msg in self._developmental_milestone_proto.active_milestones:
            milestone_id = active_milestone_msg.milestone_id
            milestone = milestone_manager.get(milestone_id)
            if milestone is None:
                logger.info('Trying to load unavailable DEVELOPMENTAL_MILESTONE resource: {}', milestone_id)
                continue
            if not self.is_milestone_valid_for_sim(milestone):
                continue
            milestone_data = self.create_milestone(milestone)
            self._load_milestone_data_from_proto(active_milestone_msg, milestone_data)

        for archived_milestone_msg in self._developmental_milestone_proto.archived_milestones:
            milestone_id = archived_milestone_msg.milestone_id
            milestone = milestone_manager.get(milestone_id)
            if milestone is None:
                logger.info('Trying to load unavailable DEVELOPMENTAL_MILESTONE resource: {}', milestone_id)
                continue
            milestone_data = self.create_milestone(milestone)
            self._load_milestone_data_from_proto(archived_milestone_msg, milestone_data, reassociate_goal=False)

        self._developmental_milestone_proto = None

    def _save_milestone_data_to_message(self, msg, milestone_data):
        msg.milestone_id = milestone_data.milestone.guid64
        msg.state = milestone_data.state
        msg.new_in_ui = milestone_data.new_in_ui
        if milestone_data.age_completed is not None:
            msg.age_completed = milestone_data.age_completed
        if milestone_data.goal is not None:
            goal_seed = milestone_data.goal.create_seedling()
            goal_seed.finalize_creation_for_save()
            goal_seed.serialize_to_proto(msg.goal_data)
        for previous_goal_data in milestone_data.previous_goals.values():
            with ProtocolBufferRollback(msg.previous_goals) as (previous_goal_msg):
                previous_goal_msg.new_in_ui = previous_goal_data.new_in_ui
                previous_goal_msg.age_completed = previous_goal_data.age_completed
                if previous_goal_data.goal is not None:
                    previous_goal_seed = previous_goal_data.goal.create_seedling()
                    previous_goal_seed.finalize_creation_for_save()
                    previous_goal_seed.serialize_to_proto(previous_goal_msg.goal_data)

    def save_milestones_info_to_proto(self, developmental_milestone_tracker_proto, copy_existing=True):
        if copy_existing:
            if self._developmental_milestone_proto is not None:
                developmental_milestone_tracker_proto.CopyFrom(self._developmental_milestone_proto)
                return
        developmental_milestone_tracker_proto.initial_loot_applied = self._initial_loot_applied
        for milestone_data in self._active_milestones_data.values():
            with ProtocolBufferRollback(developmental_milestone_tracker_proto.active_milestones) as (active_milestone_msg):
                self._save_milestone_data_to_message(active_milestone_msg, milestone_data)

        for milestone_data in self._archived_milestones_data.values():
            with ProtocolBufferRollback(developmental_milestone_tracker_proto.archived_milestones) as (archived_milestone_msg):
                self._save_milestone_data_to_message(archived_milestone_msg, milestone_data)

    def _should_include_goal_message(self, milestone_data, previous_goal_id):
        return milestone_data.state == DevelopmentalMilestoneStates.UNLOCKED or previous_goal_id is not None

    def _get_milestone_update_msg(self, milestone_data, previous_goal_id=None):
        msg = Sims_pb2.DevelopmentalMilestoneUpdate()
        msg.sim_id = self._sim_info.sim_id
        msg.developmental_milestone_id = milestone_data.milestone.guid64
        msg.state = milestone_data.state if previous_goal_id is None else DevelopmentalMilestoneStates.UNLOCKED
        milestone_state_data = milestone_data.previous_goals.get(previous_goal_id, milestone_data)
        msg.new_in_ui = milestone_state_data.new_in_ui
        if milestone_state_data.age_completed is not None:
            msg.age_completed = milestone_state_data.age_completed
        goal = milestone_state_data.goal
        if self._should_include_goal_message(milestone_data, previous_goal_id=previous_goal_id):
            if goal:
                msg.goal_id = goal.id
                target_sim_info = goal.get_actual_target_sim_info()
                if target_sim_info is not None:
                    msg.unlocked_with_sim_id = target_sim_info.id
                target_object_id = goal.get_actual_target_object_definition_id()
                if target_object_id is not None:
                    catalog_name_key = get_object_catalog_name(target_object_id)
                    if catalog_name_key is not None:
                        msg.unlocked_with_object_name = Localization_pb2.LocalizedString()
                        msg.unlocked_with_object_name.hash = catalog_name_key
                unlocked_zone_id = goal.get_actual_zone_id()
                if unlocked_zone_id is not None:
                    persistence_service = services.get_persistence_service()
                    zone_data = persistence_service.get_zone_proto_buff(unlocked_zone_id)
                    if zone_data is not None:
                        msg.unlocked_in_lot_name = zone_data.name
                    world_id = persistence_service.get_world_id_from_zone(unlocked_zone_id)
                    if world_id:
                        msg.unlocked_in_region_id = persistence_service.get_region_id_from_world_id(world_id)
                unlocked_career_track = goal.get_career_track()
                if unlocked_career_track is not None:
                    career_track = services.get_instance_manager(sims4.resources.Types.CAREER_TRACK).get(unlocked_career_track)
                    if career_track is not None:
                        msg.unlocked_career_name = career_track.get_career_name(self._sim_info)
                        unlocked_career_level = goal.get_career_level()
                        if unlocked_career_level is not None and unlocked_career_level < len(career_track.career_levels):
                            career_level = career_track.career_levels[unlocked_career_level]
                            if career_level is not None:
                                msg.unlocked_career_level = career_level.get_title(self._sim_info)
                unlocked_death_type = goal.get_death_type_info()
                if unlocked_death_type is not None:
                    death_trait = DeathTracker.DEATH_TYPE_GHOST_TRAIT_MAP.get(unlocked_death_type)
                    if death_trait is not None:
                        msg.unlocked_death_type = death_trait.display_name(self._sim_info)
                unlocked_trait_guid = goal.get_trait_guid()
                if unlocked_trait_guid is not None:
                    trait = services.get_instance_manager(sims4.resources.Types.TRAIT).get(unlocked_trait_guid)
                    if trait is not None:
                        msg.unlocked_trait_name = trait.display_name(self._sim_info)
                if goal.completed_time is not None:
                    msg.completed_time = goal.completed_time
        return msg

    def try_send_milestone_update_to_client(self, milestone_data, previous_goal_id=None):
        if services.current_zone().is_zone_shutting_down:
            return
        else:
            resolver = SingleSimResolver(self._sim_info)
            return self.is_milestone_visible(milestone_data.milestone, resolver) or None
        msg = self._get_milestone_update_msg(milestone_data, previous_goal_id=previous_goal_id)
        owner = self._sim_info
        distributor = Distributor.instance()
        distributor.add_op(owner, GenericProtocolBufferOp(Operation.DEVELOPMENTAL_MILESTONE_UPDATE, msg))

    def send_all_milestones_update_to_client--- This code section failed: ---

 L.1159         0  LOAD_GLOBAL              services
                2  LOAD_METHOD              current_zone
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  STORE_FAST               'zone'

 L.1160         8  LOAD_FAST                'zone'
               10  LOAD_ATTR                have_households_and_sim_infos_loaded
               12  POP_JUMP_IF_TRUE     18  'to 18'

 L.1163        14  LOAD_CONST               None
               16  RETURN_VALUE     
             18_0  COME_FROM            12  '12'

 L.1165        18  LOAD_FAST                'zone'
               20  LOAD_ATTR                is_zone_shutting_down
               22  POP_JUMP_IF_FALSE    28  'to 28'

 L.1166        24  LOAD_CONST               None
               26  RETURN_VALUE     
             28_0  COME_FROM            22  '22'

 L.1168        28  LOAD_GLOBAL              Sims_pb2
               30  LOAD_METHOD              AllDevelopmentalMilestonesUpdate
               32  CALL_METHOD_0         0  '0 positional arguments'
               34  STORE_FAST               'msg'

 L.1169        36  LOAD_FAST                'self'
               38  LOAD_ATTR                _sim_info
               40  LOAD_ATTR                sim_id
               42  LOAD_FAST                'msg'
               44  STORE_ATTR               sim_id

 L.1172        46  LOAD_GLOBAL              SingleSimResolver
               48  LOAD_FAST                'self'
               50  LOAD_ATTR                _sim_info
               52  CALL_FUNCTION_1       1  '1 positional argument'
               54  STORE_FAST               'resolver'

 L.1173        56  SETUP_LOOP          202  'to 202'
               58  LOAD_FAST                'self'
               60  LOAD_ATTR                _active_milestones_data
               62  LOAD_METHOD              items
               64  CALL_METHOD_0         0  '0 positional arguments'
               66  GET_ITER         
               68  FOR_ITER            200  'to 200'
               70  UNPACK_SEQUENCE_2     2 
               72  STORE_FAST               'milestone'
               74  STORE_FAST               'milestone_data'

 L.1176        76  LOAD_FAST                'self'
               78  LOAD_METHOD              is_milestone_visible
               80  LOAD_FAST                'milestone'
               82  LOAD_FAST                'resolver'
               84  CALL_METHOD_2         2  '2 positional arguments'
               86  POP_JUMP_IF_FALSE   120  'to 120'

 L.1177        88  LOAD_FAST                'milestone'
               90  LOAD_ATTR                repeatable
               92  POP_JUMP_IF_FALSE   132  'to 132'
               94  LOAD_FAST                'milestone'
               96  LOAD_ATTR                repeatable
               98  POP_JUMP_IF_FALSE   120  'to 120'
              100  LOAD_FAST                'milestone'
              102  LOAD_ATTR                is_primary_milestone
              104  POP_JUMP_IF_FALSE   120  'to 120'
              106  LOAD_GLOBAL              len
              108  LOAD_FAST                'milestone_data'
              110  LOAD_ATTR                previous_goals
              112  CALL_FUNCTION_1       1  '1 positional argument'
              114  LOAD_CONST               1
              116  COMPARE_OP               <
              118  POP_JUMP_IF_TRUE    132  'to 132'
            120_0  COME_FROM           104  '104'
            120_1  COME_FROM            98  '98'
            120_2  COME_FROM            86  '86'

 L.1178       120  LOAD_FAST                'milestone'
              122  LOAD_ATTR                repeatable
              124  POP_JUMP_IF_FALSE   154  'to 154'
              126  LOAD_FAST                'milestone'
              128  LOAD_ATTR                retroactive_only
              130  POP_JUMP_IF_FALSE   154  'to 154'
            132_0  COME_FROM           118  '118'
            132_1  COME_FROM            92  '92'

 L.1179       132  LOAD_FAST                'self'
              134  LOAD_METHOD              _get_milestone_update_msg
              136  LOAD_FAST                'milestone_data'
              138  CALL_METHOD_1         1  '1 positional argument'
              140  STORE_FAST               'milestone_msg'

 L.1180       142  LOAD_FAST                'msg'
              144  LOAD_ATTR                milestones
              146  LOAD_METHOD              append
              148  LOAD_FAST                'milestone_msg'
              150  CALL_METHOD_1         1  '1 positional argument'
              152  POP_TOP          
            154_0  COME_FROM           130  '130'
            154_1  COME_FROM           124  '124'

 L.1182       154  SETUP_LOOP          198  'to 198'
              156  LOAD_FAST                'milestone_data'
              158  LOAD_ATTR                previous_goals
              160  LOAD_METHOD              keys
              162  CALL_METHOD_0         0  '0 positional arguments'
              164  GET_ITER         
              166  FOR_ITER            196  'to 196'
              168  STORE_FAST               'previous_goal_id'

 L.1183       170  LOAD_FAST                'self'
              172  LOAD_METHOD              _get_milestone_update_msg
              174  LOAD_FAST                'milestone_data'
              176  LOAD_FAST                'previous_goal_id'
              178  CALL_METHOD_2         2  '2 positional arguments'
              180  STORE_FAST               'prev_milestone_msg'

 L.1184       182  LOAD_FAST                'msg'
              184  LOAD_ATTR                milestones
              186  LOAD_METHOD              append
              188  LOAD_FAST                'prev_milestone_msg'
              190  CALL_METHOD_1         1  '1 positional argument'
              192  POP_TOP          
              194  JUMP_BACK           166  'to 166'
              196  POP_BLOCK        
            198_0  COME_FROM_LOOP      154  '154'
              198  JUMP_BACK            68  'to 68'
              200  POP_BLOCK        
            202_0  COME_FROM_LOOP       56  '56'

 L.1187       202  SETUP_LOOP          300  'to 300'
              204  LOAD_FAST                'self'
              206  LOAD_ATTR                _archived_milestones_data
              208  LOAD_METHOD              items
              210  CALL_METHOD_0         0  '0 positional arguments'
              212  GET_ITER         
              214  FOR_ITER            298  'to 298'
              216  UNPACK_SEQUENCE_2     2 
              218  STORE_FAST               'milestone'
              220  STORE_FAST               'milestone_data'

 L.1188       222  LOAD_FAST                'milestone'
              224  LOAD_ATTR                repeatable
              226  POP_JUMP_IF_TRUE    250  'to 250'

 L.1189       228  LOAD_FAST                'self'
              230  LOAD_METHOD              _get_milestone_update_msg
              232  LOAD_FAST                'milestone_data'
              234  CALL_METHOD_1         1  '1 positional argument'
              236  STORE_FAST               'archived_milestone_msg'

 L.1190       238  LOAD_FAST                'msg'
              240  LOAD_ATTR                milestones
              242  LOAD_METHOD              append
              244  LOAD_FAST                'archived_milestone_msg'
              246  CALL_METHOD_1         1  '1 positional argument'
              248  POP_TOP          
            250_0  COME_FROM           226  '226'

 L.1192       250  SETUP_LOOP          296  'to 296'
              252  LOAD_FAST                'milestone_data'
              254  LOAD_ATTR                previous_goals
              256  LOAD_METHOD              keys
              258  CALL_METHOD_0         0  '0 positional arguments'
              260  GET_ITER         
              262  FOR_ITER            294  'to 294'
              264  STORE_FAST               'previous_goal_id'

 L.1193       266  LOAD_FAST                'self'
              268  LOAD_METHOD              _get_milestone_update_msg
              270  LOAD_FAST                'milestone_data'
              272  LOAD_FAST                'previous_goal_id'
              274  CALL_METHOD_2         2  '2 positional arguments'
              276  STORE_FAST               'prev_milestone_msg'

 L.1194       278  LOAD_FAST                'msg'
              280  LOAD_ATTR                milestones
              282  LOAD_METHOD              append
              284  LOAD_FAST                'prev_milestone_msg'
              286  CALL_METHOD_1         1  '1 positional argument'
              288  POP_TOP          
          290_292  JUMP_BACK           262  'to 262'
              294  POP_BLOCK        
            296_0  COME_FROM_LOOP      250  '250'
              296  JUMP_BACK           214  'to 214'
              298  POP_BLOCK        
            300_0  COME_FROM_LOOP      202  '202'

 L.1196       300  LOAD_FAST                'self'
              302  LOAD_ATTR                _sim_info
              304  STORE_FAST               'owner'

 L.1197       306  LOAD_GLOBAL              Distributor
              308  LOAD_METHOD              instance
              310  CALL_METHOD_0         0  '0 positional arguments'
              312  STORE_FAST               'distributor'

 L.1198       314  LOAD_FAST                'distributor'
              316  LOAD_METHOD              add_op
              318  LOAD_FAST                'owner'
              320  LOAD_GLOBAL              GenericProtocolBufferOp
              322  LOAD_GLOBAL              Operation
              324  LOAD_ATTR                ALL_DEVELOPMENTAL_MILESTONES_UPDATE
              326  LOAD_FAST                'msg'
              328  CALL_FUNCTION_2       2  '2 positional arguments'
              330  CALL_METHOD_2         2  '2 positional arguments'
              332  POP_TOP          

Parse error at or near `COME_FROM_LOOP' instruction at offset 202_0