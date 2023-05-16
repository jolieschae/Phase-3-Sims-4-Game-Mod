# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\sectional_sofa_handlers.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 3120 bytes
import services
from objects.modular.sectional_sofa_tuning import SectionalSofaTuning
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
sectional_sofa_schema = GsiGridSchema(label='Sectional Sofa Pieces', auto_refresh=False)
sectional_sofa_schema.add_field('sofaObjId', label='Sofa Object Id', width=1)
sectional_sofa_schema.add_field('objId', label='Object Id', width=1, unique_field=True)
sectional_sofa_schema.add_field('classStr', label='Class', width=1)
sectional_sofa_schema.add_field('definitionStr', label='Definition', width=1)
sectional_sofa_schema.add_field('modelStr', label='Model', width=1)
sectional_sofa_schema.add_field('locationStr', label='Location', width=2)
with sectional_sofa_schema.add_view_cheat('debugvis.sectional_sofas.start', label='Visualize Piece Sofa Grouping') as (cheat):
    cheat.add_token_param('sofaObjId')
    cheat.add_token_param('objId')
sectional_sofa_schema.add_view_cheat('debugvis.sectional_sofas.stop', label='Clear All Visualization')
with sectional_sofa_schema.add_view_cheat('objects.focus_camera_on_object', label='Focus On Selected Object') as (cheat):
    cheat.add_token_param('objId')
with sectional_sofa_schema.add_has_many('Part Data', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('part_identifier', label='Part Name', width=1)
    sub_schema.add_field('part_location', label='Part Location', width=3)
    sub_schema.add_field('adjacent_parts', label='Adjacent Parts', width=2)
    sub_schema.add_field('overlapping_parts', label='Overlapping Parts', width=2)

@GsiHandler('sectional_sofa_pieces', sectional_sofa_schema)
def generate_sectional_sofa_data(*args, **kwargs):
    zone = services.current_zone()
    piece_data = []
    if zone.object_manager is None:
        return piece_data
    for obj in tuple(zone.object_manager.objects):
        if not isinstance(obj, SectionalSofaTuning.SECTIONAL_SOFA_OBJECT_DEF.cls):
            continue
        for piece in obj.sofa_pieces:
            part_data = []
            for part in piece.provided_parts:
                part_info = {}
                part_info['part_identifier'] = part.part_identifier
                part_info['part_location'] = str(part.location)
                part_info['adjacent_parts'] = '\n'.join((part.part_identifier for part in part.adjacent_parts_gen()))
                part_info['overlapping_parts'] = '\n'.join((part.part_identifier for part in part.get_overlapping_parts()))
                part_data.append(part_info)

            piece_data.append({'objId':str(piece.id), 
             'sofaObjId':str(piece._sofa_container.id), 
             'classStr':type(piece).__name__, 
             'definitionStr':piece.definition.name, 
             'modelStr':str(piece.model), 
             'locationStr':str(piece.location), 
             'Part Data':part_data})

    return piece_data