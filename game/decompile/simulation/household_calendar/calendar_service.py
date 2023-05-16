# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\household_calendar\calendar_service.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 8938 bytes
import weakref
from protocolbuffers import UI_pb2, Calendar_pb2
from protocolbuffers.DistributorOps_pb2 import Operation
from collections import defaultdict
from distributor.ops import GenericProtocolBufferOp
from distributor.system import Distributor
from distributor.rollback import ProtocolBufferRollback
from drama_scheduler.drama_node import DramaNodeUiDisplayType
from sims4.service_manager import Service
from sims4.utils import classproperty
import alarms, services, sims4.log, persistence_error_types
logger = sims4.log.Logger('Calendar', default_owner='bosee')

class CalendarService(Service):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._event_data_map = {}
        self._event_alarm_map = {}
        self._event_favorite_map = defaultdict(set)

    def mark_on_calendar(self, event, advance_notice_time=None):
        event_id = event.uid
        self._event_data_map[event_id] = weakref.ref(event)
        self._send_calendary_entry(event, UI_pb2.CalendarUpdate.ADD)
        self._set_up_alert(event, advance_notice_time)

    def remove_on_calendar(self, event_id):
        if event_id not in self._event_data_map:
            logger.debug("Trying to remove a calendar entry which doesn't exist {}", event_id)
            return
            stored_event = self._event_data_map[event_id]()
            if stored_event is None:
                logger.error('Trying to remove a calendar entry which has been destroyed {}', event_id)
                return
        else:
            self._send_calendary_entry(stored_event, UI_pb2.CalendarUpdate.REMOVE)
            self._remove_alert(event_id)
            del self._event_data_map[event_id]
            household_id = services.active_household_id()
            if household_id is not None:
                if event_id in self._event_favorite_map[household_id]:
                    self._event_favorite_map[household_id].remove(event_id)
                    if not self._event_favorite_map[household_id]:
                        del self._event_favorite_map[household_id]

    def update_on_calendar(self, event, advance_notice_time=None):
        event_id = event.uid
        if event_id not in self._event_data_map:
            logger.debug("Trying to update a calendar entry which doesn't exist {}", event_id)
            return
        stored_event = self._event_data_map[event_id]()
        if stored_event is None:
            logger.error('Trying to update a calendar entry which has been destroyed {}', event_id)
            return
        self._send_calendary_entry(stored_event, UI_pb2.CalendarUpdate.UPDATE)
        self._remove_alert(event_id)
        self._set_up_alert(event, advance_notice_time)

    def is_on_calendar(self, event_id):
        return event_id in self._event_data_map

    def _set_up_alert(self, event, advance_notice_time):
        if advance_notice_time is None:
            return
        event_id = event.uid
        entry_start_time = event.get_calendar_start_time()
        alarm_time_span = entry_start_time - services.game_clock_service().now() - advance_notice_time
        if alarm_time_span.in_minutes() <= 0:
            return
        alarm_handle = alarms.add_alarm(self, alarm_time_span, lambda _: self._on_alert_alarm(self._event_data_map[event_id]()))
        self._event_alarm_map[event_id] = alarm_handle

    def _remove_alert(self, event_id):
        if event_id not in self._event_alarm_map:
            return
        alarms.cancel_alarm(self._event_alarm_map[event_id])
        del self._event_alarm_map[event_id]

    def _on_alert_alarm(self, event):
        if event is None:
            logger.error('Trying to send alert for drama node which has been destroyed. We might be leaking memory.')
            return
        del self._event_alarm_map[event.uid]
        event.on_calendar_alert_alarm()

    def _send_calendary_entry(self, event, update_type):
        if event.ui_display_type == DramaNodeUiDisplayType.ALERTS_ONLY:
            return
        household_id = services.active_household_id()
        calendar_entry = event.create_calendar_entry()
        calendar_entry.favorited = event.uid in self._event_favorite_map[household_id]
        calendar_msg = UI_pb2.CalendarUpdate()
        calendar_msg.updated_entry = calendar_entry
        calendar_msg.update_type = update_type
        op = GenericProtocolBufferOp(Operation.MSG_CALENDAR_UPDATE, calendar_msg)
        Distributor.instance().add_op_with_no_owner(op)

    def set_favorited_calendar_entry(self, event_id, is_favorite):
        if event_id not in self._event_data_map:
            logger.debug("Trying to favorite a calendar entry which doesn't exist {}", event_id)
            return
            stored_event = self._event_data_map[event_id]()
            if stored_event is None:
                logger.error('Trying to favorite a calendar entry which has been destroyed {}', event_id)
                return
            household_id = services.active_household_id()
            if is_favorite:
                self._event_favorite_map[household_id].add(stored_event.uid)
        elif stored_event.uid in self._event_favorite_map[household_id]:
            self._event_favorite_map[household_id].remove(stored_event.uid)
            if not self._event_favorite_map[household_id]:
                del self._event_favorite_map[household_id]
        self._send_calendary_entry(stored_event, UI_pb2.CalendarUpdate.UPDATE)

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_CALENDAR_SERVICE

    def save(self, save_slot_data=None, **kwargs):
        calendar_service_data = Calendar_pb2.PersistableCalendarService()
        for household_id, favorited_event_ids in self._event_favorite_map.items():
            with ProtocolBufferRollback(calendar_service_data.favorite_data) as (calendar_favorite_data):
                calendar_favorite_data.household_id = household_id
                calendar_favorite_data.favorited_event_ids.extend(favorited_event_ids)

        save_slot_data.gameplay_data.calendar_service = calendar_service_data

    def on_all_households_and_sim_infos_loaded(self, client):
        save_slot_data_msg = services.get_persistence_service().get_save_slot_proto_buff()
        calendar_service_data = save_slot_data_msg.gameplay_data.calendar_service
        household_manager = services.household_manager()
        for calendar_favorite_data in calendar_service_data.favorite_data:
            household = household_manager.get(calendar_favorite_data.household_id)
            if not household is None:
                if household.hidden:
                    continue
                favorited_event_ids = set()
                for favorite_event_id in calendar_favorite_data.favorited_event_ids:
                    favorited_event_ids.add(favorite_event_id)

                self._event_favorite_map[calendar_favorite_data.household_id] = favorited_event_ids