# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\retail\retail_tests.py
# Compiled at: 2018-11-05 18:06:53
# Size of source mod 2**32: 3701 bytes
from event_testing.results import TestResult
from sims4.math import almost_equal
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, Tunable, TunableVariant
import event_testing.test_base, services

class _RetailTest(HasTunableSingletonFactory, AutoFactoryInit):

    def __call__(self, tooltip=None):
        retail_manager = services.business_service().get_retail_manager_for_zone()
        if retail_manager is None:
            return TestResult(False, 'Current zone has no retail manager.')
        return self._run_test(retail_manager, tooltip=tooltip)

    def _run_test(self, retail_manager, tooltip=None):
        raise NotImplementedError


class RetailOpenTest(_RetailTest):
    FACTORY_TUNABLES = {'is_open': Tunable(description='\n            If enabled, the test will pass if the current lot is a retail lot and is open.\n            If disabled, the test will pass if the current lot is a retail lot and is closed.\n            ',
                  tunable_type=bool,
                  default=True)}

    def _run_test(self, retail_manager, tooltip=None):
        if retail_manager.is_open != self.is_open:
            return TestResult(False, "Retail lot open/close status doesn't match what the test asked for.", tooltip=tooltip)
        return TestResult.TRUE


class RetailMarkupTest(_RetailTest):
    FACTORY_TUNABLES = {'markup_multiplier':Tunable(description='\n            If the current multiplier matches this tuned multiplier, the test\n            will pass.\n            ',
       tunable_type=float,
       default=1), 
     'negate':Tunable(description='\n            Will negate the result of the test. e.g. if the current markup is\n            not equal the test will pass\n            ',
       tunable_type=bool,
       default=False)}

    def _run_test(self, retail_manager, tooltip=None):
        current_markup = retail_manager.markup_multiplier
        if not almost_equal(current_markup, self.markup_multiplier):
            return self.negate or TestResult(False, "Current retail markup [{}] doesn't match the tested markup [{}].", current_markup, (self.markup_multiplier), tooltip=tooltip)
        else:
            if self.negate:
                return TestResult(False, 'Current retail markup [{}] matches the tested markup but is negated [{}].', current_markup, (self.markup_multiplier), tooltip=tooltip)
        return TestResult.TRUE


class RetailTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'retail_test': TunableVariant(description='\n            Tests to check various things about the current retail lot.\n            ',
                      retail_open_test=(RetailOpenTest.TunableFactory()),
                      retail_markup_test=(RetailMarkupTest.TunableFactory()))}

    def get_expected_args(self):
        return {}

    def __call__(self):
        return self.retail_test(tooltip=(self.tooltip))