# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\global_flags\global_flag_test.py
# Compiled at: 2021-06-01 17:46:37
# Size of source mod 2**32: 1518 bytes
import services
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from global_flags.global_flags import GlobalFlags
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumFlags, Tunable

class GlobalFlagTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'flags':TunableEnumFlags(description='\n            The flags to check against being set in\n            the global flag service.\n            ',
       enum_type=GlobalFlags), 
     'negate':Tunable(description='\n            If enabled then we will check if any of the flags\n            are not set.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {}

    def __call__(self):
        if services.global_flag_service().has_any_flag(self.flags):
            if self.negate:
                return TestResult(False, 'At least one of flags {} is set.', self.flags)
            return TestResult.TRUE
        else:
            if self.negate:
                return TestResult.TRUE
            return TestResult(False, 'None of flags {} are set.', self.flags)