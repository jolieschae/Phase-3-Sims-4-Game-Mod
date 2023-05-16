# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\services\prom_service.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 19225 bytes
import alarms, enum, persistence_error_types, services, sims4
from date_and_time import create_time_span
from interactions import ParticipantType
from protocolbuffers import GameplaySaveData_pb2
from event_testing.resolver import DoubleSimResolver, SingleSimResolver
from relationships.relationship_bit import RelationshipBit
from relationships.relationship_tests import TunableRelationshipTest
from sims.sim_info_types import SimZoneSpinUpAction
from sims4.common import Pack
from sims4.service_manager import Service
from sims4.tuning.tunable import TunableList, TunableReference, TunablePackSafeReference, TunableTuple, OptionalTunable, TunableEnumEntry
from sims4.utils import classproperty
from tunable_time import TunableTimeSpan
logger = sims4.log.Logger('PromService', default_owner='skorman')

class PromRelationshipBitType(enum.Int):
    INVITED = 1
    SKIP_PROM_PACT = 2


class PromRelationshipBit(RelationshipBit):
    INSTANCE_TUNABLES = {'bit_type': TunableEnumEntry(description='\n            The type of prom rel bit. This will determine the effects that will be applied to the sim when the \n            prom situatioin starts.\n            ',
                   tunable_type=PromRelationshipBitType,
                   default=(PromRelationshipBitType.INVITED))}

    def on_add_to_relationship(self, sim, target_sim_info, relationship, from_load):
        super().on_add_to_relationship(sim, target_sim_info, relationship, from_load)
        prom_service = services.get_prom_service()
        if prom_service is None:
            return
        elif self.bit_type == PromRelationshipBitType.INVITED:
            prom_service.add_prom_teen_attendee_ids({sim.sim_id, target_sim_info.id})
        else:
            if self.bit_type == PromRelationshipBitType.SKIP_PROM_PACT:
                prom_service.add_skip_prom_pact_teen_ids({sim.sim_id, target_sim_info.id})

    def on_remove_from_relationship(self, sim, target_sim_info):
        super().on_remove_from_relationship(sim, target_sim_info)
        prom_service = services.get_prom_service()
        if prom_service is None:
            return
        elif self.bit_type == PromRelationshipBitType.INVITED:
            prom_service.remove_prom_teen_attendee_ids({sim.sim_id, target_sim_info.id})
        else:
            if self.bit_type == PromRelationshipBitType.SKIP_PROM_PACT:
                prom_service.remove_skip_prom_pact_teen_ids({sim.sim_id, target_sim_info.id})


