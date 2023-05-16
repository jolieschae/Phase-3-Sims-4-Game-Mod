# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\university\university_scholarship_enums.py
# Compiled at: 2019-08-20 21:43:41
# Size of source mod 2**32: 313 bytes
import enum

class ScholarshipStatus(enum.Int):
    ACTIVE = 0
    PENDING = 1
    ACCEPTED = 2
    REJECTED = 3