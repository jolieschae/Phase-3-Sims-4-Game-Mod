# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\formal_dances_situation.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 30032 bytes
import itertools, services, sims4.resources
from date_and_time import create_time_span
from event_testing.resolver import SingleSimResolver, DoubleSimResolver
from event_testing.test_events import TestEvent
from indexed_manager import CallbackTypes
from role.role_state import RoleState
from sims4 import random
from sims4.tuning.tunable import TunableRange, TunableReference, TunableSimMinute
from sims4.tuning.tunable_base import GroupNames
from situations.situation_complex import CommonInteractionCompletedSituationState, CommonSituationState, SituationComplexCommon, SituationStateData, TunableSituationJobAndRoleState
from tag import TunableTags
from tunable_multiplier import TunableMultiplier
from ui.ui_dialog_notification import UiDialogNotification
logger = sims4.log.Logger('PromSituation', default_owner='sucywang')
PROM_ROYALTY_WINNER_TOKEN = 'prom_royalty_winner_token'
PROM_JESTER_WINNER_TOKEN = 'prom_jester_winner_token'
WINNER_NOTIFICATION_SHOWN_TOKEN = 'winner_notification_shown_token'

class _AwardsStatesBase(CommonInteractionCompletedSituationState):

    def on_activate(self, reader=None):
        super().on_activate(reader=reader)
        for custom_key in self._interaction_of_interest.custom_keys_gen():
            self._test_event_register(TestEvent.InteractionExitedPipeline, custom_key)

    def handle_podium_displacement(self):
        pass

    def _on_interaction_of_interest_complete(self, resolver=None, **kwargs):
        if services.current_zone().is_in_build_buy:
            return
        if resolver is not None:
            if resolver.interaction.has_been_reset or resolver.interaction.has_been_canceled:
                self._change_state(self.owner.announce_awards_in_route_fail_state())
                return
        self.go_to_next_state()

    def go_to_next_state(self):
        pass

    def on_hit_their_marks(self):
        if self.owner.get_target_object() is None:
            self._change_state(self.owner.announce_awards_in_route_fail_state())


class _GatherAndDanceState(CommonSituationState):

    def timer_expired(self):
        self._change_state(self.owner.presenter_goto_podium_state())

    def on_hit_their_marks(self):
        pass

    def handle_podium_displacement(self):
        pass


class _PresenterGoToPodiumState(_AwardsStatesBase):

    def on_activate(self, reader=None):
        super().on_activate(reader)
        if self.owner.is_running:
            if self.owner.get_target_object() is None:
                self._change_state(self.owner.announce_awards_in_route_fail_state())

    def handle_podium_displacement(self):
        self._change_state(self.owner.announce_awards_in_route_fail_state())

    def go_to_next_state(self):
        self._change_state(self.owner.prepare_for_awards_state())

    def timer_expired(self):
        self._change_state(self.owner.announce_awards_in_route_fail_state())


class _PrepareForAwardsState(_AwardsStatesBase):

    def on_activate(self, reader=None):
        super().on_activate(reader)
        if self.owner.is_running:
            if self.owner.get_target_object() is None:
                self._change_state(self.owner.announce_awards_in_route_fail_state())

    def timer_expired(self):
        self._change_state(self.owner.present_awards_state())

    def handle_podium_displacement(self):
        self._change_state(self.owner.announce_awards_in_route_fail_state())


class _PresentAwardsState(_AwardsStatesBase):

    def go_to_next_state(self):
        self.owner.present_awards()
        self._change_state(self.owner.accept_awards_state())

    def timer_expired(self):
        self._change_state(self.owner.announce_awards_in_route_fail_state())

    def handle_podium_displacement(self):
        self._change_state(self.owner.announce_awards_in_route_fail_state())


class _AcceptAwardsState(_AwardsStatesBase):

    def on_activate(self, reader=None):
        super().on_activate(reader)
        if self.owner.is_running:
            self.owner.assign_sim_winner_role(self.owner.prom_royalty_winner_id, self.owner.royalty_winner_role_state)
            self.owner.assign_sim_winner_role(self.owner.prom_jester_winner_id, self.owner.jester_winner_role_state)

    def on_hit_their_marks(self):
        self.owner.assign_sim_winner_role(self.owner.prom_royalty_winner_id, self.owner.royalty_winner_role_state)
        self.owner.assign_sim_winner_role(self.owner.prom_jester_winner_id, self.owner.jester_winner_role_state)

    def handle_podium_displacement(self):
        self._change_state(self.owner.accept_awards_in_route_fail_state())

    def timer_expired(self):
        self._change_state(self.owner.more_dancing_state())


