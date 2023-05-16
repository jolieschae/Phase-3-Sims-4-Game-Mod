# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\fame\fame_tests.py
# Compiled at: 2020-11-12 10:43:19
# Size of source mod 2**32: 2806 bytes
from event_testing.resolver import RESOLVER_PARTICIPANT
from event_testing.results import TestResult
from caches import cached_test
from interactions import ParticipantType
from sims4.tuning.tunable import TunableEnumEntry, Tunable, HasTunableSingletonFactory, AutoFactoryInit
import event_testing.test_base

class LifestyleBrandTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n            The subject to check for an active Lifestyle Brand.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'negate':Tunable(description='\n            If checked then this test will return True when the subject does\n            not have an active lifestyle brand.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'subjects': self.subject}

    @cached_test
    def __call__(self, subjects):
        for subject in subjects:
            lifestyle_brand_tracker = subject.lifestyle_brand_tracker
            if lifestyle_brand_tracker is None:
                return TestResult(False, "Subject ({}) doesn't have a lifestyle brand tracker.", subject, tooltip=(self.tooltip))
                if lifestyle_brand_tracker.active == self.negate:
                    return TestResult(False, "Subject ({}) doesn't have an active lifestyle brand", subject, tooltip=(self.tooltip))

        return TestResult.TRUE


class FameMomentTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'negate': Tunable(description='\n            If checked then this test will return True when the current\n            interaction does not have a scheduled fame moment.\n            ',
                 tunable_type=bool,
                 default=False)}

    def get_expected_args(self):
        return {'resolver': RESOLVER_PARTICIPANT}

    def __call__(self, resolver):
        interaction = resolver.interaction
        if interaction is None:
            return False
        return interaction.fame_moment_active != self.negate