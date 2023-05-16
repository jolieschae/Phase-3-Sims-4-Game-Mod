# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\autonomy\autonomy_mixer_provider_scoring.py
# Compiled at: 2016-09-09 12:46:11
# Size of source mod 2**32: 4326 bytes
from _collections import defaultdict
import sims4.random, random

class _MixerProviderScoring:

    def __init__(self, gsi_enabled_at_start=False):
        self._postive_scoring_mixer_providers = {}
        self._zero_scoring_mixer_providers = {}
        self._invalid_mixer_provider_to_mixer_group = defaultdict(set)
        self.gsi_mixer_provider_data = None if not gsi_enabled_at_start else {}

    def is_valid(self):
        return self._postive_scoring_mixer_providers or self._zero_scoring_mixer_providers

    def add_mixer_provider(self, provider_score, mixer_provider, gsi_mixer_provider_data):
        if provider_score > 0:
            self._postive_scoring_mixer_providers[mixer_provider] = provider_score
        else:
            self._zero_scoring_mixer_providers[mixer_provider] = provider_score
        if self.gsi_mixer_provider_data is not None:
            self.gsi_mixer_provider_data[mixer_provider] = gsi_mixer_provider_data

    def get_mixer_provider(self):
        if self._postive_scoring_mixer_providers:
            return sims4.random.weighted_random_item([(mixer_provider_score, mixer_provider) for mixer_provider, mixer_provider_score in self._postive_scoring_mixer_providers.items()])
        if self._zero_scoring_mixer_providers:
            mixer_provider = random.choice(list(self._zero_scoring_mixer_providers.keys()))
            return mixer_provider
        return

    def remove_invalid_mixer_provider(self, invalid_mixer_provider):
        self._postive_scoring_mixer_providers.pop(invalid_mixer_provider, None)
        self._zero_scoring_mixer_providers.pop(invalid_mixer_provider, None)

    def is_mixer_group_valid(self, mixer_provider, mixer_interaction_group):
        if mixer_provider not in self._invalid_mixer_provider_to_mixer_group:
            return True
        if mixer_interaction_group not in self._invalid_mixer_provider_to_mixer_group[mixer_provider]:
            return True
        return False

    def invalidate_group_for_mixer_provider(self, mixer_provider, mixer_interaction_group):
        self._invalid_mixer_provider_to_mixer_group[mixer_provider].add(mixer_interaction_group)

    def add_mixer_provider_mixer_result_to_gsi(self, mixer_provider, mixer_interaction_group, gsi_reason, run_gen_call_count):
        if self.gsi_mixer_provider_data is not None:
            self.gsi_mixer_provider_data[mixer_provider].mixer_interaction_group_scoring_detail.append((mixer_interaction_group,
             gsi_reason,
             run_gen_call_count))