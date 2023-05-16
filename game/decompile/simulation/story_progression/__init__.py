# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\__init__.py
# Compiled at: 2022-03-10 20:35:10
# Size of source mod 2**32: 1014 bytes
import enum

class StoryProgressionFlags(enum.IntFlags, export=False):
    DISABLED = 0
    ALLOW_POPULATION_ACTION = 1
    ALLOW_INITIAL_POPULATION = 2
    SIM_INFO_FIREMETER = 4


class StoryProgressionArcSeedReason(enum.Int, export=False):
    SYSTEM = 0
    LOOT = 1


STORY_PROGRESSION_ARC_SEED_REASON_STRINGS = {StoryProgressionArcSeedReason.SYSTEM: 'SYSTEM', 
 StoryProgressionArcSeedReason.LOOT: 'LOOT'}