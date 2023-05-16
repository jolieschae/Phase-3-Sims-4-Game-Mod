# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\festival_contest_drama_node_mixin.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 28532 bytes
from dataclasses import dataclass
from date_and_time import create_time_span
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.resolver import SingleSimResolver
from event_testing.tests import TunableTestSet
from sims4.localization import LocalizationHelperTuning
from sims4 import random
from sims4.tuning.tunable import TunableReference, TunableSimMinute, TunableRange, TunableInterval, TunableList, OptionalTunable, TunableTuple, Tunable, HasTunableSingletonFactory, AutoFactoryInit, TunableVariant
from sims4.tuning.tunable_base import GroupNames
from tunable_multiplier import TunableMultiplier
from ui.ui_dialog_notification import UiDialogNotification, TunableUiDialogNotificationSnippet
import alarms, services, sims4
logger = sims4.log.Logger('DramaNode', default_owner='msundaram')

@dataclass
class ContestScore:
    score: float
    sim_id: int
    object_id: int

    def __init__(self, score, sim_id=0, object_id=0):
        self.score = score
        self.sim_id = sim_id
        self.object_id = object_id


class _FestivalContestWinnerSelectionMethod(HasTunableSingletonFactory, AutoFactoryInit):

    def get_winners_losers(self, contest):
        raise NotImplementedError

    def max_scores_to_consider(self):
        pass

    def uses_ranking(self):
        return True


class _FestivalContestWinnerSelectionMethod_Ranked(_FestivalContestWinnerSelectionMethod):
    FACTORY_TUNABLES = {'_scores_to_consider': TunableRange(description='\n            How many scores should be considered for the prizes.\n            ',
                              tunable_type=int,
                              default=3,
                              minimum=1,
                              tuning_group=(GroupNames.FESTIVAL_CONTEST))}

    def get_winners_losers(self, contest):
        return (
         contest._scores, [])

    def max_scores_to_consider(self):
        return self._scores_to_consider


class _FestivalContestWinnerSelectionMethod_WeightedRandom(_FestivalContestWinnerSelectionMethod):
    FACTORY_TUNABLES = {}

    def get_winners_losers(self, contest):
        num_rewards = len(contest.festival_contest_tuning._win_rewards)
        potential_scores = [(contest_score.score * contest._score_multipliers.get(contest_score.sim_id, 1.0), contest_score) for contest_score in contest._scores]
        winners = []
        while potential_scores and len(winners) < num_rewards:
            winner = random.pop_weighted(potential_scores)
            winners.append(winner)

        return (
         winners, [potential_score[1] for potential_score in potential_scores])

    def uses_ranking(self):
        return False


class _FestivalContestScoreMethodBase(HasTunableSingletonFactory, AutoFactoryInit):

    def calculate_score_for_contest(self, obj_entry, resolver):
        raise NotImplementedError


class _FestivalContestScoreMethodStatistic(_FestivalContestScoreMethodBase):
    FACTORY_TUNABLES = {'_object_statistic':TunableReference(description="\n            The value of the statistic is used as the sim's score in the contest.\n            For example in fishing competition this is the weight of the fish entry.\n            ",
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC)), 
     'remove_statistic_after_submission':Tunable(description='\n            If checked then after the score has been submitted the tuned object_statistic will be removed from the\n            object that has been submitted.\n            ',
       tunable_type=bool,
       default=False)}

    def calculate_score_for_contest(self, obj_entry, resolver):
        statistic_tracker = obj_entry.get_tracker(self._object_statistic)
        if statistic_tracker is None:
            logger.error('{} picked object does not have the stat {}', resolver, self._object_statistic)
            return
        return statistic_tracker.get_value(self._object_statistic)

    def post_submit(self, obj):
        if not self.remove_statistic_after_submission:
            return
        if obj is None:
            return
        statistic_tracker = obj.get_tracker(self._object_statistic)
        if statistic_tracker is None:
            return
        statistic_tracker.remove_statistic(self._object_statistic)


