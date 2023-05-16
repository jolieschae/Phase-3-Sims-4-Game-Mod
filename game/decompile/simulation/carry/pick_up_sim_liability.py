# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\carry\pick_up_sim_liability.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 1606 bytes
from interactions.liability import Liability

class PickUpSimLiability(Liability):
    LIABILITY_TOKEN = 'PickUpSimLiability'

    def __init__(self, original_interaction, on_finish_callback):
        super().__init__()
        self._interaction = None
        self._original_interaction = original_interaction
        self._on_finish_callback = on_finish_callback
        original_interaction.is_waiting_pickup_putdown = True

    @property
    def original_interaction(self):
        return self._original_interaction

    def on_add(self, interaction):
        self._interaction = interaction

    def should_transfer(self, continuation):
        return continuation.is_putdown or continuation.carry_target is self._interaction.target

    def transfer(self, interaction):
        self._interaction = interaction

    def release(self):
        if self._on_finish_callback is not None:
            self._on_finish_callback(self._interaction)
        self._original_interaction.is_waiting_pickup_putdown = False