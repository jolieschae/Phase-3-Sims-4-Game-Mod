# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\adoption\adoption_liability.py
# Compiled at: 2017-04-10 20:13:28
# Size of source mod 2**32: 793 bytes
from interactions.liability import Liability

class AdoptionLiability(Liability):
    LIABILITY_TOKEN = 'AdoptionLiability'

    def __init__(self, household, sim_ids, **kwargs):
        (super().__init__)(**kwargs)
        self._household = household
        self._sim_ids = sim_ids

    def on_add(self, interaction):
        for sim_id in self._sim_ids:
            self._household.add_adopting_sim(sim_id)

    def release(self):
        for sim_id in self._sim_ids:
            self._household.remove_adopting_sim(sim_id)