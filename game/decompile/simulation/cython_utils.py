# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\cython_utils.py
# Compiled at: 2021-02-23 16:06:48
# Size of source mod 2**32: 644 bytes
import cython, sims4.log
from postures.posture_specs import cython_log
from sims4.log import Logger
logger = Logger('CythonUtils')
if cython.compiled:
    cython_log.always('CYTHON cython_utils is imported!', color=(sims4.log.LEVEL_WARN))
else:
    cython_log.always('Pure Python cython_utils is imported!', color=(sims4.log.LEVEL_WARN))
if not cython.compiled:
    from cython_utils_ph import *