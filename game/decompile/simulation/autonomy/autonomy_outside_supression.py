# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\autonomy\autonomy_outside_supression.py
# Compiled at: 2018-02-23 19:42:39
# Size of source mod 2**32: 2610 bytes
import functools, operator, services, sims4
logger = sims4.log.Logger('OutsideSupressor', default_owner='camilogarcia')

class OutsideSupressor:

    def __init__(self):
        self._outside_lock_counter = 0
        self._outside_unlock_counter = 0
        self.outside_multiplier = 1
        self._outside_multiplier_list = []

    def is_not_allowed_outside(self):
        return self._outside_unlock_counter > 0 or services.time_service().is_sun_out() or False
        return self._outside_lock_counter > 0

    def add_lock_counter(self):
        self._outside_lock_counter += 1

    def remove_lock_counter(self):
        if self._outside_lock_counter == 0:
            logger.error('Trying to remove a lock from a Sim that had no locks applied')
            return
        self._outside_lock_counter -= 1

    def add_multiplier(self, value):
        self._outside_multiplier_list.append(value)
        self.outside_multiplier *= value

    def remove_multiplier(self, value):
        self._outside_multiplier_list.remove(value)
        self.outside_multiplier = functools.reduce(operator.mul, self._outside_multiplier_list, 1)

    def add_unlock_counter(self):
        self._outside_unlock_counter += 1

    def remove_unlock_counter(self):
        if self._outside_unlock_counter == 0:
            logger.error('Trying to remove an unlock from a Sim that had no locks applied')
            return
        self._outside_unlock_counter -= 1