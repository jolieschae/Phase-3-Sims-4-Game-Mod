# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\prep_tasks\linked_statistic_updater.py
# Compiled at: 2018-08-06 16:04:09
# Size of source mod 2**32: 1427 bytes


class LinkedStatisticUpdater:

    def __init__(self, sim_info, statistic, linked_statistic, multiplier):
        self._sim_info = sim_info
        self._statistic = statistic
        self._linked_statistic = linked_statistic
        self._multiplier = multiplier
        self._watcher = None

    def setup_watcher(self):
        tracker = self._sim_info.get_tracker(self._linked_statistic)
        self._watcher = tracker.add_delta_watcher(self._on_statistic_updated)

    def remove_watcher(self):
        tracker = self._sim_info.get_tracker(self._linked_statistic)
        if tracker.has_delta_watcher(self._watcher):
            tracker.remove_delta_watcher(self._watcher)
            self._watcher = None

    def _on_statistic_updated(self, stat_type, delta):
        if stat_type is self._linked_statistic:
            self._sim_info.get_statistic(self._statistic).add_value(delta * self._multiplier)