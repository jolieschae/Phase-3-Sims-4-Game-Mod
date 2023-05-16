# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\restaurants\restaurant_host_log_handler.py
# Compiled at: 2016-02-23 20:05:32
# Size of source mod 2**32: 926 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema
import services, sims4.log
logger = sims4.log.Logger('GSI')
restaurant_host_schema = GsiGridSchema(label='Restaurant Host Log')
restaurant_host_schema.add_field('game_time', label='Game Time', width=2)
restaurant_host_schema.add_field('action', label='Action', width=2)
restaurant_host_schema.add_field('result', label='Result', width=2)
host_archiver = GameplayArchiver('hostActions', restaurant_host_schema, add_to_archive_enable_functions=True)

def log_host_action(action, result):
    archive_data = {'action':action, 
     'result':result}
    host_archiver.archive(data=archive_data)