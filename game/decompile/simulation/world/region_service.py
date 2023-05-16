# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\region_service.py
# Compiled at: 2020-06-08 16:31:54
# Size of source mod 2**32: 2602 bytes
from distributor.rollback import ProtocolBufferRollback
from protocolbuffers import GameplaySaveData_pb2
from sims4.service_manager import Service
from sims4.utils import classproperty
import persistence_error_types, services, sims4

class RegionService(Service):

    def __init__(self):
        super().__init__()
        self._region_instances = {}

    def get_region_instance_by_tuning(self, region_tuning):
        return self._region_instances.get(region_tuning)

    def save(self, object_list=None, zone_data=None, open_street_data=None, save_slot_data=None):
        service_data = GameplaySaveData_pb2.PersistableRegionService()
        for region_inst in self._region_instances.values():
            with ProtocolBufferRollback(service_data.region_data) as (region_data):
                region_inst.save(region_data)

        save_slot_data.gameplay_data.region_service = service_data

    def load(self, zone_data=None):
        save_slot_data_msg = services.get_persistence_service().get_save_slot_proto_buff()
        service_data = save_slot_data_msg.gameplay_data.region_service
        guid64_to_region = {}
        manager = services.get_instance_manager(sims4.resources.Types.REGION)
        for region_tuning in manager.types.values():
            if not region_tuning.is_persistable:
                continue
            region_inst = region_tuning()
            self._region_instances[region_tuning] = region_inst
            guid64_to_region[region_inst.guid64] = region_inst

        for region_data in service_data.region_data:
            region = guid64_to_region.get(region_data.region_id)
            if region is not None:
                region.load(region_data)

        for region_inst in self._region_instances.values():
            region_inst.on_finalize_load()

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_REGION_SERVICE