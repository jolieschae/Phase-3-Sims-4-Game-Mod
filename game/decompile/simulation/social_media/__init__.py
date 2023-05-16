# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\social_media\__init__.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 923 bytes
import enum

class SocialMediaNarrative(enum.Int):
    FRIENDLY = 0
    FLIRTY = 1
    MEAN = 2
    PROUD = 3
    EMBARRASSED = 4
    EXCITED = 5
    HAPPY = 6
    SAD = 7
    STRESSED = 8
    FUNNY = 9
    UNCOMFORTABLE = 10
    PRANK = 11


class SocialMediaPostType(enum.Int):
    DEFAULT = 0
    DIRECT_MESSAGE = 1
    FRIEND_REQUEST = 2
    FOLLOWERS_UPDATE = 3
    PUBLIC_POST = 4


class SocialMediaPolarity(enum.Int):
    POSITIVE = 0
    NEGATIVE = 1