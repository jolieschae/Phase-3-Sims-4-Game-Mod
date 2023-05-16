# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\clans\clan_service.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 18553 bytes
import alarms, enum, persistence_error_types, services, sims4.log, sims4.resources
from _collections import defaultdict
from protocolbuffers import GameplaySaveData_pb2, DistributorOps_pb2
from clans.clan_ops import ClanMembershipUpdateOp, ClanUpdateOp
from date_and_time import TimeSpan, sim_ticks_per_day
from distributor.rollback import ProtocolBufferRollback
from distributor.system import Distributor
from event_testing.resolver import SingleSimResolver
from event_testing.test_events import TestEvent
from interactions.utils.loot import LootActions
from math import floor
from sims4.common import Pack
from sims4.service_manager import Service
from sims4.tuning.tunable import TunableMapping, TunableReference, TunableTuple, TunableEnumEntry
from sims4.utils import classproperty
from tunable_time import TunableTimeOfDay
logger = sims4.log.Logger('Clans', default_owner='nsavalani')

class ClanAllianceState(enum.Int):
    ALLIED = ...
    NEUTRAL = ...
    FEUDING = ...


class ClanService(Service):
    CLAN_DATA = TunableMapping(description='\n        A mapping from clan to the different types of loots that need to be applied to clan members for clan\n        related operations.\n        ',
      key_type=TunableReference(description='\n            A reference to a clan for which we are defining a rival clan and the various loots that need to be \n            applied.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.CLAN)),
      pack_safe=True),
      value_type=TunableTuple(information_dialog_loot=LootActions.TunableReference(description='\n                The loot to display clan information in a dialog.\n                ',
      pack_safe=True),
      join_clan_loot=LootActions.TunableReference(description='\n                The loot to apply to a Sim when they join a clan.\n                ',
      pack_safe=True),
      leave_clan_loot=LootActions.TunableReference(description='\n                The loot to apply to a Sim when they leave a clan.\n                ',
      pack_safe=True),
      promote_leader_loot=LootActions.TunableReference(description='\n                The loot to apply to a Sim when they are assigned leader of a clan.\n                ',
      pack_safe=True),
      demote_leader_loot=LootActions.TunableReference(description='\n                The loot to apply to the existing leader of a clan when they are being replaced by another Sim.\n                ',
      pack_safe=True),
      rival_clan=TunableReference(description='\n                A reference to another clan that will be treated as the rival clan for the given key.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.CLAN)),
      pack_safe=True),
      find_new_clan_leader_filter=TunableReference(description='\n                A reference to a sim filter that will be used to find a sim to make into the clan leader if the clan\n                currently has no leader. It is recommended that the sim filter does NOT create a sim from template to\n                prevent bugs where multiple sims could get turned into leaders.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER)),
      pack_safe=True)))
    NARRATIVE_TO_ALLIANCE_STATE_MAP = TunableMapping(description='\n        A mapping of narrative to the clan alliance state it represents. When the clan service detects a narrative\n        change, it will map the active narrative to one of the alliance states and update the UI if needed.\n        ',
      key_type=TunableReference(description='\n            A reference to a narrative for which the clan service will attempt to update the UI.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.NARRATIVE)),
      pack_safe=True),
      value_type=TunableEnumEntry(description='\n            The clan alliance state that the narrative corresponds to.\n            ',
      tunable_type=ClanAllianceState,
      default=(ClanAllianceState.NEUTRAL)))
    LEADER_CHECK_HOUR = TunableTimeOfDay(description='\n        The time of day to check for clans without a leader.\n        ',
      default_hour=4)

    def __init__(self):
        self._clan_guid_to_leader_sim_id_map = {}
        self._clan_guid_to_members_map = defaultdict(set)
        self._current_clan_alliance_state = None
        self._daily_leader_check_handler = None

    @classproperty
    def required_packs(cls):
        return (Pack.GP12,)

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_CLAN_SERVICE

    @property
    def clan_guid_to_leader_sim_id_map(self):
        return self._clan_guid_to_leader_sim_id_map

    @property
    def current_clan_alliance_state(self):
        return self._current_clan_alliance_state

    def add_sim_to_clan(self, sim_info, clan):
        clan_data = self.CLAN_DATA.get(clan)
        if clan_data is not None:
            clan_data.join_clan_loot.apply_to_resolver(SingleSimResolver(sim_info))
        self._clan_guid_to_members_map[clan.guid64].add(sim_info.id)
        clan_membership_update_op = ClanMembershipUpdateOp(DistributorOps_pb2.ClanMembershipUpdate.ADD, clan.guid64)
        Distributor.instance().add_op(sim_info, clan_membership_update_op)

    def remove_sim_from_clan(self, sim_info, clan):
        if self.is_clan_leader(sim_info, clan):
            self.remove_clan_leader(clan)
        clan_data = self.CLAN_DATA.get(clan)
        if clan_data is not None:
            clan_data.leave_clan_loot.apply_to_resolver(SingleSimResolver(sim_info))
        self._clan_guid_to_members_map[clan.guid64].remove(sim_info.id)
        clan_membership_update_op = ClanMembershipUpdateOp(DistributorOps_pb2.ClanMembershipUpdate.REMOVE, clan.guid64)
        Distributor.instance().add_op(sim_info, clan_membership_update_op)

    def reassign_clan_leader(self, sim_info, clan):
        clan_guid = clan.guid64
        clan_data = self.CLAN_DATA.get(clan)
        self.remove_clan_leader(clan, distribute_update=False)
        self._clan_guid_to_leader_sim_id_map[clan_guid] = sim_info.id
        if clan_data is not None:
            clan_data.promote_leader_loot.apply_to_resolver(SingleSimResolver(sim_info))
        self._send_clan_update_message()

    def remove_clan_leader(self, clan, distribute_update=True):
        clan_guid = clan.guid64
        clan_data = self.CLAN_DATA.get(clan)
        existing_leader_sim_id = self._clan_guid_to_leader_sim_id_map.get(clan_guid)
        if existing_leader_sim_id is None:
            return
        existing_leader_sim_info = services.sim_info_manager().get(existing_leader_sim_id)
        if existing_leader_sim_info is None:
            logger.error('Attempting to remove clan leader with Sim Id {} for Clan {}, but the clan leader sim info is None.', existing_leader_sim_id, clan_guid)
        if clan_data is not None:
            if existing_leader_sim_info is not None:
                clan_data.demote_leader_loot.apply_to_resolver(SingleSimResolver(existing_leader_sim_info))
        self._clan_guid_to_leader_sim_id_map.pop(clan_guid, None)
        if distribute_update:
            self._send_clan_update_message()

    def show_clan_information(self, clan, active_sim_info):
        clan_data = self.CLAN_DATA.get(clan)
        if clan_data is not None:
            clan_data.information_dialog_loot.apply_to_resolver(SingleSimResolver(active_sim_info))

    def is_clan_leader(self, sim_info, clan):
        leader_sim_id = self._clan_guid_to_leader_sim_id_map.get(clan.guid64)
        return leader_sim_id is not None and leader_sim_id == sim_info.id

    def has_clan_leader(self, clan):
        leader_exists = False
        leader_sim_id = self._clan_guid_to_leader_sim_id_map.get(clan.guid64)
        if leader_sim_id is not None:
            sim_info_manager = services.sim_info_manager()
            leader_exists = sim_info_manager.get(leader_sim_id) is not None
            if not leader_exists:
                logger.error('Leader Id {} exists in Clan to Leader Id map but Leader Sim Info is None.', leader_sim_id)
        return leader_exists

    def get_clan_leader(self, sim_info):
        clan_instance_manager = services.get_instance_manager(sims4.resources.Types.CLAN)
        sim_info_manager = services.sim_info_manager()
        for clan_guid, leader_sim_id in self._clan_guid_to_leader_sim_id_map.items():
            clan = clan_instance_manager.get(clan_guid)
            if clan is None:
                return
                if sim_info.trait_tracker.has_trait(clan.clan_trait):
                    return sim_info_manager.get(leader_sim_id)

    def start(self):
        for narrative in self.NARRATIVE_TO_ALLIANCE_STATE_MAP.keys():
            services.get_event_manager().register_with_custom_key(self, TestEvent.NarrativesUpdated, narrative)

    def stop(self):
        for narrative in self.NARRATIVE_TO_ALLIANCE_STATE_MAP.keys():
            services.get_event_manager().unregister_with_custom_key(self, TestEvent.NarrativesUpdated, narrative)

    def handle_event(self, sim_info, event, resolver):
        if event == TestEvent.NarrativesUpdated:
            self._update_from_narrative_service()
            return

    def _update_from_narrative_service(self):
        for active_narrative in services.narrative_service().active_narratives:
            clan_alliance_state = self.NARRATIVE_TO_ALLIANCE_STATE_MAP.get(active_narrative)
            if clan_alliance_state is not None and self._current_clan_alliance_state != clan_alliance_state:
                self._current_clan_alliance_state = clan_alliance_state
                self._send_clan_update_message()
                return

    def save(self, save_slot_data=None, **__):
        clan_proto = GameplaySaveData_pb2.PersistableClanService()
        for clan_guid, leader_sim_id in self._clan_guid_to_leader_sim_id_map.items():
            with ProtocolBufferRollback(clan_proto.clan_leaders) as (clan_leaders_msg):
                clan_leaders_msg.clan_guid = clan_guid
                clan_leaders_msg.leader_sim_id = leader_sim_id

        for clan_guid, members in self._clan_guid_to_members_map.items():
            with ProtocolBufferRollback(clan_proto.clan_members) as (clan_members_msg):
                clan_members_msg.clan_guid = clan_guid
                for member_sim_id in members:
                    clan_members_msg.member_sim_ids.append(member_sim_id)

        save_slot_data.gameplay_data.clan_service = clan_proto

    def load(self, **__):
        save_slot_data_msg = services.get_persistence_service().get_save_slot_proto_buff()
        if save_slot_data_msg.gameplay_data.HasField('clan_service'):
            data = save_slot_data_msg.gameplay_data.clan_service
            for clan_leader_data in data.clan_leaders:
                self._clan_guid_to_leader_sim_id_map[clan_leader_data.clan_guid] = clan_leader_data.leader_sim_id

            for clan_member_data in data.clan_members:
                clan_guid = clan_member_data.clan_guid
                for member_id in clan_member_data.member_sim_ids:
                    self._clan_guid_to_members_map[clan_guid].add(member_id)

    def on_zone_load(self):
        sim_info_manager = services.sim_info_manager()
        for clan_guid, members in self._clan_guid_to_members_map.items():
            sim_ids_to_remove = []
            for member_id in members:
                sim_info = sim_info_manager.get(member_id)
                if sim_info is None:
                    sim_ids_to_remove.append(member_id)
                    continue
                clan_membership_update_op = ClanMembershipUpdateOp(DistributorOps_pb2.ClanMembershipUpdate.ADD, clan_guid)
                Distributor.instance().add_op(sim_info, clan_membership_update_op)

            for sim_id in sim_ids_to_remove:
                if sim_id == self._clan_guid_to_leader_sim_id_map.get(clan_guid):
                    self._clan_guid_to_leader_sim_id_map.pop(clan_guid, None)
                members.remove(sim_id)

        self._update_from_narrative_service()
        self._send_clan_update_message()
        if self._daily_leader_check_handler is None:
            sim_now = services.time_service().sim_now
            one_day = TimeSpan(sim_ticks_per_day())
            next_alarm_time = ClanService.LEADER_CHECK_HOUR + one_day * floor(sim_now.absolute_days())
            if sim_now.absolute_ticks() >= next_alarm_time.absolute_ticks():
                next_alarm_time = next_alarm_time + one_day
            self._daily_leader_check_handler = alarms.add_alarm(self, (next_alarm_time - sim_now),
              (self._on_daily_leader_check),
              repeating=True,
              repeating_time_span=one_day,
              cross_zone=True)

    def on_sim_killed_or_culled(self, sim_info):
        clan_instance_manager = services.get_instance_manager(sims4.resources.Types.CLAN)
        for clan_guid, members in self._clan_guid_to_members_map.items():
            clan = clan_instance_manager.get(clan_guid)
            if sim_info.id in members and clan is not None:
                self.remove_sim_from_clan(sim_info, clan)
                break

    def _on_daily_leader_check(self, handle):
        for clan_tuning_data in ClanService.CLAN_DATA:
            clan_guid = clan_tuning_data.guid64
            leader_sim_id = self._clan_guid_to_leader_sim_id_map.get(clan_guid)
            if leader_sim_id is None:
                self.create_clan_leader(clan_tuning_data)

    def create_clan_leader(self, clan):
        clan_data = self.CLAN_DATA.get(clan)
        leader_filter = clan_data.find_new_clan_leader_filter
        if leader_filter is None:
            return
        results = services.sim_filter_service().submit_matching_filter(sim_filter=leader_filter, allow_yielding=False,
          gsi_source_fn=(lambda: f"create_clan_leader - {str(clan_data)}"))
        if len(results) >= 1:
            self.reassign_clan_leader(results[0].sim_info, clan)

    def _send_clan_update_message(self):
        clan_update_op = ClanUpdateOp(self._clan_guid_to_leader_sim_id_map, self._current_clan_alliance_state)
        Distributor.instance().add_op_with_no_owner(clan_update_op)