# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\pool_size_test.py
# Compiled at: 2020-03-05 21:17:59
# Size of source mod 2**32: 2031 bytes
from sims4.tuning.tunable import TunableEnumEntry, HasTunableSingletonFactory, AutoFactoryInit, TunableInterval
from event_testing import test_base
from event_testing.results import TestResult
from interactions import ParticipantType
import build_buy, terrain

class PoolSizeTest(HasTunableSingletonFactory, AutoFactoryInit, test_base.BaseTest):
    FACTORY_TUNABLES = {'target':TunableEnumEntry(description='\n            The target of the test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Object), 
     'allowable_size':TunableInterval(description='\n            The range (inclusive min, exclusive max) of pool sizes for which \n            this test will pass. Pool size is measured in half tiles.\n            ',
       tunable_type=float,
       default_lower=0,
       default_upper=0)}

    def get_expected_args(self):
        return {'targets': self.target}

    def __call__(self, targets):
        for target in targets:
            pool_size = build_buy.get_pool_size_at_location(target.location.world_transform.translation, target.level)
            if pool_size is None:
                if 0.0 < terrain.get_water_depth_at_location(target.location):
                    return TestResult.TRUE
                return TestResult(False, 'PoolSizeTest: Target is not a pool or ocean')
                min_size = self.allowable_size.lower_bound
                max_size = self.allowable_size.upper_bound
                if pool_size < min_size or pool_size >= max_size:
                    return TestResult(False, f"PoolSizeTest: A pool size of {pool_size} is not within the allowable range of {min_size} to {max_size}")

        return TestResult.TRUE