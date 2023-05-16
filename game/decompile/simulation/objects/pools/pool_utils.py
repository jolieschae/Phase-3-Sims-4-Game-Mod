# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\pools\pool_utils.py
# Compiled at: 2021-02-02 19:19:39
# Size of source mod 2**32: 832 bytes
from _weakrefset import WeakSet
import services, sims4.log, sims4.reload
logger = sims4.log.Logger('Pool Utils', default_owner='skorman')
with sims4.reload.protected(globals()):
    cached_pool_objects = WeakSet()
POOL_LANDING_SURFACE = 'Water'

def get_main_pool_objects_gen():
    yield from cached_pool_objects
    if False:
        yield None


def get_pool_by_block_id(block_id):
    for pool in get_main_pool_objects_gen():
        if pool.block_id == block_id:
            return pool

    logger.error('No Pool Matching block Id: {}', block_id, owner='camilogarcia')