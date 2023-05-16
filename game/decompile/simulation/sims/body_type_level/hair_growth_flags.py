# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\body_type_level\hair_growth_flags.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 922 bytes
import enum
from sims.outfits.outfit_enums import BodyType

class HairGrowthFlags(enum.IntFlags, export=False):
    NONE = 0
    FACIAL_HAIR = 256
    ARM_HAIR = 512
    LEG_HAIR = 1024
    TORSOFRONT_HAIR = 2048
    TORSOBACK_HAIR = 4096
    ALL = FACIAL_HAIR | ARM_HAIR | LEG_HAIR | TORSOFRONT_HAIR | TORSOBACK_HAIR


HAIR_GROWTH_TO_BODY_TYPE = {HairGrowthFlags.NONE: BodyType.NONE, 
 HairGrowthFlags.FACIAL_HAIR: BodyType.FACIAL_HAIR, 
 HairGrowthFlags.ARM_HAIR: BodyType.BODYHAIR_ARM, 
 HairGrowthFlags.LEG_HAIR: BodyType.BODYHAIR_LEG, 
 HairGrowthFlags.TORSOFRONT_HAIR: BodyType.BODYHAIR_TORSOFRONT, 
 HairGrowthFlags.TORSOBACK_HAIR: BodyType.BODYHAIR_TORSOBACK}