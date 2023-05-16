# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\trait_plumbbob_override.py
# Compiled at: 2016-07-14 16:28:10
# Size of source mod 2**32: 1504 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableEnumEntry
from sims4.tuning.tunable_hash import TunableStringHash64

class PlumbbobOverridePriority(DynamicEnum):
    INVALID = 0


class PlumbbobOverrideRequest(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'active_sim_plumbbob':TunableStringHash64(description='\n            The plumbbob model to use when this is the active sim,\n            '), 
     'active_sim_club_leader_plumbbob':TunableStringHash64(description="\n            The plumbbob model to use when this is the active sim and they're\n            the leader of the club.\n            "), 
     'priority':TunableEnumEntry(description='\n            The requests priority.\n            ',
       tunable_type=PlumbbobOverridePriority,
       default=PlumbbobOverridePriority.INVALID,
       invalid_enums={
      PlumbbobOverridePriority.INVALID})}