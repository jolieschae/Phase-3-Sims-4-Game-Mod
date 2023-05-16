# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\test_based_score_threshold.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 2660 bytes
from event_testing.resolver import RESOLVER_PARTICIPANT
from event_testing.results import TestResult
from interactions import ParticipantType
from sims4.math import Operator
from sims4.tuning.tunable import TunableSingletonFactory, TunableThreshold, TunableEnumEntry, TunableReference
import event_testing.test_base, services, sims4.log
logger = sims4.log.Logger('Tests')

class TestBasedScoreThresholdTest(event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'description':'Gate availability by a statistic on the actor or target.', 
     'who':TunableEnumEntry(ParticipantType, ParticipantType.Actor, description='Who or what to apply this test to.'), 
     'test_based_score':TunableReference(manager=services.get_instance_manager(sims4.resources.Types.TEST_BASED_SCORE), description='The specific cumulative test.  This is pack safe because this particular test was being used for module tuning, so be careful that you are not referencing from one pack to the next.', pack_safe=True), 
     'threshold':TunableThreshold(description="The threshold to control availability based on the statistic's value")}

    def __init__(self, who, test_based_score, threshold, **kwargs):
        (super().__init__)(safe_to_skip=True, **kwargs)
        self.who = who
        self.test_based_score = test_based_score
        self.threshold = threshold

    def get_expected_args(self):
        return {'resolver': RESOLVER_PARTICIPANT}

    def __call__(self, resolver=None):
        if self.test_based_score is None:
            return TestResult(False, 'Failed, no test_based_score provided.')
        else:
            operator_symbol = self.test_based_score.passes_threshold(resolver, self.threshold) or Operator.from_function(self.threshold.comparison).symbol
            return TestResult(False, 'Failed {}. Operator: {}. Threshold: {}', (self.test_based_score.__name__),
              operator_symbol, (self.threshold),
              tooltip=(self.tooltip))
        return TestResult.TRUE


TunableTestBasedScoreThresholdTest = TunableSingletonFactory.create_auto_factory(TestBasedScoreThresholdTest)