# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\route_events\route_event_mixins.py
# Compiled at: 2019-03-18 15:20:10
# Size of source mod 2**32: 3046 bytes
from event_testing.results import TestResult
from sims4.math import MAX_INT32

class RouteEventBase:

    def __init__(self, time=None, *args, **kwargs):
        self.time = time
        self.event_data = None
        self._run_duration = MAX_INT32

    @property
    def duration(self):
        return self._run_duration

    def copy_from(self, other):
        self.time = other.time
        self.event_data = other.event_data
        self._run_duration = other.duration


class RouteEventDataBase:

    @classmethod
    def test(cls, actor, event_data_tuning):
        return TestResult.TRUE

    def prepare(self, actor):
        raise NotImplementedError

    def is_valid_for_scheduling(self, actor, path):
        return True

    def should_remove_on_execute(self):
        return True

    def execute(self, actor, **kwargs):
        raise NotImplementedError

    def process(self, actor):
        raise NotImplementedError