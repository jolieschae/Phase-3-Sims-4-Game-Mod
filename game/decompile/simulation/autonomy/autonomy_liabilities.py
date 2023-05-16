# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\autonomy\autonomy_liabilities.py
# Compiled at: 2017-06-08 19:33:37
# Size of source mod 2**32: 609 bytes
from interactions.liability import Liability

class AutonomousGetComfortableLiability(Liability):
    LIABILITY_TOKEN = 'AutonomousGetComfortable'

    def __init__(self, sim, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._sim = sim

    def release(self):
        self._sim.push_get_comfortable_interaction()