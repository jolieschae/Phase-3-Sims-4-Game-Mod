# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\dynamic_situation_goal_tracker.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 11462 bytes
from protocolbuffers import Situations_pb2
from distributor.rollback import ProtocolBufferRollback
from distributor.system import Distributor
from holidays.holiday_globals import HolidayTuning
from situations.base_situation_goal_tracker import BaseSituationGoalTracker
from situations.situation_goal import UiSituationGoalStatus
from situations.situation_serialization import GoalTrackerType
import distributor, services, sims4, sims4.log
logger = sims4.log.Logger('SituationGoals', default_owner='jjacobson')

class SimpleSituationGoalTracker(BaseSituationGoalTracker):

    def __init__(self, situation):
        super().__init__(situation)
        self._goals = []
        self._situation_goal_types = None

    def destroy(self):
        super().destroy()
        for goal in self._goals:
            goal.destroy()

        self._goals = None

    @property
    def goals(self):
        return self._goals

    @property
    def starting_goals(self):
        if self._situation_goal_types is None:
            if self._situation.situation_goal_type_ids:
                situation_goal_manager = services.get_instance_manager(sims4.resources.Types.SITUATION_GOAL)
                self._situation_goal_types = [situation_goal_manager.get(goal_type_id) for goal_type_id in self._situation.situation_goal_type_ids]
        return self._situation_goal_types

    def save_to_seed(self, situation_seed):
        tracker_seedling = situation_seed.setup_for_goal_tracker_save(GoalTrackerType.DYNAMIC_GOAL_TRACKER, self._has_offered_goals, 0)
        for goal in self._goals:
            goal_seedling = goal.create_seedling()
            if goal.completed_time is not None:
                goal_seedling.set_completed()
            tracker_seedling.add_minor_goal(goal_seedling)

    def load_from_seedling(self, tracker_seedling):
        if self._has_offered_goals:
            raise AssertionError('Attempting to load goals for situation: {} but goals have already been offered.'.format(self))
        self._has_offered_goals = tracker_seedling.has_offered_goals
        for goal_seedling in tracker_seedling.minor_goals:
            sim_info = services.sim_info_manager().get(goal_seedling.actor_id)
            goal = goal_seedling.goal_type(sim_info=sim_info, situation=(self._situation),
              goal_id=(self._goal_id_generator()),
              count=(goal_seedling.count),
              reader=(goal_seedling.reader),
              locked=(goal_seedling.locked),
              completed_time=(goal_seedling.completed_time))
            if not goal_seedling.completed:
                goal.setup()
                goal.register_for_on_goal_completed_callback(self._on_goal_completed)
            self._goals.append(goal)

        for goal in self._goals:
            goal.validate_completion()

    def _on_goal_completed(self, goal, goal_completed):
        if goal_completed:
            goal.decommision()
            self._situation.on_goal_completed(goal)
            self.refresh_goals(completed_goal=goal)
        else:
            if goal.score_on_iteration_complete is not None:
                self.update_situation_score(goal)
            self.send_goal_update_to_client()

    def _offer_goals(self):
        if self._has_offered_goals:
            return False
        self._has_offered_goals = True
        goal_actor = self._situation.get_situation_goal_actor()
        if self.starting_goals is None:
            return False
        for goal in self.starting_goals:
            inst_goal = goal(sim_info=goal_actor, situation=(self._situation), goal_id=(self._goal_id_generator()))
            self._goals.append(inst_goal)
            inst_goal.setup()
            inst_goal.on_goal_offered()
            inst_goal.register_for_on_goal_completed_callback(self._on_goal_completed)

        return True

    def send_goal_update_to_client(self, completed_goal=None):
        situation_manager = services.get_zone_situation_manager()
        return situation_manager is None or situation_manager.sim_assignment_complete or None
        situation = self._situation
        if situation.is_running:
            msg = Situations_pb2.SituationGoalsUpdate()
            msg.goal_status = UiSituationGoalStatus.COMPLETED
            msg.situation_id = situation.id
            goal_sub_text = situation.get_goal_sub_text()
            if goal_sub_text is not None:
                msg.goal_sub_text = goal_sub_text
            goal_button_text = situation.get_goal_button_text()
            if goal_button_text is not None:
                msg.goal_button_data.button_text = goal_button_text
                msg.goal_button_data.is_enabled = situation.is_goal_button_enabled
            for goal in self.goals:
                self.build_goal_message(msg, goal)

            if completed_goal is not None:
                msg.completed_goal_id = completed_goal.id
            op = distributor.ops.SituationGoalUpdateOp(msg)
            Distributor.instance().add_op(situation, op)

    def get_goal_info(self):
        return list(((goal, None) for goal in self._goals))

    def get_completed_goal_info(self):
        return []

    def all_goals_gen(self):
        if self._goals is not None:
            for goal in self._goals:
                yield goal

    def update_situation_score(self, goal):
        self._situation.score_update(goal.score_on_iteration_complete)

    def build_goal_message(self, msg, goal):
        with ProtocolBufferRollback(msg.goals) as (goal_msg):
            goal.build_goal_message(goal_msg)


class DynamicSituationGoalTracker(SimpleSituationGoalTracker):

    def __init__(self, situation):
        super().__init__(situation)
        self._goal_preferences = None

    @property
    def starting_goals(self):
        return self._situation._dynamic_goals

    def set_goal_preferences(self, goal_preferences):
        self._goal_preferences = goal_preferences

    def update_goals(self, goals_to_add, goals_to_remove, goal_type_order=None):
        for goal in tuple(self._goals):
            if type(goal) in goals_to_remove:
                goal.decommision()
                self._goals.remove(goal)

        goal_actor = self._situation.get_situation_goal_actor()
        for goal in goals_to_add:
            inst_goal = goal(sim_info=goal_actor, situation=(self._situation), goal_id=(self._goal_id_generator()))
            self._goals.append(inst_goal)
            inst_goal.setup()
            inst_goal.on_goal_offered()
            inst_goal.register_for_on_goal_completed_callback(self._on_goal_completed)

        if goal_type_order is None:
            return
        if len(goal_type_order) != len(self._goals):
            logger.error('Attempting to sort dynamic situation goals tracker with mismatching goals {} != {}', goal_type_order, self._goals)
            return
        type_to_goals = {type(goal): goal for goal in self._goals}
        self._goals = [type_to_goals[goal_type] for goal_type in goal_type_order]

    def build_goal_message(self, msg, goal):
        with ProtocolBufferRollback(msg.goals) as (goal_msg):
            goal.build_goal_message(goal_msg)
            if self._goal_preferences is not None:
                preference, reason = self._goal_preferences[type(goal)]
                goal_msg.goal_preference = preference
                if reason is not None:
                    goal_msg.goal_preference_tooltip = reason

    def refresh_goals(self, completed_goal=None):
        self._offer_goals()
        if completed_goal is not None:
            self.send_goal_update_to_client(completed_goal=completed_goal)

    def update_situation_score(self, goal):
        score = goal.score_on_iteration_complete
        preference, _ = self._goal_preferences[type(goal)]
        if preference in HolidayTuning.TRADITION_PREFERENCE_SCORE_MULTIPLIER:
            score *= HolidayTuning.TRADITION_PREFERENCE_SCORE_MULTIPLIER[preference]
        self._situation.score_update(score)