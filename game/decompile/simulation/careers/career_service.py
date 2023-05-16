# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\career_service.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 27777 bytes
from _collections import deque
from collections import namedtuple
from date_and_time import TimeSpan
from random import Random
import math, random
from date_and_time import create_time_span
from event_testing.resolver import GlobalResolver
from protocolbuffers import GameplaySaveData_pb2
from sims4.localization import LocalizationHelperTuning
from sims4.math import MAX_UINT64
from sims4.service_manager import Service
from sims4.utils import classproperty
from ui.ui_dialog import ButtonType
from ui.ui_dialog_picker import SimPickerRow
from world.region import get_region_instance_from_zone_id
import persistence_error_types, services, sims4.log
logger = sims4.log.Logger('Career Save Game Data')
_PendingCareerEvent = namedtuple('_PendingCareerEvent', ('career', 'career_event',
                                                         'additional_careers'))

class CareerService(Service):

    def __init__(self):
        self._shuffled_career_list = None
        self._career_list_seed = None
        self._last_day_updated = None
        self._pending_career_events = deque()
        self._main_career_event_zone_id = None
        self._save_lock = None
        self.enabled = True
        self._career_event_subvenue_zone_ids = None
        self._career_lay_off_enabled = True

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_CAREER_SERVICE

    def start(self):
        services.venue_service().on_venue_type_changed.register(self._remove_invalid_careers)
        return super().start()

    def stop(self):
        services.venue_service().on_venue_type_changed.unregister(self._remove_invalid_careers)
        return super().stop()

    def load(self, zone_data=None):
        save_slot_data_msg = services.get_persistence_service().get_save_slot_proto_buff()
        if save_slot_data_msg.gameplay_data.HasField('career_choices_seed'):
            self._career_list_seed = save_slot_data_msg.gameplay_data.career_choices_seed
        else:
            if not save_slot_data_msg.gameplay_data.HasField('career_service'):
                return
            return save_slot_data_msg.gameplay_data.career_service.subvenue_zone_ids or None
        self._career_event_subvenue_zone_ids = {}
        for zone_id in save_slot_data_msg.gameplay_data.career_service.subvenue_zone_ids:
            self._career_event_subvenue_zone_ids[zone_id] = set()

    def save(self, object_list=None, zone_data=None, open_street_data=None, save_slot_data=None):
        if self._career_list_seed is not None:
            save_slot_data.gameplay_data.career_choices_seed = self._career_list_seed
        if self._career_event_subvenue_zone_ids is not None:
            career_service_data = GameplaySaveData_pb2.PersistableCareerService()
            career_service_data.subvenue_zone_ids.extend(self._career_event_subvenue_zone_ids.keys())
            save_slot_data.gameplay_data.career_service = career_service_data

    def _remove_invalid_careers(self):
        for sim_info in services.sim_info_manager().get_all():
            if sim_info.career_tracker is None:
                continue
            sim_info.career_tracker.remove_invalid_careers()

    def save_options(self, options_proto):
        options_proto.career_lay_off_enabled = self._career_lay_off_enabled

    def load_options(self, options_proto):
        self._career_lay_off_enabled = options_proto.career_lay_off_enabled

    @property
    def career_lay_off_enabled(self):
        return self._career_lay_off_enabled

    @career_lay_off_enabled.setter
    def career_lay_off_enabled(self, value):
        self._career_lay_off_enabled = value

    def get_days_from_time(self, time):
        return math.floor(time.absolute_days())

    def get_seed(self, days_now):
        if self._career_list_seed is None:
            self._career_list_seed = random.randint(0, MAX_UINT64)
        return self._career_list_seed + days_now

    def get_career_list(self):
        career_list = []
        career_manager = services.get_instance_manager(sims4.resources.Types.CAREER)
        for career_id in career_manager.types:
            career_tuning = career_manager.get(career_id)
            career_list.append(career_tuning)

        return career_list

    def get_shuffled_career_list(self):
        time_now = services.time_service().sim_now
        days_now = self.get_days_from_time(time_now)
        if self._shuffled_career_list is None or self._last_day_updated != days_now:
            career_seed = self.get_seed(days_now)
            career_rand = Random(career_seed)
            self._last_day_updated = days_now
            self._shuffled_career_list = self.get_career_list()
            career_rand.shuffle(self._shuffled_career_list)
        return self._shuffled_career_list

    def get_careers_by_category_gen(self, career_category):
        career_manager = services.get_instance_manager(sims4.resources.Types.CAREER)
        for career in career_manager.types.values():
            if career.career_category == career_category:
                yield career

    def get_random_career_type_for_sim(self, sim_info):
        career_types = tuple((career_type for career_type in self.get_career_list() if career_type.is_valid_career(sim_info=sim_info)))
        if career_types:
            return random.choice(career_types)

    def restore_career_state(self):
        try:
            manager = services.sim_info_manager()
            for sim_info in manager.get_all():
                if sim_info.is_npc:
                    continue
                current_work_career = sim_info.career_tracker.get_currently_at_work_career()
                for career in sim_info.careers.values():
                    if not career.currently_at_work:
                        continue
                    else:
                        if career is not current_work_career:
                            logger.error('Found a second at work career {} for a sim already at work at {}. This is invalid.', career, current_work_career)
                            if career.is_at_active_event:
                                career.end_career_event_without_payout()
                            else:
                                career.leave_work(left_early=True)
                                continue
                        if career.is_at_active_event:
                            if not career.career_event_manager.is_valid_zone_id(sim_info.zone_id):
                                career.end_career_event_without_payout()
                            else:
                                for career_event, subvenue_zone_id in career.career_event_manager.get_subvenue_datas().items():
                                    career_event_set = self._career_event_subvenue_zone_ids.get(subvenue_zone_id)
                                    if career_event_set is None:
                                        logger.error('Subvenue for career event {} not found on load', career_event)
                                        continue
                                    career_event_set.add(career_event)

                                continue
                        elif not career._rabbit_hole_id:
                            career.put_sim_in_career_rabbit_hole()
                            career.resend_career_data()
                    if not sim_info.can_go_to_work(zone_id=(sim_info.zone_id)):
                        career.leave_work(left_early=True)

            if self._career_event_subvenue_zone_ids:
                venue_game_service = services.venue_game_service()
                if venue_game_service:
                    zone_ids_to_remove = [zone_id for zone_id, current_zone_set in self._career_event_subvenue_zone_ids.items() if not current_zone_set]
                    for zone_id in zone_ids_to_remove:
                        venue_game_service.restore_venue_type(zone_id, create_time_span(minutes=30))
                        del self._career_event_subvenue_zone_ids[zone_id]

        except:
            logger.exception('Exception raised while trying to restore career state.', owner='rrodgers')

    def create_career_event_situations_during_zone_spin_up(self):
        try:
            active_household = services.active_household()
            if active_household is None:
                return
            current_zone_id = services.current_zone_id()
            for sim_info in active_household:
                if sim_info.zone_id == current_zone_id:
                    career = sim_info.career_tracker.career_currently_within_hours
                    if career is not None:
                        career.create_career_event_situations_during_zone_spin_up()

        except:
            logger.exception('Exception raised while trying to restore career event.', owner='tingyul')

    def get_career_in_career_event(self):
        active_household = services.active_household()
        if active_household is not None:
            for sim_info in active_household:
                career = sim_info.career_tracker.get_at_work_career()
                if career is not None and career.is_at_active_event:
                    return career

    def try_add_pending_career_event_offer(self, career, career_event):
        additional_careers = []
        if career.is_multi_sim_active:
            for pending_event in self._pending_career_events:
                if pending_event.career_event == career_event and career in pending_event.additional_careers:
                    return

            household = career.sim_info.household
            region = get_region_instance_from_zone_id(household.home_zone_id)
            for sim_info in household.sim_info_gen():
                if sim_info is career.sim_info:
                    continue
                else:
                    if sim_info.career_tracker is None:
                        continue
                    if not career.allow_active_offlot:
                        if not sim_info.is_instanced():
                            continue
                if not region.is_sim_info_compatible(sim_info):
                    continue
                additional_career = sim_info.career_tracker.careers.get(career.guid64)
                if additional_career is not None and additional_career.follow_enabled and career_event in additional_career.career_events:
                    best_work_time, _, _ = additional_career.get_next_work_time(check_if_can_go_now=True, ignore_pto=True)
                    if best_work_time == TimeSpan.ZERO:
                        additional_careers.append(additional_career)

        pending = _PendingCareerEvent(career=career,
          career_event=career_event,
          additional_careers=additional_careers)
        self._pending_career_events.append(pending)
        if len(self._pending_career_events) == 1:
            self._try_offer_next_career_event()

    def is_sim_info_in_pending_career_event(self, sim_info, ignorable_careers=None):
        for pending_career_event in self._pending_career_events:
            if pending_career_event.career.sim_info is sim_info:
                if ignorable_careers:
                    if pending_career_event.career in ignorable_careers:
                        continue
                return True
            for pending_career in pending_career_event.additional_careers:
                if pending_career.sim_info is sim_info:
                    if ignorable_careers:
                        if pending_career in ignorable_careers:
                            continue
                    return True

        return False

    def _try_offer_next_career_event(self):
        if self._pending_career_events:
            pending = self._pending_career_events[0]
            if pending.additional_careers:
                dialog = pending.career.career_messages.career_event_multi_sim_confirmation_dialog
                response = self._on_career_event_multi_sim_response
            else:
                dialog = pending.career.career_messages.career_event_confirmation_dialog
                response = self._on_career_event_response
            pending.career.send_career_message(dialog,
              on_response=response,
              auto_response=(ButtonType.DIALOG_RESPONSE_OK))

    def _on_career_event_response(self, dialog):
        pending = self._pending_career_events.popleft()
        career_event = pending.career_event
        if dialog.accepted:
            self._cancel_pending_career_events()
            pending.career.on_career_event_accepted(career_event)
        else:
            self._try_offer_next_career_event()
            pending.career.on_career_event_declined(career_event)

    def _on_career_event_multi_sim_response(self, dialog):
        if dialog.accepted:
            pending = self._pending_career_events[0]
            dialog = pending.career.career_messages.career_event_multi_sim_picker_dialog(None, resolver=(GlobalResolver()))
            sim_id = pending.career.sim_info.id
            dialog.add_row(SimPickerRow(sim_id=sim_id, tag=sim_id, select_default=(not (pending.career.requested_day_off or pending.career.taking_day_off))))
            for career in pending.additional_careers:
                sim_id = career.sim_info.id
                dialog.add_row(SimPickerRow(sim_id=sim_id, tag=sim_id, select_default=(not (career.requested_day_off or career.taking_day_off))))

            dialog.add_listener(self._on_career_event_sim_pick_response)
            dialog.show_dialog()
        else:
            pending = self._pending_career_events.popleft()
            career_event = pending.career_event
            self._try_offer_next_career_event()
            pending.career.on_career_event_declined(career_event)
            for career in pending.additional_careers:
                career.on_career_event_declined(career_event)

    def _on_career_event_sim_pick_response(self, dialog):
        pending = self._pending_career_events.popleft()
        career_event = pending.career_event
        results = set(dialog.get_result_tags())
        if dialog.accepted and results:
            self._cancel_pending_career_events()
            additional_sims = set()
            additional_careers = []
            primary_career = None
            rabbithole_careers = []
            if pending.career.sim_info.id in results:
                primary_career = pending.career
            else:
                rabbithole_careers.append(pending.career)
            for career in pending.additional_careers:
                if career.sim_info.id in results:
                    if primary_career is None:
                        primary_career = career
                    else:
                        additional_careers.append(career)
                        additional_sims.add(career.sim_info.id)
                else:
                    rabbithole_careers.append(career)

            primary_career.on_career_event_accepted(career_event, additional_sims=additional_sims)
            for career in additional_careers:
                career.on_career_event_accepted(career_event, is_additional_sim=True)

        else:
            rabbithole_careers = pending.additional_careers
            rabbithole_careers.append(pending.career)
            self._try_offer_next_career_event()
        for career in rabbithole_careers:
            career.on_career_event_declined(career_event)

    def _cancel_pending_career_events(self):
        for pending in self._pending_career_events:
            pending.career.on_career_event_declined(pending.career_event)
            for career in pending.additional_careers:
                career.on_career_event_declined(pending.career_event)

        self._pending_career_events.clear()

    def get_career_event_situation_is_running(self):
        career = self.get_career_in_career_event()
        if career is not None:
            manager = career.career_event_manager
            if manager is not None:
                if manager.scorable_situation_id is not None:
                    return True
        return False

    def set_main_career_event_zone_id_and_lock_save(self, main_zone_id):

        class _SaveLock:

            def get_lock_save_reason(self):
                return LocalizationHelperTuning.get_raw_text('')

        self._save_lock = _SaveLock()
        services.get_persistence_service().lock_save(self._save_lock)
        self._main_career_event_zone_id = main_zone_id

    def get_main_career_event_zone_id_and_unlock_save(self):
        if self._save_lock is not None:
            services.get_persistence_service().unlock_save(self._save_lock)
            self._save_lock = None
        zone_id = self._main_career_event_zone_id
        self._main_career_event_zone_id = None
        return zone_id

    def start_career_event_subvenue(self, career_event, zone_id, venue):
        if self._career_event_subvenue_zone_ids is None:
            self._career_event_subvenue_zone_ids = {}
        else:
            career_event_set = self._career_event_subvenue_zone_ids.get(zone_id)
            if career_event_set is None:
                career_event_set = set()
                self._career_event_subvenue_zone_ids[zone_id] = career_event_set
                venue_game_service = services.venue_game_service()
                if venue_game_service is not None:
                    venue_game_service.change_venue_type(zone_id, venue)
                else:
                    logger.error("Career event {} tuned with subvenue but VenueGameService isn't running.", career_event)
        career_event_set.add(career_event)

    def stop_career_event_subvenue(self, career_event, zone_id, delay):
        if self._career_event_subvenue_zone_ids is None:
            logger.error('Career event {} trying to stop subvenue when no subvenues are started', career_event)
            return
            career_event_set = self._career_event_subvenue_zone_ids.get(zone_id)
            if career_event_set is None:
                logger.error("Career event {} trying to stop subvenue that wasn't started", career_event)
                return
            if career_event not in career_event_set:
                return
            career_event_set.remove(career_event)
            if not career_event_set:
                del self._career_event_subvenue_zone_ids[zone_id]
                venue_game_service = services.venue_game_service()
                if venue_game_service is not None:
                    venue_game_service.restore_venue_type(zone_id, delay())
        else:
            logger.error("Career event {} tuned with subvenue but VenueGameService isn't running.", career_event)