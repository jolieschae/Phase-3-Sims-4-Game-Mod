# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\fixup\sim_info_fixup_action.py
# Compiled at: 2020-05-01 15:47:38
# Size of source mod 2**32: 920 bytes
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit
import enum

class SimInfoFixupActionTiming(enum.Int):
    ON_FIRST_SIMINFO_LOAD = 0
    ON_ADDED_TO_ACTIVE_HOUSEHOLD = 1
    ON_SIM_INFO_CREATED = 2


class _SimInfoFixupAction(HasTunableSingletonFactory, AutoFactoryInit):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.fixup_guid = 0

    def __call__(self, sim_info):
        raise NotImplementedError