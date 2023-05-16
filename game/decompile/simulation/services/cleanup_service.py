# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\services\cleanup_service.py
# Compiled at: 2017-05-23 22:11:51
# Size of source mod 2**32: 2686 bytes
from alarms import add_alarm, cancel_alarm
from sims4.service_manager import Service
from situations.service_npcs.modify_lot_items_tuning import ModifyAllLotItems
import date_and_time, services, tunable_time

class CleanupService(Service):
    OPEN_STREET_CLEANUP_ACTIONS = ModifyAllLotItems.TunableFactory()
    OPEN_STREET_CLEANUP_TIME = tunable_time.TunableTimeOfDay(description='\n        What time of day the open street cleanup will occur.\n        ',
      default_hour=4)

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._alarm_handle = None

    def start(self):
        current_time = services.time_service().sim_now
        initial_time_span = current_time.time_till_next_day_time(self.OPEN_STREET_CLEANUP_TIME)
        repeating_time_span = date_and_time.create_time_span(days=1)
        self._alarm_handle = add_alarm(self, initial_time_span, (self._on_update), repeating=True, repeating_time_span=repeating_time_span)

    def stop(self):
        if self._alarm_handle is not None:
            cancel_alarm(self._alarm_handle)
            self._alarm_handle = None

    def _on_update(self, _):
        self._do_cleanup()

    def _do_cleanup(self):
        cleanup = CleanupService.OPEN_STREET_CLEANUP_ACTIONS()

        def object_criteria(obj):
            if obj.in_use:
                return False
            if obj.is_on_active_lot():
                return False
            return True

        cleanup.modify_objects(object_criteria=object_criteria)

    def on_cleanup_zone_objects(self, client):
        time_of_last_save = services.current_zone().time_of_last_save()
        now = services.time_service().sim_now
        time_to_now = now - time_of_last_save
        time_to_cleanup = time_of_last_save.time_till_next_day_time(CleanupService.OPEN_STREET_CLEANUP_TIME)
        if time_to_now > time_to_cleanup:
            self._do_cleanup()