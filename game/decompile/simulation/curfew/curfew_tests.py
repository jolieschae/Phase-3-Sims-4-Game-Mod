# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\curfew\curfew_tests.py
# Compiled at: 2018-11-05 17:19:40
# Size of source mod 2**32: 1295 bytes
from event_testing.results import TestResult
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, Tunable
import event_testing.test_base, services

class CurfewTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'curfew_active': Tunable(description='\n            If True the test will return True if the current lot is under\n            curfew restrictions. If not checked it will only return True when\n            outside of curfew enforced hours.\n            ',
                        tunable_type=bool,
                        default=True)}

    def get_expected_args(self):
        return {}

    def __call__(self):
        lot_curfew_active = services.get_curfew_service().is_curfew_active_on_lot_id(services.current_zone_id())
        if self.curfew_active == lot_curfew_active:
            return TestResult.TRUE
        return TestResult(False, 'Curfew Active is supposed to be {} and it is {}', (self.curfew_active), lot_curfew_active, tooltip=(self.tooltip))