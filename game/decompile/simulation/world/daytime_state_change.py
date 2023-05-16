# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\daytime_state_change.py
# Compiled at: 2019-01-17 17:28:39
# Size of source mod 2**32: 213 bytes
import enum

class DaytimeStateChange(enum.Int):
    Sunrise = 1
    Sunset = 2