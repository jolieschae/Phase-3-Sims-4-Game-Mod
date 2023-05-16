# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\autonomy\autonomy_modifier_enums.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 838 bytes
import enum

class SuperAffordanceSuppression(enum.Int):
    AUTONOMOUS_ONLY = 0
    USER_DIRECTED = 1
    USE_AFFORDANCE_COMPATIBILITY_AND_WHITELIST = 2


class SuppressionCheckOption(enum.Int, export=False):
    AFFORDANCE_ONLY = 0
    PROVIDED_AFFORDANCE_ONLY = 1
    AFFORDANCE_AND_PROVIDED_AFFORDANCE = 2