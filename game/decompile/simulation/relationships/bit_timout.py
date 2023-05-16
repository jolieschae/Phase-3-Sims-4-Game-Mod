# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\bit_timout.py
# Compiled at: 2017-06-13 19:38:01
# Size of source mod 2**32: 2549 bytes
import alarms, clock, services, sims4.log
logger = sims4.log.Logger('Relationship', default_owner='jjacobson')

class BitTimeoutData:

    def __init__(self, bit, alarm_callback):
        self._bit = bit
        self._alarm_callback = alarm_callback
        self._alarm_handle = None
        self._start_time = 0

    @property
    def bit(self):
        return self._bit

    @property
    def alarm_handle(self):
        return self._alarm_handle

    def reset_alarm(self):
        logger.assert_raise(self._bit is not None, '_bit is None in BitTimeoutData.')
        if self._alarm_handle is not None:
            self.cancel_alarm()
        self._set_alarm(self._bit.timeout)

    def cancel_alarm(self):
        if self._alarm_handle is not None:
            alarms.cancel_alarm(self._alarm_handle)
            self._alarm_handle = None

    def load_bit_timeout(self, time):
        self.cancel_alarm()
        time_left = self._bit.timeout - time
        if time_left > 0:
            self._set_alarm(time_left)
            return True
        logger.warn('Invalid time loaded for timeout for bit {}.  This is valid if the tuning data changed.', self._bit)
        return False

    def get_elapsed_time(self):
        if self._alarm_handle is not None:
            now = services.time_service().sim_now
            delta = now - self._start_time
            return delta.in_minutes()
        return 0

    def _set_alarm(self, time):
        time_span = clock.interval_in_sim_minutes(time)
        self._alarm_handle = alarms.add_alarm(self, time_span, (self._alarm_callback), repeating=False, cross_zone=True)
        logger.assert_raise(self._alarm_handle is not None, 'Failed to create timeout alarm for rel bit {}'.format(self.bit))
        self._start_time = services.time_service().sim_now