# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\civic_policies\street_civic_policy_tuning.py
# Compiled at: 2020-04-22 17:39:37
# Size of source mod 2**32: 3706 bytes
from sims4.tuning.tunable import TunableVariant, TunablePackSafeReference, HasTunableSingletonFactory, AutoFactoryInit
from zone_tests import ActiveZone, PickInfoZone, PickedZoneIds, ParticipantHomeZone
from interactions import ParticipantType
import services, sims4
logger = sims4.log.Logger('Street Civic Policy Tuning')

class StreetParticipant(HasTunableSingletonFactory, AutoFactoryInit):

    def get_expected_args(self):
        return {'subjects': ParticipantType.Street}

    def get_street(self, *, subjects):
        street_service = services.street_service()
        if street_service is None:
            return
        if not subjects:
            logger.error('Failed to resolve participant ParticipantType.Street.')
            return
        return street_service.get_street(subjects[0])


class StreetCivicPolicySelectorMixin(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'street': TunableVariant(description='\n            Select what street to test.\n            ',
                 literal=TunablePackSafeReference(description='\n                Identify a specific Street.\n                ',
                 manager=(services.get_instance_manager(sims4.resources.Types.STREET))),
                 via_zone_source=TunableVariant(description='\n                Select the street to use by specifying a Zone Source.\n                ',
                 use_current_zone=(ActiveZone.TunableFactory()),
                 use_pick_info=(PickInfoZone.TunableFactory()),
                 use_picked_zone_ids=(PickedZoneIds.TunableFactory()),
                 use_participant_home_zone=(ParticipantHomeZone.TunableFactory()),
                 default='use_current_zone'),
                 via_street_participant=(StreetParticipant.TunableFactory()),
                 default='literal')}

    def _get_street(self, **kwargs):
        if self.street is None or hasattr(self.street, 'civic_policy'):
            street = self.street
        else:
            if isinstance(self.street, (StreetParticipant,)):
                return (self.street.get_street)(**kwargs)
            zone_id = (self.street.get_zone_id)(**kwargs)
            if zone_id is None:
                return
            from world.street import get_street_instance_from_zone_id
            street = get_street_instance_from_zone_id(zone_id)
        return street

    def _get_civic_policy_provider(self, *args, **kwargs):
        street_service = services.street_service()
        if street_service is None:
            return
        street = (self._get_street)(**kwargs)
        if street is not None:
            return street_service.get_provider(street)