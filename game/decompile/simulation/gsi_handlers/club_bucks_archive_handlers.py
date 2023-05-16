# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\club_bucks_archive_handlers.py
# Compiled at: 2015-08-12 16:45:21
# Size of source mod 2**32: 1068 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema
club_bucks_archive_schema = GsiGridSchema(label='Club Bucks Archive', sim_specific=False)
club_bucks_archive_schema.add_field('club_id', label='Club ID', hidden=False)
club_bucks_archive_schema.add_field('amount', label='Amount', hidden=False)
club_bucks_archive_schema.add_field('reason', label='Reason', hidden=False)
archiver = GameplayArchiver('club_bucks_archive', club_bucks_archive_schema, add_to_archive_enable_functions=True)

def is_archive_enabled():
    return archiver.enabled


def archive_club_bucks_reward(club_id, amount, reason):
    archive_data = {'club_id':club_id, 
     'amount':amount, 
     'reason':reason}
    archiver.archive(archive_data)