# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\unlock_tracker_tests.py
# Compiled at: 2021-06-03 19:14:34
# Size of source mod 2**32: 6561 bytes
from event_testing.results import TestResult, TestResultNumeric
from event_testing.test_events import TestEvent
from caches import cached_test
from interactions import ParticipantType
from sims.unlock_tracker import TunableUnlockVariant
from sims4.tuning.tunable import TunableFactory, TunableEnumEntry, Tunable, TunableThreshold, HasTunableSingletonFactory, AutoFactoryInit, TunableEnumWithFilter
from sims4.tuning.tunable_base import EnumBinaryExportType
from tag import Tag
import event_testing.test_base, sims4.tuning.tunable
logger = sims4.log.Logger('Unlock Tracker Tests')

class UnlockTrackerTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):

    @TunableFactory.factory_option
    def participant_type_override(participant_type_enum, participant_type_default):
        return {'subject': TunableEnumEntry(description='\n                    Who or what to apply this test to\n                    ',
                      tunable_type=participant_type_enum,
                      default=participant_type_default)}

    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n            Who or what to apply this test to\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'unlock_item':TunableUnlockVariant(description='\n            The unlock item that Sim has or not.\n            '), 
     'invert':Tunable(description='\n            If checked, test will pass if any subject does NOT have the unlock.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'test_targets': self.subject}

    @cached_test
    def __call__(self, test_targets=()):
        reason = 'There are no targets to test!' if not test_targets else None
        for target in test_targets:
            if not target.is_sim:
                reason = 'Cannot test unlock on non-Sim object {} as subject {}.'.format(target, self.subject)
                continue
            if not target.unlock_tracker is None:
                if not target.unlock_tracker.is_unlocked(self.unlock_item):
                    reason = "Sim {} hasn't unlocked {}.".format(target, self.unlock_item)
                    continue
                return self.invert or TestResult.TRUE

        if self.invert:
            if test_targets:
                if reason is None:
                    reason = 'No subjects have {} locked'.format(self.unlock_item)
                else:
                    return TestResult.TRUE
        return TestResult(False, reason, tooltip=(self.tooltip))


class UnlockTrackerAmountTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    test_events = (
     TestEvent.UnlockTrackerItemUnlocked,)
    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n            Who or what to apply this test to\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'test_tag':TunableEnumWithFilter(description='\n            This test will look how many items with this tag have been unlocked.\n            ',
       tunable_type=Tag,
       filter_prefixes=('recipe', 'spell'),
       default=Tag.INVALID,
       invalid_enums=(
      Tag.INVALID,),
       pack_safe=True,
       binary_type=EnumBinaryExportType.EnumUint32), 
     'threshold':TunableThreshold(description='\n            The required number of specified things required to pass the test.\n            ')}

    def get_expected_args(self):
        return {'test_targets': self.subject}

    @cached_test
    def __call__(self, test_targets=()):
        for target in test_targets:
            if not target.is_sim:
                return TestResult(False, 'Cannot test unlock on none_sim object {} as subject {}.',
                  target,
                  (self.subject),
                  tooltip=(self.tooltip))
                if target.unlock_tracker is None:
                    return TestResult(False, 'Sim {} does not have an unlock tracker.', target, tooltip=(self.tooltip))
                number_unlocked = target.unlock_tracker.get_number_unlocked(self.test_tag)
                return self.threshold.compare(number_unlocked) or TestResultNumeric(False, "Sim {} hasn't unlocked the required amount of {}.",
                  target,
                  (self.test_tag),
                  current_value=number_unlocked,
                  goal_value=(self.threshold.value),
                  tooltip=(self.tooltip))

        return TestResult.TRUE

    def goal_value(self):
        return self.threshold.value