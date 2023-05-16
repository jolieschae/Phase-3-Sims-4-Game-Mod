# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\narrative\narrative_tests.py
# Compiled at: 2021-05-14 15:10:06
# Size of source mod 2**32: 3746 bytes
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from event_testing.test_events import TestEvent
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableVariant
from tunable_utils.tunable_white_black_list import TunableWhiteBlackList
import services

class _ActiveNarrativeTest(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'narratives': TunableWhiteBlackList(tunable=TunableReference(manager=(services.get_instance_manager(Types.NARRATIVE)),
                     pack_safe=True))}

    def test(self, tooltip):
        if self.narratives.test_collection(services.narrative_service().active_narratives):
            return TestResult.TRUE
        return TestResult(False, 'Failed to pass narrative white/black list.', tooltip=tooltip)


class _LockedNarrativeTest(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'narratives': TunableWhiteBlackList(tunable=TunableReference(manager=(services.get_instance_manager(Types.NARRATIVE)),
                     pack_safe=True))}

    def test(self, tooltip):
        if self.narratives.test_collection(services.narrative_service().locked_narratives):
            return TestResult.TRUE
        return TestResult(False, 'Failed to pass narrative white/black list.', tooltip=tooltip)


class _CompletedNarrativeTest(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'narratives': TunableWhiteBlackList(tunable=TunableReference(manager=(services.get_instance_manager(Types.NARRATIVE)),
                     pack_safe=True))}

    def test(self, tooltip):
        if self.narratives.test_collection(services.narrative_service().completed_narratives):
            return TestResult.TRUE
        return TestResult(False, 'Failed to pass narrative white/black list.', tooltip=tooltip)


class NarrativeTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'test_type': TunableVariant(description='\n            The type of test to run.\n            ',
                    active_narrative_test=(_ActiveNarrativeTest.TunableFactory()),
                    completed_narrative_test=(_CompletedNarrativeTest.TunableFactory()),
                    locked_narrative_test=(_LockedNarrativeTest.TunableFactory()),
                    default='active_narrative_test')}

    def get_expected_args(self):
        return {}

    def get_custom_event_registration_keys(self):
        keys = []
        narratives_to_register = self.test_type.narratives.get_items()
        for narrative in narratives_to_register:
            keys.append((TestEvent.NarrativesUpdated, narrative))

        return keys

    def __call__(self):
        return self.test_type.test(self.tooltip)