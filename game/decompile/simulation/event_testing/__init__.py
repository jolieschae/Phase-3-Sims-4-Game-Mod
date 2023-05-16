# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\__init__.py
# Compiled at: 2018-11-09 19:40:16
# Size of source mod 2**32: 357 bytes
import enum

class TargetIdTypes(enum.Int):
    DEFAULT = 0
    INSTANCE = 1
    DEFINITION = 2
    HOUSEHOLD = 3
    PICKED_ITEM_ID = 4