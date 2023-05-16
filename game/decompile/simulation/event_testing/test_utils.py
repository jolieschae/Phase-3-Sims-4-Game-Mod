# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\test_utils.py
# Compiled at: 2017-06-08 14:18:00
# Size of source mod 2**32: 641 bytes
from sims.sim_info_tests import SimInfoTest
import caches, sims.sim_info_types

@caches.cached
def get_disallowed_ages(affordance):
    disallowed_ages = set()
    for test in affordance.test_globals:
        if isinstance(test, SimInfoTest):
            if test.ages is None:
                continue
            for age in sims.sim_info_types.Age:
                if age not in test.ages:
                    disallowed_ages.add(age)

    return disallowed_ages