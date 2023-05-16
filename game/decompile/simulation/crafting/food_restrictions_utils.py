# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\food_restrictions_utils.py
# Compiled at: 2021-02-22 12:43:26
# Size of source mod 2**32: 576 bytes
import services, sims4
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.tunable import TunableReference, TunableEnumEntry, TunableMapping
logger = sims4.log.Logger('Food Restrictions')

class FoodRestrictionUtils:

    class FoodRestrictionEnum(DynamicEnum):
        INVALID = 0