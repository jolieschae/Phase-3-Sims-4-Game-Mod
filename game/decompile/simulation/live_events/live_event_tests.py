# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\live_events\live_event_tests.py
# Compiled at: 2021-11-22 21:29:05
# Size of source mod 2**32: 2578 bytes
from live_events.live_event_service import LiveEventState, LiveEventName
from event_testing.results import TestResult
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, Tunable, TunableEnumEntry
import event_testing.test_base, services

class LiveEventStateTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'live_event_name':TunableEnumEntry(description='\n            The name of the live event we are checking.\n            ',
       tunable_type=LiveEventName,
       default=LiveEventName.DEFAULT,
       invalid_enums=(
      LiveEventName.DEFAULT,)), 
     'state':TunableEnumEntry(description='\n            If the live event is in this state, this test passes.\n            ',
       tunable_type=LiveEventState,
       default=LiveEventState.ACTIVE), 
     'negate':Tunable(description='\n            If checked then the result of the test will be negated.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {}

    def __call__(self, *args, **kwargs):
        live_event_service = services.get_live_event_service()
        if live_event_service is None:
            return TestResult(False, 'There is no active Live Event service.',
              tooltip=(self.tooltip))
        live_event_state = live_event_service.get_live_event_state(self.live_event_name)
        if live_event_state != self.state:
            if self.negate:
                return TestResult.TRUE
            return TestResult(False, 'The live event {} is in {} state, not {}.',
              (self.live_event_name.name),
              live_event_state,
              (self.state),
              tooltip=(self.tooltip))
        if self.negate:
            return TestResult(False, 'The live event {} is in {} state, but this test is negated.',
              (self.live_event_name.name),
              live_event_state,
              tooltip=(self.tooltip))
        return TestResult.TRUE