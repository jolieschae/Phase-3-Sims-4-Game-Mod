# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\aspirations\aspiration_types.py
# Compiled at: 2019-01-10 13:12:50
# Size of source mod 2**32: 554 bytes
import enum

class AspriationType(enum.Int):
    BASIC = 0
    FULL_ASPIRATION = 1
    SIM_INFO_PANEL = 2
    CAREER = 3
    WHIM_SET = 4
    FAMILIAL = 5
    NOTIFICATION = 6
    ASSIGNMENT = 7
    ZONE_DIRECTOR = 8
    TIMED_ASPIRATION = 9
    GIG = 10