# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\buffs\appearance_modifier\appearance_modifier_type.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 365 bytes
import enum

class AppearanceModifierType(enum.Int):
    SET_CAS_PART = 0
    RANDOMIZE_BODY_TYPE_COLOR = 1
    RANDOMIZE_SKINTONE_FROM_TAGS = 2
    GENERATE_OUTFIT = 3
    RANDOMIZE_CAS_PART = 4
    SET_ATTACHMENT = 5