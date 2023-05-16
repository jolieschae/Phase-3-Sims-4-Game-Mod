# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\adoption\adoption_interaction_loot.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 1518 bytes
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    from sims.sim_info import SimInfo
from interactions.utils.loot_basic_op import BaseTargetedLootOperation
import services, sims4
logger = sims4.log.Logger('AddAdoptedSimToFamilyLoot', default_owner='micfisher')

class AddAdoptedSimToFamilyLootOp(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'description': "\n            This loot will add the specified Sim to the Parent's household.\n            "}

    def __init__(self, **kwargs):
        (super().__init__)(**kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        adopted_sim_info = target
        parent_a = subject
        parent_b = services.sim_info_manager().get(parent_a.spouse_sim_id)
        pregnancy_tracker = parent_a.pregnancy_tracker
        if pregnancy_tracker is not None:
            pregnancy_tracker.initialize_sim_info(adopted_sim_info, parent_a, parent_b)
        else:
            logger.warn('Attempted to add a Sim to a family, but the parent Sim has no pregnancy tracker. Parent: {}', parent_a.full_name)