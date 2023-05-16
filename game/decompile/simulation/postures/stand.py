# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\stand.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 1373 bytes
from interactions.base.super_interaction import SuperInteraction
from sims4.tuning.tunable import TunableReference
import services, sims4.resources

class StandSuperInteraction(SuperInteraction):
    STAND_POSTURE_TYPE = TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.POSTURE)), description='The Posture Type for the Stand posture.')

    @classmethod
    def _is_linked_to(cls, super_affordance):
        return cls is not super_affordance

    def get_cancel_replacement_aops_contexts_postures(self, can_transfer_ownership=True, carry_cancel_override=None):
        if self.target is None:
            if self.sim.posture.posture_type == self.STAND_POSTURE_TYPE:
                return []
        return super().get_cancel_replacement_aops_contexts_postures(can_transfer_ownership=can_transfer_ownership, carry_cancel_override=carry_cancel_override)