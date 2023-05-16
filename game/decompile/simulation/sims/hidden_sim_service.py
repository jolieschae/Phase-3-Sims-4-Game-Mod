# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\hidden_sim_service.py
# Compiled at: 2019-08-01 13:20:45
# Size of source mod 2**32: 5244 bytes
from protocolbuffers import GameplaySaveData_pb2
from distributor.rollback import ProtocolBufferRollback
from sims4.service_manager import Service
from sims4.utils import classproperty
import persistence_error_types, services, sims4
logger = sims4.log.Logger('Hidden Sim Service', default_owner='skorman')

class HiddenSimService(Service):

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_HIDDEN_SIM_SERVICE

    def __init__(self):
        self._hidden_sim_ids_dict = {}

    def is_hidden(self, sim_id):
        return sim_id in self._hidden_sim_ids_dict

    def default_away_action(self, sim_id):
        return self._hidden_sim_ids_dict.get(sim_id)

    def hide_sim(self, sim_id, default_away_action=None):
        if sim_id in self._hidden_sim_ids_dict:
            logger.error('Attempted to hide sim {}, who is already hidden.', sim_id)
            return
        else:
            self._hidden_sim_ids_dict.update({sim_id: default_away_action})
            sim_info = services.sim_info_manager().get(sim_id)
            if sim_info is None:
                logger.error('Could not get the sim_info when attempting to hide sim {}. Maybe it was culled?', sim_id)
            if default_away_action is not None and sim_info.away_action_tracker is not None:
                sim_info.away_action_tracker.create_and_apply_away_action(default_away_action)
        client = services.client_manager().get_client_by_household_id(sim_info._household_id)
        if client is not None:
            client.selectable_sims.notify_dirty()

    def unhide_sim(self, sim_id):
        if not self.is_hidden(sim_id):
            logger.error('Attempted to unhide sim {}, who is already unhidden.', sim_id)
            return
        self._hidden_sim_ids_dict.pop(sim_id)
        sim_info = services.sim_info_manager().get(sim_id)
        if sim_info is None:
            return
        client = services.client_manager().get_client_by_household_id(sim_info._household_id)
        if client is not None:
            client.selectable_sims.notify_dirty()
        if sim_info.away_action_tracker is not None:
            sim_info.away_action_tracker.stop()

    def save(self, save_slot_data=None, **kwargs):
        hidden_sim_service_proto = GameplaySaveData_pb2.PersistableHiddenSimService()
        for sim_id, away_action in self._hidden_sim_ids_dict.items():
            with ProtocolBufferRollback(hidden_sim_service_proto.hidden_sim_data) as (entry):
                entry.sim_id = sim_id
                if away_action is not None:
                    entry.away_action = away_action.guid64

        save_slot_data.gameplay_data.hidden_sim_service = hidden_sim_service_proto

    def load(self, **_):
        save_slot_data = services.get_persistence_service().get_save_slot_proto_buff()
        for entry in save_slot_data.gameplay_data.hidden_sim_service.hidden_sim_data:
            away_action = services.get_instance_manager(sims4.resources.Types.AWAY_ACTION).get(entry.away_action)
            self._hidden_sim_ids_dict.update({entry.sim_id: away_action})