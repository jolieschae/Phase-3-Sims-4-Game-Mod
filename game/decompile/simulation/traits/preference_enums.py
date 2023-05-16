# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\preference_enums.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 1039 bytes
from traits.trait_type import TraitType
import enum

class PreferenceTypes(enum.Int):
    LIKE = TraitType.LIKE
    DISLIKE = TraitType.DISLIKE


class GameplayObjectPreferenceTypes(enum.Int):
    NONE = 0
    UNSURE = 1
    DISLIKE = 2
    LIKE = 3
    LOVE = 4


class PreferenceSubject(enum.Int):
    OBJECT = 0
    DECOR = 1
    CHARACTERISTIC = 2
    CONVERSATION = 3