class PromService(Service):
    PROM_PACT_FULFILLED_LOOTS = TunableList(description='\n        A list of loot actions to apply if the prom pact between two sims is \n        fulfilled (prom was canceled or neither sim attended). \n        ',
      tunable=TunableReference(description='\n            Loot action to apply if the pact is fulfilled. \n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
      class_restrictions=('LootActions', ),
      pack_safe=True))
    PROM_PACT_BROKEN_LOOTS = TunableList(description='\n        A list of loot actions to apply if the prom pact between two sims is \n        broken (one of the sims attended prom). Subject is the pact breaker,\n        target is the other sim in the pact.\n        ',
      tunable=TunableReference(description='\n            Loot action to apply if the pact is broken. \n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
      class_restrictions=('LootActions', ),
      pack_safe=True))
    TEEN_LOOTS_ON_PROM_TIME = TunableList(description='\n        A list of loot actions to apply to played teens when it is time for prom, \n        regardless if prom happens or not.\n        ',
      tunable=TunableTuple(target_relationship_test=OptionalTunable(description='\n                If enabled, only sims that pass this relationship test will be considered\n                for this loot. Sims that do not pass the test will not have loots applied\n                to them.\n                ',
      tunable=TunableRelationshipTest(description='\n                    The relationship test sims will have to pass to be considered for this loot.\n                    ',
      locked_args={'subject':ParticipantType.Actor, 
     'target_sim':ParticipantType.TargetSim})),
      loots=TunablePackSafeReference(description='\n                A list of loot actions to apply to the teen and the target (if enabled).\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
      class_restrictions=('LootActions', ))))
    PROM_SUBVENUE = TunablePackSafeReference(description='\n        A reference to the prom subvenue type.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.VENUE)))
    RESTORE_VENUE_DELAY = TunableTimeSpan(description='\n        A delay in minutes to restore the venue when the situation ends.\n        ',
      default_minutes=1)
    PROM_CLEANUP_ALARM_DELAY = 1

    def __init__(self):
        self._prom_teen_attendee_ids = None
        self._skip_prom_pact_sim_ids = None
        self._cleanup_prom_alarm_handle = None
        self._prom_zone_id = None

    @classproperty
    def required_packs(cls):
        return (Pack.EP12,)

    def add_skip_prom_pact_teen_ids(self, sim_ids):
        if self._skip_prom_pact_sim_ids is None:
            self._skip_prom_pact_sim_ids = set()
        self._skip_prom_pact_sim_ids |= sim_ids

    def remove_skip_prom_pact_teen_ids(self, sim_ids):
        if self._skip_prom_pact_sim_ids is not None:
            self._skip_prom_pact_sim_ids -= sim_ids

    def get_prom_pact_sim_ids(self):
        if self._skip_prom_pact_sim_ids is None:
            return set()
        return self._skip_prom_pact_sim_ids

    def add_prom_teen_attendee_ids(self, attendee_ids):
        if self._prom_teen_attendee_ids is None:
            self._prom_teen_attendee_ids = set()
        self._prom_teen_attendee_ids |= attendee_ids

    def remove_prom_teen_attendee_ids(self, attendee_ids):
        if self._prom_teen_attendee_ids is not None:
            self._prom_teen_attendee_ids -= attendee_ids

    def handle_time_for_prom(self):
        sims_to_check = set(services.active_household())
        active_household = services.active_household()
        while sims_to_check:
            sim_info = sims_to_check.pop()
            if not sim_info.is_teen:
                continue
            sim_relationship_tracker = sim_info.relationship_tracker
            for loot_data in self.TEEN_LOOTS_ON_PROM_TIME:
                if loot_data.loots is None:
                    continue
                if loot_data.target_relationship_test is None:
                    resolver = SingleSimResolver(sim_info)
                    loot_data.loots.apply_to_resolver(resolver)
                else:
                    for target_info in sim_relationship_tracker.get_target_sim_infos():
                        if target_info not in sims_to_check:
                            if target_info in active_household:
                                continue
                        resolver = DoubleSimResolver(sim_info, target_info)
                        relationship_match = resolver(loot_data.target_relationship_test)
                        if not relationship_match:
                            continue
                        loot_data.loots.apply_to_resolver(resolver)

    def on_pact_fulfilled(self, sim_id, target_id):
        sim_info_manager = services.sim_info_manager()
        sim_info = sim_info_manager.get(sim_id)
        target_sim_info = sim_info_manager.get(target_id)
        resolver = DoubleSimResolver(sim_info, target_sim_info)
        for loot in self.PROM_PACT_FULFILLED_LOOTS:
            loot.apply_to_resolver(resolver)

    def on_sim_added_to_prom(self, sim):
        if not services.current_zone().is_zone_running:
            if sim.is_npc:
                services.sim_info_manager().schedule_sim_spin_up_action((sim.sim_info), (SimZoneSpinUpAction.PREROLL), can_override=True)
        if self._skip_prom_pact_sim_ids is None or sim.id not in self._skip_prom_pact_sim_ids:
            return
        sim_info = sim.sim_info
        sim_info_manager = services.sim_info_manager()
        sim_relationship_tracker = sim_info.relationship_tracker
        relationship_bits = services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT).get_ordered_types(only_subclasses_of=PromRelationshipBit)
        pact_bits = [bit for bit in relationship_bits if bit.bit_type == PromRelationshipBitType.SKIP_PROM_PACT]
        skipping_prom_teens = self.get_prom_pact_sim_ids().copy()
        for target_id in skipping_prom_teens:
            if sim.id == target_id:
                continue
            if sim_relationship_tracker.has_bits(target_id, pact_bits):
                target_sim_info = sim_info_manager.get(target_id)
                resolver = DoubleSimResolver(sim_info, target_sim_info)
                for loot in self.PROM_PACT_BROKEN_LOOTS:
                    loot.apply_to_resolver(resolver)

                sim_relationship_tracker.remove_relationship_bits(target_id, pact_bits)

    def get_prom_teen_attendee_ids(self):
        if self._prom_teen_attendee_ids is None:
            return set()
        return self._prom_teen_attendee_ids

    def on_prom_situation_created(self, situation_type, zone_id):
        self._cleanup_prom_alarm_handle = alarms.add_alarm(self, create_time_span(minutes=(situation_type.duration + self.PROM_CLEANUP_ALARM_DELAY)),
          (lambda _: self.cleanup_prom()),
          cross_zone=True)
        if self._prom_zone_id is not None:
            logger.error('Attempting to start a new prom situation while an existing one has not fully shutdown.')
            return
        services.venue_game_service().change_venue_type(zone_id, self.PROM_SUBVENUE)
        self._prom_zone_id = zone_id

    @property
    def cleanup_scheduled(self):
        return self._cleanup_prom_alarm_handle is not None

    def remove_relbits_from_sims(self, relbits, sim_ids, apply_loots=False):
        relationship_service = services.relationship_service()
        sim_ids_copy = sim_ids.copy()
        while sim_ids_copy:
            sim_id = sim_ids_copy.pop()
            for rel_bit in relbits:
                for target_id in sim_ids_copy:
                    if relationship_service.has_bit(sim_id, target_id, rel_bit):
                        relationship_service.remove_relationship_bit(sim_id, target_id, rel_bit)
                        if apply_loots:
                            self.on_pact_fulfilled(sim_id, target_id)

    def cleanup_prom(self):
        if self._cleanup_prom_alarm_handle is not None:
            alarms.cancel_alarm(self._cleanup_prom_alarm_handle)
            self._cleanup_prom_alarm_handle = None
        if self._prom_zone_id is not None:
            services.venue_game_service().restore_venue_type(self._prom_zone_id, self.RESTORE_VENUE_DELAY())
            self._prom_zone_id = None
        relationship_bits = services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT).get_ordered_types(only_subclasses_of=PromRelationshipBit)
        skip_prom_relbits, prom_invite_relbits = [], []
        for rel_bit in relationship_bits:
            if rel_bit.bit_type == PromRelationshipBitType.SKIP_PROM_PACT:
                skip_prom_relbits.append(rel_bit)
            else:
                prom_invite_relbits.append(rel_bit)

        self.remove_relbits_from_sims(skip_prom_relbits, self.get_prom_pact_sim_ids(), True)
        self.remove_relbits_from_sims(prom_invite_relbits, self.get_prom_teen_attendee_ids())
        self._skip_prom_pact_sim_ids = None
        self._prom_teen_attendee_ids = None

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_PROM_SERVICE

    def save(self, object_list=None, zone_data=None, open_street_data=None, save_slot_data=None):
        prom_service_data = GameplaySaveData_pb2.PersistablePromService()
        if self._cleanup_prom_alarm_handle is not None:
            cleanup_prom_alarm_time = int(self._cleanup_prom_alarm_handle.get_remaining_time().in_minutes())
            prom_service_data.cleanup_prom_alarm_time = cleanup_prom_alarm_time
        if self._prom_teen_attendee_ids is not None:
            prom_service_data.prom_attendee_ids.extend(self._prom_teen_attendee_ids)
        if self._skip_prom_pact_sim_ids is not None:
            prom_service_data.skipping_prom_ids.extend(self._skip_prom_pact_sim_ids)
        if self._prom_zone_id is not None:
            prom_service_data.prom_zone_id = self._prom_zone_id
        save_slot_data.gameplay_data.prom_service = prom_service_data

    def on_all_households_and_sim_infos_loaded(self, client):
        save_slot_data_msg = services.get_persistence_service().get_save_slot_proto_buff()
        prom_service_data = save_slot_data_msg.gameplay_data.prom_service
        prom_attendee_ids = prom_service_data.prom_attendee_ids
        if prom_attendee_ids is not None:
            self._prom_teen_attendee_ids = set(prom_attendee_ids)
        skip_prom_pact_ids = prom_service_data.skipping_prom_ids
        if skip_prom_pact_ids is not None:
            self._skip_prom_pact_sim_ids = set(skip_prom_pact_ids)
        if prom_service_data.HasField('cleanup_prom_alarm_time'):
            self._cleanup_prom_alarm_handle = alarms.add_alarm(self, create_time_span(minutes=(prom_service_data.cleanup_prom_alarm_time)),
              (lambda _: self.cleanup_prom()),
              cross_zone=True)
        if prom_service_data.HasField('prom_zone_id'):
            self._prom_zone_id = prom_service_data.prom_zone_id