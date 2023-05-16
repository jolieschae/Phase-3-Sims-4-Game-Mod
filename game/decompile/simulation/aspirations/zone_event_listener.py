# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\aspirations\zone_event_listener.py
# Compiled at: 2019-02-20 16:28:38
# Size of source mod 2**32: 2820 bytes
from aspirations.aspiration_tuning import AspirationBasic
from aspirations.aspiration_types import AspriationType
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableList, TunableTuple
from sims4.utils import constproperty
from tunable_time import TunableTimeOfDay
import services, sims4.log
logger = sims4.log.Logger('ZoneEventListener')

class ZoneDirectorEventListener(AspirationBasic):
    INSTANCE_TUNABLES = {'valid_times': TunableList(description='\n            The valid times that this event listener can be completed.\n            ',
                      tunable=TunableTuple(description='\n                A period time that this event listener can be completed.\n                ',
                      start_time=TunableTimeOfDay(description='\n                    The start of this period of time that this event listener\n                    can be completed.\n                    ',
                      default_hour=9),
                      end_time=TunableTimeOfDay(description='\n                    The end time of this period of time that this event\n                    listener can be completed.\n                    ',
                      default_hour=17)))}

    @classmethod
    def _verify_tuning_callback(cls):
        for objective in cls.objectives:
            if not objective.resettable:
                logger.error('Objective {} tuned in {} is not resettable.', objective, cls)

    @constproperty
    def aspiration_type():
        return AspriationType.ZONE_DIRECTOR

    @classmethod
    def handle_event(cls, sim_info, event, resolver):
        if sim_info is None:
            return
        else:
            if sim_info.aspiration_tracker is None:
                return
            now = services.time_service().sim_now
            return any((now.time_between_day_times(time_period.start_time, time_period.end_time) for time_period in cls.valid_times)) or None
        sim_info.aspiration_tracker.handle_event(cls, event, resolver)


lock_instance_tunables(ZoneDirectorEventListener, do_not_register_events_on_load=True,
  screen_slam=None)