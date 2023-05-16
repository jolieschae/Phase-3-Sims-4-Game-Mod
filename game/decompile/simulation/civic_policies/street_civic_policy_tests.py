# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\civic_policies\street_civic_policy_tests.py
# Compiled at: 2020-03-02 20:50:14
# Size of source mod 2**32: 1496 bytes
from civic_policies.base_civic_policy_tests import BaseCivicPolicyTest
import services
from civic_policies.street_civic_policy_tuning import StreetCivicPolicySelectorMixin

class StreetCivicPolicySelectorTestMixin(StreetCivicPolicySelectorMixin):

    def get_expected_args(self):
        if self.street is None or hasattr(self.street, 'civic_policy'):
            return {}
        return self.street.get_expected_args()

    def get_custom_event_registration_keys(self):
        return self.street is None or hasattr(self.street, 'civic_policy') or ()
        keys = []
        for test in self.civic_policy_tests:
            custom_keys = test.get_custom_event_keys(self.street)
            if not custom_keys:
                continue
            keys.extend(custom_keys)

        return keys


class StreetCivicPolicyTest(StreetCivicPolicySelectorTestMixin, BaseCivicPolicyTest):
    pass