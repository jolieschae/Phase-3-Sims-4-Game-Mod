# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\lod_mixin.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 706 bytes
from sims.sim_info_lod import SimInfoLODLevel
from sims4.tuning.tunable import TunableEnumEntry

class HasTunableLodMixin:
    INSTANCE_TUNABLES = {'min_lod_value': TunableEnumEntry(description='\n            The minimum Sim info LOD necessary for this information to persist\n            on the sim info. e.g. A statistic tuned to FULL will not persist on\n            sims that are lower than FULL. LOD order, high to low, is FULL, INTERACTED,\n            BASE, BACKGROUND, MINIMUM.\n            ',
                        tunable_type=SimInfoLODLevel,
                        default=(SimInfoLODLevel.BACKGROUND))}