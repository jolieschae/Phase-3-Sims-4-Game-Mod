# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\spawner_component_enums.py
# Compiled at: 2020-08-11 12:25:53
# Size of source mod 2**32: 333 bytes
import enum

class SpawnerType(enum.Int):
    GROUND = 0
    SLOT = 1
    INTERACTION = 2


class SpawnLocation(enum.Int):
    SPAWNER = 0
    PORTAL = 1