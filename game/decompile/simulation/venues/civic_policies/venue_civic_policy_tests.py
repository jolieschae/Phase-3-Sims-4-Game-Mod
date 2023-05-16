# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\civic_policies\venue_civic_policy_tests.py
# Compiled at: 2020-01-30 16:00:00
# Size of source mod 2**32: 2272 bytes
from civic_policies.base_civic_policy_tests import BaseCivicPolicyTest
import services
from sims4.tuning.tunable import TunableVariant
from zone_tests import ActiveZone, PickInfoZone, PickedZoneIds, ParticipantHomeZone

class VenueCivicPolicyTest(BaseCivicPolicyTest):
    FACTORY_TUNABLES = {'venue': TunableVariant(description="\n            Select the zone's venue to test by specifying a Zone Source.\n            ",
                use_current_zone=(ActiveZone.TunableFactory()),
                use_pick_info=(PickInfoZone.TunableFactory()),
                use_picked_zone_ids=(PickedZoneIds.TunableFactory()),
                use_participant_home_zone=(ParticipantHomeZone.TunableFactory()),
                default='use_current_zone')}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)

    def _get_zone_id(self, **kwargs):
        return (self.venue.get_zone_id)(**kwargs)

    def get_expected_args(self):
        return self.venue.get_expected_args()

    def _get_civic_policy_provider(self, *args, **kwargs):
        zone_id = (self._get_zone_id)(**kwargs)
        if zone_id is None:
            return
        venue_game_service = services.venue_game_service()
        if venue_game_service is None:
            return
        return venue_game_service.get_provider(zone_id)

    def get_custom_event_registration_keys(self):
        return ()