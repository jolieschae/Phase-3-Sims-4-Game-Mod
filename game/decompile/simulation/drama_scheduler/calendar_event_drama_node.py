# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\calendar_event_drama_node.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 9501 bytes
from date_and_time import TimeSpan
from distributor.shared_messages import build_icon_info_msg, IconInfoData
from drama_scheduler.drama_node import BaseDramaNode, DramaNodeParticipantOption, DramaNodeUiDisplayType, SenderSimInfoType, DramaNodeRunOutcome
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.resolver import SingleSimResolver
from event_testing.test_events import TestEvent
from event_testing.tests import TunableTestSet
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import OptionalTunable, Tunable, TunableEnumEntry, TunableSet
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import classproperty
from tunable_time import TunableTimeSpan, TunableTimeOfDay, date_and_time_from_days_hours_minutes
from types import SimpleNamespace
import services, sims4
logger = sims4.log.Logger('CalendarEventDramaNode', default_owner='nabaker')

class CalendarEventDramaNode(BaseDramaNode):
    INSTANCE_TUNABLES = {'advance_notice_time':OptionalTunable(description='\n            If enabled, a calender alarm will be triggered at the specified time\n            prior to the event.\n            ',
       tunable=TunableTimeSpan(description='\n                The amount of time between the alert and the start of the event.\n                ',
       default_minutes=0,
       default_hours=0,
       default_days=0)), 
     'sim_of_interest_tests':TunableTestSet(description="\n            Tests used to determine which active household sims this event\n            involves.  Any sim in the active household that passes the test \n            will be indicated as participating in the calendar.  If no household sims\n            Are participating, event won't be on calendar.\n            "), 
     'events_of_interest':TunableSet(description='\n            When any of these events fire, the sims of interest will be updated, and the event added/removed\n            from the calendar as appropriate\n            ',
       tunable=TunableEnumEntry(tunable_type=TestEvent,
       default=(TestEvent.Invalid))), 
     '_simless':Tunable(description="\n            If True, the drama node will behave simlessly and won't need (or use) the receiver sim.\n            ",
       tunable_type=bool,
       default=True,
       tuning_group=GroupNames.PARTICIPANT), 
     'calendar_start_time_override':OptionalTunable(description='\n            If enabled, this will be the time of day shown in the calendar as the start time instead\n            of the scheduled time.\n            ',
       tunable=TunableTimeOfDay(description='\n                The time this event will display as the start time in the calendar.\n                ')), 
     'calendar_end_time_override':OptionalTunable(description='\n            If enabled, this will be the time of day shown in the calendar as the end time instead\n            of the time calculated from the start time.\n            ',
       tunable=TunableTimeOfDay(description='\n                The time of day to display as the end time for this event in the calendar.\n                '))}

    @classproperty
    def simless(cls):
        return cls._simless

    @classproperty
    def drama_node_type(cls):
        return DramaNodeType.CALENDAR

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._sims_of_interest = None

    def create_calendar_alert(self):
        calendar_alert = super().create_calendar_alert()
        if self.ui_display_data:
            build_icon_info_msg(IconInfoData(icon_resource=(self.ui_display_data.icon)), self.ui_display_data.name, calendar_alert.calendar_icon)
        calendar_alert.show_go_to_button = True
        return calendar_alert

    def get_calendar_start_time(self):
        if self.calendar_start_time_override is not None:
            days = self.selected_time.week() * 7 + self.selected_time.day()
            return date_and_time_from_days_hours_minutes(days, self.calendar_start_time_override.hour(), self.calendar_start_time_override.minute())
        return super().get_calendar_start_time()

    def get_calendar_end_time(self):
        if self.calendar_end_time_override is not None:
            days = self.selected_time.week() * 7 + self.selected_time.day()
            return date_and_time_from_days_hours_minutes(days, self.calendar_end_time_override.hour(), self.calendar_end_time_override.minute())
        return super().get_calendar_end_time()

    def load(self, drama_node_proto, schedule_alarm=True):
        success = super().load(drama_node_proto, schedule_alarm=schedule_alarm)
        if success:
            if self.ui_display_type != DramaNodeUiDisplayType.NO_UI:
                self._begin_calendar_updates()
        return success

    def schedule(self, resolver, specific_time=None, time_modifier=TimeSpan.ZERO, **kwargs):
        success = (super().schedule)(resolver, specific_time=specific_time, time_modifier=time_modifier, **kwargs)
        if success:
            if self.ui_display_type != DramaNodeUiDisplayType.NO_UI:
                self._begin_calendar_updates()
        return success

    def _run(self):
        return DramaNodeRunOutcome.SUCCESS_NODE_COMPLETE

    def _begin_calendar_updates(self):
        self._update_sims_of_interest()
        if self._sims_of_interest:
            services.calendar_service().mark_on_calendar(self, None if not self.advance_notice_time else self.advance_notice_time())
        services.get_event_manager().register(self, self.events_of_interest)

    def cleanup(self, from_service_stop=False):
        if not from_service_stop:
            if self._sims_of_interest:
                services.calendar_service().remove_on_calendar(self.uid)
            services.get_event_manager().unregister(self, self.events_of_interest)
        super().cleanup(from_service_stop=from_service_stop)

    def handle_event(self, sim_info, event, resolver):
        if event in self.events_of_interest:
            if sim_info.is_selectable or sim_info in self._sims_of_interest:
                calendar_service = services.calendar_service()
                if not self._sims_of_interest:
                    if self._update_sims_of_interest():
                        services.calendar_service().mark_on_calendar(self, None if not self.advance_notice_time else self.advance_notice_time())
            elif self._update_sims_of_interest():
                if self._sims_of_interest:
                    calendar_service.update_on_calendar(self)
                else:
                    calendar_service.remove_on_calendar(self.uid)

    def get_calendar_sims(self):
        if self._sims_of_interest is None:
            self._update_sims_of_interest()
        return self._sims_of_interest

    def _update_sims_of_interest(self):
        old_sims_of_interest = self._sims_of_interest
        self._sims_of_interest = set()
        for sim_info in services.active_household():
            if self.sim_of_interest_tests.run_tests(SingleSimResolver(sim_info)):
                self._sims_of_interest.add(sim_info)

        return self._sims_of_interest != old_sims_of_interest


lock_instance_tunables(CalendarEventDramaNode, override_picked_sim_info_resolver=False,
  picked_sim_info=SimpleNamespace(type=(DramaNodeParticipantOption.DRAMA_PARTICIPANT_OPTION_NONE)),
  sender_sim_info=SimpleNamespace(type=(DramaNodeParticipantOption.DRAMA_PARTICIPANT_OPTION_NONE)),
  sender_sim_info_type=(SenderSimInfoType.UNINSTANCED_ONLY))