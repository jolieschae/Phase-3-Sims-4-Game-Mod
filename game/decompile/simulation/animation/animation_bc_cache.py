# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\animation_bc_cache.py
# Compiled at: 2020-10-21 17:14:18
# Size of source mod 2**32: 4787 bytes
import pickle
from sims4.common import get_available_packs
import sims4.log, sims4.resources
from singletons import DEFAULT
logger = sims4.log.Logger('ACCBCC')
BC_CACHE_FILENAME = 'bc_pickle_cache'
BC_CACHE_PY_UNOPT_FILENAME = 'bc_pickle_cache_py_unopt'
BC_FILENAME_EXTENSION = '.bch'
BC_CACHE_VERSION = b'version#0002'
_wrong_bc_cache_version = False
TEST_LOCAL_CACHE = False

def read_bc_cache_from_resource(available_packs=DEFAULT):
    global _wrong_bc_cache_version
    if _wrong_bc_cache_version:
        return {}
    key_name = None
    key_name = BC_CACHE_FILENAME
    bc_cache_combined = {}
    if available_packs is DEFAULT:
        available_packs = get_available_packs()
    logger.info('Available packs: {}', available_packs)
    if TEST_LOCAL_CACHE:
        file_name = None
        file_name = 'C:\\tmp\\ac_bc_cache\\bc_pickle_cache'
        for pack in available_packs:
            pack_name = str(pack).replace('Pack.', '')
            pack_file = file_name + '_' + pack_name + BC_FILENAME_EXTENSION
            logger.always('Loading BC cache file {}.'.format(pack_file))
            with open(pack_file, 'rb') as (bc_cache_file):
                try:
                    resource_version = bc_cache_file.read(len(BC_CACHE_VERSION))
                    ret = pickle.load(bc_cache_file)
                    logger.always('Loaded BC cache with {} entries.', len(ret))
                    bc_cache_combined.update(ret)
                except pickle.UnpicklingError as exc:
                    try:
                        logger.exception('Unpickling the Boundary Condition cache failed. Startup will be slower as a consequence.', exc=exc,
                          level=(sims4.log.LEVEL_WARN))
                    finally:
                        exc = None
                        del exc

        return bc_cache_combined
    for pack in available_packs:
        pack_name = str(pack).replace('Pack.', '')
        pack_key = key_name + '_' + pack_name
        key = sims4.resources.Key.hash64(pack_key, sims4.resources.Types.BC_CACHE)
        loader = sims4.resources.ResourceLoader(key)
        bc_cache_file = loader.load()
        logger.info('Loading BC cache {} (key: {}) as file {}.', pack_key, key, bc_cache_file)
        if not bc_cache_file:
            logger.debug('Failed to load boundary condition cache file from the resource loader (key = {})', pack_key)
            continue
        resource_version = bc_cache_file.read(len(BC_CACHE_VERSION))
        if resource_version != BC_CACHE_VERSION:
            _wrong_bc_cache_version = True
            logger.warn('The Boundary Condition cache in the resource manager is from a different version. Current version is {}, resource manager version is {}.\nStartup will be slower until the versions are aligned.', BC_CACHE_VERSION, resource_version)
            return {}
        try:
            bc_cache_combined.update(pickle.load(bc_cache_file))
        except pickle.UnpicklingError as exc:
            try:
                logger.exception('Unpickling the Boundary Condition cache failed. Startup will be slower as a consequence.', exc=exc,
                  level=(sims4.log.LEVEL_WARN))
                return {}
            finally:
                exc = None
                del exc

    return bc_cache_combined