class _MoreDancingState(_AwardsStatesBase):

    def timer_expired(self):
        self.owner._self_destruct()


class _AnnounceAwardsInRouteFailState(_AwardsStatesBase):

    def on_activate(self, reader=None):
        super().on_activate(reader)
        if self.owner.is_running:
            self.owner.present_awards()

    def on_hit_their_marks(self):
        self.owner.present_awards()

    def timer_expired(self):
        self._change_state(self.owner.accept_awards_in_route_fail_state())


class _AcceptAwardsInRouteFailState(_AwardsStatesBase):
    FACTORY_TUNABLES = {'royalty_winner_route_fail_role_state':RoleState.TunableReference(description='\n            A role state that forces prom royalty winner to spin into crown on the spot, \n            by not setting a constraint.\n            '), 
     'jester_winner_route_fail_role_state':RoleState.TunableReference(description='\n            A role state that forces prom jester winner to spin into crown on the spot, \n            by not setting a constraint.\n            ')}

    def __init__(self, *args, royalty_winner_route_fail_role_state=None, jester_winner_route_fail_role_state=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.royalty_winner_route_fail_role_state = royalty_winner_route_fail_role_state
        self.jester_winner_route_fail_role_state = jester_winner_route_fail_role_state

    def on_activate(self, reader=None):
        super().on_activate(reader)
        if self.owner.is_running:
            self.owner.assign_sim_winner_role(self.owner.prom_royalty_winner_id, self.royalty_winner_route_fail_role_state)
            self.owner.assign_sim_winner_role(self.owner.prom_jester_winner_id, self.jester_winner_route_fail_role_state)

    def on_hit_their_marks(self):
        self.owner.assign_sim_winner_role(self.owner.prom_royalty_winner_id, self.royalty_winner_route_fail_role_state)
        self.owner.assign_sim_winner_role(self.owner.prom_jester_winner_id, self.jester_winner_route_fail_role_state)

    def timer_expired(self):
        self.owner._change_state(self.owner.more_dancing_state())


class PromSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'gather_and_dance_state':_GatherAndDanceState.TunableFactory(description='\n            A state where sims in the situation gathers and dance near stereos.\n            ',
       tuning_group=GroupNames.STATE,
       display_name='01_gather_and_dance_state'), 
     'presenter_goto_podium_state':_PresenterGoToPodiumState.TunableFactory(description='\n            A situation state where the presenter routes to the podium in preparation\n            for the awards ceremony. If the presenter fails to route to the podium, the\n            state will go to announce_awards_in_route_fail_state.\n            ',
       tuning_group=GroupNames.STATE,
       display_name='02_presenter_go_to_podium_state'), 
     'prepare_for_awards_state':_PrepareForAwardsState.TunableFactory(description='\n            A situation state that gathers the sim by the podium to prepare for awards.\n            If the podium cannot be found, the state will go to announce_awards_in_route_fail_state.\n            ',
       tuning_group=GroupNames.STATE,
       display_name='03_teens_prepare_for_awards_state'), 
     'present_awards_state':_PresentAwardsState.TunableFactory(description='\n            A state where the prom royalty and jester winners are announced via a TNS.\n            The state will go to announce_awards_in_route_fail_state if presenting interaction gets cancelled.\n            ',
       tuning_group=GroupNames.STATE,
       display_name='04_present_awards_state'), 
     'accept_awards_state':_AcceptAwardsState.TunableFactory(description='\n            A state where the winners goes near the podium and spins into crown/jester hat.\n            If the winners fails to route to the podium, the situation will go to accept awards in route fail state.\n            ',
       tuning_group=GroupNames.STATE,
       display_name='05_accept_awards_state'), 
     'announce_awards_in_route_fail_state':_AnnounceAwardsInRouteFailState.TunableFactory(description='\n            A situation state where the presenter, teens fails to route to the podium,\n            or the podium is not found. The winners notification will be pushed and teens will not gather.\n            ',
       tuning_group=GroupNames.STATE,
       display_name='06_announce_awards_in_route_fail_state'), 
     'accept_awards_in_route_fail_state':_AcceptAwardsInRouteFailState.TunableFactory(description='\n            A state after the route fail state where the awards winners will be forced to \n            spin into crown where they are standing, usually in the case where we cannot find the podium.\n            ',
       tuning_group=GroupNames.STATE,
       display_name='07_accept_awards_in_route_fail_state'), 
     'more_dancing_state':_MoreDancingState.TunableFactory(description='\n            A state where teens go back to dancing and socializing.\n            ',
       tuning_group=GroupNames.STATE,
       display_name='08_more_dancing_state'), 
     'chaperone_situation_job':TunableSituationJobAndRoleState(description='\n            Job and role for chaperones at prom.\n            ',
       tuning_group=GroupNames.ROLES), 
     'announcer_situation_job':TunableSituationJobAndRoleState(description='\n            Job and role for the announcer.\n            ',
       tuning_group=GroupNames.ROLES), 
     'teens_situation_job':TunableSituationJobAndRoleState(description='\n            Job and role for teens that attend prom.\n            ',
       tuning_group=GroupNames.ROLES), 
     'active_sims_job':TunableSituationJobAndRoleState(description='\n            Job and role for the instanced active household sims.\n            ',
       tuning_group=GroupNames.ROLES), 
     'per_vote_weight':TunableRange(description='\n            The weight of a single vote the sim receives. This weight will affect the chance\n            of a sim winning a prom royalty/jester title.\n            ',
       tunable_type=float,
       default=1.2,
       minimum=1.0,
       tuning_group=GroupNames.SITUATION), 
     'prom_royalty_vote_statistic':TunableReference(description='\n            The statistic that we will use in order to determine how\n            many nominations the sim received for prom royalty title.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC),
       tuning_group=GroupNames.SITUATION), 
     'prom_jester_vote_statistic':TunableReference(description='\n            The statistic that we will use in order to determine how\n            many nominations the sim received for prom jester title.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC),
       tuning_group=GroupNames.SITUATION), 
     'prom_royalty_multiplier':TunableMultiplier.TunableFactory(description='\n            A multiplier to the weight for the sims in the situation to win the prom\n            royalty title if they passed these tests.\n            ',
       tuning_group=GroupNames.SITUATION), 
     'prom_jester_multiplier':TunableMultiplier.TunableFactory(description='\n            A multiplier to the weight for the sims in the situation to win the prom\n            jester title if they passed these tests.\n            ',
       tuning_group=GroupNames.SITUATION), 
     'podium_tag':TunableTags(description='\n            Tags used to find the podium which the sims will gather around in the \n            present awards state.\n            ',
       tuning_group=GroupNames.SITUATION), 
     'royalty_winner_role_state':RoleState.TunableReference(description='\n            A role state the prom royalty winner will use to spin into crown. This will be pushed through code.\n            ',
       tuning_group=GroupNames.SITUATION), 
     'jester_winner_role_state':RoleState.TunableReference(description='\n            A role state the prom jester title winner will use to spin into crown. This will be pushed through code.\n            ',
       tuning_group=GroupNames.SITUATION), 
     'prom_winners_notification':UiDialogNotification.TunableFactory(description='\n            A TNS that is displayed to announce the prom royalty and jester winners.\n            ',
       tuning_group=GroupNames.SITUATION), 
     'post_prom_drama_node':TunableReference(description='\n            A drama node used to trigger the post prom party invite.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.DRAMA_NODE),
       tuning_group=GroupNames.SITUATION), 
     'post_prom_schedule_delay':TunableSimMinute(description='\n            Post prom drama node will trigger after this amount of time in sim minutes after\n            prom ends. This number should be less than the venue switch timer so the screens\n            wont happen at the same time.\n            ',
       default=10,
       tuning_group=GroupNames.SITUATION)}

    def __init__(self, *arg, **kwargs):
        (super().__init__)(*arg, **kwargs)
        reader = self._seed.custom_init_params_reader
        if reader is not None:
            self.prom_royalty_winner_id = reader.read_uint64(PROM_ROYALTY_WINNER_TOKEN, None)
            self.prom_jester_winner_id = reader.read_uint64(PROM_JESTER_WINNER_TOKEN, None)
            self.winner_notification_shown = reader.read_bool(WINNER_NOTIFICATION_SHOWN_TOKEN, False)
        else:
            self.prom_royalty_winner_id = None
            self.prom_jester_winner_id = None
            self.winner_notification_shown = False
        self.podium = None
        self.podium_displaced = False
        self._register_test_event(TestEvent.OnExitBuildBuy)

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _GatherAndDanceState, factory=(cls.gather_and_dance_state)),
         SituationStateData(2, _PresenterGoToPodiumState, factory=(cls.presenter_goto_podium_state)),
         SituationStateData(3, _PrepareForAwardsState, factory=(cls.prepare_for_awards_state)),
         SituationStateData(4, _PresentAwardsState, factory=(cls.present_awards_state)),
         SituationStateData(5, _AcceptAwardsState, factory=(cls.accept_awards_state)),
         SituationStateData(6, _AnnounceAwardsInRouteFailState, factory=(cls.announce_awards_in_route_fail_state)),
         SituationStateData(7, _AcceptAwardsInRouteFailState, factory=(cls.accept_awards_in_route_fail_state)),
         SituationStateData(8, _MoreDancingState, factory=(cls.more_dancing_state)))

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.chaperone_situation_job.job, cls.chaperone_situation_job.role_state),
         (
          cls.announcer_situation_job.job, cls.announcer_situation_job.role_state),
         (
          cls.teens_situation_job.job, cls.teens_situation_job.role_state),
         (
          cls.active_sims_job.job, cls.active_sims_job.role_state)]

    def start_situation(self):
        super().start_situation()
        self._change_state(self.gather_and_dance_state())

    def handle_event(self, sim_info, event, resolver):
        if event == TestEvent.OnExitBuildBuy:
            if self.podium_displaced:
                self._cur_state.handle_podium_displacement()
                self.podium_displaced = False
        super().handle_event(sim_info, event, resolver)

    @classmethod
    def default_job(cls):
        return cls.teens_situation_job.job

    def _situation_timed_out(self, *args, **kwargs):
        (super()._situation_timed_out)(*args, **kwargs)
        drama_scheduler = services.drama_scheduler_service()
        if drama_scheduler is not None:
            resolver = SingleSimResolver(services.active_sim_info())
            time = services.time_service().sim_now + create_time_span(minutes=(self.post_prom_schedule_delay))
            (
             drama_scheduler.schedule_node((self.post_prom_drama_node), resolver,
               specific_time=time),)

    def get_prom_royalty_multiplier(self, sim_info):
        return self.prom_royalty_multiplier.get_multiplier(SingleSimResolver(sim_info))

    def get_prom_jester_multiplier(self, sim_info):
        return self.prom_jester_multiplier.get_multiplier(SingleSimResolver(sim_info))

    def present_awards(self):
        self.generate_prom_winners()
        self.push_winner_notification()

    def generate_prom_winners(self):
        if self.prom_jester_winner_id:
            if self.prom_royalty_winner_id:
                royalty_info = services.sim_info_manager().get(self.prom_royalty_winnerharvestid)
                jester_info = services.sim_info_manager().get(self.prom_jester_winner_id)
                if royalty_info:
                    if self.is_sim_info_in_situation(royalty_info):
                        if jester_info:
                            if self.is_sim_info_in_situation(jester_info):
                                return
        weighted_sims_royalty = []
        weighted_sims_jester = []
        for sim in itertools.chain(self.all_sims_in_job_gen(self.teens_situation_job.job), self.all_sims_in_job_gen(self.active_sims_job.job)):
            sim_id = sim.id
            royalty_votes_stat = sim.get_statistic(self.prom_royalty_vote_statistic)
            jester_votes_stat = sim.get_statistic(self.prom_jester_vote_statistic)
            royalty_multiplier = self.get_prom_royalty_multiplier(sim)
            jester_multiplier = self.get_prom_jester_multiplier(sim)
            if royalty_votes_stat is not None:
                if royalty_votes_stat.get_value() != 0:
                    weighted_sims_royalty.append((
                     royalty_votes_stat.get_value() * self.per_vote_weight * royalty_multiplier, sim_id))
                else:
                    weighted_sims_royalty.append((royalty_multiplier, sim_id))
                if jester_votes_stat is not None and jester_votes_stat.get_value() != 0:
                    weighted_sims_jester.append((
                     jester_votes_stat.get_value() * self.per_vote_weight * jester_multiplier, sim_id))
            else:
                weighted_sims_jester.append((jester_multiplier, sim_id))

        weighted_sims_royalty.sort(key=(lambda x: x[0]))
        self.prom_royalty_winner_id = random.weighted_random_item(weighted_sims_royalty)
        jester_list = [(weight, sim_id) for weight, sim_id in weighted_sims_jester if sim_id is not self.prom_royalty_winner_id]
        jester_list.sort(key=(lambda x: x[0]))
        self.prom_jester_winner_id = random.weighted_random_item(jester_list)

    def assign_sim_winner_role(self, winner_id, winner_role_state):
        winner = services.sim_info_manager().get(winner_id)
        if winner is not None:
            if self.is_sim_info_in_situation(winner):
                self._set_sim_role_state(winner.get_sim_instance(), winner_role_state)

    def push_winner_notification(self):
        if self.winner_notification_shown:
            return
        royalty_winner = services.sim_info_manager().get(self.prom_royalty_winner_id)
        jester_winner = services.sim_info_manager().get(self.prom_jester_winner_id)
        dialog = self.prom_winners_notification((services.active_sim_info()),
          resolver=(DoubleSimResolver(royalty_winner, jester_winner)))
        dialog.show_dialog()
        self.winner_notification_shown = True

    def _destroy(self):
        object_manager = services.object_manager()
        if object_manager.is_callback_registered(CallbackTypes.ON_OBJECT_REMOVE, self._on_podium_object_displaced):
            object_manager.unregister_callback(CallbackTypes.ON_OBJECT_REMOVE, self._on_podium_object_displaced)
        services.get_event_manager().unregister_single_event(self, TestEvent.OnExitBuildBuy)
        zone = services.current_zone()
        if zone is not None:
            if not zone.is_zone_shutting_down:
                services.get_prom_service().cleanup_prom()
        super()._destroy()

    @property
    def should_preroll_during_zone_spin_up(self):
        return True

    def _on_add_sim_to_situation(self, sim, job_type, role_state_type_override=None):
        super()._on_add_sim_to_situation(sim, job_type, role_state_type_override)
        services.get_prom_service().on_sim_added_to_prom(sim)

    def on_hit_their_marks(self):
        self.get_target_object()
        services.get_prom_service().handle_time_for_prom()
        self._cur_state.on_hit_their_marks()
        super().on_hit_their_marks()

    def give_level_rewards(self, end_msg, sim_info=None):
        super().give_level_rewards(end_msg, services.active_sim_info())

    def get_target_object(self):
        if self.podium is not None:
            return self.podium
        if self.podium_tag is None:
            logger.error('No tags were set for podium_tag.')
            return
        sim = next(self.all_sims_in_job_gen(self.announcer_situation_job.job), None)
        if sim is None:
            logger.error('Could not find sim with presenter situation job.')
            return
        object_manager = services.object_manager()
        matched_objects = object_manager.get_objects_matching_tags(self.podium_tag)
        for obj in matched_objects:
            if obj.is_connected(sim):
                object_manager.register_callback(CallbackTypes.ON_OBJECT_REMOVE, self._on_podium_object_displaced)
                obj.register_on_location_changed(self._on_podium_object_displaced)
                self.podium = obj
                return self.podium

        logger.error('Could not find a valid target object.')

    def _on_podium_object_displaced(self, script_object, *args, **kwargs):
        if script_object is not self.podium:
            return
        else:
            if self.podium:
                if self.podium.is_on_location_changed_callback_registered(self._on_podium_object_displaced):
                    self.podium.unregister_on_location_changed(self._on_podium_object_displaced)
            if services.current_zone().is_in_build_buy:
                self.podium_displaced = True
            else:
                self._cur_state.handle_podium_displacement()

    def _save_custom_situation(self, writer):
        super()._save_custom_situation(writer)
        if self.prom_royalty_winner_id is not None:
            writer.write_uint64(PROM_ROYALTY_WINNER_TOKEN, self.prom_royalty_winner_id)
        if self.prom_jester_winner_id is not None:
            writer.write_uint64(PROM_JESTER_WINNER_TOKEN, self.prom_jester_winner_id)
        writer.write_bool(WINNER_NOTIFICATION_SHOWN_TOKEN, self.winner_notification_shown)