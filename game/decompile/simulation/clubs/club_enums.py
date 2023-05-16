# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\clubs\club_enums.py
# Compiled at: 2015-10-21 19:16:44
# Size of source mod 2**32: 2117 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
import enum

class ClubRuleEncouragementStatus(enum.Int):
    ENCOURAGED = 0
    DISCOURAGED = 1
    NO_EFFECT = 2


class ClubHangoutSetting(enum.Int, export=False):
    HANGOUT_NONE = 0
    HANGOUT_VENUE = 1
    HANGOUT_LOT = 2


class ClubGatheringKeys:
    ASSOCIATED_CLUB_ID = 'associated_club_id'
    DISBAND_TICKS = 'disband_ticks'
    GATHERING_BUFF = 'gathering_buff'
    GATHERING_VIBE = 'gathering_vibe'
    START_SOURCE = 'start_source'
    HOUSEHOLD_ID_OVERRIDE = 'household_id_override'


class ClubGatheringStartSource(enum.Int, export=False):
    DEFAULT = 0
    APPLY_FOR_INVITE = 1


class ClubOutfitSetting(enum.Int):
    NO_OUTFIT = 0
    STYLE = 1
    COLOR = 2
    OVERRIDE = 3


class ClubGatheringVibe(DynamicEnum):
    NO_VIBE = 0