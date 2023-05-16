# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\career_event_zone_requirement.py
# Compiled at: 2021-05-06 14:00:00
# Size of source mod 2**32: 10624 bytes
from sims4.random import weighted_random_item
from sims4.tuning.tunable import AutoFactoryInit, TunableLotDescription, TunableVariant, HasTunableSingletonFactory, TunableReference, TunableList, TunableTuple, Tunable, TunableRange, TunableHouseDescription, OptionalTunable
import build_buy, services, sims4.log, sims4.resources
from world import get_lot_id_from_instance_id
logger = sims4.log.Logger('CareerEventZone')

class RequiredCareerEventZoneTunableVariant(TunableVariant):
    __slots__ = ()

    def __init__(self, **kwargs):
        (super().__init__)(any=RequiredCareerEventZoneAny.TunableFactory(), 
         home_zone=RequiredCareerEventZoneHome.TunableFactory(), 
         lot_description=RequiredCareerEventZoneLotDescription.TunableFactory(), 
         random_lot=RequiredCareerEventZoneRandom.TunableFactory(), 
         career_customer_lot=RequiredCareerEventZoneCustomerLot.TunableFactory(), 
         default='any', **kwargs)


class RequiredCareerEventZone(HasTunableSingletonFactory, AutoFactoryInit):

    def get_required_zone_id(self, sim_info):
        raise NotImplementedError

    def is_zone_id_valid(self, zone_id):
        return self.get_required_zone_id() == zone_id


class RequiredCareerEventZoneAny(RequiredCareerEventZone):

    def get_required_zone_id(self, sim_info):
        pass

    def is_zone_id_valid(self, zone_id):
        return True


class RequiredCareerEventZoneHome(RequiredCareerEventZone):

    def get_required_zone_id(self, sim_info):
        return sim_info.household.home_zone_id


class RequiredCareerEventZoneLotDescription(RequiredCareerEventZone):
    FACTORY_TUNABLES = {'lot_description':TunableLotDescription(description='\n            Lot description of required zone.\n            '), 
     'house_description':OptionalTunable(description='\n            If tuned, this house description will be used for this career event.\n            For example, for the acting career loads into the same lot but different\n            houses (studio sets). \n            ',
       tunable=TunableHouseDescription(description='\n                House description used for this career event.\n                '))}

    def get_required_zone_id(self, sim_info):
        lot_id = get_lot_id_from_instance_id(self.lot_description)
        if self.house_description is not None:
            for zone_proto in services.get_persistence_service().zone_proto_buffs_gen():
                if zone_proto.lot_description_id == self.lot_description:
                    zone_proto.pending_house_desc_id = self.house_description
                    break

        zone_id = services.get_persistence_service().resolve_lot_id_into_zone_id(lot_id, ignore_neighborhood_id=True)
        return zone_id


class RequiredCareerEventZoneCustomerLot(RequiredCareerEventZone):
    FACTORY_TUNABLES = {'career': TunableReference(description="\n            The career used to look up the client's lot.\n            ",
                 manager=(services.get_instance_manager(sims4.resources.Types.CAREER)))}

    def get_required_zone_id(self, sim_info):
        career = sim_info.careers.get(self.career.guid64, None)
        if career is None:
            logger.error("Trying to get the Customer's Lot but the Sim ({}) doesn't have the Career ({}).", sim_info, self.career)
            return 0
        customer_lot_id = career.get_customer_lot_id()
        if not customer_lot_id:
            logger.error("Trying to get the Customer's Lot but the Career ({}) doesn't have a Customer Lot ID. Sim {}", self.career, sim_info)
            return 0
        return customer_lot_id


class ZoneTestNpc(HasTunableSingletonFactory):

    def is_valid_zone(self, zone_proto):
        household = services.household_manager().get(zone_proto.household_id)
        return household is not None and not household.is_player_household


class ZoneTestActivePlayer(HasTunableSingletonFactory):

    def is_valid_zone(self, zone_proto):
        return zone_proto.household_id == services.active_household_id()


class ZoneTestOwnedByHousehold(HasTunableSingletonFactory):

    def is_valid_zone(self, zone_proto):
        return zone_proto.household_id != 0


class ZoneTestActiveZone(HasTunableSingletonFactory):

    def is_valid_zone(self, zone_proto):
        return zone_proto.zone_id == services.current_zone_id()


class ZoneTestIsPlex(HasTunableSingletonFactory):

    def is_valid_zone(self, zone_proto):
        return services.get_plex_service().is_zone_a_plex(zone_proto.zone_id)


class ZoneTestVenueType(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'venues': TunableList(description='\n            If the venue is in this list, the test passes.\n            ',
                 tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.VENUE)),
                 pack_safe=True))}

    def is_valid_zone(self, zone_proto):
        venue_tuning_id = build_buy.get_current_venue(zone_proto.zone_id)
        return venue_tuning_id in (venue.guid64 for venue in self.venues)


class RequiredCareerEventZoneRandom(RequiredCareerEventZone):
    FORBIDDEN = 'FORBIDDEN'
    FACTORY_TUNABLES = {'random_weight_terms': TunableList(description='\n            A list of tests to use and the weights to add for each test.\n            By default, zones start with a weight of 1.0 and this can be\n            increased through these tests.\n            ',
                              tunable=TunableTuple(test=TunableVariant(belongs_to_active_player=(ZoneTestActivePlayer.TunableFactory()),
                              is_owned_by_any_household=(ZoneTestOwnedByHousehold.TunableFactory()),
                              is_npc_household=(ZoneTestNpc.TunableFactory()),
                              venue_type=(ZoneTestVenueType.TunableFactory()),
                              is_active_zone=(ZoneTestActiveZone.TunableFactory()),
                              is_plex=(ZoneTestIsPlex.TunableFactory()),
                              default='venue_type'),
                              weight=TunableVariant(add_weight=TunableRange(description='\n                        The amount of extra weight to add to the probability of zones\n                        that pass this test.\n                        ',
                              tunable_type=float,
                              default=1.0,
                              minimum=0.0),
                              locked_args={'forbid': FORBIDDEN},
                              default='add_weight'),
                              negate=Tunable(description='\n                    If checked, extra weight will be applied to zones that do NOT\n                    pass this test, instead of zones that do pass.\n                    ',
                              tunable_type=bool,
                              default=False)))}

    def _get_random_weight(self, zone_proto):
        weight = 1.0
        for random_weight_term in self.random_weight_terms:
            if random_weight_term.negate ^ random_weight_term.test.is_valid_zone(zone_proto):
                if random_weight_term.weight == self.FORBIDDEN:
                    return 0.0
                weight += random_weight_term.weight

        return weight

    def get_required_zone_id(self, sim_info):
        zone_ids = [(self._get_random_weight(zone_proto), zone_proto.zone_id) for zone_proto in services.get_persistence_service().zone_proto_buffs_gen()]
        zone_reservation_service = services.get_zone_reservation_service()
        zone_ids = [(x, zone_id) for x, zone_id in zone_ids if not zone_reservation_service.is_reserved(zone_id)]
        zone_id = weighted_random_item(zone_ids)
        if zone_id is None:
            logger.warn('Failed to find any zones that were not forbidden for career event travel with terms: {}', (self.random_weight_terms),
              owner='bhill')
            return
        return zone_id