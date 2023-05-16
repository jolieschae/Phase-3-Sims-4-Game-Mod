# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\global_policies\global_policy_enums.py
# Compiled at: 2019-01-16 20:35:04
# Size of source mod 2**32: 440 bytes
import enum

class GlobalPolicyProgressEnum(enum.Int):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    COMPLETE = 2


class GlobalPolicyTokenType(enum.Int):
    NAME = 0
    PROGRESS = 1