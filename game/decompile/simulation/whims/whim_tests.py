# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\whims\whim_tests.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 2750 bytes
import services, sims4
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from interactions import ParticipantType
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableEnumEntry, TunableSet, TunableReference, Tunable
logger = sims4.log.Logger('WhimTests')

class WhimTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'who':TunableEnumEntry(description='\n            The sim(s) to test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'whims':TunableSet(description='\n            If any of the whims in this list are active on the sim(s), then the test\n            will pass.\n            ',
       tunable=TunableReference(description='\n                A whim, that if active, will cause the test to return True.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.WHIM)),
       pack_safe=True),
       minlength=1), 
     'invert':Tunable(description='\n            If true, will take the output of the test and invert it.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'test_targets': self.who}

    def __call__(self, test_targets=()):
        test_result = TestResult.TRUE
        if len(self.whims) > 0:
            for target in test_targets:
                tracker = target.whim_tracker
                if tracker is None:
                    test_result = TestResult(False, 'Target {} did not have a whim tracker.', target)
                    break
                for whim in self.whims:
                    if tracker.is_whim_active(whim):
                        break
                else:
                    test_result = TestResult(False, 'Target {} did not have any of the supplied whims active.', target)
                    break

        else:
            test_result = TestResult(False, 'Either no whims were added to the test or they were all from packs that are not present.')
        if self.invert:
            if test_result:
                test_result = TestResult(False, 'Initial test result passed, but test is inverted.')
            else:
                test_result = TestResult.TRUE
        return test_result