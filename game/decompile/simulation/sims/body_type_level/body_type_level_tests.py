# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\body_type_level\body_type_level_tests.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 3696 bytes
import sims4
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from interactions import ParticipantTypeSingleSim
from sims.body_type_level.body_type_level_commodity import BODY_TYPE_TO_LEVEL_COMMODITY
from sims.outfits.outfit_enums import BodyType
from sims4.math import Threshold, Operator
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableOperator

class PreferredBodyTypeLevelTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n            The sim to test.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'body_type':TunableEnumEntry(description='\n            The body type to test against.\n            ',
       tunable_type=BodyType,
       default=BodyType.NONE,
       invalid_enums=(
      BodyType.NONE,)), 
     'preferred_value_comparison':TunableOperator(description='\n            The current level of the BodyType will be compared to the \n            preferred level via this operator (current level OPERATOR \n            preferred level).\n            ',
       default=sims4.math.Operator.EQUAL)}

    def get_expected_args(self):
        return {'subject': self.subject}

    def __call__(self, subject=None):
        subject = next(iter(subject))
        if subject is None:
            return TestResult(False, 'Subject not found. Check participant type {}.',
              (self.subject),
              tooltip=(self.tooltip))
            if self.body_type not in BODY_TYPE_TO_LEVEL_COMMODITY:
                return TestResult(False, 'BodyType {} does not have an associated BodyTypeLevelCommodity.',
                  (self.body_type),
                  tooltip=(self.tooltip))
            commodity_type = BODY_TYPE_TO_LEVEL_COMMODITY[self.body_type]
            commodity = subject.get_statistic(commodity_type)
            if commodity is None:
                return TestResult(False, 'Sim does not have BodyType commodity {}.',
                  commodity_type,
                  tooltip=(self.tooltip))
            current_is_preferred = subject.base.is_preferred_growth_part(self.body_type)
            operator = Operator.from_function(self.preferred_value_comparison)
            if current_is_preferred:
                if operator in (Operator.EQUAL, Operator.LESS_OR_EQUAL, Operator.GREATER_OR_EQUAL):
                    return TestResult.TRUE
        elif operator == Operator.NOTEQUAL:
            return TestResult.TRUE
        preferred_level = subject.base.get_preferred_growth_level(self.body_type)
        current_level = commodity.get_level()
        threshold = Threshold(preferred_level, self.preferred_value_comparison)
        if threshold.compare(current_level):
            return TestResult.TRUE
        return TestResult(False, 'Failed comparison test.', tooltip=(self.tooltip))