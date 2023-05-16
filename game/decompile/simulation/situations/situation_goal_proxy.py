# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_proxy.py
# Compiled at: 2020-09-16 21:28:49
# Size of source mod 2**32: 1069 bytes
from situations.situation_goal import SituationGoal

class SituationGoalProxy(SituationGoal):
    REMOVE_INSTANCE_TUNABLES = ('_post_tests', )

    def setup(self):
        super().setup()
        if self._situation is None:
            return
        self._situation._on_proxy_situation_goal_setup(self)

    def set_count(self, value):
        self._count = int(value)
        if self._count >= self._iterations:
            super()._on_goal_completed()
        else:
            self._on_iteration_completed()