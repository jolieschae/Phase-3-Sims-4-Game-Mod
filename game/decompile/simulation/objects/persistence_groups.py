# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\persistence_groups.py
# Compiled at: 2014-03-03 19:40:53
# Size of source mod 2**32: 350 bytes
import enum

class PersistenceGroups(enum.Int, export=False):
    NONE = 0
    OBJECT = 1
    SIM = 2
    IN_OPEN_STREET = 3