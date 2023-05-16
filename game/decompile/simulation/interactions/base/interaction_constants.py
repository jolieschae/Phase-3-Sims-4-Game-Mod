# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\base\interaction_constants.py
# Compiled at: 2019-02-05 14:05:58
# Size of source mod 2**32: 327 bytes
import enum

class InteractionQueuePreparationStatus(enum.Int, export=False):
    FAILURE = 0
    SUCCESS = 1
    NEEDS_DERAIL = 2
    PUSHED_REPLACEMENT = 3