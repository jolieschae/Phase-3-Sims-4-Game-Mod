# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\visualization\sectional_sofa_visualizer.py
# Compiled at: 2020-12-17 19:20:56
# Size of source mod 2**32: 3077 bytes
from collections import defaultdict
import services
from debugvis import Context
from indexed_manager import CallbackTypes
from sims4 import commands
from sims4.color import Color

class SectionalSofaVisualizer:

    def __init__(self, layer, sectional_sofa_id, sectional_sofa_piece_id=0):
        self.layer = layer
        self.sectional_sofa_id = sectional_sofa_id
        self.sectional_sofa_piece_id = sectional_sofa_piece_id
        self._start()

    def _start(self):
        obj_mgr = services.current_zone().object_manager
        sofa = obj_mgr.get(self.sectional_sofa_id)
        obj_mgr.register_callback(CallbackTypes.ON_OBJECT_REMOVE, self._on_object_deleted)
        if sofa is not None:
            self._draw_sofa(sofa)

    def stop(self):
        obj_mgr = services.current_zone().object_manager
        obj_mgr.unregister_callback(CallbackTypes.ON_OBJECT_REMOVE, self._on_object_deleted)

    def _draw_sofa(self, sofa):
        ARROW_LENGTH = 0.75
        with Context(self.layer) as (layer):
            for piece in sofa.sofa_pieces:
                text_colors = {'color_foreground':Color.WHITE,  'color_background':Color.BLUE} if piece.id == self.sectional_sofa_piece_id else {'color_foreground':Color.YELLOW, 
                 'color_background':Color.BLACK}
                (layer.add_text_world)(piece.transform.translation, str(sofa.sofa_pieces.index(piece)), altitude=0.5, **text_colors)
                part_location_dict = defaultdict(set)
                for part in piece.provided_parts:
                    part_location_dict[part.transform].add(part.part_identifier)

                for transform, part_names in part_location_dict.items():
                    layer.add_arrow_for_transform(transform, length=ARROW_LENGTH)
                    layer.add_text_world(transform.translation + transform.orientation.transform_vector(part.forward_direction_for_picking) * ARROW_LENGTH, '\n'.join(part_names))

    def _on_object_deleted(self, obj):
        if self.sectional_sofa_id:
            if obj.id == self.sectional_sofa_id:
                full_command = 'debugvis.sectional_sofas.stop' + ' {}'.format(self.sectional_sofa_id)
                client_id = services.client_manager().get_first_client_id()
                commands.execute(full_command, client_id)