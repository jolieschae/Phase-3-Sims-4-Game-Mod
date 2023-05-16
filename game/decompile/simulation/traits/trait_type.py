# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\trait_type.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 1118 bytes
import enum

class TraitType(enum.Int):
    PERSONALITY = 0
    GAMEPLAY = 1
    WALKSTYLE = 2
    HIDDEN = 4
    GHOST = 5
    ASPIRATION = 6
    TAILSTYLE = 7
    GENDER_OPTIONS = 8
    SIM_PHONE = 9
    PHASE = 10
    AGENT = 11
    INFECTION = 12
    CURSE = 13
    ROOMMATE = 14
    ROBOT_MODULE = 15
    ROBOT = 16
    PROFESSOR = 17
    UNIVERSITY_DEGREE = 18
    ROBOT_MODULE_LOCKED = 19
    BATUU_ALIEN = 20
    LIFESTYLE = 21
    LIKE = 22
    DISLIKE = 23
    FOOD_RESTRICTION = 24
    TRADITION = 25
    TEMPERAMENT = 26
    PACK_MEMBER = 27
    PACK_FRIEND = 28
    FEAR = 29
    HIGH_SCHOOL = 30
    GAMEPLAY_OBJECT_PREFERENCE = 31
    INFANT_CARRIER = 32
    GAMEPLAY_GENERIC = 33