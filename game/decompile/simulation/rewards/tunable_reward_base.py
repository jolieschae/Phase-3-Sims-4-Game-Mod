# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\rewards\tunable_reward_base.py
# Compiled at: 2020-05-27 18:09:26
# Size of source mod 2**32: 2166 bytes
import sims4, telemetry_helper
from interactions import ParticipantType
from interactions.utils.has_display_text_mixin import HasDisplayTextMixin
from rewards.reward_enums import RewardDestination
from sims4.tuning.tunable import HasTunableFactory
from sims4.utils import constproperty
TELEMETRY_GROUP_UNLOCK = 'UNLK'
TELEMETRY_HOOK_UNLOCK_ITEM = 'ITEM'
TELEMETRY_FIELD_UNLOCK_SOURCE = 'trgr'
TELEMETRY_FIELD_UNLOCK_ITEM = 'itid'
unlock_telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_UNLOCK)

class TunableRewardBase(HasTunableFactory, HasDisplayTextMixin):

    @constproperty
    def reward_type():
        pass

    def open_reward(self, sim_info, reward_destination=RewardDestination.HOUSEHOLD, **kwargs):
        raise NotImplementedError

    def valid_reward(self, sim_info):
        return True

    @classmethod
    def send_unlock_telemetry(cls, sim_info, item_id, reward_source_guid):
        with telemetry_helper.begin_hook(unlock_telemetry_writer, TELEMETRY_HOOK_UNLOCK_ITEM,
          sim_info=sim_info) as (hook):
            hook.write_int(TELEMETRY_FIELD_UNLOCK_SOURCE, reward_source_guid)
            hook.write_int(TELEMETRY_FIELD_UNLOCK_ITEM, item_id)

    def _get_display_text_tokens(self, resolver=None):
        if resolver is None:
            return super()._get_display_text_tokens()
        return resolver.get_participants(participant_type=(ParticipantType.Actor))