class _FestivalContestScoreMethodMultiplier(_FestivalContestScoreMethodBase):
    FACTORY_TUNABLES = {'_score_multipliers': TunableMultiplier.TunableFactory(description='\n            We use the value calculated from multipliers as the score for the object entry.\n            Use PickedObject as the participant type if you want to test the object entry.\n            ')}

    def calculate_score_for_contest(self, obj_entry, resolver):
        return self._score_multipliers.get_multiplier(resolver)

    def post_submit(self, obj):
        pass


class FestivalContestDramaNodeMixin:
    SIM_ID_SAVE_TOKEN = 'sim_ids'
    OBJECT_ID_SAVE_TOKEN = 'object_ids'
    SCORE_SAVE_TOKEN = 'scores'
    WINNERS_AWARDED_TOKEN = 'awarded'
    USER_SUBMITTED_TOKEN = 'submitted'
    RUNNING_SUB_NODES_TOKEN = 'sub_nodes'
    SCORE_MULTIPLIER_SIMS_TOKEN = 'score_multiplier_sims'
    SCORE_MULTIPLIER_MULTIPLIERS_TOKEN = 'score_multiplier_multipliers'
    INSTANCE_TUNABLES = {'festival_contest_tuning': OptionalTunable(description='\n            Optional contest tuning\n            ',
                                  tunable=TunableTuple(_score_update_frequency=TunableSimMinute(description='\n                    How often a fake new score should be submitted to the tournament.\n                    ',
                                  default=30,
                                  minimum=0,
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _score_update_value_interval=TunableInterval(description='\n                    When a fake new score is submitted, the interval determining what the value should be.\n                    ',
                                  tunable_type=float,
                                  default_lower=0,
                                  default_upper=10,
                                  minimum=0,
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _win_rewards=TunableList(description='\n                    List of Loots applied to the winners of the contest. Index refers to the \n                    winner who receives that loot. 1st, 2nd, 3rd, etc.\n                    ',
                                  tunable=TunableReference(description='\n                        A reference to a loot that will be applied to one of the winners.\n                        ',
                                  manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
                                  class_restrictions=('LootActions', )),
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _win_notifications=TunableList(description="\n                    List of notifications applied to the winners of the contest. These display regardless of whether\n                    the rewards have already been given out. Index refers to the winners of that rank. 1st, 2nd, 3rd, etc.\n                    \n                    First additional token is the name of the next festival in the same scheduling group.  Empty string if\n                    there isn't one.\n                    ",
                                  tunable=(UiDialogNotification.TunableFactory()),
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _lose_notification=TunableUiDialogNotificationSnippet(description="\n                    Notification displayed if there are no player sim winners of the contest. Only displayed if the \n                    winners are requested, not at the end of the festival.\n                    \n                    First additional token is the name of the next festival in the same scheduling group.  Empty string if\n                    there isn't one.\n                    ",
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _contest_duration=TunableSimMinute(description='\n                    The amount of time in sim minutes that we should allow scores to be\n                    submitted to the contest and that we should submit fake scores.\n                    ',
                                  default=60,
                                  minimum=0,
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _score_method=TunableVariant(description='\n                    Which method to use for calculating score of each entered object for the contest.\n                    ',
                                  by_statistic=(_FestivalContestScoreMethodStatistic.TunableFactory()),
                                  by_multipliers=(_FestivalContestScoreMethodMultiplier.TunableFactory()),
                                  default='by_statistic',
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _allow_multiple_entries_per_sim=Tunable(description='\n                    If checked, the same sim can have more than one object in\n                    the scores list. If false (default) only the highest scoring\n                    submission per sim is maintained.\n                    ',
                                  tunable_type=bool,
                                  default=False,
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _destroy_object_on_submit=Tunable(description='\n                    If checked, the submitted object will be destroyed when it\n                    is submitted for the contest.\n                    ',
                                  tunable_type=bool,
                                  default=True,
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _winner_selection_method=TunableVariant(description='\n                    Which method to use for choosing a winner (or winners) of the contest.\n                    ',
                                  ranked=(_FestivalContestWinnerSelectionMethod_Ranked.TunableFactory()),
                                  weighted_random=(_FestivalContestWinnerSelectionMethod_WeightedRandom.TunableFactory()),
                                  default='ranked',
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _festival_contest_sub_nodes=TunableList(description='\n                    A list of additional contest sub nodes that we will run\n                    when this drama node is run and complete when this drama\n                    node completes.\n                    ',
                                  tunable=TunableReference(description='\n                        A sub drama node that we will run/complete along with this drama node.\n                        ',
                                  manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)),
                                  class_restrictions=('FestivalContestSubDramaNode', ))),
                                  _object_tests=TunableTestSet(description='\n                    Tests to run when determining if an object can be entered to the contest.\n                    Use Object as the participant type for the thing you want to test.\n                    '),
                                  losers_loot=OptionalTunable(description='\n                    A loot to apply onto losers of the contest.\n                    ',
                                  tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
                                  class_restrictions=('LootActions', )))))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        if self.festival_contest_tuning is None:
            return
        self._scores = []
        self._score_alarm = None
        self._has_awarded_winners = False
        self._running_contest_sub_nodes = []
        self._score_multipliers = {}

    def _try_and_start_festival(self, from_resume=False):
        super()._try_and_start_festival(from_resume)
        if self.festival_contest_tuning is None:
            return
        self._setup_score_add_alarm()
        if not from_resume:
            self._setup_contest_sub_nodes()

    def _setup_contest_sub_nodes(self):
        resolver = self._get_resolver()
        self._running_contest_sub_nodes = []
        for sub_node in self.festival_contest_tuning._festival_contest_sub_nodes:
            sub_node_uid = services.drama_scheduler_service().run_node(sub_node, resolver)
            if sub_node_uid is not None:
                self._running_contest_sub_nodes.append(sub_node_uid)

    def _setup_score_add_alarm(self):
        if self.festival_contest_tuning._score_update_frequency > 0:
            duration = create_time_span(minutes=(self.festival_contest_tuning._score_update_frequency))
            self._score_alarm = alarms.add_alarm(self, duration, self._score_add_callback, True)
        else:
            if self.festival_contest_tuning._score_update_value_interval.upper_bound > 0:
                self._add_fake_score()

    def _score_add_callback(self, _):
        if self._get_remaining_contest_time().in_minutes() <= 0:
            if self._score_alarm is not None:
                alarms.cancel_alarm(self._score_alarm)
                self._score_alarm = None
            return
        self._add_fake_score()

    def _get_remaining_contest_time(self):
        now = services.time_service().sim_now
        time_since_started = now - self._selected_time
        duration = create_time_span(minutes=(self.festival_contest_tuning._contest_duration + self.pre_festival_duration))
        time_left_to_go = duration - time_since_started
        return time_left_to_go

    def _add_fake_score(self):
        score = self.festival_contest_tuning._score_update_value_interval.random_float()
        self.add_score(sim_id=0, object_id=0, score=score)

    def add_score(self, sim_id, object_id, score):
        scores = self._scores
        if sim_id == 0:
            scores.append(ContestScore(score, sim_id=sim_id, object_id=object_id))
        else:
            found_score = False
            for current_score_obj in scores:
                if current_score_obj.sim_id == sim_id:
                    if self.festival_contest_tuning._allow_multiple_entries_per_sim:
                        if current_score_obj.object_id != object_id:
                            continue
                    current_score = current_score_obj.score
                    if current_score >= score:
                        return
                    current_score_obj.score = score
                    found_score = True
                    break

            if not found_score:
                scores.append(ContestScore(score, sim_id=sim_id, object_id=object_id))
            else:
                scores.sort(key=(lambda item: item.score * self._score_multipliers.get(item.sim_id, 1.0)), reverse=True)
                scores_to_consider = self.festival_contest_tuning._winner_selection_method.max_scores_to_consider()
                if scores_to_consider is not None and len(scores) > scores_to_consider:
                    scores = scores[:scores_to_consider]
                    self._scores = scores
            if not self.festival_contest_tuning._winner_selection_method.uses_ranking():
                return
            for rank, obj in enumerate(scores):
                if obj.sim_id == sim_id:
                    return rank
            else:
                return

    def get_scores_gen(self):
        self._scores.sort(key=(lambda item: item.score * self._score_multipliers.get(item.sim_id, 1.0)), reverse=False)
        yield from self._scores
        if False:
            yield None

    def add_sim_score_multiplier(self, sim_id, multiplier):
        if sim_id not in self._score_multipliers:
            self._score_multipliers[sim_id] = 1.0
        self._score_multipliers[sim_id] *= multiplier
        self._scores.sort(key=(lambda item: item.score * self._score_multipliers.get(item.sim_id, 1.0)), reverse=False)

    def is_during_contest(self):
        if self.is_during_pre_festival():
            return False
        remaining_time = self._get_remaining_contest_time()
        return remaining_time.in_minutes() > 0

    def award_winners(self, show_fallback_dialog=False):
        drama_scheduler = services.drama_scheduler_service()
        rootnode = self
        possible_nodes = [node for node in drama_scheduler.active_nodes_gen() if node.drama_node_type == DramaNodeType.FESTIVAL]
        while 1:
            for node in possible_nodes:
                if hasattr(node, '_running_contest_sub_nodes') and rootnode.uid in node._running_contest_sub_nodes:
                    rootnode = node
                    break
            else:
                break

        best_time = None
        best_node = None
        schedule_group = rootnode.weekly_scheduling_rules.scheduling_group if rootnode.weekly_scheduling_rules is not None else None
        for node in drama_scheduler.scheduled_nodes_gen():
            if node is rootnode:
                continue
            if node.drama_node_type != DramaNodeType.FESTIVAL:
                continue
            target_schedule_group = node.weekly_scheduling_rules.scheduling_group if node.weekly_scheduling_rules is not None else None
            if schedule_group != target_schedule_group:
                continue
            new_time = node._selected_time - services.time_service().sim_now
            if best_time is None or new_time < best_time:
                best_node = node
                best_time = new_time

        if best_node is not None and best_node.festival_dynamic_sign_info is not None:
            additional_tokens = (
             best_node.festival_dynamic_sign_info.festival_name,)
        else:
            additional_tokens = (
             LocalizationHelperTuning.get_raw_text(''),)
        valid_sim_won = False
        winners, losers = self.festival_contest_tuning._winner_selection_method.get_winners_losers(self)
        sim_info_manager = services.sim_info_manager()
        for contest_score, award in zip(winners, self.festival_contest_tuning._win_rewards):
            if not contest_score.sim_id is None:
                if contest_score.sim_id is 0:
                    continue
                else:
                    if not sim_info_manager.is_sim_id_valid(contest_score.sim_id):
                        continue
                    valid_sim_won = True
                    sim = sim_info_manager.get(contest_score.sim_id)
                    resolver = SingleSimResolver(sim)
                    self._has_awarded_winners or award.apply_to_resolver(resolver)
                rank = winners.index(contest_score)
                if rank >= len(self.festival_contest_tuning._win_notifications):
                    continue
                notification = self.festival_contest_tuning._win_notifications[rank]
                dialog = notification(sim, target_sim_id=(contest_score.sim_id),
                  resolver=resolver)
                dialog.show_dialog(additional_tokens=additional_tokens)

        if self.festival_contest_tuning.losers_loot is not None:
            for loser_content_score in losers:
                if not sim_info_manager.is_sim_id_valid(loser_content_score.sim_id):
                    continue
                sim = sim_info_manager.get(loser_content_score.sim_id)
                resolver = SingleSimResolver(sim)
                self.festival_contest_tuning.losers_loot.apply_to_resolver(resolver)

        if show_fallback_dialog:
            if not valid_sim_won:
                active_sim = services.get_active_sim()
                resolver = SingleSimResolver(active_sim)
                dialog = self.festival_contest_tuning._lose_notification(active_sim, target_sim_id=(active_sim.id if active_sim is not None else None),
                  resolver=resolver)
                dialog.show_dialog(additional_tokens=additional_tokens)
        self._has_awarded_winners = True

    def cleanup(self, from_service_stop=False):
        super().cleanup(from_service_stop=from_service_stop)
        if self.festival_contest_tuning is None:
            return
        if self._score_alarm is not None:
            alarms.cancel_alarm(self._score_alarm)
            self._score_alarm = None

    def complete(self, **kwargs):
        (super().complete)(**kwargs)
        if self.festival_contest_tuning is None:
            return
        for running_sub_node_uid in self._running_contest_sub_nodes:
            services.drama_scheduler_service().complete_node(running_sub_node_uid)

        self._running_contest_sub_nodes.clear()
        if self.is_during_pre_festival():
            return
        if self.is_during_contest():
            if not self.is_festival_contest_sub_node():
                return
        if self._has_awarded_winners:
            return
        self.award_winners(show_fallback_dialog=(self.has_user_submitted_entry()))

    def is_festival_contest_sub_node(self):
        return False

    def _save_custom_data(self, writer):
        super()._save_custom_data(writer)
        if self.festival_contest_tuning is None:
            return
        if not self._scores or len(self._scores) == 0:
            return
        scores = []
        sim_ids = []
        object_ids = []
        for score in self.get_scores_gen():
            scores.append(score.score)
            sim_ids.append(score.sim_id)
            object_ids.append(score.object_id)

        writer.write_floats(self.SCORE_SAVE_TOKEN, scores)
        writer.write_uint64s(self.SIM_ID_SAVE_TOKEN, sim_ids)
        writer.write_uint64s(self.OBJECT_ID_SAVE_TOKEN, object_ids)
        writer.write_bool(self.WINNERS_AWARDED_TOKEN, self._has_awarded_winners)
        writer.write_uint64s(self.RUNNING_SUB_NODES_TOKEN, self._running_contest_sub_nodes)
        writer.write_uint64s(self.SCORE_MULTIPLIER_SIMS_TOKEN, self._score_multipliers.keys())
        writer.write_floats(self.SCORE_MULTIPLIER_MULTIPLIERS_TOKEN, self._score_multipliers.values())

    def _load_custom_data(self, reader):
        super_success = super()._load_custom_data(reader)
        if self.festival_contest_tuning is None:
            return
        else:
            return super_success or False
        self._scores = []
        scores = reader.read_floats(self.SCORE_SAVE_TOKEN, ())
        sim_ids = reader.read_uint64s(self.SIM_ID_SAVE_TOKEN, ())
        object_ids = reader.read_uint64s(self.OBJECT_ID_SAVE_TOKEN, None)
        if object_ids is None:
            object_ids = (0, ) * len(sim_ids)
        for score, sim_id, object_id in zip(scores, sim_ids, object_ids):
            self._scores.append(ContestScore(score, sim_id, object_id))

        self._has_awarded_winners = reader.read_bool(self.WINNERS_AWARDED_TOKEN, False)
        self._running_contest_sub_nodes = list(reader.read_uint64s(self.RUNNING_SUB_NODES_TOKEN, []))
        multiplier_sim_ids = reader.read_uint64s(self.SCORE_MULTIPLIER_SIMS_TOKEN, ())
        multiplier_multipliers = reader.read_floats(self.SCORE_MULTIPLIER_MULTIPLIERS_TOKEN, ())
        self._score_multipliers = {sim_id: multiplier for sim_id, multiplier in zip(multiplier_sim_ids, multiplier_multipliers)}
        return True

    def has_user_submitted_entry(self):
        if self._scores:
            active_sim = services.get_active_sim()
            if active_sim is not None:
                sim_id = active_sim.sim_id
                for current_score_obj in self._scores:
                    if current_score_obj.sim_id == sim_id:
                        return True

        return False