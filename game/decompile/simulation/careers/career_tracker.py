# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\career_tracker.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 60220 bytes
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
import itertools
from careers.career_custom_data import CustomCareerData
from careers.career_enums import CareerShiftType, GigResult, DecoratorGigLotType, TestEventCareersOrigin
from careers.career_enums import WORK_CAREER_CATEGORIES, WORK_PART_TIME_CAREER_CATEGORIES, CareerCategory
from careers.career_gig_history import GigHistory
from careers.career_history import CareerHistory
from careers.career_scheduler import get_career_schedule_for_level
from careers.career_tuning import Career
from careers.retirement import Retirement
from date_and_time import DATE_AND_TIME_ZERO
from distributor.rollback import ProtocolBufferRollback
from event_testing.resolver import SingleSimResolver
from objects import ALL_HIDDEN_REASONS
from objects.mixins import AffordanceCacheMixin, ProvidedAffordanceData
from rewards.reward_enums import RewardType
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_info_tracker import SimInfoTracker
from sims4.utils import classproperty
from singletons import DEFAULT
import distributor
from ui.ui_utils import UIUtils
import protocolbuffers, services, sims4.resources
from _collections import defaultdict
logger = sims4.log.Logger('CareerTracker')

class CareerTracker(AffordanceCacheMixin, SimInfoTracker):

    def __init__(self, sim_info, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._sim_info = sim_info
        self._careers = {}
        self._career_history = defaultdict(dict)
        self._retirement = None
        self._custom_data = None
        self._gig_history = {}
        self._last_gig_history_key = None

    def __iter__(self):
        return iter(self._careers.values())

    @classproperty
    def _tracker_lod_threshold(cls):
        return SimInfoLODLevel.BACKGROUND

    @property
    def careers(self):
        return self._careers

    @property
    def custom_career_data(self):
        return self._custom_data

    def resend_career_data(self):
        if services.current_zone().is_zone_shutting_down:
            return
        else:
            return self._sim_info.valid_for_distribution or None
        op = distributor.ops.SetCareers(self)
        distributor.system.Distributor.instance().add_op(self._sim_info, op)
        careers = self.careers
        for career in careers.values():
            career.send_prep_task_update()

    def _at_work_infos(self):
        at_work_infos = []
        for career in self._careers.values():
            at_work_infos.append(career.create_work_state_msg())

        return at_work_infos

    def resend_at_work_infos(self):
        if self._sim_info.is_npc:
            return
        op = distributor.ops.SetAtWorkInfos(self._at_work_infos())
        distributor.system.Distributor.instance().add_op(self._sim_info, op)

    @property
    def has_custom_career(self):
        return self._custom_data is not None

    @property
    def has_career(self):
        return bool(self._careers)

    def has_career_outfit(self):
        return any((career.has_outfit() for career in self._careers.values()))

    def has_part_time_career_outfit(self):
        return any((career.has_outfit() and career.career_category in WORK_PART_TIME_CAREER_CATEGORIES for career in self._careers.values()))

    def has_school_outfit(self):
        return any((career.has_outfit() and career.career_category == CareerCategory.School for career in self._careers.values()))

    def _on_confirmation_dialog_response(self, dialog, new_career, career_track=None, career_level_override=None, schedule_shift_override=CareerShiftType.ALL_DAY, disallowed_reward_types=()):
        if dialog.accepted:
            self.add_career(new_career, career_track=career_track, career_level_override=career_level_override,
              schedule_shift_override=schedule_shift_override,
              disallowed_reward_types=disallowed_reward_types)

    def set_custom_career_data(self, **kwargs):
        if self._custom_data is None:
            self._custom_data = CustomCareerData()
        (self._custom_data.set_custom_career_data)(**kwargs)
        register_loot = Career.CUSTOM_CAREER_REGISTER_LOOT
        register_loot.apply_to_resolver(SingleSimResolver(self._sim_info))
        self.resend_career_data()

    def remove_custom_career_data(self, send_update=True):
        if self._custom_data is None:
            return
        self._custom_data = None
        unregister_loot = Career.CUSTOM_CAREER_UNREGISTER_LOOT
        unregister_loot.apply_to_resolver(SingleSimResolver(self._sim_info))
        if send_update:
            self.resend_career_data()

    def add_career(self, new_career, show_confirmation_dialog=False, career_track=None, user_level_override=None, career_level_override=None, give_skipped_rewards=True, defer_rewards=False, post_quit_msg=True, schedule_shift_override=DEFAULT, show_join_msg=True, disallowed_reward_types=(), force_rewards_to_sim_info_inventory=False, defer_first_assignment=False, schedule_init_only=False, allow_outfit_generation=True, show_icon_override_picker=True):
        if show_confirmation_dialog or schedule_shift_override is DEFAULT:
            level, _, track = new_career.get_career_entry_data(career_track=career_track,
              career_history=(self._career_history),
              user_level_override=user_level_override,
              career_level_override=career_level_override)
            if career_track is None:
                career_track = track
            career_level_tuning = track.career_levels[level]
            if schedule_shift_override is DEFAULT:
                for shift in CareerShiftType:
                    test_schedule = get_career_schedule_for_level(career_level_tuning, schedule_shift_type=shift)
                    if test_schedule and test_schedule.supports_shift(shift):
                        schedule_shift_override = shift
                        break
                else:
                    schedule_shift_override = CareerShiftType.ALL_DAY

            if show_confirmation_dialog:
                if self._retirement is not None:
                    self._retirement.send_dialog((Career.UNRETIRE_DIALOG), (career_level_tuning.get_title(self._sim_info)),
                      icon_override=DEFAULT,
                      on_response=(lambda dialog: self._on_confirmation_dialog_response(dialog, new_career, career_track=career_track, career_level_override=career_level_override, schedule_shift_override=schedule_shift_override)))
                    return
                if new_career.can_quit:
                    quittable_careers = self.get_quittable_careers(schedule_shift_type=schedule_shift_override, career_category=(new_career.career_category))
                    if quittable_careers:
                        career = next(iter(quittable_careers.values()))
                        switch_jobs_dialog = Career.SWITCH_JOBS_DIALOG
                        if len(quittable_careers) > 1:
                            switch_jobs_dialog = Career.SWITCH_MANY_JOBS_DIALOG
                        career.send_career_message(switch_jobs_dialog, (career_level_tuning.get_title(self._sim_info)),
                          icon_override=DEFAULT,
                          on_response=(lambda dialog: self._on_confirmation_dialog_response(dialog, new_career,
                          career_track=career_track,
                          career_level_override=career_level_override,
                          schedule_shift_override=schedule_shift_override,
                          disallowed_reward_types=(
                         RewardType.MONEY,))))
                        return
        self.end_retirement()
        self.remove_custom_career_data(send_update=False)
        if new_career.guid64 in self._careers:
            logger.callstack('Attempting to add career {} sim {} is already in.', new_career, self._sim_info)
            return
        if new_career.can_quit:
            self.quit_quittable_careers(post_quit_msg=post_quit_msg, schedule_shift_type=schedule_shift_override, career_category=(new_career.career_category))
        self._careers[new_career.guid64] = new_career
        new_career.join_career(career_history=(self._career_history), user_level_override=user_level_override,
          career_level_override=career_level_override,
          give_skipped_rewards=give_skipped_rewards,
          defer_rewards=defer_rewards,
          schedule_shift_override=schedule_shift_override,
          show_join_msg=show_join_msg,
          disallowed_reward_types=disallowed_reward_types,
          force_rewards_to_sim_info_inventory=force_rewards_to_sim_info_inventory,
          defer_first_assignment=defer_first_assignment,
          schedule_init_only=schedule_init_only,
          allow_outfit_generation=allow_outfit_generation,
          show_icon_override_picker=show_icon_override_picker)
        self.resend_career_data()
        self.update_affordance_caches()
        if self._on_promoted not in new_career.on_promoted:
            new_career.on_promoted.append(self._on_promoted)
        if self._on_demoted not in new_career.on_demoted:
            new_career.on_demoted.append(self._on_demoted)

    def _on_promoted(self, sim_info):
        self.update_affordance_caches()

    def _on_demoted(self, sim_info):
        self.update_affordance_caches()

    def remove_career(self, career_uid, post_quit_msg=True, update_ui=True, test_event_origin=TestEventCareersOrigin.UNSPECIFIED):
        if career_uid in self._careers:
            career = self._careers[career_uid]
            career.career_stop()
            career.quit_career(post_quit_msg=post_quit_msg, update_ui=update_ui, test_event_origin=test_event_origin)
            career.on_career_removed(self._sim_info)
            self.update_affordance_caches()
            if self._on_promoted in career.on_promoted:
                career.on_promoted.remove(self._on_promoted)
            if self._on_demoted in career.on_demoted:
                career.on_demoted.remove(self._on_demoted)

    def remove_invalid_careers(self):
        for career_uid, career in list(self._careers.items()):
            if not career.is_valid_career():
                self.remove_career(career_uid, post_quit_msg=False,
                  test_event_origin=(TestEventCareersOrigin.INVALID_SIM_CAREER))

    def add_ageup_careers(self):
        for career in list(self._careers.values()):
            if career.current_level_tuning.ageup_branch_career is not None:
                new_career = career.current_level_tuning.ageup_branch_career(self._sim_info)
                default_shift_type = CareerShiftType.EVENING
                if career.schedule_shift_type != CareerShiftType.ALL_DAY:
                    default_shift_type = career.schedule_shift_type
                if career.icon_override is not None:
                    new_career.icon_override = career.icon_override
                self.add_career(new_career, user_level_override=(career.user_level),
                  post_quit_msg=False,
                  schedule_shift_override=default_shift_type,
                  show_join_msg=False,
                  show_icon_override_picker=False)

    def get_career_by_uid(self, career_uid):
        if career_uid in self._careers:
            return self._careers[career_uid]

    def has_career_by_uid(self, career_uid):
        return career_uid in self._careers

    def get_careers_by_category_gen(self, career_category):
        for career in self:
            if career.career_category == career_category:
                yield career

    def get_multigig_and_standard_careers(self):
        standard_careers = []
        multi_gig_careers = []
        for career in self._careers.values():
            if career.current_gig_limit > 1:
                multi_gig_careers.append(career)
            else:
                standard_careers.append(career)

        return (
         standard_careers, multi_gig_careers)

    def has_work_career(self):
        return any((career.career_category in WORK_CAREER_CATEGORIES for career in self))

    def has_quittable_career(self, career_category=None):
        if self.get_quittable_careers(career_category):
            return True
        return False

    def get_quittable_careers(self, schedule_shift_type=CareerShiftType.ALL_DAY, career_category=None):
        quittable_careers = dict(((uid, career) for uid, career in self._careers.items() if career.can_quit if career.get_is_quittable_shift(schedule_shift_type, career_category)))
        return quittable_careers

    def quit_quittable_careers(self, post_quit_msg=True, schedule_shift_type=CareerShiftType.ALL_DAY, num_careers_to_quit=None, career_category=None):
        careers_quit = []
        for career_uid, career in self.get_quittable_careers(schedule_shift_type, career_category).items():
            self.remove_career(career_uid, post_quit_msg=post_quit_msg)
            careers_quit.append((career_uid, career))
            if num_careers_to_quit is not None and len(careers_quit) >= num_careers_to_quit:
                break

        return careers_quit

    def get_at_work_career(self):
        for career in self._careers.values():
            if career.currently_at_work:
                return career

    def get_on_assignment_career(self):
        for career in self._careers.values():
            if career.on_assignment:
                return career

    def available_for_work(self, career):
        existing_at_work_career = self.get_at_work_career()
        if existing_at_work_career:
            if existing_at_work_career.guid64 != career.guid64:
                return False
        if services.get_career_service().is_sim_info_in_pending_career_event((self._sim_info), ignorable_careers=(career,)):
            return False
        return True

    @property
    def currently_at_work(self):
        for career in self._careers.values():
            if career.currently_at_work:
                return True

        return False

    @property
    def currently_during_work_hours(self):
        for career in self._careers.values():
            if career.is_work_time:
                return True

        return False

    def career_during_work_hours(self, career):
        if career is None:
            return False
        return career.is_work_time

    @property
    def career_currently_within_hours(self):
        found_career = None
        rabbit_hole_service = services.get_rabbit_hole_service()
        head_rabbit_hole = rabbit_hole_service.get_head_rabbit_hole_id(self._sim_info.id)
        for career in self._careers.values():
            if career.is_work_time:
                rabbit_hole_id = career._rabbit_hole_id
                if rabbit_hole_id is not None:
                    if head_rabbit_hole == rabbit_hole_id:
                        found_career = career
                        break
                else:
                    found_career = career

        return found_career

    def get_currently_at_work_career(self):
        for career in self._careers.values():
            if career.currently_at_work:
                return career

    def career_leave(self, career):
        self.update_history(career, from_leave=True)
        del self._careers[career.guid64]

    def get_all_career_aspirations(self):
        return tuple(itertools.chain.from_iterable((career.get_all_aspirations() for career in self._careers.values())))

    @property
    def career_history(self):
        return self._career_history

    def update_history(self, career, from_leave=False):
        cur_track = career.current_track_tuning
        highest_level = self.get_highest_level_reached_for_track(career.guid64, cur_track.guid64)
        if career.user_level > highest_level:
            highest_level = career.user_level
        else:
            days_worked = 0 if career.days_worked_statistic is None else career.days_worked_statistic.get_value()
            active_days_worked = 0 if career.active_days_worked_statistic is None else career.active_days_worked_statistic.get_value()
            key = (career.guid64, career.current_track_tuning.guid64)
            if from_leave:
                time_of_leave = services.time_service().sim_now
            else:
                current_history = self._career_history.get(key, None)
            time_of_leave = current_history.time_of_leave if current_history is not None else DATE_AND_TIME_ZERO
        self._career_history[key] = CareerHistory(career_track=(career.current_track_tuning), level=(career.level),
          user_level=(career.user_level),
          overmax_level=(career.overmax_level),
          highest_level=highest_level,
          time_of_leave=time_of_leave,
          daily_pay=(career.get_daily_pay()),
          days_worked=days_worked,
          active_days_worked=active_days_worked,
          player_rewards_deferred=(career.player_rewards_deferred),
          schedule_shift_type=(career.schedule_shift_type))

    def get_highest_level_reached_for_track(self, career_uid, track_id):
        key = (
         career_uid, track_id)
        entry = self._career_history.get(key, None)
        if entry is not None:
            return entry.highest_level
        return 0

    def get_highest_level_reached(self, career_uid):
        matching_careers = [value for (career_id_key, _), value in self._career_history.items() if career_id_key == career_uid]
        if matching_careers:
            return max((entry.highest_level for entry in matching_careers))
        return 0

    @property
    def retirement(self):
        return self._retirement

    def retire_career(self, career_uid):
        career = self._careers[career_uid]
        cur_track_id = career.current_track_tuning.guid64
        for uid in list(self._careers):
            self.remove_career(uid, post_quit_msg=False, test_event_origin=(TestEventCareersOrigin.RETIRE_CAREER))

        self._retirement = Retirement(self._sim_info, career_uid, cur_track_id)
        self._retirement.start(send_retirement_notification=True)

    def end_retirement(self):
        if self._retirement is not None:
            self._retirement.stop()
            self._retirement = None

    @property
    def retired_career_uid(self):
        if self._retirement is not None:
            return self._retirement.career_uid
        return 0

    def start_retirement(self):
        if self._retirement is not None:
            self._retirement.start()

    def set_gig(self, gig, gig_time, gig_customer=None, gig_budget=None):
        gig_career = self.get_career_by_uid(gig.career.guid64)
        if gig_career is None:
            logger.error("Tried to set gig {} for career {} on sim {} but sim doesn't have career.", gig, gig.career, self._sim_info)
            return
        gig_career.add_gig(gig, gig_time, gig_customer=gig_customer, gig_budget=gig_budget)
        self.resend_career_data()
        if gig.open_career_panel:
            UIUtils.toggle_sim_info_panel(UIUtils.SimInfoPanelType.SIM_INFO_CAREER_PANEL)

    def on_sim_added_to_skewer(self):
        for career in self._careers.values():
            key = (
             career.guid64, career.current_track_tuning.guid64)
            career_history = self._career_history.get(key, None)
            if career_history is not None:
                if career_history.deferred_rewards:
                    career.award_deferred_promotion_rewards()
            sim = self._sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if sim is not None:
                career.create_objects()

        self.resend_career_data()
        self.resend_at_work_infos()

    def on_loading_screen_animation_finished(self):
        for career in self._careers.values():
            career.on_loading_screen_animation_finished()

    def on_zone_unload(self):
        for career in self._careers.values():
            career.on_zone_unload()

    def on_zone_load(self):
        self.start_retirement()
        for career in self._careers.values():
            career.on_zone_load()

    def on_sim_startup(self):
        for career in self._careers.values():
            career.startup_career()

        self.update_affordance_caches()

    def on_death(self):
        for uid, career in list(self._careers.items()):
            if career.is_at_active_event:
                career.end_career_event_without_payout()
            self.remove_career(uid, post_quit_msg=False,
              update_ui=False,
              test_event_origin=(TestEventCareersOrigin.DEATH))

        self.end_retirement()

    def clean_up(self):
        for career in self._careers.values():
            career.career_stop()

        self._careers.clear()
        self.end_retirement()

    def on_situation_request(self, situation):
        career = self.get_at_work_career()
        if career is not None:
            if self._sim_info.is_npc:
                career_location = career.get_career_location()
                if services.current_zone_id() == career_location.get_zone_id():
                    return
            if situation.can_remove_sims_from_work:
                if not career.is_at_active_event:
                    career.leave_work_early()

    def clear_career_history(self, career_guid, track_guid):
        key = (
         career_guid, track_guid)
        if self._career_history.get(key, None) is not None:
            del self._career_history[key]

    def get_previous_career_id(self, career_category=None):
        prev_career_key = None
        career_manager = services.get_instance_manager(sims4.resources.Types.CAREER)
        if career_manager is None:
            return
        for key, career_history in self._career_history.items():
            if career_category is not None:
                career = career_manager.get(key[0])
                if not (career is None or career.career_category == career_category):
                    continue
            if prev_career_key is None:
                prev_career_key = key
                continue
            prev_career_history = self._career_history[prev_career_key]
            if prev_career_history.time_of_leave < career_history.time_of_leave:
                prev_career_key = key

        if prev_career_key is not None:
            return prev_career_key[0]

    def save(self):
        save_data = protocolbuffers.SimObjectAttributes_pb2.PersistableSimCareers()
        for career in self._careers.values():
            with ProtocolBufferRollback(save_data.careers) as (career_proto):
                career_proto.MergeFrom(career.get_persistable_sim_career_proto())

        for key, career_history in self._career_history.items():
            with ProtocolBufferRollback(save_data.career_history) as (career_history_proto):
                career_history_proto.career_uid = key[0]
                career_history_proto.track_uid = key[1]
                career_history.save_career_history(career_history_proto)

        if self._retirement is not None:
            save_data.retirement_career_uid = self._retirement.career_uid
            save_data.retirement_career_track_uid = self._retirement.retired_track_uid
        if self._custom_data is not None:
            self._custom_data.save_custom_data(save_data)
        for history_key, gig_history in self._gig_history.items():
            with ProtocolBufferRollback(save_data.gig_history) as (gig_history_proto):
                gig_history.save_gig_history(gig_history_proto)

        if self._last_gig_history_key is not None:
            last_customer_id = self._last_gig_history_key[0]
            if last_customer_id is not None:
                save_data.last_gig_history.customer_sim_id = last_customer_id
            last_lot_id = self._last_gig_history_key[1]
            if last_lot_id is not None:
                save_data.last_gig_history.client_lot_id = last_lot_id
        return save_data

    def load(self, save_data, skip_load=False):
        self._careers.clear()
        for career_save_data in save_data.careers:
            career_uid = career_save_data.career_uid
            career_type = services.get_instance_manager(sims4.resources.Types.CAREER).get(career_uid)
            if career_type is not None:
                career = career_type(self._sim_info)
                career.load_from_persistable_sim_career_proto(career_save_data, skip_load=skip_load)
                self._careers[career_uid] = career

        self._career_history.clear()
        for history_entry in save_data.career_history:
            if skip_load:
                if history_entry.career_uid not in self._careers:
                    continue
            career_history = CareerHistory.load_career_history(self._sim_info, history_entry)
            if career_history is not None:
                key = (
                 history_entry.career_uid, history_entry.track_uid)
                self._career_history[key] = career_history
                if career_history.deferred_rewards and history_entry.career_uid in self._careers:
                    self._careers[history_entry.career_uid].defer_player_rewards()

        self._retirement = None
        retired_career_uid = save_data.retirement_career_uid
        retired_track_uid = save_data.retirement_career_track_uid
        key = (retired_career_uid, retired_track_uid)
        if key in self._career_history:
            self._retirement = Retirement(self._sim_info, retired_career_uid, retired_track_uid)
        if save_data.HasField('custom_career_name'):
            self._custom_data = CustomCareerData()
            self._custom_data.load_custom_data(save_data)
        self._gig_history.clear()
        for gig_history_entry in save_data.gig_history:
            gig_history = GigHistory.load_gig_history(gig_history_entry)
            if gig_history is not None:
                history_key = (
                 gig_history.customer_id, None)
                if gig_history.gig_lot_type == DecoratorGigLotType.COMMERCIAL:
                    history_key = (
                     None, gig_history.lot_id)
                self._gig_history[history_key] = gig_history

        if save_data.HasField('last_gig_history'):
            last_customer_id = None
            last_lot_id = None
            if save_data.last_gig_history.HasField('customer_sim_id'):
                last_customer_id = save_data.last_gig_history.customer_sim_id
            if save_data.last_gig_history.HasField('client_lot_id'):
                last_lot_id = save_data.last_gig_history.client_lot_id
            self._last_gig_history_key = (
             last_customer_id, last_lot_id)

    def activate_career_aspirations(self):
        for career in self._careers.values():
            for aspiration_to_activate in career.aspirations_to_activate:
                aspiration_to_activate.register_callbacks()
                self._sim_info.aspiration_tracker.validate_and_return_completed_status(aspiration_to_activate)
                self._sim_info.aspiration_tracker.process_test_events_for_aspiration(aspiration_to_activate)

            career_aspiration = career._current_track.career_levels[career._level].get_aspiration()
            if career_aspiration is not None:
                career_aspiration.register_callbacks()
                self._sim_info.aspiration_tracker.validate_and_return_completed_status(career_aspiration)
                self._sim_info.aspiration_tracker.process_test_events_for_aspiration(career_aspiration)
            for gig in career.get_current_gigs():
                gig.register_aspiration_callbacks()

    def get_provided_super_affordances(self):
        provided_affordances, target_provided_affordances = set(), list()
        for career in self:
            current_level = career.current_level_tuning()
            provided_affordances.update(current_level.super_affordances)
            for affordance in current_level.target_super_affordances:
                provided_affordance_data = ProvidedAffordanceData(affordance.affordance, affordance.object_filter, affordance.allow_self)
                target_provided_affordances.append(provided_affordance_data)

        return (
         provided_affordances, target_provided_affordances)

    def get_actor_and_provided_mixers_list(self):
        actor_mixers, provided_mixers = [], []
        for career in self:
            current_level = career.current_level_tuning()
            actor_mixers.append(current_level.actor_mixers)
            provided_mixers.append(current_level.provided_mixers)

        return (
         actor_mixers, provided_mixers)

    def get_sim_info_from_provider(self):
        return self._sim_info

    def on_lod_update(self, old_lod, new_lod):
        if new_lod == SimInfoLODLevel.MINIMUM:
            self.clean_up()

    @property
    def gig_history(self):
        return self._gig_history

    def add_gig_history(self, gig):
        customer_id = gig.get_gig_customer()
        lot_id = gig.get_customer_lot_id()
        client_hh_name = None
        customer_sim_info = services.sim_info_manager().get(customer_id)
        if customer_sim_info is not None:
            client_hh_name = customer_sim_info.household.name
        gig_result = GigResult.SUCCESS
        gig_score = 0
        if gig.gig_result is not None:
            gig_result = gig.gig_result
            gig_score = gig.gig_score
        lot_type = DecoratorGigLotType.RESIDENTIAL
        history_key = gig.get_gig_history_key()
        project_title = gig.display_name(self._sim_info)
        decorator_tuning = gig.decorator_gig_tuning
        if decorator_tuning is not None:
            if decorator_tuning.gig_short_title is not None:
                project_title = decorator_tuning.gig_short_title()
            lot_type = decorator_tuning.decorator_gig_lot_type
        new_gig_history = GigHistory(customer_id=customer_id, lot_id=lot_id,
          gig_id=(gig.guid64),
          career_id=(gig.career.guid64),
          gig_result=gig_result,
          gig_score=gig_score,
          customer_name=client_hh_name,
          lot_type=lot_type,
          project_title=project_title)
        existing_gig_history = self._gig_history.get(history_key, None)
        if existing_gig_history is not None:
            new_gig_history.after_photos.extend(existing_gig_history.after_photos)
            new_gig_history.before_photos.extend(existing_gig_history.before_photos)
            new_gig_history.hi_low_res_dict.update(existing_gig_history.hi_low_res_dict)
            new_gig_history.selected_photos.update(existing_gig_history.selected_photos)
        self._gig_history[history_key] = new_gig_history
        self._last_gig_history_key = history_key

    def get_gig_history_by_key(self, gig_history_key):
        return self._gig_history.get(gig_history_key)

    def get_gig_history_by_customer(self, customer_id):
        return self._gig_history.get((customer_id, None))

    def get_gig_history_by_venue(self, lot_id):
        return self._gig_history.get((None, lot_id))

    def get_any_gig_history_for_lot(self, lot_id):
        for history in self._gig_history.values():
            if history.lot_id == lot_id:
                return history

    def get_gig_histories_with_result(self, min_gig_result, max_gig_result):
        return [history for history in self._gig_history.values() if history.gig_result.within_range(min_gig_result, max_gig_result)]

    def get_last_gig_history(self):
        if self._last_gig_history_key is None:
            return
        return self._gig_history.get(self._last_gig_history_key)

    def has_gig_history_with_key(self, gig_history_key):
        return gig_history_key in self._gig_history

    def has_gig_history_for_customer(self, customer_id):
        return any((history.customer_id == customer_id for history in self._gig_history.values()))

    def has_gig_history_for_venue(self, lot_id):
        return any((history.lot_id == lot_id for history in self._gig_history.values()))

    def has_gig_history_with_result(self, min_gig_result, max_gig_result, include_active_gig=False):
        return any((history.gig_result.within_range(min_gig_result, max_gig_result) and (include_active_gig or not self.is_gig_history_active(history)) for history in self._gig_history.values()))

    def set_before_after_photo(self, gig_history_key, resource_key, resource_key_low_res, before=True):
        gig_history = self.get_gig_history_by_key(gig_history_key)
        if gig_history is None:
            return False
        elif before:
            gig_history.before_photos.append(resource_key)
        else:
            gig_history.after_photos.append(resource_key)
        gig_history.hi_low_res_dict[resource_key.instance] = resource_key_low_res
        return True

    def get_before_and_after_photos(self, career):
        current_gig = career.get_current_gig()
        if current_gig is None:
            logger.error('No active gig for career {}', career)
            return (None, None)
        gig_history = current_gig.get_gig_history_key()
        if gig_history is None:
            logger.error('No gig history key registered for active gig {}', current_gig)
            return (None, None)
        gig_history = self.get_gig_history_by_key(gig_history)
        if gig_history is None:
            logger.error('No gig-history is tracked on the current gig {}', current_gig)
            return (None, None)
        return (gig_history.before_photos, gig_history.after_photos)

    def get_selected_photos(self, career, active_gig=True):
        if active_gig:
            return self.get_active_gig_selected_photos(career)
        return self.get_gig_history_selected_photos(career)

    def get_active_gig_selected_photos(self, career):
        current_gig = career.get_current_gig()
        if current_gig is None:
            logger.error('No active gig for career {}', career)
            return
        gig_history_key = current_gig.get_gig_history_key()
        if gig_history_key is None:
            logger.error('No valid key registered for active gig {}', current_gig)
            return
        gig_history = self.get_gig_history_by_key(gig_history_key)
        if gig_history is None:
            logger.error('No gig-history is tracked on the current gig {}', current_gig)
            return
        return gig_history.get_selected_photos()

    def get_gig_history_selected_photos(self, career):
        selected_photo_sequenced_gig_history = {}
        for history in self._gig_history.values():
            gig_history_selected = history.selected_photos
            if history.career_id != career.guid64:
                continue
            if not gig_history_selected:
                continue
            for sequence_id, before_then_after_list in gig_history_selected.items():
                if sequence_id in selected_photo_sequenced_gig_history:
                    before = before_then_after_list[0] or selected_photo_sequenced_gig_history[sequence_id][0]
                    after = before_then_after_list[1] or selected_photo_sequenced_gig_history[sequence_id][1]
                else:
                    before = before_then_after_list[0]
                    after = before_then_after_list[1]
                selected_photo_sequenced_gig_history[sequence_id] = [
                 before, after]

        return selected_photo_sequenced_gig_history.values()

    def is_gig_history_active(self, gig_history):
        gig_career = self.get_career_by_uid(gig_history.career_id)
        if gig_career:
            current_gig = gig_career.get_current_gig()
            if current_gig:
                current_gig_id = current_gig.guid64
                current_customer_id = current_gig.get_gig_customer()
                return current_gig_id == gig_history.gig_id and current_customer_id == gig_history.customer_id
        return False

    def has_selected_photos(self, gig_history):
        return len(gig_history.selected_photos) > 0

    def has_before_photos(self, gig_history):
        return len(gig_history.before_photos) > 0

    def has_after_photos(self, gig_history):
        return len(gig_history.after_photos) > 0

    def has_any_selected_photos(self):
        return any((self.has_selected_photos(history) for history in self._gig_history.values()))

    def has_any_before_photos(self):
        return any((self.has_before_photos(history) for history in self._gig_history.values()))

    def has_any_after_photos(self):
        return any((self.has_after_photos(history) for history in self._gig_history.values()))

    def _get_gig_history(self, career, active_gig):
        gig_histories = []
        if active_gig:
            current_gig = career.get_current_gig()
            if current_gig is None:
                logger.error('No active gig for career {}', career)
                return
            gig_history_key = current_gig.get_gig_history_key()
            if gig_history_key is None:
                logger.error('No gig history key registered for active gig {}', current_gig)
                return
            gig_history = self.get_gig_history_by_key(gig_history_key)
            if gig_history is None:
                logger.error('No gig-history is tracked on the current gig {}', current_gig)
                return
            gig_histories = [
             gig_history]
        else:
            career_gig_histories = self.gig_history.values()
            for gig_history in career_gig_histories:
                if gig_history.career_id == career.guid64:
                    gig_histories.append(gig_history)

        return gig_histories

    def update_photo_difference(self, career, active_gig):
        gig_histories = self._get_gig_history(career, active_gig)
        for gig_history in gig_histories:
            gig_history.update_photo_difference()

    def clear_deletion_cache_from_gig_history(self, career, active_gig):
        gig_histories = self._get_gig_history(career, active_gig)
        for gig_history in gig_histories:
            gig_history.clear_deletion_cache()

    def clear_selected_photos_from_gig_history(self, career, active_gig):
        gig_histories = self._get_gig_history(career, active_gig)
        for gig_history in gig_histories:
            gig_history.clear_selected_photos()

    def clear_photos_from_gig_history(self):
        for gig_history in self.gig_history.values():
            gig_history.before_photos.clear()
            gig_history.after_photos.clear()
            gig_history.selected_photos.clear()
            gig_history.hi_low_res_dict.clear()