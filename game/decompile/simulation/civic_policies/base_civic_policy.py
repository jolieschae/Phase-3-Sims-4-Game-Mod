# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\civic_policies\base_civic_policy.py
# Compiled at: 2020-01-10 12:02:38
# Size of source mod 2**32: 4603 bytes
import random
from sims4.tuning.tunable import TunableInterval, TunableReference
import sims4
from display_snippet_tuning import DisplaySnippet
from distributor.rollback import ProtocolBufferRollback
import services

class BaseCivicPolicy(DisplaySnippet):
    INSTANCE_TUNABLES = {'vote_count_statistic':TunableReference(description='\n            The statistic keeping a vote count for this policy.  If not enacted,\n            votes in this statistic would be counting toward an enactment vote. If\n            enacted, votes would be counting toward a repeal vote.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC)), 
     'initial_vote_random_range':TunableInterval(description='\n            Range within which to randomize an initial vote count for this policy at\n            the start of the voting period.  Only used if the policy is balloted.\n            ',
       tunable_type=int,
       default_lower=0,
       default_upper=1,
       minimum=0), 
     'daily_vote_random_range':TunableInterval(description='\n            Range within which to randomize a daily vote count addition for this policy at\n            the start of each day during the voting period.  Only used if the policy is balloted.\n            ',
       tunable_type=int,
       default_lower=0,
       default_upper=1,
       minimum=0)}

    def __init__(self, provider):
        self._provider = provider
        self._enacted = False

    def finalize_startup(self):
        pass

    def get_initial_vote_count(self):
        return random.Random().randint(self.initial_vote_random_range.lower_bound, self.initial_vote_random_range.upper_bound)

    def get_daily_vote_count(self):
        return random.Random().randint(self.daily_vote_random_range.lower_bound, self.daily_vote_random_range.upper_bound)

    @property
    def provider(self):
        return self._provider

    @property
    def enacted(self):
        return self._enacted

    def enact(self):
        self._enacted = True

    def repeal(self):
        self._enacted = False

    def save(self, provider_data):
        if self.enacted:
            with ProtocolBufferRollback(provider_data.policy_data) as (policy_data):
                policy_data.policy_id = self.guid64

    def load(self, policy_data):
        if policy_data is not None:
            if policy_data.policy_id == self.guid64:
                if not policy_data.custom_data:
                    self._enacted = True