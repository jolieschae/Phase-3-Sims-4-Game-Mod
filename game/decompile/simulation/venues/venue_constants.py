# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\venue_constants.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 1485 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.tunable import TunableReference
import enum, services, sims4.resources

class ZoneDirectorRequestType(enum.Int, export=False):
    CAREER_EVENT = ...
    SOCIAL_EVENT = ...
    DRAMA_SCHEDULER = ...
    AMBIENT_SUB_VENUE = ...
    AMBIENT_VENUE = ...


class NPCSummoningPurpose(DynamicEnum):
    DEFAULT = 0
    PLAYER_BECOMES_GREETED = 1
    BRING_PLAYER_SIM_TO_LOT = 2
    ZONE_FIXUP = 3