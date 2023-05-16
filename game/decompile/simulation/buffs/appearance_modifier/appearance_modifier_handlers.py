# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\buffs\appearance_modifier\appearance_modifier_handlers.py
# Compiled at: 2020-07-13 21:28:25
# Size of source mod 2**32: 2685 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
appearance_modifier_schema = GsiGridSchema(label='Appearance Modifiers', sim_specific=True)
appearance_modifier_schema.add_field('sim_id', label='simID', type=(GsiFieldVisualizers.INT), hidden=True)
appearance_modifier_schema.add_field('request_type', label='Request Type', width=2)
appearance_modifier_schema.add_field('source', label='Source', width=2)
appearance_modifier_schema.add_field('priority', label='Priority', width=2)
appearance_modifier_schema.add_field('apply_to_all_outfits', label='Apply To All Outfits', width=2)
with appearance_modifier_schema.add_has_many('Breakdown', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('appearance_modifier', label='Appearance Modifier', width=2)
    sub_schema.add_field('is_permanent', label='Is Permanent', width=2)
    sub_schema.add_field('chosen_modifier', label='Chosen Modifier', width=2)
archiver = GameplayArchiver('appearance_modifier', appearance_modifier_schema)

def add_appearance_modifier_data(sim_info, appearance_modifiers, priority, apply_to_all_outfits, source, chosen_modifier):
    entry = {}
    entry['sim_id'] = sim_info.id
    entry['request_type'] = 'Add Appearance Modifier'
    entry['source'] = str(source)
    entry['priority'] = str(priority)
    entry['apply_to_all_outfits'] = apply_to_all_outfits
    modifiers = []
    for modifier in appearance_modifiers:
        modifiers.append({'appearance_modifier':str(modifier),  'is_permanent':modifier.is_permanent_modification, 
         'chosen_modifier':str(chosen_modifier is modifier)})

    entry['Breakdown'] = modifiers
    archiver.archive(data=entry, object_id=(sim_info.id))


def remove_appearance_modifier_data(sim_info, appearance_modifiers, source):
    entry = {}
    entry['sim_id'] = sim_info.id
    entry['request_type'] = 'Remove All Appearance Modifiers'
    entry['source'] = str(source)
    modifiers = []
    for modifier in appearance_modifiers:
        modifiers.append({'appearance_modifier': str(modifier)})

    entry['Breakdown'] = modifiers
    archiver.archive(data=entry, object_id=(sim_info.id))