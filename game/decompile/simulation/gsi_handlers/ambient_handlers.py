# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\ambient_handlers.py
# Compiled at: 2016-10-19 20:36:30
# Size of source mod 2**32: 798 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema
ambient_archive_schema = GsiGridSchema(label='Situations/Ambient Log')
ambient_archive_schema.add_field('sources', label='Sources')
ambient_archive_schema.add_field('created_situation', label='Created Situation')
archiver = GameplayArchiver('ambient', ambient_archive_schema)

def archive_ambient_data(description, created_situation=''):
    entry = {}
    entry['sources'] = description
    entry['created_situation'] = created_situation
    archiver.archive(data=entry)