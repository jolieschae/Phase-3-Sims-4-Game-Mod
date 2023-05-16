# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\route_events\route_event_utils.py
# Compiled at: 2018-01-25 15:11:29
# Size of source mod 2**32: 290 bytes
import enum

class RouteEventSchedulePreference(enum.Int):
    BEGINNING = 0
    END = 1
    RANDOM = 2