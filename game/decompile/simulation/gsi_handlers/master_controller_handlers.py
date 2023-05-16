# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\master_controller_handlers.py
# Compiled at: 2015-01-27 20:10:34
# Size of source mod 2**32: 1456 bytes
from sims4.gsi.schema import GsiGridSchema
from gsi_handlers.gameplay_archiver import GameplayArchiver
mc_archive_schema = GsiGridSchema(label='Master Controller Log')
mc_archive_schema.add_field('sims_with_active_work', label='Sims With Active Work Start', width=2)
mc_archive_schema.add_field('sims_with_active_work_after', label='Sims With Work After', width=2)
mc_archive_schema.add_field('last_time_stamp', label='Time Stamp At Start', width=2)
mc_archive_schema.add_field('last_time_stamp_end', label='Time Stamp At End', width=2)
with mc_archive_schema.add_has_many('Log', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('tag', label='Tag', width=0.25)
    sub_schema.add_field('sim', label='Sim', width=0.15)
    sub_schema.add_field('log', label='log')
with mc_archive_schema.add_has_many('active_work_start', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('sim', label='ID', width=0.2)
    sub_schema.add_field('work_entry', label='Work')
with mc_archive_schema.add_has_many('active_work_end', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('sim', label='ID', width=0.2)
    sub_schema.add_field('work_entry', label='Work')
archiver = GameplayArchiver('master_controller', mc_archive_schema)

def archive_master_controller_entry(entry):
    archiver.archive(data=entry)