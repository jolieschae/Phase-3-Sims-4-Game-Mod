# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\modular\modular_object_component.py
# Compiled at: 2021-01-14 13:40:08
# Size of source mod 2**32: 2751 bytes
from objects.components import Component, types
from protocolbuffers import SimObjectAttributes_pb2 as protocols

class ModularObjectComponent(Component, component_name=types.MODULAR_OBJECT_COMPONENT, persistence_key=protocols.PersistenceMaster.PersistableData.ModularObjectComponent):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._piece_ids = None
        self._piece_provided_affordances = None

    def track_modular_piece_ids(self, piece_ids):
        self._piece_ids = tuple(piece_ids)

    @property
    def modular_piece_ids(self):
        if self._piece_ids:
            return self._piece_ids
        return ()

    def set_piece_provided_affordances(self, affordances):
        self._piece_provided_affordances = affordances

    @property
    def piece_provided_affordances(self):
        if self._piece_provided_affordances:
            return self._piece_provided_affordances
        return ()

    def component_super_affordances_gen(self, **kwargs):
        yield from self._piece_provided_affordances
        if False:
            yield None

    def save(self, persistence_master_message):
        if not self._piece_ids:
            return
        persistable_data = protocols.PersistenceMaster.PersistableData()
        persistable_data.type = protocols.PersistenceMaster.PersistableData.ModularObjectComponent
        modular_object_component_data = persistable_data.Extensions[protocols.PersistableModularObjectComponent.persistable_data]
        modular_object_component_data.piece_ids.extend(self._piece_ids)
        persistence_master_message.data.extend([persistable_data])

    def load(self, persistable_data):
        modular_object_component_data = persistable_data.Extensions[protocols.PersistableModularObjectComponent.persistable_data]
        self._piece_ids = []
        for piece_id in modular_object_component_data.piece_ids:
            self._piece_ids.append(piece_id)