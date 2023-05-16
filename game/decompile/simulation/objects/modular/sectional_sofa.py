# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\modular\sectional_sofa.py
# Compiled at: 2021-04-20 17:48:15
# Size of source mod 2**32: 6346 bytes
from _sims4_collections import frozendict
import itertools, services, sims4.log, zone_types
from objects.game_object import GameObject
from objects.modular.modular_object_component import ModularObjectComponent
from objects.parts.part_data import PartAdjacency
from sims4.tuning.instances import lock_instance_tunables
logger = sims4.log.Logger('Sectional Sofa', default_owner='jdimailig')

class SectionalSofa(GameObject):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._parts = []
        self._sofa_pieces = []
        self._parts_moved = False
        self.add_component(ModularObjectComponent(self))

    def set_modular_pieces(self, piece_ids, from_load=False):
        obj_mgr = services.object_manager()
        pieces = []
        for piece_id in piece_ids:
            piece = obj_mgr.get(piece_id)
            if piece is None:
                logger.error('Invalid piece id, object not found {}', piece_id, owner='jdimailig')
                return
            piece.clear_adjacencies()
            pieces.append(piece)

        with services.posture_graph_service().object_moving(self):
            self._parts_moved = False
            prev_piece = None
            for piece in pieces:
                if prev_piece is not None:
                    piece.add_adjacency(prev_piece, PartAdjacency.LEFT)
                    prev_piece.add_adjacency(piece, PartAdjacency.RIGHT)
                prev_piece = piece

            self._sofa_pieces = []
            for obj_piece_idx, piece in enumerate(pieces):
                first_index = pieces.index(piece)
                loop_end_piece = False
                if first_index != obj_piece_idx:
                    if first_index > 0 or obj_piece_idx < len(pieces) - 1:
                        logger.error('Repeating pieces can only exist at both ends of the piece listbut {} exists at indices {} and {}', piece, first_index, obj_piece_idx)
                        self.clear_modular_pieces()
                        return
                    loop_end_piece = True
                if not loop_end_piece:
                    self._sofa_pieces.append(piece)
                    self._parts.extend(piece.generate_parts(self, obj_piece_idx))

        self.modular_object_component.track_modular_piece_ids(piece_ids)
        piece_provided_affordances = frozenset((itertools.chain)(*(part.provided_super_affordances for part in self._parts)))
        self.modular_object_component.set_piece_provided_affordances(piece_provided_affordances)

    def clear_modular_pieces(self):
        self._parts.clear()
        self._sofa_pieces.clear()
        self.modular_object_component.track_modular_piece_ids(())
        self.modular_object_component.set_piece_provided_affordances(None)

    def get_bounding_box(self):
        p = self.transform.translation
        p = sims4.math.Vector2(p.x, p.z)
        return sims4.geometry.QtRect(p + sims4.math.Vector2(-0.5, -0.5), p + sims4.math.Vector2(0.5, 0.5))

    @property
    def sofa_pieces(self):
        return tuple(self._sofa_pieces)

    def try_mark_as_new_object(self):
        pass

    def on_buildbuy_exit(self):
        super().on_buildbuy_exit()
        if self._parts_moved:
            with services.posture_graph_service().object_moving(self):
                self._parts_moved = False

    def load_object(self, object_data, **kwargs):
        (super().load_object)(object_data, **kwargs)
        services.current_zone().register_callback(zone_types.ZoneState.OBJECTS_LOADED, self._on_all_zone_objects_loaded_callback)

    def _on_all_zone_objects_loaded_callback(self):
        if self.modular_object_component:
            self.set_modular_pieces((self.modular_object_component.modular_piece_ids), from_load=True)


lock_instance_tunables(SectionalSofa, _part_data=(tuple()),
  _part_data_map=(frozendict()))