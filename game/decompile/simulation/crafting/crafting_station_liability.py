# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\crafting_station_liability.py
# Compiled at: 2016-08-09 18:37:06
# Size of source mod 2**32: 1430 bytes
from interactions import ParticipantType
from interactions.liability import Liability
from sims4.tuning.tunable import HasTunableFactory

class CraftingStationLiability(Liability, HasTunableFactory):
    LIABILITY_TOKEN = 'CraftingStation'

    def __init__(self, interaction, **kwargs):
        (super().__init__)(**kwargs)
        self._obj = interaction.get_participant(ParticipantType.Object)
        self._removed_from_cache = False

    def on_run(self):
        if self._removed_from_cache:
            return
        if self._obj is None:
            return
        self._obj.remove_from_crafting_cache()
        self._removed_from_cache = True

    def release(self):
        if not self._removed_from_cache:
            return
        if self._obj is None:
            return
        self._obj.add_to_crafting_cache()