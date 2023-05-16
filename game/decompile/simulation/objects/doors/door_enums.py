# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\doors\door_enums.py
# Compiled at: 2019-08-06 17:30:11
# Size of source mod 2**32: 285 bytes
import enum

class VenueFrontdoorRequirement(enum.Int):
    NEVER = 0
    ALWAYS = 1
    OWNED_OR_RENTED = 2