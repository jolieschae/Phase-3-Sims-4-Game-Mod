# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\services\relgraph_service.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 5730 bytes
from cas import cas
from sims4 import protocol_buffer_utils
from sims4.service_manager import Service
import services

class RelgraphService(Service):
    RELGRAPH_ENABLED = False

    @classmethod
    def get_relgraph_service(cls):
        if cls.RELGRAPH_ENABLED:
            return RelgraphService()
        return

    @classmethod
    def is_relgraph_initialized(cls):
        if cls.RELGRAPH_ENABLED:
            save_slot_data_msg = services.get_persistence_service().get_save_slot_proto_buff()
            relgraph_service_data = save_slot_data_msg.gameplay_data.relgraph_service
            return protocol_buffer_utils.has_field(relgraph_service_data, 'relgraph_data')
        return False

    def save(self, save_slot_data, **kwargs):
        if self.RELGRAPH_ENABLED:
            save_slot_data.gameplay_data.relgraph_service.relgraph_data = self.relgraph_get()

    def load(self, **_):
        if self.RELGRAPH_ENABLED:
            save_slot_data_msg = services.get_persistence_service().get_save_slot_proto_buff()
            relgraph_service_data = save_slot_data_msg.gameplay_data.relgraph_service
            if protocol_buffer_utils.has_field(relgraph_service_data, 'relgraph_data'):
                self.relgraph_set(relgraph_service_data.relgraph_data)

    @classmethod
    def relgraph_set_edge(cls, sim_id, target_sim_id, relationship_type):
        if cls.RELGRAPH_ENABLED:
            cas.relgraph_set_edge(sim_id, target_sim_id, relationship_type)

    @classmethod
    def relgraph_get_genealogy(cls, sim_id):
        if cls.RELGRAPH_ENABLED:
            cas.relgraph_get_genealogy(sim_id)

    @classmethod
    def relgraph_set_marriage(cls, sim_id, spouse_sim_id, is_married):
        if cls.RELGRAPH_ENABLED:
            cas.relgraph_set_marriage(sim_id, spouse_sim_id, is_married)

    @classmethod
    def relgraph_set_engagement(cls, sim_id, fiance_sim_id, is_engaged):
        if cls.RELGRAPH_ENABLED:
            cas.relgraph_set_engagement(sim_id, fiance_sim_id, is_engaged)

    @classmethod
    def relgraph_add_child(cls, parent_a_id, parent_b_id, child_sim_id):
        if cls.RELGRAPH_ENABLED:
            cas.relgraph_add_child(parent_a_id, parent_b_id, child_sim_id)

    @classmethod
    def relgraph_get(cls):
        if cls.RELGRAPH_ENABLED:
            return cas.relgraph_get()

    @classmethod
    def relgraph_set(cls, relgraph_data):
        if cls.RELGRAPH_ENABLED:
            cas.relgraph_set(relgraph_data)

    @classmethod
    def relgraph_cull(cls, sim_id_list, cull_threshold=None):
        if cls.RELGRAPH_ENABLED:
            if cull_threshold is None:
                cas.relgraph_cull(sim_id_list)
            else:
                cas.relgraph_cull(sim_id_list, cull_threshold)