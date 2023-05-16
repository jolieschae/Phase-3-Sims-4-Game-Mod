# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\organizations\organization_enums.py
# Compiled at: 2019-06-25 14:16:07
# Size of source mod 2**32: 524 bytes
from sims4.tuning.dynamic_enum import DynamicEnumLocked

class OrganizationStatusEnum(DynamicEnumLocked):
    ACTIVE = 0
    INACTIVE = 1
    NONMEMBER = 2


class OrganizationMembershipActionEnum(DynamicEnumLocked):
    JOIN = 0
    LEAVE = 1
    UPDATE = 2