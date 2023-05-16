# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\bucks\currency_tests.py
# Compiled at: 2020-11-12 10:43:18
# Size of source mod 2**32: 3354 bytes
import event_testing, sims4
from bucks.bucks_enums import BucksType
from bucks.bucks_utils import BucksUtils
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from event_testing.test_events import TestEvent
from interactions import ParticipantType
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableThreshold, TunableEnumEntry
from caches import cached_test
logger = sims4.log.Logger('CurrencyTests', default_owner='skorman')

class BucksTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    test_events = (
     TestEvent.BucksEarned,)
    USES_EVENT_DATA = True
    FACTORY_TUNABLES = {'bucks_type':TunableEnumEntry(description='\n            Bucks type that will be tested against the value threshold.\n            ',
       tunable_type=BucksType,
       default=BucksType.INVALID), 
     'value_threshold':TunableThreshold(description='\n            Bucks amount required to pass\n            '), 
     'subject':TunableEnumEntry(description='\n            Who or what to test against.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor)}

    def get_expected_args(self):
        return {'test_targets':self.subject, 
         'bucks_data':event_testing.test_constants.FROM_DATA_OBJECT, 
         'objective_guid64':event_testing.test_constants.OBJECTIVE_GUID64}

    @cached_test
    def __call__(self, test_targets=(), bucks_data=None, objective_guid64=None, tooltip=None):
        for target in test_targets:
            current_bucks = 0
            bucks_tracker = BucksUtils.get_tracker_for_bucks_type((self.bucks_type), owner_id=(target.id))
            if objective_guid64 is not None and bucks_data is not None:
                current_bucks = bucks_data.get_bucks_earned(self.bucks_type)
                relative_start_values = bucks_data.get_starting_values(objective_guid64)
                if relative_start_values is not None:
                    current_bucks -= relative_start_values[0]
                else:
                    if bucks_tracker is not None:
                        current_bucks = bucks_tracker.get_bucks_amount_for_type(self.bucks_type)
                return self.value_threshold.compare(current_bucks) or TestResult(False, 'Bucks type {} value does not pass the value threshold.', (self.bucks_type),
                  tooltip=(self.tooltip))

        return TestResult.TRUE

    def save_relative_start_values(self, objective_guid64, bucks_data):
        bucks_data.set_starting_values(objective_guid64, (bucks_data.get_bucks_earned(self.bucks_type),))