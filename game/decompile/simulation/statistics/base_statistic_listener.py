# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\base_statistic_listener.py
# Compiled at: 2020-04-17 18:57:55
# Size of source mod 2**32: 4171 bytes
from sims4 import hash_util
from sims4.repr_utils import standard_repr
import sims4.log
logger = sims4.log.Logger('SimStatistics')

class BaseStatisticCallbackListener:
    __slots__ = ('_stat', '_stat_type', '_threshold', '_callback', '_on_callback_alarm_reset',
                 '_callback_hash', '_on_callback_alarm_reset_hash', '_should_seed')

    def __init__(self, stat, stat_type, threshold, callback, on_callback_alarm_reset, should_seed=True):
        self._stat = stat
        if self.stat is None:
            self._stat_type = stat_type
        else:
            self._stat_type = stat.stat_type
        self._threshold = threshold
        self._callback = callback
        self._callback_hash = hash_util.obj_str_hash(self._callback)
        self._on_callback_alarm_reset = on_callback_alarm_reset
        self._on_callback_alarm_reset_hash = hash_util.obj_str_hash(self._on_callback_alarm_reset)
        self._should_seed = should_seed

    @property
    def statistic_type(self):
        return self._stat_type

    def __repr__(self):
        return standard_repr(self, stat=(self.statistic_type.__name__), threshold=(self._threshold), callback=(self._callback))

    def __eq__(self, other):
        if other is None:
            return False
        return self._stat_type == other._stat_type and self._threshold == other._threshold and self._callback_hash == other._callback_hash and self._on_callback_alarm_reset_hash == other._on_callback_alarm_reset_hash

    def destroy(self):
        pass

    def check_for_threshold(self, old_value, new_value):
        if not self._threshold.compare(old_value):
            if self._threshold.compare(new_value):
                return True
        return False

    def trigger_callback(self):
        logger.debug('Triggering callback for stat {} at threshold {}; value = {}', self._stat, self._threshold, self._stat.get_value())
        self._callback(self._stat)

    @property
    def stat(self):
        return self._stat

    @stat.setter
    def stat(self, value):
        self._stat = value
        if self.stat is not None:
            self._stat_type = self.stat.stat_type

    @property
    def threshold(self):
        return self._threshold

    @property
    def is_seed(self):
        return self.stat is None

    @property
    def should_seed(self):
        return self._should_seed