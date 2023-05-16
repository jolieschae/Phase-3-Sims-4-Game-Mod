# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\uninstantiated_zone.py
# Compiled at: 2014-09-25 14:25:13
# Size of source mod 2**32: 1633 bytes
from world.lot import Lot
import services

class UninstantiatedZone:

    def __init__(self, zone_id):
        self.id = zone_id
        self.neighborhood_id = 0
        self.lot = Lot(zone_id)

    @property
    def is_instantiated(self):
        return False

    def _get_zone_proto(self):
        return services.get_persistence_service().get_zone_proto_buff(self.id)

    def save_zone(self, save_slot_data=None):
        zone_data_msg = self._get_zone_proto()
        self.lot.save((zone_data_msg.gameplay_zone_data), is_instantiated=False)

    def load(self):
        zone_data_msg = self._get_zone_proto()
        self.neighborhood_id = zone_data_msg.neighborhood_id
        self.lot.load(zone_data_msg.gameplay_zone_data)