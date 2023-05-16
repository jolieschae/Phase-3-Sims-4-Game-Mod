# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\business\business_enums.py
# Compiled at: 2017-04-26 21:36:51
# Size of source mod 2**32: 1959 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
import enum

class BusinessType(enum.Int):
    INVALID = 0
    RETAIL = 1
    RESTAURANT = 2
    VET = 3


class BusinessEmployeeType(DynamicEnum):
    INVALID = 0


class BusinessCustomerStarRatingBuffBuckets(DynamicEnum):
    INVALID = 0


class BusinessAdvertisingType(DynamicEnum):
    INVALID = 0


class BusinessQualityType(DynamicEnum):
    INVALID = 0