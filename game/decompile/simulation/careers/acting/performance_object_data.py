# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\acting\performance_object_data.py
# Compiled at: 2018-09-17 18:30:33
# Size of source mod 2**32: 2272 bytes
import services

class PerformanceObjectData:

    def __init__(self, objects, pre_performance_states, performance_states, post_performance_states):
        self._objects = objects
        self._pre_performance_states = pre_performance_states
        self._performance_states = performance_states
        self._post_performance_states = post_performance_states

    def set_performance_states(self):
        self._set_states(self._performance_states)

    def set_pre_performance_states(self):
        bucks_tracker = services.active_sim_info().get_bucks_tracker()
        for state_data in self._pre_performance_states:
            skip_perk = state_data.skip_with_perk
            state_value = state_data.state_value
            if skip_perk is not None:
                if bucks_tracker is not None:
                    if bucks_tracker.is_perk_unlocked(skip_perk):
                        continue
            for obj in self._objects:
                if obj.has_state(state_value.state):
                    obj.set_state((state_value.state), state_value, immediate=True, force_update=True)

    def set_post_performance_states(self):
        self._set_states(self._post_performance_states)

    def _set_states(self, states):
        for state_value in states:
            for obj in self._objects:
                if obj.has_state(state_value.state):
                    obj.set_state((state_value.state), state_value, immediate=True, force_update=True)