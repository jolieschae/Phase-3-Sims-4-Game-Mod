# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\portals\portal_tuning.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 1987 bytes
from sims4.tuning.dynamic_enum import DynamicEnumFlags
from sims4.tuning.tunable import TunableRange
import enum

class PortalTuning:
    SURFACE_PORTAL_HEIGH_OFFSET = TunableRange(description='\n        A height offset on meters increase the height of the raycast test\n        to consider two connecting portals valid over an objects footprint.\n        For example this height is high enough so two portals on counters pass\n        a raycast test over a stove or a sink (low objects), but is not high\n        enough to pass over a microwave (which would cause our sims to clip\n        through the object when transitioning through the portal.\n        ',
      tunable_type=float,
      default=0.2,
      minimum=0)


class PortalFlags(DynamicEnumFlags):
    DEFAULT = 0
    REQUIRE_NO_CARRY = 1
    REQUIRE_NO_CARRY_BACK = 2
    STAIRS_PORTAL_LONG = 4
    STAIRS_PORTAL_SHORT = 8
    SPECIES_HUMAN = 16
    SPECIES_DOG = 32
    SPECIES_CAT = 64
    SPECIES_SMALLDOG = 128
    SPECIES_FOX = 256
    AGE_INFANT = 512
    AGE_TODDLER = 1024
    AGE_CHILD = 2048
    AGE_TYAE = 4096
    CLEARANCE_HIGH = 8192
    CLEARANCE_MEDIUM = 16384
    CLEARANCE_LOW = 32768


class PortalType(enum.Int, export=False):
    PortalType_Wormhole = 0
    PortalType_Walk = 1
    PortalType_Animate = 2