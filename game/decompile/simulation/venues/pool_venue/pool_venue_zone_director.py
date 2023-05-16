# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\pool_venue\pool_venue_zone_director.py
# Compiled at: 2017-01-23 16:56:42
# Size of source mod 2**32: 2255 bytes
from scheduler import SituationWeeklySchedule
from situations.situation_guest_list import SituationGuestList
from venues.scheduling_zone_director import SchedulingZoneDirector
from venues.visitor_situation_on_arrival_zone_director_mixin import VisitorSituationOnArrivalZoneDirectorMixin
import services

class PoolVenueZoneDirector(VisitorSituationOnArrivalZoneDirectorMixin, SchedulingZoneDirector):
    INSTANCE_TUNABLES = {'special_pool_schedule': SituationWeeklySchedule.TunableFactory(description='\n            The schedule to trigger pool scheduled events (e.g. parties, etc)\n            ',
                                schedule_entry_data={'pack_safe': True})}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._special_pool_schedule = None

    def on_loading_screen_animation_finished(self):
        super().on_loading_screen_animation_finished()
        self._special_pool_schedule = self.special_pool_schedule(start_callback=(self._start_special_pool_event))

    def _start_special_pool_event(self, scheduler, alarm_data, extra_data):
        situation = alarm_data.entry.situation
        if not situation.situation_meets_starting_requirements():
            return
        situation_manager = services.get_zone_situation_manager()
        if any((situation is type(running_situation) for running_situation in situation_manager.running_situations())):
            return
        guest_list = SituationGuestList(invite_only=True)
        situation_manager.create_situation(situation, guest_list=guest_list,
          user_facing=False,
          scoring_enabled=False,
          creation_source=(self.instance_name))