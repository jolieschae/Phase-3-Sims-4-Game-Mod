# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_time.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 3834 bytes
from clock import interval_in_sim_hours
from date_and_time import TimeSpan
from sims4.tuning.tunable import TunableRange
from sims4.utils import flexproperty
from situations.situation_goal import SituationGoal
import alarms, services

class SituationGoalTime(SituationGoal):
    DURATION_RUN = 'duration_run'
    REMOVE_INSTANCE_TUNABLES = ('_post_tests', )
    INSTANCE_TUNABLES = {'duration': TunableRange(description='\n            The amount of time in Sim Hours that this goal has to run before\n            completing.\n            ',
                   tunable_type=int,
                   default=5,
                   minimum=1)}

    def __init__(self, *args, reader=None, **kwargs):
        (super().__init__)(args, reader=reader, **kwargs)
        self._total_time_ran = TimeSpan.ZERO
        self._last_started_time = None
        self._alarm_handle = None
        self._total_duration = interval_in_sim_hours(self.duration)
        if reader is not None:
            duration_run = reader.read_uint64(self.DURATION_RUN, 0)
            self._total_time_ran = TimeSpan(duration_run)

    def setup(self):
        super().setup()
        self._start_alarm()

    def create_seedling(self):
        self._start_alarm()
        seedling = super().create_seedling()
        writer = seedling.writer
        writer.write_uint64(self.DURATION_RUN, self._total_time_ran.in_ticks())
        return seedling

    def _decommision(self):
        self._stop_alarm()
        super()._decommision()

    def _on_hour_reached(self, alarm_handle=None):
        self._stop_alarm()
        if self._total_time_ran >= self._total_duration:
            super()._on_goal_completed()
        else:
            self._on_iteration_completed()
            self._start_alarm()

    def _start_alarm(self):
        self._stop_alarm()
        next_hour = interval_in_sim_hours(int(self._total_time_ran.in_hours()) + 1)
        time_till_completion = next_hour - self._total_time_ran
        self._alarm_handle = alarms.add_alarm(self, time_till_completion, self._on_hour_reached)
        self._last_started_time = services.time_service().sim_now

    def _stop_alarm(self):
        if self._alarm_handle is not None:
            alarms.cancel_alarm(self._alarm_handle)
            self._alarm_handle = None
            self._total_time_ran += services.time_service().sim_now - self._last_started_time
            self._last_started_time = None

    @property
    def completed_iterations(self):
        return int(self._total_time_ran.in_hours())

    @flexproperty
    def max_iterations(cls, inst):
        return cls.duration