# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\gardening\gardening_component_shoot.py
# Compiled at: 2018-02-01 17:40:39
# Size of source mod 2**32: 804 bytes
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from objects.gardening.gardening_component import _GardeningComponent
import objects.components.types

class GardeningShootComponent(_GardeningComponent, component_name=objects.components.types.GARDENING_COMPONENT, persistence_key=protocols.PersistenceMaster.PersistableData.GardeningComponent):

    @property
    def is_shoot(self):
        return True